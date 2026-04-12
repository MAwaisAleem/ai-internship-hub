"""Run automated evaluation on submissions (writing, programming, design)."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from flask import current_app

from app.extensions import mongo
from app.schemas.submission_schema import (
    SUBMISSION_STATUS_EVALUATED,
    SUBMISSION_STATUS_FAILED,
    TASK_TYPE_DESIGN,
    TASK_TYPE_PROGRAMMING,
    TASK_TYPE_WRITING,
)
from app.services.evaluators.design_evaluator import evaluate_design_file
from app.services.evaluators.programming_evaluator import evaluate_python_code
from app.services.evaluators.writing_evaluator import evaluate_writing_text


def _utcnow():
    return datetime.now(timezone.utc)


def evaluate_submission_by_id(submission_id: str) -> dict[str, Any]:
    """
    Load submission + task, run evaluator, persist evaluation on submission document.
    On failure, sets status failed and stores evaluation_error; returns a dict (never raises).
    """
    try:
        sid = ObjectId(submission_id)
    except InvalidId:
        return {'error': 'Invalid submission id', 'ok': False}

    sub = mongo.db.submissions.find_one({'_id': sid})
    if not sub:
        return {'error': 'Submission not found', 'ok': False}

    task_type = (sub.get('task_type') or '').lower()
    if task_type not in (TASK_TYPE_WRITING, TASK_TYPE_PROGRAMMING, TASK_TYPE_DESIGN):
        err = 'Unsupported task type for automated evaluation'
        mongo.db.submissions.update_one(
            {'_id': sid},
            {'$set': {'status': SUBMISSION_STATUS_FAILED, 'evaluation_error': err, 'updated_at': _utcnow()}},
        )
        return {'error': err, 'ok': False}

    task = mongo.db.tasks.find_one({'_id': sub.get('task_id')})
    if not task:
        err = 'Task not found'
        mongo.db.submissions.update_one(
            {'_id': sid},
            {'$set': {'status': SUBMISSION_STATUS_FAILED, 'evaluation_error': err, 'updated_at': _utcnow()}},
        )
        return {'error': err, 'ok': False}

    try:
        if task_type == TASK_TYPE_WRITING:
            text = sub.get('text_content') or ''
            task_config = {
                'min_words': task.get('min_words', 100),
                'max_words': task.get('max_words', 800),
                'keywords': task.get('keywords') or [],
                'reference_text': task.get('reference_text') or task.get('reference_passage'),
            }
            evaluation = evaluate_writing_text(text, task_config)
        elif task_type == TASK_TYPE_DESIGN:
            df = sub.get('design_file') or {}
            rel = (df.get('relative_path') or '').strip()
            orig = (df.get('original_filename') or 'upload').strip() or 'upload'
            if not rel:
                err = 'Design file metadata missing'
                mongo.db.submissions.update_one(
                    {'_id': sid},
                    {'$set': {'status': SUBMISSION_STATUS_FAILED, 'evaluation_error': err, 'updated_at': _utcnow()}},
                )
                return {'error': err, 'ok': False}

            upload_root = os.path.abspath(
                (current_app.config.get('UPLOAD_FOLDER') or '').strip() or os.path.join(os.getcwd(), 'uploads')
            )
            rel_norm = rel.replace('\\', '/').strip()
            if '..' in rel_norm.split('/') or not rel_norm.startswith('design/'):
                err = 'Invalid design file path'
                mongo.db.submissions.update_one(
                    {'_id': sid},
                    {'$set': {'status': SUBMISSION_STATUS_FAILED, 'evaluation_error': err, 'updated_at': _utcnow()}},
                )
                return {'error': err, 'ok': False}

            abs_path = os.path.abspath(os.path.join(upload_root, *rel_norm.split('/')))
            if abs_path != upload_root and not abs_path.startswith(upload_root + os.sep):
                err = 'Invalid design file path'
                mongo.db.submissions.update_one(
                    {'_id': sid},
                    {'$set': {'status': SUBMISSION_STATUS_FAILED, 'evaluation_error': err, 'updated_at': _utcnow()}},
                )
                return {'error': err, 'ok': False}
            if not os.path.isfile(abs_path):
                err = 'Design file not found on disk'
                mongo.db.submissions.update_one(
                    {'_id': sid},
                    {'$set': {'status': SUBMISSION_STATUS_FAILED, 'evaluation_error': err, 'updated_at': _utcnow()}},
                )
                return {'error': err, 'ok': False}

            task_config = {
                'allowed_extensions': task.get('allowed_extensions'),
                'max_file_mb': task.get('max_file_mb') or task.get('max_upload_mb'),
                'max_image_width': task.get('max_image_width'),
                'max_image_height': task.get('max_image_height'),
                'min_image_width': task.get('min_image_width'),
                'min_image_height': task.get('min_image_height'),
            }
            evaluation = evaluate_design_file(
                abs_path,
                orig,
                task_config,
                relative_path_for_details=rel,
            )
        else:
            # programming
            lang = (task.get('language') or 'python').lower()
            if lang != 'python':
                err = 'Only Python is supported for automated programming evaluation'
                mongo.db.submissions.update_one(
                    {'_id': sid},
                    {'$set': {'status': SUBMISSION_STATUS_FAILED, 'evaluation_error': err, 'updated_at': _utcnow()}},
                )
                return {'error': err, 'ok': False}

            code = sub.get('code_content') or ''
            task_config = {
                'test_cases': task.get('test_cases') or [],
                'timeout_seconds': float(task.get('timeout_seconds') or 5),
            }
            evaluation = evaluate_python_code(code, task_config)

        mongo.db.submissions.update_one(
            {'_id': sid},
            {
                '$set': {
                    'status': SUBMISSION_STATUS_EVALUATED,
                    'evaluation': evaluation,
                    'updated_at': _utcnow(),
                },
                '$unset': {'evaluation_error': ''},
            },
        )
        return {'evaluation': evaluation, 'ok': True}
    except Exception as e:
        mongo.db.submissions.update_one(
            {'_id': sid},
            {
                '$set': {
                    'status': SUBMISSION_STATUS_FAILED,
                    'evaluation_error': str(e),
                    'updated_at': _utcnow(),
                }
            },
        )
        return {'error': str(e), 'ok': False}
