"""FR3: Recommend tasks using FR2 assessment + assignments (rule-based hybrid)."""
from __future__ import annotations

from datetime import datetime, timezone

from bson import ObjectId

from app.extensions import mongo
from app.services.assessment_service import DOMAINS, get_latest_result
from app.utils.recommendation_helpers import (
    build_domain_score_map,
    combine_weighted_score,
    difficulty_fit_points,
    domain_alignment_points,
    keyword_overlap_points,
    overall_score_to_level,
    pick_weak_strong_domains,
    repetition_penalty,
    weak_area_boost,
)


def _utcnow():
    return datetime.now(timezone.utc)


def get_student_recommendation_context(user_id: str) -> dict | None:
    """
    Build context from FR2 latest assessment + task assignment history.
    Returns None if user has no assessment (caller may still show generic browse).
    """
    try:
        uid = ObjectId(user_id)
    except Exception:
        return None

    assessment = get_latest_result(user_id)
    if not assessment:
        return None

    domain_scores = assessment.get('domain_scores') or []
    if not domain_scores and assessment.get('scores_by_domain'):
        # legacy shape: dict domain -> score
        sbd = assessment.get('scores_by_domain') or {}
        domain_scores = [{'domain': k, 'score': v} for k, v in sbd.items()]

    overall = int(assessment.get('overall_score') or 0)
    student_level = overall_score_to_level(overall)
    weak, strong = pick_weak_strong_domains(domain_scores)
    domain_scores_map = build_domain_score_map(domain_scores)

    recommended_domain = assessment.get('recommended_domain')
    recommended_domains = assessment.get('recommended_domains') or []

    # Assignments
    cur = mongo.db.task_assignments.find({'user_id': uid})
    completed_ids: set[str] = set()
    active_ids: set[str] = set()
    completed_by_domain: dict[str, int] = {d: 0 for d in DOMAINS}

    for a in cur:
        tid = str(a.get('task_id'))
        st = (a.get('status') or '').lower()
        if st == 'completed':
            completed_ids.add(tid)
            # count domain from task doc
            try:
                t = mongo.db.tasks.find_one({'_id': a.get('task_id')})
                if t and t.get('domain'):
                    dom = t['domain']
                    completed_by_domain[dom] = completed_by_domain.get(dom, 0) + 1
            except Exception:
                pass
        elif st in ('claimed', 'in_progress', 'submitted'):
            active_ids.add(tid)

    return {
        'user_id': user_id,
        'overall_score': overall,
        'student_level': student_level,
        'recommended_domain': recommended_domain,
        'recommended_domains': recommended_domains,
        'domain_scores_map': domain_scores_map,
        'domain_scores': domain_scores,
        'weak_domains': weak,
        'strong_domains': strong,
        'completed_task_ids': completed_ids,
        'active_task_ids': active_ids,
        'completed_count_by_domain': completed_by_domain,
    }


def score_task_for_student(task: dict, ctx: dict) -> tuple[float, list[dict[str, str]]]:
    """
    Compute 0-100 recommendation score and human-readable reasons.
    """
    reasons: list[dict[str, str]] = []

    td = task.get('domain') or ''
    diff = (task.get('difficulty') or 'intermediate').lower()
    keywords = task.get('keywords') or []
    if not isinstance(keywords, list):
        keywords = []

    d_pts, d_reasons = domain_alignment_points(
        td,
        ctx.get('recommended_domain'),
        ctx.get('recommended_domains'),
        ctx.get('domain_scores_map') or {},
    )
    reasons.extend(d_reasons)

    diff_pts, diff_reasons = difficulty_fit_points(diff, ctx.get('student_level', 'intermediate'))
    reasons.extend(diff_reasons)

    rep_pts, rep_reasons = repetition_penalty(
        task.get('_id'),
        ctx.get('completed_task_ids') or set(),
        ctx.get('active_task_ids') or set(),
    )
    reasons.extend(rep_reasons)

    w_pts, w_reasons = weak_area_boost(td, ctx.get('weak_domains') or [])
    reasons.extend(w_reasons)

    k_pts, k_reasons = keyword_overlap_points(
        keywords,
        ctx.get('strong_domains') or [],
        ctx.get('recommended_domain'),
    )
    reasons.extend(k_reasons)

    final = combine_weighted_score(d_pts, diff_pts, rep_pts, w_pts, k_pts)

    # If already completed, force to bottom
    if rep_pts < 5:
        final = min(final, 5.0)

    reasons.append({
        'code': 'SCORE_SUMMARY',
        'message': f'Combined match score: {final} / 100.',
    })
    return final, reasons


