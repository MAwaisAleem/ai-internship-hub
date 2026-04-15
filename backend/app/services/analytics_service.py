"""FR9: Reporting and analytics — read-only aggregates over existing MongoDB data."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId

from app.extensions import mongo
from app.schemas.mentor_schema import MENTOR_REVIEW_STATUS_COMPLETED
from app.schemas.submission_schema import SUBMISSION_STATUS_EVALUATED
from app.schemas.task_schema import (
    ASSIGNMENT_COMPLETED,
    ASSIGNMENT_DROPPED,
)
from app.services.auth_service import ROLES
from app.services import mentor_service as mentor_svc


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


def ensure_analytics_indexes() -> None:
    """Idempotent indexes for analytics queries."""
    mentor_svc.ensure_mentor_indexes()
    try:
        mongo.db.task_assignments.create_index([('user_id', 1), ('status', 1)], name='analytics_assignment_user_status')
    except Exception:
        pass
    try:
        mongo.db.submissions.create_index([('user_id', 1), ('status', 1)], name='analytics_submission_user_status')
    except Exception:
        pass
    try:
        mongo.db.submissions.create_index([('task_id', 1)], name='analytics_submission_task')
    except Exception:
        pass
    try:
        mongo.db.mentor_reviews.create_index([('student_id', 1), ('status', 1)], name='analytics_review_student_status')
    except Exception:
        pass


def _numeric_score_from_evaluation(evaluation: dict | None) -> float | None:
    """Extract a 0–100 score from stored evaluation (read-only; aligns with portfolio_service)."""
    if not evaluation or not isinstance(evaluation, dict):
        return None
    raw = evaluation.get('overall_score')
    if raw is not None and isinstance(raw, (int, float)):
        return float(raw)
    sb = evaluation.get('score_breakdown')
    if isinstance(sb, dict):
        for key in ('automated_validation', 'correctness'):
            if key in sb and sb[key] is not None:
                try:
                    return float(sb[key])
                except (TypeError, ValueError):
                    pass
    return None


def _assignment_counts(assignments: list[dict]) -> tuple[int, int, int]:
    """Returns total, completed, pending (active / not finished)."""
    total = len(assignments)
    completed = 0
    pending = 0
    for a in assignments:
        st = (a.get('status') or '').lower()
        if st == ASSIGNMENT_COMPLETED:
            completed += 1
        elif st not in (ASSIGNMENT_DROPPED,):
            pending += 1
    return total, completed, pending


def _progress_percent(completed: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round(100.0 * completed / total, 1)


def _avg_scores_for_submissions(subs: list[dict]) -> tuple[list[float], float | None]:
    scores: list[float] = []
    for s in subs:
        if (s.get('status') or '').lower() != SUBMISSION_STATUS_EVALUATED:
            continue
        n = _numeric_score_from_evaluation(s.get('evaluation') if isinstance(s.get('evaluation'), dict) else None)
        if n is not None:
            scores.append(n)
    if not scores:
        return [], None
    return scores, round(sum(scores) / len(scores), 2)


def _domain_performance_for_submissions(subs: list[dict]) -> list[dict[str, Any]]:
    """Group evaluated submissions by task domain."""
    task_ids = [s.get('task_id') for s in subs if s.get('task_id')]
    if not task_ids:
        return []
    unique_ids = list({tid for tid in task_ids})
    tasks = {
        str(t['_id']): t
        for t in mongo.db.tasks.find({'_id': {'$in': unique_ids}})
    }
    by_domain: dict[str, list[float]] = defaultdict(list)
    counts: dict[str, int] = defaultdict(int)
    for s in subs:
        if (s.get('status') or '').lower() != SUBMISSION_STATUS_EVALUATED:
            continue
        tid = s.get('task_id')
        task = tasks.get(str(tid)) if tid else None
        domain = (task.get('domain') if task else None) or 'Unknown'
        sc = _numeric_score_from_evaluation(s.get('evaluation') if isinstance(s.get('evaluation'), dict) else None)
        counts[domain] += 1
        if sc is not None:
            by_domain[domain].append(sc)
    out: list[dict[str, Any]] = []
    for domain in sorted(counts.keys()):
        scores = by_domain[domain]
        out.append({
            'domain': domain,
            'submissions_count': counts[domain],
            'average_score': round(sum(scores) / len(scores), 2) if scores else None,
        })
    return out


def _mentor_feedback_trend_for_student(student_oid: ObjectId, limit: int = 10) -> list[dict[str, Any]]:
    cur = (
        mongo.db.mentor_reviews.find(
            {'student_id': student_oid, 'status': MENTOR_REVIEW_STATUS_COMPLETED},
        )
        .sort('completed_at', -1)
        .limit(limit)
    )
    rows: list[dict[str, Any]] = []
    for r in cur:
        fb = r.get('feedback') or ''
        preview = (fb[:120] + '…') if len(fb) > 120 else fb
        rows.append({
            'review_id': str(r['_id']),
            'mentor_id': str(r['mentor_id']),
            'completed_at': _iso(r.get('completed_at')),
            'feedback_preview': preview or None,
        })
    return rows


def get_student_analytics(user_id: str) -> dict[str, Any]:
    """Analytics for the current student only."""
    ensure_analytics_indexes()
    uid = _oid(user_id, 'user_id')

    assignments = list(mongo.db.task_assignments.find({'user_id': uid}))
    total_a, completed_a, pending_a = _assignment_counts(assignments)
    progress_pct = _progress_percent(completed_a, total_a)

    subs = list(mongo.db.submissions.find({'user_id': uid}))
    evaluated = [s for s in subs if (s.get('status') or '').lower() == SUBMISSION_STATUS_EVALUATED]
    scores, avg_score = _avg_scores_for_submissions(evaluated)
    domain_performance = _domain_performance_for_submissions(subs)
    feedback_trend = _mentor_feedback_trend_for_student(uid)

    return {
        'role': 'Student',
        'progress': {
            'percentage': progress_pct,
            'completed_task_assignments': completed_a,
            'pending_task_assignments': pending_a,
            'total_task_assignments': total_a,
        },
        'submissions': {
            'total': len(subs),
            'evaluated_count': len(evaluated),
            'average_evaluation_score': avg_score,
        },
        'domain_performance': domain_performance,
        'mentor_feedback_trend': feedback_trend,
        'generated_at': _iso(_utcnow()),
    }


def _student_snapshot(student_id: ObjectId) -> dict[str, Any]:
    """Compact stats for one student (used by mentor aggregate)."""
    u = mongo.db.users.find_one({'_id': student_id}, {'password_hash': 0})
    assignments = list(mongo.db.task_assignments.find({'user_id': student_id}))
    total_a, completed_a, pending_a = _assignment_counts(assignments)
    subs = list(mongo.db.submissions.find({'user_id': student_id}))
    evaluated = [s for s in subs if (s.get('status') or '').lower() == SUBMISSION_STATUS_EVALUATED]
    _, avg_score = _avg_scores_for_submissions(evaluated)
    return {
        'student_id': str(student_id),
        'email': u.get('email') if u else None,
        'name': u.get('name') if u else None,
        'completed_task_assignments': completed_a,
        'pending_task_assignments': pending_a,
        'total_task_assignments': total_a,
        'submissions_evaluated': len(evaluated),
        'average_evaluation_score': avg_score,
    }


def get_mentor_analytics(mentor_id: str) -> dict[str, Any]:
    """Analytics scoped to students on the mentor's active roster."""
    ensure_analytics_indexes()
    mid = _oid(mentor_id, 'mentor_id')
    roster_rows = mentor_svc.list_assigned_students(mentor_id)
    student_ids = [_oid(s['id'], 'student_id') for s in roster_rows if s.get('id')]
    roster_snapshots = [_student_snapshot(sid) for sid in student_ids]

    reviews_total = mongo.db.mentor_reviews.count_documents(
        {'mentor_id': mid, 'status': MENTOR_REVIEW_STATUS_COMPLETED},
    )
    recent = list(
        mongo.db.mentor_reviews.find({'mentor_id': mid, 'status': MENTOR_REVIEW_STATUS_COMPLETED})
        .sort('completed_at', -1)
        .limit(8),
    )
    recent_items: list[dict[str, Any]] = []
    for r in recent:
        recent_items.append({
            'review_id': str(r['_id']),
            'submission_id': str(r['submission_id']),
            'student_id': str(r['student_id']),
            'completed_at': _iso(r.get('completed_at')),
            'feedback_preview': ((r.get('feedback') or '')[:100] + '…')
            if len((r.get('feedback') or '')) > 100
            else (r.get('feedback') or None),
        })

    agg_completed = sum(s['completed_task_assignments'] for s in roster_snapshots)
    agg_pending = sum(s['pending_task_assignments'] for s in roster_snapshots)
    scores_all: list[float] = []
    for s in roster_snapshots:
        if s.get('average_evaluation_score') is not None:
            scores_all.append(float(s['average_evaluation_score']))

    return {
        'role': 'Mentor',
        'roster': {
            'student_count': len(student_ids),
            'students': roster_snapshots,
            'roster_totals': {
                'completed_assignments': agg_completed,
                'pending_assignments': agg_pending,
            },
            'roster_average_score_of_averages': round(sum(scores_all) / len(scores_all), 2)
            if scores_all
            else None,
        },
        'mentor_feedback_activity': {
            'completed_reviews_total': reviews_total,
            'recent_reviews': recent_items,
        },
        'generated_at': _iso(_utcnow()),
    }


