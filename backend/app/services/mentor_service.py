"""FR5: Mentor roster, submission review queue, and feedback storage."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId

from app.extensions import mongo
from app.schemas.mentor_schema import (
    MENTOR_REVIEW_STATUS_COMPLETED,
    MENTOR_REVIEW_STATUS_PENDING,
)
from app.schemas.submission_schema import SUBMISSION_STATUS_EVALUATED
from app.services import submission_service as submission_svc


def _utcnow():
    return datetime.now(timezone.utc)


def _oid(s: str, label: str = 'id') -> ObjectId:
    try:
        return ObjectId(s)
    except Exception as e:
        raise ValueError(f'Invalid {label}') from e


def ensure_mentor_indexes() -> None:
    """Idempotent index creation for mentor collections."""
    try:
        mongo.db.mentor_roster.create_index(
            [('mentor_id', 1), ('student_id', 1)],
            unique=True,
            name='mentor_student_unique',
        )
    except Exception:
        pass
    try:
        mongo.db.mentor_reviews.create_index(
            [('submission_id', 1)],
            unique=True,
            name='mentor_review_per_submission',
        )
    except Exception:
        pass
    try:
        mongo.db.mentor_reviews.create_index(
            [('mentor_id', 1), ('status', 1), ('completed_at', -1)],
            name='mentor_review_history',
        )
    except Exception:
        pass


def _roster_student_ids(mentor_id: ObjectId) -> list[ObjectId]:
    cur = mongo.db.mentor_roster.find({'mentor_id': mentor_id, 'active': True})
    return [r['student_id'] for r in cur if r.get('student_id')]


def assert_mentor_can_access_student(mentor_id: str, student_id: str) -> tuple[ObjectId, ObjectId]:
    mid = _oid(mentor_id, 'mentor_id')
    sid = _oid(student_id, 'student_id')
    link = mongo.db.mentor_roster.find_one(
        {'mentor_id': mid, 'student_id': sid, 'active': True},
    )
    if not link:
        raise PermissionError('Student is not on your roster or link is inactive')
    return mid, sid


def list_assigned_students(mentor_id: str) -> list[dict[str, Any]]:
    mid = _oid(mentor_id, 'mentor_id')
    rows = list(mongo.db.mentor_roster.find({'mentor_id': mid, 'active': True}))
    out: list[dict[str, Any]] = []
    for r in rows:
        su = mongo.db.users.find_one({'_id': r['student_id']}, {'password_hash': 0})
        if not su:
            continue
        out.append(
            {
                'id': str(su['_id']),
                'email': su.get('email'),
                'name': su.get('name'),
                'roster_since': r.get('created_at').isoformat()
                if r.get('created_at') and hasattr(r['created_at'], 'isoformat')
                else None,
            }
        )
    return out


def get_student_progress_summary(mentor_id: str, student_id: str) -> dict[str, Any]:
    assert_mentor_can_access_student(mentor_id, student_id)
    sid = _oid(student_id, 'student_id')

    assignments = list(mongo.db.task_assignments.find({'user_id': sid}))
    by_status: dict[str, int] = {}
    for a in assignments:
        st = (a.get('status') or 'unknown').lower()
        by_status[st] = by_status.get(st, 0) + 1

    subs = mongo.db.submissions.count_documents({'user_id': sid})
    completed_reviews = mongo.db.mentor_reviews.count_documents(
        {'student_id': sid, 'mentor_id': _oid(mentor_id, 'mentor_id'), 'status': MENTOR_REVIEW_STATUS_COMPLETED},
    )

    return {
        'student_id': student_id,
        'assignments_total': len(assignments),
        'assignments_by_status': by_status,
        'submissions_total': subs,
        'mentor_reviews_completed_for_this_mentor': completed_reviews,
    }


def _serialize_task_min(t: dict | None) -> dict[str, Any] | None:
    if not t:
        return None
    return {
        'id': str(t['_id']),
        'title': t.get('title'),
        'domain': t.get('domain'),
        'task_type': (t.get('task_type') or t.get('type') or '').lower(),
        'description': (t.get('description') or '')[:500],
    }


def _submission_summary_row(sub: dict, task: dict | None) -> dict[str, Any]:
    ev = sub.get('evaluation') or {}
    mreq = ev.get('mentor_review_required')
    base = {
        'id': str(sub['_id']),
        'student_id': str(sub['user_id']),
        'assignment_id': str(sub['assignment_id']),
        'task_id': str(sub['task_id']),
        'task_type': sub.get('task_type'),
        'status': sub.get('status'),
        'created_at': sub['created_at'].isoformat()
        if sub.get('created_at') and hasattr(sub['created_at'], 'isoformat')
        else None,
        'mentor_review_required': mreq if isinstance(mreq, bool) else None,
        'task': _serialize_task_min(task),
    }
    return base


def list_pending_submissions_for_mentor(mentor_id: str, limit: int = 50) -> list[dict[str, Any]]:
    """Submissions from roster students that are not yet completed by this mentor."""
    mid = _oid(mentor_id, 'mentor_id')
    student_ids = _roster_student_ids(mid)
    if not student_ids:
        return []

    done_sub_ids = {
        r['submission_id']
        for r in mongo.db.mentor_reviews.find(
            {'mentor_id': mid, 'status': MENTOR_REVIEW_STATUS_COMPLETED},
            {'submission_id': 1},
        )
    }

    query: dict[str, Any] = {
        'user_id': {'$in': student_ids},
        'status': SUBMISSION_STATUS_EVALUATED,
    }
    cursor = mongo.db.submissions.find(query).sort('created_at', -1).limit(limit * 2)
    out: list[dict[str, Any]] = []
    for sub in cursor:
        if sub['_id'] in done_sub_ids:
            continue
        tid = sub.get('task_id')
        task = mongo.db.tasks.find_one({'_id': tid}) if tid else None
        row = _submission_summary_row(sub, task)
        rev = mongo.db.mentor_reviews.find_one({'submission_id': sub['_id'], 'mentor_id': mid})
        row['mentor_review_status'] = rev.get('status') if rev else None
        out.append(row)
        if len(out) >= limit:
            break

    def sort_key(r: dict) -> tuple:
        req = r.get('mentor_review_required')
        return (0 if req else 1, r.get('created_at') or '')

    out.sort(key=sort_key)
    return out[:limit]


def get_submission_detail_for_mentor(mentor_id: str, submission_id: str) -> dict[str, Any] | None:
    mid = _oid(mentor_id, 'mentor_id')
    sid = _oid(submission_id, 'submission_id')
    sub = mongo.db.submissions.find_one({'_id': sid})
    if not sub:
        return None
    student_oid = sub.get('user_id')
    link = mongo.db.mentor_roster.find_one(
        {'mentor_id': mid, 'student_id': student_oid, 'active': True},
    )
    if not link:
        raise PermissionError('You cannot access this submission')

    task = mongo.db.tasks.find_one({'_id': sub.get('task_id')})
    student = mongo.db.users.find_one({'_id': student_oid}, {'password_hash': 0})
    review = mongo.db.mentor_reviews.find_one({'submission_id': sid, 'mentor_id': mid})

    ser_sub = submission_svc._serialize_submission(sub)
    return {
        'submission': ser_sub,
        'task': _serialize_task_min(task),
        'student': {
            'id': str(student['_id']) if student else str(student_oid),
            'email': student.get('email') if student else None,
            'name': student.get('name') if student else None,
        },
        'mentor_review': _serialize_review(review) if review else None,
    }


def _serialize_review(r: dict | None) -> dict[str, Any] | None:
    if not r:
        return None
    out = {
        'id': str(r['_id']),
        'submission_id': str(r['submission_id']),
        'mentor_id': str(r['mentor_id']),
        'student_id': str(r['student_id']),
        'feedback': r.get('feedback'),
        'status': r.get('status'),
        'created_at': r['created_at'].isoformat()
        if r.get('created_at') and hasattr(r['created_at'], 'isoformat')
        else None,
        'updated_at': r['updated_at'].isoformat()
        if r.get('updated_at') and hasattr(r['updated_at'], 'isoformat')
        else None,
        'completed_at': r['completed_at'].isoformat()
        if r.get('completed_at') and hasattr(r['completed_at'], 'isoformat')
        else None,
    }
    return out


def submit_mentor_feedback(mentor_id: str, submission_id: str, feedback: str) -> dict[str, Any]:
    if not feedback or not str(feedback).strip():
        raise ValueError('feedback is required')
    feedback = str(feedback).strip()
    if len(feedback) > 20000:
        raise ValueError('feedback is too long')

    mid = _oid(mentor_id, 'mentor_id')
    sid = _oid(submission_id, 'submission_id')
    sub = mongo.db.submissions.find_one({'_id': sid})
    if not sub:
        raise ValueError('Submission not found')
    student_oid = sub.get('user_id')
    link = mongo.db.mentor_roster.find_one(
        {'mentor_id': mid, 'student_id': student_oid, 'active': True},
    )
    if not link:
        raise PermissionError('You cannot review this submission')

    now = _utcnow()
    existing = mongo.db.mentor_reviews.find_one({'submission_id': sid})
    doc = {
        'submission_id': sid,
        'mentor_id': mid,
        'student_id': student_oid,
        'feedback': feedback,
        'status': MENTOR_REVIEW_STATUS_COMPLETED,
        'updated_at': now,
        'completed_at': now,
    }
    if existing:
        doc['created_at'] = existing.get('created_at', now)
        mongo.db.mentor_reviews.update_one({'_id': existing['_id']}, {'$set': doc})
        out = mongo.db.mentor_reviews.find_one({'_id': existing['_id']})
    else:
        doc['created_at'] = now
        ins = mongo.db.mentor_reviews.insert_one(doc)
        out = mongo.db.mentor_reviews.find_one({'_id': ins.inserted_id})

    return _serialize_review(out) or {}


def list_feedback_history(mentor_id: str, limit: int = 50, skip: int = 0) -> tuple[list[dict[str, Any]], int]:
    mid = _oid(mentor_id, 'mentor_id')
    q = {'mentor_id': mid, 'status': MENTOR_REVIEW_STATUS_COMPLETED}
    total = mongo.db.mentor_reviews.count_documents(q)
    cursor = (
        mongo.db.mentor_reviews.find(q).sort('completed_at', -1).skip(max(0, skip)).limit(min(100, max(1, limit)))
    )
    rows: list[dict[str, Any]] = []
    for r in cursor:
        sub = mongo.db.submissions.find_one({'_id': r['submission_id']})
        task = mongo.db.tasks.find_one({'_id': sub.get('task_id')}) if sub else None
        student = mongo.db.users.find_one({'_id': r['student_id']}, {'password_hash': 0})
        item = _serialize_review(r)
        if item:
            item['submission_summary'] = _submission_summary_row(sub, task) if sub else None
            item['student'] = {
                'id': str(student['_id']) if student else str(r['student_id']),
                'name': (student.get('name') if student else None),
                'email': (student.get('email') if student else None),
            }
            rows.append(item)
    return rows, total
