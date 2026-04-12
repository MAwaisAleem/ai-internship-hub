"""Pure helper functions for FR3 task recommendation (rule-based + light content match)."""
from __future__ import annotations

from typing import Any


def overall_score_to_level(overall_score: int) -> str:
    """Map FR2 overall_score (0-100) to a coarse skill band."""
    if overall_score < 41:
        return 'beginner'
    if overall_score < 71:
        return 'intermediate'
    return 'advanced'


def difficulty_rank(difficulty: str) -> int:
    """Order difficulties for comparison."""
    order = {'beginner': 0, 'intermediate': 1, 'advanced': 2}
    return order.get((difficulty or '').lower(), 1)


def build_domain_score_map(domain_scores: list | None) -> dict[str, int]:
    """Normalize FR2 domain_scores list to domain -> percentage."""
    out: dict[str, int] = {}
    if not domain_scores:
        return out
    for row in domain_scores:
        if isinstance(row, dict) and row.get('domain'):
            out[row['domain']] = int(row.get('score', 0))
    return out


def pick_weak_strong_domains(
    domain_scores: list | None,
    weak_cutoff: int = 40,
    strong_cutoff: int = 70,
) -> tuple[list[str], list[str]]:
    """
    From FR2 domain_scores, label weak (below weak_cutoff) and strong (at or above strong_cutoff).
    Only considers domains that appeared in the assessment (non-zero total implied by presence in list).
    """
    weak: list[str] = []
    strong: list[str] = []
    if not domain_scores:
        return weak, strong
    for row in domain_scores:
        if not isinstance(row, dict):
            continue
        d = row.get('domain')
        s = int(row.get('score', 0))
        if not d:
            continue
        if s <= weak_cutoff:
            weak.append(d)
        if s >= strong_cutoff:
            strong.append(d)
    return weak, strong


def domain_alignment_points(
    task_domain: str,
    recommended_domain: str | None,
    recommended_domains: list | None,
    domain_scores_map: dict[str, int],
) -> tuple[float, list[dict[str, str]]]:
    """
    Returns sub-score 0-100 and reason entries for domain match.
    """
    reasons: list[dict[str, str]] = []
    td = (task_domain or '').strip()
    if not td:
        return 20.0, [{'code': 'DOMAIN_UNKNOWN', 'message': 'Task domain is unspecified; low default match.'}]

    rd = (recommended_domain or '').strip()
    rlist = recommended_domains or []

    if rd and td == rd:
        reasons.append({'code': 'PRIMARY_DOMAIN', 'message': f'Matches your top recommended domain ({td}).'})
        return 100.0, reasons

    if td in rlist:
        reasons.append({'code': 'TOP_DOMAIN', 'message': f'Aligns with one of your recommended domains ({td}).'})
        return 85.0, reasons

    pct = domain_scores_map.get(td)
    if pct is not None:
        # Partial credit by assessed strength in this domain
        sub = 40.0 + (pct / 100.0) * 45.0
        reasons.append({
            'code': 'DOMAIN_SCORE',
            'message': f'Your assessed strength in {td} is {pct}%.',
        })
        return min(100.0, sub), reasons

    reasons.append({'code': 'DOMAIN_EXPLOR', 'message': f'Explore {td}; not in your latest assessment breakdown.'})
    return 35.0, reasons


def difficulty_fit_points(
    task_difficulty: str,
    student_level: str,
) -> tuple[float, list[dict[str, str]]]:
    """How well task difficulty matches student band from FR2 overall score."""
    td = difficulty_rank(task_difficulty)
    sl = difficulty_rank(student_level)
    diff = abs(td - sl)
    if diff == 0:
        return 100.0, [{'code': 'DIFFICULTY_FIT', 'message': 'Task difficulty matches your current skill band.'}]
    if diff == 1:
        return 70.0, [{'code': 'DIFFICULTY_NEAR', 'message': 'Slightly above or below your band — good stretch.'}]
    return 45.0, [{'code': 'DIFFICULTY_MISMATCH', 'message': 'Challenge level differs from your band; still doable with effort.'}]


def repetition_penalty(
    task_id: Any,
    completed_task_ids: set,
    active_task_ids: set,
) -> tuple[float, list[dict[str, str]]]:
    """Down-rank tasks already completed or already active."""
    sid = str(task_id)
    if sid in completed_task_ids:
        return 0.0, [{'code': 'ALREADY_DONE', 'message': 'You already completed this task.'}]
    if sid in active_task_ids:
        return 15.0, [{'code': 'ALREADY_ACTIVE', 'message': 'You already have this task in progress.'}]
    return 100.0, []


def weak_area_boost(task_domain: str, weak_domains: list[str]) -> tuple[float, list[dict[str, str]]]:
    """Small boost for practicing in weak domains."""
    if not weak_domains:
        return 50.0, []
    td = (task_domain or '').strip()
    if td in weak_domains:
        return 100.0, [{'code': 'SKILL_GAP', 'message': f'Practice in an area you can improve: {td}.'}]
    return 40.0, []


def keyword_overlap_points(
    task_keywords: list[str],
    strong_domains: list[str],
    recommended_domain: str | None,
) -> tuple[float, list[dict[str, str]]]:
    """Light content-based: overlap between task keywords and domain labels."""
    if not task_keywords:
        return 50.0, []
    norm_kw = {k.lower().strip() for k in task_keywords if k}
    seeds: set[str] = set()
    if recommended_domain:
        seeds.add(recommended_domain.lower())
    for d in strong_domains or []:
        seeds.add(d.lower())
        for part in d.lower().replace('/', ' ').split():
            seeds.add(part)
    overlap = norm_kw & seeds
    if not overlap:
        return 45.0, []
    return 80.0, [{'code': 'KEYWORD_MATCH', 'message': 'Task keywords align with your profile domains.'}]


def combine_weighted_score(
    domain_pts: float,
    difficulty_pts: float,
    repeat_pts: float,
    weak_pts: float,
    keyword_pts: float,
) -> float:
    """
    Weighted hybrid score (0-100).
    Weights: domain 0.42, difficulty 0.23, repeat 0.18, weak 0.12, keyword 0.05
    """
    total = (
        0.42 * domain_pts
        + 0.23 * difficulty_pts
        + 0.18 * repeat_pts
        + 0.12 * weak_pts
        + 0.05 * keyword_pts
    )
    return round(min(100.0, max(0.0, total)), 2)
