"""Create and fetch submissions (writing, programming, design); ties to task_assignments + tasks."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.extensions import mongo
from app.schemas.submission_schema import (
    SUBMISSION_STATUS_PENDING,
    TASK_TYPE_DESIGN,
    TASK_TYPE_PROGRAMMING,
    TASK_TYPE_WRITING,
)
from app.services.evaluation_service import evaluate_submission_by_id


def _utcnow():
    return datetime.now(timezone.utc)


def _oid(s: str) -> ObjectId:
    try:
        return ObjectId(s)
    except Exception as e:
        raise ValueError('Invalid id') from e


def _load_assignment_and_task(user_id: str, assignment_id: str) -> tuple[ObjectId, ObjectId, dict, dict]:
    """Validate assignment belongs to user and return ids + task doc."""
    uid = _oid(user_id)
    aid = _oid(assignment_id)

    assignment = mongo.db.task_assignments.find_one({'_id': aid, 'user_id': uid})
    if not assignment:
        raise ValueError('Assignment not found or access denied')

    st = (assignment.get('status') or '').lower()
    if st not in ('claimed', 'in_progress', 'submitted'):
        raise ValueError('Assignment must be active (in progress) to submit')

    tid = assignment.get('task_id')
    if not tid:
        raise ValueError('Assignment has no task')

    task = mongo.db.tasks.find_one({'_id': tid})
    if not task:
        raise ValueError('Task not found')

    return uid, aid, assignment, task


def _assert_task_type(task: dict, expected: str) -> None:
    ttype = (task.get('task_type') or task.get('type') or '').lower()
    if ttype != expected:
        raise ValueError(
            f'This submission type does not match the task (expected task_type: {expected})'
        )


def create_writing_submission(user_id: str, assignment_id: str, text_content: str) -> dict[str, Any]:
    if not text_content or not str(text_content).strip():
        raise ValueError('text_content is required')

    uid, aid, _assignment, task = _load_assignment_and_task(user_id, assignment_id)
    _assert_task_type(task, TASK_TYPE_WRITING)

    now = _utcnow()
    doc = {
        'user_id': uid,
        'assignment_id': aid,
        'task_id': task['_id'],
        'task_type': TASK_TYPE_WRITING,
        'text_content': text_content.strip(),
        'status': SUBMISSION_STATUS_PENDING,
        'created_at': now,
        'updated_at': now,
    }

    result = mongo.db.submissions.insert_one(doc)
    sub_id = str(result.inserted_id)
    evaluate_submission_by_id(sub_id)
    out = mongo.db.submissions.find_one({'_id': result.inserted_id})
    return _serialize_submission(out)


def create_programming_submission(user_id: str, assignment_id: str, code_content: str) -> dict[str, Any]:
    if not code_content or not str(code_content).strip():
        raise ValueError('code_content is required')

    uid, aid, _assignment, task = _load_assignment_and_task(user_id, assignment_id)
    _assert_task_type(task, TASK_TYPE_PROGRAMMING)

    lang = (task.get('language') or 'python').lower()
    if lang != 'python':
        raise ValueError('Only Python submissions are supported in this version (set task.language to "python")')

    now = _utcnow()
    doc = {
        'user_id': uid,
        'assignment_id': aid,
        'task_id': task['_id'],
        'task_type': TASK_TYPE_PROGRAMMING,
        'code_content': code_content.strip(),
        'status': SUBMISSION_STATUS_PENDING,
        'created_at': now,
        'updated_at': now,
    }

    result = mongo.db.submissions.insert_one(doc)
    sub_id = str(result.inserted_id)
    evaluate_submission_by_id(sub_id)
    out = mongo.db.submissions.find_one({'_id': result.inserted_id})
    return _serialize_submission(out)


def create_design_submission(
    user_id: str,
    assignment_id: str,
    file_storage: FileStorage,
    student_notes: str | None = None,
) -> dict[str, Any]:
    if not file_storage or not getattr(file_storage, 'filename', None):
        raise ValueError('file is required')

    uid, aid, _assignment, task = _load_assignment_and_task(user_id, assignment_id)
    _assert_task_type(task, TASK_TYPE_DESIGN)

    notes = (student_notes or '').strip() or None

    now = _utcnow()
    doc: dict[str, Any] = {
        'user_id': uid,
        'assignment_id': aid,
        'task_id': task['_id'],
        'task_type': TASK_TYPE_DESIGN,
        'status': SUBMISSION_STATUS_PENDING,
        'student_notes': notes,
        'design_file': {},
        'created_at': now,
        'updated_at': now,
    }

    result = mongo.db.submissions.insert_one(doc)
    sid = result.inserted_id
    sub_id_str = str(sid)

    try:
        meta = _save_design_upload(uid, sub_id_str, file_storage)
        mongo.db.submissions.update_one(
            {'_id': sid},
            {'$set': {'design_file': meta, 'updated_at': _utcnow()}},
        )
        evaluate_submission_by_id(sub_id_str)
    except Exception:
        mongo.db.submissions.delete_one({'_id': sid})
        raise

    out = mongo.db.submissions.find_one({'_id': sid})
    return _serialize_submission(out)


def _save_design_upload(user_oid: ObjectId, submission_id: str, file_storage: FileStorage) -> dict[str, Any]:
    root = current_app.config.get('UPLOAD_FOLDER') or 'uploads'
    user_part = str(user_oid)
    subdir = os.path.join(root, 'design', user_part, submission_id)
    os.makedirs(subdir, exist_ok=True)

    orig = file_storage.filename or 'upload'
    safe = secure_filename(orig)
    if not safe:
        safe = 'upload.bin'
    ext = os.path.splitext(safe)[1].lower()
    dest_name = f'original{ext}' if ext else 'original'
    dest_path = os.path.join(subdir, dest_name)
    file_storage.save(dest_path)

    size = os.path.getsize(dest_path)
    rel = '/'.join(['design', user_part, submission_id, dest_name])
    return {
        'relative_path': rel,
        'original_filename': orig,
        'content_type': (file_storage.content_type or '') or '',
        'size_bytes': int(size),
    }


def get_submission(submission_id: str, user_id: str) -> dict | None:
    try:
        sid = ObjectId(submission_id)
        uid = ObjectId(user_id)
    except Exception:
        return None

    sub = mongo.db.submissions.find_one({'_id': sid, 'user_id': uid})
    if not sub:
        return None
    return _serialize_submission(sub)


def get_latest_submission_for_assignment(assignment_id: str, user_id: str) -> dict | None:
    try:
        aid = ObjectId(assignment_id)
        uid = ObjectId(user_id)
    except Exception:
        return None

    sub = mongo.db.submissions.find_one(
        {'assignment_id': aid, 'user_id': uid},
        sort=[('_id', -1)],
    )
    if not sub:
        return None
    return _serialize_submission(sub)


def _serialize_submission(sub: dict) -> dict:
    out = dict(sub)
    out['id'] = str(out.pop('_id'))
    out['user_id'] = str(out['user_id'])
    out['assignment_id'] = str(out['assignment_id'])
    out['task_id'] = str(out['task_id'])
    for key in ('created_at', 'updated_at'):
        if out.get(key) is not None and hasattr(out[key], 'isoformat'):
            out[key] = out[key].isoformat()
    # Do not expose server filesystem paths beyond relative upload path
    df = out.get('design_file')
    if isinstance(df, dict) and df.get('relative_path'):
        out['design_file'] = {
            'relative_path': df.get('relative_path'),
            'original_filename': df.get('original_filename'),
            'content_type': df.get('content_type'),
            'size_bytes': df.get('size_bytes'),
        }
    return out
