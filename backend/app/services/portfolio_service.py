"""FR6: Build student portfolio JSON from users, tasks, assignments, submissions, mentor_reviews."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId

from app.extensions import mongo
from app.schemas.mentor_schema import MENTOR_REVIEW_STATUS_COMPLETED
from app.schemas.portfolio_schema import PORTFOLIO_RESPONSE_VERSION
from app.schemas.submission_schema import SUBMISSION_STATUS_EVALUATED
from app.services.assessment_service import get_latest_result


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: Any) -> str | None:
    if dt is None:
        return None
    if hasattr(dt, 'isoformat'):
        return dt.isoformat()
    return None


def _oid(user_id: str) -> ObjectId:
    try:
        return ObjectId(user_id)
    except Exception as e:
        raise ValueError('Invalid user id') from e


def _task_public(task: dict | None) -> dict[str, Any] | None:
    if not task:
        return None
    tt = (task.get('task_type') or task.get('type') or '').lower()
    return {
        'id': str(task['_id']),
        'title': (task.get('title') or '')[:500],
        'domain': task.get('domain'),
        'task_type': tt or None,
        'difficulty': task.get('difficulty'),
    }


def _numeric_score(evaluation: dict | None) -> float | None:
    if not evaluation:
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


def _evaluation_public(sub: dict) -> dict[str, Any] | None:
    ev = sub.get('evaluation')
    if not isinstance(ev, dict):
        return None
    strengths = ev.get('strengths') if isinstance(ev.get('strengths'), list) else []
    areas = ev.get('areas_for_improvement') if isinstance(ev.get('areas_for_improvement'), list) else []
    return {
        'overall_score': _numeric_score(ev),
        'feedback_summary': ev.get('feedback_summary'),
        'score_breakdown': ev.get('score_breakdown'),
        'strengths': [str(s) for s in strengths[:8] if s],
        'areas_for_improvement': [str(a) for a in areas[:8] if a],
    }


def _skills_from_task(task: dict | None) -> list[str]:
    if not task:
        return []
    seen: set[str] = set()
    ordered: list[str] = []

    def add(label: str | None) -> None:
        if not label or not str(label).strip():
            return
        key = str(label).strip().lower()
        if key in seen:
            return
        seen.add(key)
        ordered.append(str(label).strip())

    add(task.get('domain'))
    tt = (task.get('task_type') or task.get('type') or '').strip()
    if tt:
        add(tt)
    for t in task.get('tags') or []:
        if isinstance(t, str):
            add(t)
    for k in task.get('keywords') or []:
        if isinstance(k, str):
            add(k)
    return ordered[:24]


def _dedupe_skills(skills: list[str], cap: int = 28) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for s in skills:
        if not s:
            continue
        k = s.strip().lower()
        if k in seen:
            continue
        seen.add(k)
        out.append(s.strip())
        if len(out) >= cap:
            break
    return out


def _mentor_feedback_block(review: dict | None) -> dict[str, Any] | None:
    if not review:
        return {'has_feedback': False, 'feedback': None, 'completed_at': None}
    fb = review.get('feedback')
    if review.get('status') != MENTOR_REVIEW_STATUS_COMPLETED or not (fb and str(fb).strip()):
        return {'has_feedback': False, 'feedback': None, 'completed_at': _iso(review.get('completed_at'))}
    return {
        'has_feedback': True,
        'feedback': str(fb).strip(),
        'completed_at': _iso(review.get('completed_at')),
    }


def build_portfolio(user_id: str) -> dict[str, Any]:
    """
    Aggregate portfolio for one student. Caller must enforce JWT + Student role.
    Uses evaluated submissions only; latest submission per assignment wins.
    """
    uid = _oid(user_id)

    user = mongo.db.users.find_one({'_id': uid}, {'password_hash': 0})
    if not user:
        raise ValueError('User not found')

    subs = list(
        mongo.db.submissions.find({'user_id': uid, 'status': SUBMISSION_STATUS_EVALUATED}).sort(
            'created_at', -1
        )
    )

    by_assignment: dict[ObjectId, dict] = {}
    for s in subs:
        aid = s.get('assignment_id')
        if aid and aid not in by_assignment:
            by_assignment[aid] = s

    projects: list[dict[str, Any]] = []
    all_skills: list[str] = []

    for aid, sub in by_assignment.items():
        task = mongo.db.tasks.find_one({'_id': sub.get('task_id')})
        if not task:
            continue
        assignment = mongo.db.task_assignments.find_one({'_id': aid})
        review = mongo.db.mentor_reviews.find_one(
            {'submission_id': sub['_id'], 'student_id': uid, 'status': MENTOR_REVIEW_STATUS_COMPLETED}
        )

        tp = _task_public(task)
        all_skills.extend(_skills_from_task(task))

        completed_at = None
        if assignment and assignment.get('completed_at'):
            completed_at = _iso(assignment.get('completed_at'))
        if not completed_at:
            completed_at = _iso(sub.get('updated_at')) or _iso(sub.get('created_at'))

        ast = (assignment.get('status') if assignment else None) or None

        projects.append(
            {
                'assignment_id': str(aid),
                'assignment_status': ast,
                'submission_id': str(sub['_id']),
                'task': tp,
                'completed_at': completed_at,
                'evaluation': _evaluation_public(sub),
                'mentor_feedback': _mentor_feedback_block(review),
            }
        )

    projects.sort(key=lambda p: p.get('completed_at') or '', reverse=True)

    domain_counts: dict[str, int] = defaultdict(int)
    domain_scores: dict[str, list[float]] = defaultdict(list)
    for p in projects:
        t = p.get('task') or {}
        dom = (t.get('domain') or 'Other').strip() or 'Other'
        domain_counts[dom] += 1
        ev = p.get('evaluation') or {}
        os_ = ev.get('overall_score')
        if os_ is not None:
            try:
                domain_scores[dom].append(float(os_))
            except (TypeError, ValueError):
                pass

    domains_out: list[dict[str, Any]] = []
    for dom, cnt in sorted(domain_counts.items(), key=lambda x: (-x[1], x[0])):
        scores = domain_scores.get(dom) or []
        avg = round(sum(scores) / len(scores), 2) if scores else None
        domains_out.append({'domain': dom, 'completed_count': cnt, 'avg_score': avg})

    skill_tags = _dedupe_skills(all_skills)

    n = len(projects)
    n_dom = len(domain_counts)
    if n == 0:
        summary = 'Complete and pass automated evaluation on tasks to build your portfolio.'
    else:
        summary = (
            f'You have {n} evaluated project(s) across {n_dom or 1} skill area(s), '
            'ready to showcase for freelancing profiles.'
        )

    assessment = get_latest_result(user_id)
    assessment_public = None
    if assessment:
        assessment_public = {
            'overall_score': assessment.get('overall_score'),
            'recommended_domain': assessment.get('recommended_domain'),
            'recommended_domains': assessment.get('recommended_domains') or [],
        }
        rec = assessment.get('recommended_domain')
        if rec:
            if n > 0:
                summary = f'{summary} Your assessment highlights interest in {rec}.'
            else:
                summary = f'{summary} Your MCQ assessment suggests strength in {rec} — add projects to match.'

    highlights: list[dict[str, str]] = []
    if n > 0:
        highlights.append({'text': f'{n} evaluated project(s) in your portfolio.'})
    if domains_out:
        top = domains_out[0]
        highlights.append(
            {'text': f'Strongest volume in {top["domain"]} ({top["completed_count"]} project(s)).'}
        )
    mentor_done = sum(1 for p in projects if (p.get('mentor_feedback') or {}).get('has_feedback'))
    if mentor_done:
        highlights.append({'text': f'Mentor feedback received on {mentor_done} submission(s).'})
    if assessment_public and assessment_public.get('overall_score') is not None:
        highlights.append(
            {'text': f'Skill assessment score: {assessment_public["overall_score"]}% (MCQ).'}
        )
    best = None
    for p in projects:
        ev = p.get('evaluation') or {}
        sc = ev.get('overall_score')
        if sc is None:
            continue
        try:
            fv = float(sc)
        except (TypeError, ValueError):
            continue
        t = (p.get('task') or {}).get('title') or 'Project'
        if best is None or fv > best[0]:
            best = (fv, t)
    if best:
        highlights.append({'text': f'Highlight: {best[1]} scored {best[0]:.1f}/100 (auto-evaluation).'})

    highlights = highlights[:8]

    profile = {
        'id': str(user['_id']),
        'name': user.get('name'),
        'email': user.get('email'),
        'role': user.get('role'),
    }

    return {
        'profile': profile,
        'readiness': {
            'summary_line': summary,
            'domains': domains_out,
            'skill_tags': skill_tags,
        },
        'assessment': assessment_public,
        'highlights': highlights,
        'projects': projects,
        'meta': {'generated_at': _iso(_utcnow()), 'version': PORTFOLIO_RESPONSE_VERSION},
    }