def rank_tasks_for_student(user_id: str, limit: int = 10) -> tuple[list[dict], dict | None]:
    """
    Returns (ranked list of {task, score, reasons}, context or None).
    Only considers tasks with status open.
    """
    ctx = get_student_recommendation_context(user_id)
    query = {'status': 'open'}
    tasks = list(mongo.db.tasks.find(query))

    if not tasks:
        return [], ctx

    if not ctx:
        # No assessment: return tasks with neutral score and a single reason
        out = []
        for t in tasks:
            out.append({
                'task': _serialize_task(t),
                'score': 50.0,
                'reasons': [{
                    'code': 'NO_ASSESSMENT',
                    'message': 'Complete the skill assessment (FR2) for personalized recommendations.',
                }],
            })
        out.sort(key=lambda x: (x['task'].get('title') or ''))
        return out[:limit], None

    scored: list[tuple[dict, float, list]] = []
    for t in tasks:
        score, reasons = score_task_for_student(t, ctx)
        scored.append((t, score, reasons))

    scored.sort(key=lambda x: x[1], reverse=True)
    ranked = []
    for t, score, reasons in scored[:limit]:
        ranked.append({
            'task': _serialize_task(t),
            'score': score,
            'reasons': reasons,
        })

    return ranked, ctx


def _serialize_task(t: dict) -> dict:
    out = dict(t)
    out['id'] = str(out.pop('_id'))
    if out.get('created_by'):
        out['created_by'] = str(out['created_by'])
    # JSON-serializable datetimes
    for key in ('created_at', 'updated_at'):
        if out.get(key) is not None and hasattr(out[key], 'isoformat'):
            out[key] = out[key].isoformat()
    return out


def get_recommendation_snapshot_for_task(user_id: str, task_id: str) -> dict | None:
    """Recompute score/reasons for one task (e.g. at claim time)."""
    try:
        tid = ObjectId(task_id)
    except Exception:
        return None

    task = mongo.db.tasks.find_one({'_id': tid})
    if not task:
        return None

    ctx = get_student_recommendation_context(user_id)
    if not ctx:
        return {'score': 50.0, 'reasons': [{'code': 'NO_ASSESSMENT', 'message': 'No assessment context.'}]}

    score, reasons = score_task_for_student(task, ctx)
    return {'score': score, 'reasons': reasons}


def persist_recommendation_snapshot(user_id: str, items: list[dict]) -> None:
    """Upsert student_progress with last recommendation results and reasons."""
    try:
        uid = ObjectId(user_id)
    except Exception:
        raise ValueError('Invalid user ID')

    now = _utcnow()
    ctx = get_student_recommendation_context(user_id)

    doc = {
        'user_id': uid,
        'last_recommendation_at': now,
        'last_recommendation_items': items,
        'updated_at': now,
    }
    if ctx:
        doc['weak_domains'] = ctx.get('weak_domains') or []
        doc['strong_domains'] = ctx.get('strong_domains') or []
        doc['completed_count_by_domain'] = ctx.get('completed_count_by_domain') or {}
        total = len(ctx.get('completed_task_ids') or [])
        doc['total_completed'] = total

    mongo.db.student_progress.update_one(
        {'user_id': uid},
        {'$set': doc},
        upsert=True,
    )
