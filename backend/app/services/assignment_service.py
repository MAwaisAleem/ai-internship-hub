"""List and fetch task assignments for the current student (FR3 / FR4 integration)."""
from __future__ import annotations

from typing import Any

from bson import ObjectId
from bson.errors import InvalidId

from app.extensions import mongo


def _iso(dt: Any) -> str | None:
    if dt is None:
        return None
    if hasattr(dt, 'isoformat'):
        return dt.isoformat()
    return str(dt)


def _serialize_task(t: dict) -> dict[str, Any]:
    """Task fields safe for student UI (no secrets)."""
    tt = (t.get('task_type') or t.get('type') or '').lower()
    out: dict[str, Any] = {
        'id': str(t['_id']),
        'title': t.get('title') or '',
        'description': t.get('description') or '',
        'task_type': tt,
        'domain': t.get('domain'),
        'difficulty': t.get('difficulty'),
        'status': t.get('status'),
    }
    if tt == 'writing':
        out['constraints'] = {
            'min_words': t.get('min_words'),
            'max_words': t.get('max_words'),
        }
    elif tt == 'programming':
        out['constraints'] = {
            'language': (t.get('language') or 'python').lower(),
        }
    elif tt == 'design':
        out['constraints'] = {
            'allowed_extensions': t.get('allowed_extensions'),
            'max_file_mb': t.get('max_file_mb') or t.get('max_upload_mb'),
        }
    return out


def _serialize_assignment_row(a: dict, task: dict | None) -> dict[str, Any]:
    return {
        'id': str(a['_id']),
        'status': a.get('status'),
        'claimed_at': _iso(a.get('claimed_at')),
        'started_at': _iso(a.get('started_at')),
        'task': _serialize_task(task) if task else None,
    }


def list_assignments_for_student(user_id: str) -> list[dict[str, Any]]:
    try:
        uid = ObjectId(user_id)
    except Exception:
        return []

    cursor = mongo.db.task_assignments.find({'user_id': uid}).sort('claimed_at', -1)
    rows: list[dict[str, Any]] = []
    for a in cursor:
        tid = a.get('task_id')
        task = mongo.db.tasks.find_one({'_id': tid}) if tid else None
        rows.append(_serialize_assignment_row(a, task))
    return rows


def get_assignment_for_student(user_id: str, assignment_id: str) -> dict[str, Any] | None:
    try:
        uid = ObjectId(user_id)
        aid = ObjectId(assignment_id)
    except (InvalidId, Exception):
        return None

    a = mongo.db.task_assignments.find_one({'_id': aid, 'user_id': uid})
    if not a:
        return None

    tid = a.get('task_id')
    task = mongo.db.tasks.find_one({'_id': tid}) if tid else None
    if not task:
        return None

    return _serialize_assignment_row(a, task)
