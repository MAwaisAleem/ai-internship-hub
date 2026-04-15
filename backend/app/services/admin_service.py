"""FR8: Admin panel — aggregates and management helpers (Administrator role only)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId

from app.extensions import mongo
from app.schemas.task_schema import (
    TASK_DIFFICULTY_ADVANCED,
    TASK_DIFFICULTY_BEGINNER,
    TASK_DIFFICULTY_INTERMEDIATE,
    TASK_STATUS_CLOSED,
    TASK_STATUS_OPEN,
)
from app.services import mentor_service as mentor_svc
from app.services import submission_service as submission_svc
from app.services.auth_service import ROLES, hash_password, validate_password

_VALID_DIFFICULTIES = frozenset({
    TASK_DIFFICULTY_BEGINNER,
    TASK_DIFFICULTY_INTERMEDIATE,
    TASK_DIFFICULTY_ADVANCED,
})
_VALID_TASK_STATUS = frozenset({TASK_STATUS_OPEN, TASK_STATUS_CLOSED})


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _oid(s: str, label: str = 'id') -> ObjectId:
    try:
        return ObjectId(s)
    except Exception as e:
        raise ValueError(f'Invalid {label}') from e


def _iso(dt: Any) -> str | None:
    if dt is None:
        return None
    if hasattr(dt, 'isoformat'):
        return dt.isoformat()
    return str(dt)


def _serialize_public_user(u: dict) -> dict[str, Any]:
    return {
        'id': str(u['_id']),
        'email': u.get('email'),
        'name': u.get('name'),
        'role': u.get('role'),
    }


def ensure_admin_indexes() -> None:
    """Idempotent indexes useful for admin list/filter queries."""
    mentor_svc.ensure_mentor_indexes()
    try:
        mongo.db.submissions.create_index([('created_at', -1)], name='submissions_created_at')
    except Exception:
        pass
    try:
        mongo.db.task_assignments.create_index([('status', 1)], name='assignment_status')
    except Exception:
        pass


def get_overview() -> dict[str, Any]:
    """High-level counts for the admin dashboard."""
    ensure_admin_indexes()
    users = mongo.db.users
    by_role: dict[str, int] = {}
    for role in ROLES:
        by_role[role] = users.count_documents({'role': role})

    tasks_open = mongo.db.tasks.count_documents({'status': TASK_STATUS_OPEN})
    tasks_closed = mongo.db.tasks.count_documents({'status': TASK_STATUS_CLOSED})
    assignments = mongo.db.task_assignments.count_documents({})
    submissions = mongo.db.submissions.count_documents({})
    roster_active = mongo.db.mentor_roster.count_documents({'active': True})
    roster_total = mongo.db.mentor_roster.count_documents({})
    reviews = mongo.db.mentor_reviews.count_documents({})

    return {
        'users_total': sum(by_role.values()),
        'users_by_role': by_role,
        'tasks_open': tasks_open,
        'tasks_closed': tasks_closed,
        'task_assignments_total': assignments,
        'submissions_total': submissions,
        'mentor_roster_links_active': roster_active,
        'mentor_roster_links_total': roster_total,
        'mentor_reviews_total': reviews,
        'generated_at': _iso(_utcnow()),
    }


def get_reports_summary() -> dict[str, Any]:
    """Lightweight breakdowns for reporting (no heavy aggregation)."""
    ensure_admin_indexes()

    assignment_by_status: list[dict[str, Any]] = []
    try:
        cur = mongo.db.task_assignments.aggregate(
            [{'$group': {'_id': '$status', 'count': {'$sum': 1}}}],
        )
        assignment_by_status = [{'status': r['_id'] or 'unknown', 'count': r['count']} for r in cur]
    except Exception:
        pass

    submission_by_status: list[dict[str, Any]] = []
    try:
        cur = mongo.db.submissions.aggregate(
            [{'$group': {'_id': '$status', 'count': {'$sum': 1}}}],
        )
        submission_by_status = [{'status': r['_id'] or 'unknown', 'count': r['count']} for r in cur]
    except Exception:
        pass

    tasks_by_domain: list[dict[str, Any]] = []
    try:
        cur = mongo.db.tasks.aggregate(
            [{'$group': {'_id': '$domain', 'count': {'$sum': 1}}}],
        )
        tasks_by_domain = [{'domain': r['_id'] or 'unknown', 'count': r['count']} for r in cur]
    except Exception:
        pass

    return {
        'overview': get_overview(),
        'assignments_by_status': sorted(assignment_by_status, key=lambda x: str(x['status'])),
        'submissions_by_status': sorted(submission_by_status, key=lambda x: str(x['status'])),
        'tasks_by_domain': sorted(tasks_by_domain, key=lambda x: str(x['domain'])),
    }


def list_users(
    *,
    role: str | None = None,
    q: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[dict[str, Any]], int]:
    if role and role not in ROLES:
        raise ValueError(f'Invalid role filter. Allowed: {", ".join(ROLES)}')

    query: dict[str, Any] = {}
    if role:
        query['role'] = role
    if q and q.strip():
        term = q.strip()
        query['$or'] = [
            {'email': {'$regex': term, '$options': 'i'}},
            {'name': {'$regex': term, '$options': 'i'}},
        ]

    coll = mongo.db.users
    total = coll.count_documents(query)
    cursor = coll.find(query).sort('email', 1).skip(max(0, skip)).limit(max(1, min(100, limit)))
    items = [_serialize_public_user(u) for u in cursor]
    return items, total


USER_PATCH_ALLOWED = frozenset({'name', 'email', 'role', 'password'})


def update_user(user_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """Apply whitelisted user fields. Email uniqueness enforced."""
    uid = _oid(user_id, 'user_id')
    incoming = {k: v for k, v in data.items() if k in USER_PATCH_ALLOWED and v is not None}
    if not incoming:
        raise ValueError('No valid fields to update')

    set_doc: dict[str, Any] = {}
    if 'name' in incoming:
        name = str(incoming['name']).strip()
        if not name:
            raise ValueError('name cannot be empty')
        set_doc['name'] = name
    if 'email' in incoming:
        email = str(incoming['email']).lower().strip()
        if not email:
            raise ValueError('email cannot be empty')
        other = mongo.db.users.find_one({'email': email, '_id': {'$ne': uid}})
        if other:
            raise ValueError('Email already in use')
        set_doc['email'] = email
    if 'role' in incoming:
        role = str(incoming['role']).strip()
        if role not in ROLES:
            raise ValueError(f'Invalid role. Must be one of: {", ".join(ROLES)}')
        set_doc['role'] = role
    if 'password' in incoming:
        pwd = str(incoming['password'])
        ok, msg = validate_password(pwd)
        if not ok:
            raise ValueError(msg or 'Invalid password')
        set_doc['password_hash'] = hash_password(pwd)

    if not set_doc:
        raise ValueError('No valid fields to update')

    set_doc['updated_at'] = _utcnow()
    result = mongo.db.users.update_one({'_id': uid}, {'$set': set_doc})
    if result.matched_count == 0:
        raise ValueError('User not found')

    updated = mongo.db.users.find_one({'_id': uid})
    return _serialize_public_user(updated) if updated else {}


def list_roster(
    *,
    mentor_id: str | None = None,
    student_id: str | None = None,
    active: bool | None = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[dict[str, Any]], int]:
    mentor_svc.ensure_mentor_indexes()
    query: dict[str, Any] = {}
    if mentor_id:
        query['mentor_id'] = _oid(mentor_id, 'mentor_id')
    if student_id:
        query['student_id'] = _oid(student_id, 'student_id')
    if active is not None:
        query['active'] = bool(active)

    coll = mongo.db.mentor_roster
    total = coll.count_documents(query)
    cursor = coll.find(query).sort('created_at', -1).skip(max(0, skip)).limit(max(1, min(100, limit)))
    rows: list[dict[str, Any]] = []
    for r in cursor:
        mid = r.get('mentor_id')
        sid = r.get('student_id')
        mu = mongo.db.users.find_one({'_id': mid}, {'password_hash': 0}) if mid else None
        su = mongo.db.users.find_one({'_id': sid}, {'password_hash': 0}) if sid else None
        rows.append({
            'id': str(r['_id']),
            'mentor_id': str(mid) if mid else None,
            'student_id': str(sid) if sid else None,
            'active': bool(r.get('active', True)),
            'created_at': _iso(r.get('created_at')),
            'updated_at': _iso(r.get('updated_at')),
            'mentor': _serialize_public_user(mu) if mu else None,
            'student': _serialize_public_user(su) if su else None,
        })
    return rows, total


def create_roster_link(mentor_id: str, student_id: str) -> dict[str, Any]:
    mentor_svc.ensure_mentor_indexes()
    mid = _oid(mentor_id, 'mentor_id')
    sid = _oid(student_id, 'student_id')

    mu = mongo.db.users.find_one({'_id': mid})
    su = mongo.db.users.find_one({'_id': sid})
    if not mu or not su:
        raise ValueError('Mentor or student not found')
    if mu.get('role') != 'Mentor':
        raise ValueError('mentor_id must refer to a user with role Mentor')
    if su.get('role') != 'Student':
        raise ValueError('student_id must refer to a user with role Student')

    now = _utcnow()
    doc = {
        'mentor_id': mid,
        'student_id': sid,
        'active': True,
        'created_at': now,
        'updated_at': now,
    }
    try:
        ins = mongo.db.mentor_roster.insert_one(doc)
    except Exception as e:
        if 'duplicate' in str(e).lower() or 'E11000' in str(e):
            raise ValueError('This mentor–student link already exists') from e
        raise

    row = mongo.db.mentor_roster.find_one({'_id': ins.inserted_id})
    if not row:
        raise ValueError('Failed to create roster link')
    muser = mongo.db.users.find_one({'_id': mid}, {'password_hash': 0})
    suser = mongo.db.users.find_one({'_id': sid}, {'password_hash': 0})
    return {
        'id': str(row['_id']),
        'mentor_id': str(mid),
        'student_id': str(sid),
        'active': True,
        'created_at': _iso(row.get('created_at')),
        'mentor': _serialize_public_user(muser) if muser else None,
        'student': _serialize_public_user(suser) if suser else None,
    }


ROSTER_PATCH_ALLOWED = frozenset({'active'})


def update_roster_link(roster_id: str, data: dict[str, Any]) -> dict[str, Any]:
    rid = _oid(roster_id, 'roster_id')
    incoming = {k: v for k, v in data.items() if k in ROSTER_PATCH_ALLOWED}
    if not incoming:
        raise ValueError('No valid fields to update')
    if 'active' in incoming:
        incoming['active'] = bool(incoming['active'])
    incoming['updated_at'] = _utcnow()

    result = mongo.db.mentor_roster.update_one({'_id': rid}, {'$set': incoming})
    if result.matched_count == 0:
        raise ValueError('Roster link not found')

    row = mongo.db.mentor_roster.find_one({'_id': rid})
    if not row:
        raise ValueError('Roster link not found')
    mid, sid = row.get('mentor_id'), row.get('student_id')
    mu = mongo.db.users.find_one({'_id': mid}, {'password_hash': 0}) if mid else None
    su = mongo.db.users.find_one({'_id': sid}, {'password_hash': 0}) if sid else None
    return {
        'id': str(row['_id']),
        'mentor_id': str(mid) if mid else None,
        'student_id': str(sid) if sid else None,
        'active': bool(row.get('active', True)),
        'created_at': _iso(row.get('created_at')),
        'updated_at': _iso(row.get('updated_at')),
        'mentor': _serialize_public_user(mu) if mu else None,
        'student': _serialize_public_user(su) if su else None,
    }


def list_tasks_admin(
    *,
    status: str | None = None,
    domain: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[dict[str, Any]], int]:
    query: dict[str, Any] = {}
    if status:
        st = status.strip().lower()
        if st not in _VALID_TASK_STATUS:
            raise ValueError(f'Invalid status. Use: {", ".join(sorted(_VALID_TASK_STATUS))}')
        query['status'] = st
    if domain:
        query['domain'] = domain.strip()

    coll = mongo.db.tasks
    total = coll.count_documents(query)
    cursor = coll.find(query).sort('created_at', -1).skip(max(0, skip)).limit(max(1, min(100, limit)))
    items = []
    for t in cursor:
        item = dict(t)
        item['id'] = str(item.pop('_id'))
        if item.get('created_by'):
            item['created_by'] = str(item['created_by'])
        for key in ('created_at', 'updated_at'):
            if item.get(key) is not None and hasattr(item[key], 'isoformat'):
                item[key] = item[key].isoformat()
        items.append(item)
    return items, total


def _normalize_new_task(data: dict[str, Any]) -> dict[str, Any]:
    """Validate and build a new task document from request body."""
    title = (data.get('title') or '').strip()
    description = (data.get('description') or '').strip()
    domain = (data.get('domain') or '').strip()
    difficulty = (data.get('difficulty') or '').lower().strip()
    task_type = (data.get('task_type') or data.get('type') or '').lower().strip()
    status = (data.get('status') or TASK_STATUS_OPEN).lower().strip()

    if not title:
        raise ValueError('title is required')
    if not description:
        raise ValueError('description is required')
    if not domain:
        raise ValueError('domain is required')
    if difficulty not in _VALID_DIFFICULTIES:
        raise ValueError(
            f'difficulty must be one of: {", ".join(sorted(_VALID_DIFFICULTIES))}',
        )
    if task_type not in ('writing', 'programming', 'design'):
        raise ValueError('task_type must be writing, programming, or design')
    if status not in _VALID_TASK_STATUS:
        raise ValueError(f'status must be one of: {", ".join(sorted(_VALID_TASK_STATUS))}')

    doc: dict[str, Any] = {
        'title': title,
        'description': description,
        'domain': domain,
        'difficulty': difficulty,
        'task_type': task_type,
        'status': status,
    }

    optional_keys = (
        'tags',
        'keywords',
        'estimated_hours',
        'timeout_seconds',
        'test_cases',
        'min_words',
        'max_words',
        'language',
        'allowed_extensions',
        'max_file_mb',
        'max_upload_mb',
    )
    for key in optional_keys:
        if key in data:
            doc[key] = data[key]

    return doc


def create_task(data: dict[str, Any], created_by_id: str | None) -> dict[str, Any]:
    base = _normalize_new_task(data)
    now = _utcnow()
    doc = {**base, 'created_at': now, 'updated_at': now}
    if created_by_id:
        try:
            doc['created_by'] = _oid(created_by_id, 'created_by')
        except ValueError:
            doc['created_by'] = None
    else:
        doc['created_by'] = None

    result = mongo.db.tasks.insert_one(doc)
    t = mongo.db.tasks.find_one({'_id': result.inserted_id})
    if not t:
        raise ValueError('Failed to create task')
    out = dict(t)
    out['id'] = str(out.pop('_id'))
    if out.get('created_by'):
        out['created_by'] = str(out['created_by'])
    for key in ('created_at', 'updated_at'):
        if out.get(key) is not None and hasattr(out[key], 'isoformat'):
            out[key] = out[key].isoformat()
    return out


TASK_PATCH_ALLOWED = frozenset({
    'title',
    'description',
    'domain',
    'difficulty',
    'task_type',
    'type',
    'status',
    'tags',
    'keywords',
    'estimated_hours',
    'timeout_seconds',
    'test_cases',
    'min_words',
    'max_words',
    'language',
    'allowed_extensions',
    'max_file_mb',
    'max_upload_mb',
})


def update_task(task_id: str, data: dict[str, Any]) -> dict[str, Any]:
    tid = _oid(task_id, 'task_id')
    subset = {k: v for k, v in data.items() if k in TASK_PATCH_ALLOWED}
    if not subset:
        raise ValueError('No valid fields to update')

    existing = mongo.db.tasks.find_one({'_id': tid})
    if not existing:
        raise ValueError('Task not found')

    set_doc: dict[str, Any] = {}
    if 'title' in subset:
        t = str(subset['title']).strip()
        if not t:
            raise ValueError('title cannot be empty')
        set_doc['title'] = t
    if 'description' in subset:
        d = str(subset['description']).strip()
        if not d:
            raise ValueError('description cannot be empty')
        set_doc['description'] = d
    if 'domain' in subset:
        dom = str(subset['domain']).strip()
        if not dom:
            raise ValueError('domain cannot be empty')
        set_doc['domain'] = dom
    if 'difficulty' in subset:
        diff = str(subset['difficulty']).lower().strip()
        if diff not in _VALID_DIFFICULTIES:
            raise ValueError(f'difficulty must be one of: {", ".join(sorted(_VALID_DIFFICULTIES))}')
        set_doc['difficulty'] = diff
    if 'task_type' in subset or 'type' in subset:
        raw = subset.get('task_type') or subset.get('type')
        tt = str(raw).lower().strip()
        if tt not in ('writing', 'programming', 'design'):
            raise ValueError('task_type must be writing, programming, or design')
        set_doc['task_type'] = tt
    if 'status' in subset:
        st = str(subset['status']).lower().strip()
        if st not in _VALID_TASK_STATUS:
            raise ValueError(f'status must be one of: {", ".join(sorted(_VALID_TASK_STATUS))}')
        set_doc['status'] = st

    optional_keys = (
        'tags',
        'keywords',
        'estimated_hours',
        'timeout_seconds',
        'test_cases',
        'min_words',
        'max_words',
        'language',
        'allowed_extensions',
        'max_file_mb',
        'max_upload_mb',
    )
    for key in optional_keys:
        if key in subset:
            set_doc[key] = subset[key]

    if not set_doc:
        raise ValueError('No valid fields to update')

    set_doc['updated_at'] = _utcnow()
    mongo.db.tasks.update_one({'_id': tid}, {'$set': set_doc})
    t = mongo.db.tasks.find_one({'_id': tid})
    if not t:
        raise ValueError('Task not found')
    out = dict(t)
    out['id'] = str(out.pop('_id'))
    if out.get('created_by'):
        out['created_by'] = str(out['created_by'])
    for key in ('created_at', 'updated_at'):
        if out.get(key) is not None and hasattr(out[key], 'isoformat'):
            out[key] = out[key].isoformat()
    return out


def _task_min(task: dict | None) -> dict[str, Any] | None:
    if not task:
        return None
    return {
        'id': str(task['_id']),
        'title': task.get('title'),
        'domain': task.get('domain'),
        'task_type': (task.get('task_type') or task.get('type') or '').lower(),
    }


def list_submissions_admin(
    *,
    user_id: str | None = None,
    status: str | None = None,
    task_type: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[dict[str, Any]], int]:
    query: dict[str, Any] = {}
    if user_id:
        query['user_id'] = _oid(user_id, 'user_id')
    if status:
        query['status'] = status.strip().lower()
    if task_type:
        query['task_type'] = task_type.strip().lower()

    coll = mongo.db.submissions
    total = coll.count_documents(query)
    cursor = coll.find(query).sort('created_at', -1).skip(max(0, skip)).limit(max(1, min(100, limit)))
    rows: list[dict[str, Any]] = []
    for sub in cursor:
        uid = sub.get('user_id')
        tid = sub.get('task_id')
        student = mongo.db.users.find_one({'_id': uid}, {'password_hash': 0}) if uid else None
        task = mongo.db.tasks.find_one({'_id': tid}) if tid else None
        rows.append({
            'id': str(sub['_id']),
            'user_id': str(uid) if uid else None,
            'assignment_id': str(sub['assignment_id']) if sub.get('assignment_id') else None,
            'task_id': str(tid) if tid else None,
            'task_type': sub.get('task_type'),
            'status': sub.get('status'),
            'created_at': _iso(sub.get('created_at')),
            'student': _serialize_public_user(student) if student else {'id': str(uid)},
            'task': _task_min(task),
        })
    return rows, total


def get_submission_detail_admin(submission_id: str) -> dict[str, Any] | None:
    try:
        sid = ObjectId(submission_id)
    except InvalidId:
        return None
    sub = mongo.db.submissions.find_one({'_id': sid})
    if not sub:
        return None
    uid = sub.get('user_id')
    tid = sub.get('task_id')
    student = mongo.db.users.find_one({'_id': uid}, {'password_hash': 0}) if uid else None
    task = mongo.db.tasks.find_one({'_id': tid}) if tid else None
    ser = submission_svc._serialize_submission(sub)

    mentor_reviews = list(mongo.db.mentor_reviews.find({'submission_id': sid}))
    reviews_out = []
    for r in mentor_reviews:
        reviews_out.append({
            'id': str(r['_id']),
            'mentor_id': str(r['mentor_id']),
            'student_id': str(r['student_id']),
            'status': r.get('status'),
            'feedback': r.get('feedback'),
            'created_at': _iso(r.get('created_at')),
            'completed_at': _iso(r.get('completed_at')),
        })

    return {
        'submission': ser,
        'student': _serialize_public_user(student) if student else {'id': str(uid)},
        'task': _task_min(task),
        'mentor_reviews': reviews_out,
    }