def get_admin_analytics_summary() -> dict[str, Any]:
    """Platform-wide summary for administrators."""
    ensure_analytics_indexes()

    users_by_role: dict[str, int] = {}
    for role in ROLES:
        users_by_role[role] = mongo.db.users.count_documents({'role': role})

    pipeline_assign = [
        {'$group': {'_id': '$status', 'count': {'$sum': 1}}},
    ]
    assignment_by_status: list[dict[str, Any]] = []
    try:
        for row in mongo.db.task_assignments.aggregate(pipeline_assign):
            assignment_by_status.append({
                'status': row['_id'] or 'unknown',
                'count': row['count'],
            })
    except Exception:
        pass

    subs_evaluated = list(
        mongo.db.submissions.find({'status': SUBMISSION_STATUS_EVALUATED}),
    )
    scores: list[float] = []
    for s in subs_evaluated:
        n = _numeric_score_from_evaluation(s.get('evaluation') if isinstance(s.get('evaluation'), dict) else None)
        if n is not None:
            scores.append(n)
    global_avg = round(sum(scores) / len(scores), 2) if scores else None

    # Domain rollup from evaluated submissions
    domain_performance = _domain_performance_for_submissions(subs_evaluated)

    reviews_completed = mongo.db.mentor_reviews.count_documents({'status': MENTOR_REVIEW_STATUS_COMPLETED})

    return {
        'role': 'Administrator',
        'users_by_role': users_by_role,
        'users_total': sum(users_by_role.values()),
        'task_assignments_by_status': sorted(assignment_by_status, key=lambda x: str(x.get('status'))),
        'submissions': {
            'evaluated_total': len(subs_evaluated),
            'average_evaluation_score': global_avg,
        },
        'domain_performance': domain_performance,
        'mentor_reviews_completed_total': reviews_completed,
        'generated_at': _iso(_utcnow()),
    }
