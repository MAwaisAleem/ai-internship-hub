"""FR3: Task catalog and student assignments."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId

from app.extensions import mongo
from app.schemas.task_schema import (
    ASSIGNMENT_IN_PROGRESS,
    TASK_STATUS_OPEN,
)
from app.services.recommendation_service import get_recommendation_snapshot_for_task


def _utcnow():
    return datetime.now(timezone.utc)


def _oid(s: str) -> ObjectId:
    try:
        return ObjectId(s)
    except Exception as e:
        raise ValueError('Invalid id') from e


def list_open_tasks(
    domain: str | None = None,
    difficulty: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[dict], int]:
    """Return serialized open tasks and total count (for pagination)."""
    query: dict[str, Any] = {'status': TASK_STATUS_OPEN}
    if domain:
        query['domain'] = domain.strip()
    if difficulty:
        query['difficulty'] = difficulty.lower().strip()

    total = mongo.db.tasks.count_documents(query)
    cursor = (
        mongo.db.tasks.find(query)
        .sort('created_at', -1)
        .skip(max(0, skip))
        .limit(min(100, max(1, limit)))
    )
    items = [_serialize_task(t) for t in cursor]
    return items, total


def get_task_by_id(task_id: str) -> dict | None:
    try:
        tid = _oid(task_id)
    except ValueError:
        return None
    t = mongo.db.tasks.find_one({'_id': tid})
    if not t:
        return None
    return _serialize_task(t)


def get_raw_task(task_id: str) -> dict | None:
    try:
        tid = _oid(task_id)
    except ValueError:
        return None
    return mongo.db.tasks.find_one({'_id': tid})


def get_user_assignments(user_id: str) -> list[dict]:
    try:
        uid = _oid(user_id)
    except ValueError:
        return []
    rows = list(mongo.db.task_assignments.find({'user_id': uid}).sort('claimed_at', -1))
    out = []
    for a in rows:
        item = {
            'id': str(a['_id']),
            'task_id': str(a['task_id']),
            'status': a.get('status'),
            'claimed_at': _iso(a.get('claimed_at')),
            'started_at': _iso(a.get('started_at')),
            'completed_at': _iso(a.get('completed_at')),
            'recommendation_snapshot': a.get('recommendation_snapshot'),
        }
        out.append(item)
    return out


def claim_task(user_id: str, task_id: str) -> dict:
    """
    Start a task: create assignment in_progress with optional recommendation snapshot.
    Raises ValueError on business rule violations.
    """
    try:
        uid = _oid(user_id)
        tid = _oid(task_id)
    except ValueError as e:
        raise ValueError('Invalid user or task id') from e

    task = mongo.db.tasks.find_one({'_id': tid})
    if not task:
        raise ValueError('Task not found')
    if task.get('status') != TASK_STATUS_OPEN:
        raise ValueError('Task is not open for assignment')

    existing = mongo.db.task_assignments.find_one({
        'user_id': uid,
        'task_id': tid,
    })
    if existing:
        st = (existing.get('status') or '').lower()
        if st == 'completed':
            raise ValueError('You have already completed this task')
        if st in ('claimed', 'in_progress', 'submitted'):
            raise ValueError('This task is already assigned to you')

    snap = get_recommendation_snapshot_for_task(user_id, task_id)
    now = _utcnow()

    doc = {
        'user_id': uid,
        'task_id': tid,
        'status': ASSIGNMENT_IN_PROGRESS,
        'claimed_at': now,
        'started_at': now,
        'completed_at': None,
        'recommendation_snapshot': snap,
    }
    result = mongo.db.task_assignments.insert_one(doc)
    return {
        'assignment_id': str(result.inserted_id),
        'task_id': task_id,
        'status': ASSIGNMENT_IN_PROGRESS,
        'claimed_at': _iso(now),
        'recommendation_snapshot': snap,
    }


def _serialize_task(t: dict) -> dict:
    out = dict(t)
    out['id'] = str(out.pop('_id'))
    if out.get('created_by'):
        out['created_by'] = str(out['created_by'])
    for key in ('created_at', 'updated_at'):
        if out.get(key) is not None and hasattr(out[key], 'isoformat'):
            out[key] = out[key].isoformat()
    return out


def _iso(dt):
    if dt is None:
        return None
    if hasattr(dt, 'isoformat'):
        return dt.isoformat()
    return dt
