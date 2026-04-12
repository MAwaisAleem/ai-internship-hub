"""
Lightweight writing evaluation: grammar-style heuristics, word count, keywords, similarity.
No external NLP dependencies — uses stdlib (re, difflib, collections).
"""
from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any


def _normalize_ws(text: str) -> str:
    return re.sub(r'\s+', ' ', (text or '').strip())


def _word_count(text: str) -> int:
    if not (text or '').strip():
        return 0
    return len(re.findall(r'\b[\w\'-]+\b', text, flags=re.UNICODE))


def _grammar_style_checks(text: str) -> tuple[float, list[str], list[str]]:
    """
    Returns grammar_score 0-100, issues (for improvements), strengths.
    Heuristic only — not a full grammar engine.
    """
    issues: list[str] = []
    strengths: list[str] = []
    t = text or ''
    if not t.strip():
        return 0.0, ['Text is empty.'], []

    # Double spaces (after normalize, still check raw)
    if '  ' in t:
        issues.append('Remove double spaces between words.')

    # Repeated words (e.g. "the the")
    if re.search(r'\b(\w+)\s+\1\b', t, flags=re.IGNORECASE):
        issues.append('Repeated words detected; proofread for duplicates.')

    words = re.findall(r'\b[\w\'-]+\b', t, flags=re.UNICODE)
    if len(words) >= 10:
        strengths.append('Adequate length for basic analysis.')

    # Sentence length — flag very long sentences
    sentences = re.split(r'(?<=[.!?])\s+', t.strip())
    long_sents = [s for s in sentences if _word_count(s) > 45]
    if long_sents:
        issues.append('Some sentences are very long; consider splitting for readability.')

    # Paragraph structure
    if '\n\n' in t or t.count('\n') >= 2:
        strengths.append('Text uses paragraph breaks.')

    # Score: start at 100, deduct per issue
    deductions = min(60, 12 * len(issues))
    score = max(40.0, 100.0 - deductions)

    if not issues:
        strengths.append('No major formatting issues detected.')
        score = min(100.0, score + 5.0)

    return float(score), issues, strengths


def _word_count_score(count: int, min_w: int, max_w: int) -> tuple[float, list[str], list[str]]:
    """0-100 based on falling inside [min_w, max_w]."""
    strengths: list[str] = []
    improvements: list[str] = []
    if min_w <= 0:
        min_w = 1
    if max_w < min_w:
        max_w = min_w + 500

    if count < min_w:
        improvements.append(f'Word count ({count}) is below the minimum ({min_w}).')
        # partial credit
        ratio = count / float(min_w) if min_w else 0
        return max(20.0, 100.0 * ratio * 0.85), [], improvements

    if count > max_w:
        improvements.append(f'Word count ({count}) exceeds the maximum ({max_w}).')
        over = count - max_w
        penalty = min(50.0, over / max(max_w, 1) * 40.0)
        return max(30.0, 100.0 - penalty), [], improvements

    strengths.append(f'Word count ({count}) meets the required range ({min_w}–{max_w}).')
    return 100.0, strengths, improvements


def _keyword_score(text: str, keywords: list[str]) -> tuple[float, list[str], list[str]]:
    """Percentage of required keywords present (case-insensitive)."""
    if not keywords:
        return 85.0, ['No keywords required for this task.'], []

    lowered = (text or '').lower()
    found = []
    missing = []
    for kw in keywords:
        k = (kw or '').strip()
        if not k:
            continue
        if k.lower() in lowered:
            found.append(k)
        else:
            missing.append(k)

    pct = len(found) / len(keywords) if keywords else 0
    score = 100.0 * pct

    strengths = []
    improvements = []
    if found:
        strengths.append(f'Keywords found: {", ".join(found[:8])}{"…" if len(found) > 8 else ""}.')
    if missing:
        improvements.append(f'Consider incorporating: {", ".join(missing[:8])}{"…" if len(missing) > 8 else ""}.')

    return float(score), strengths, improvements


def _similarity_score(text: str, reference: str | None) -> tuple[float, list[str], list[str]]:
    """
    difflib ratio on normalized strings. If no reference, neutral high score with explanation.
    """
    if not (reference or '').strip():
        return 92.0, ['No reference passage configured; similarity not measured against a model answer.'], []

    a = _normalize_ws(text).lower()
    b = _normalize_ws(reference).lower()
    if not a or not b:
        return 50.0, [], ['Provide substantive text for similarity scoring.']

    ratio = SequenceMatcher(None, a, b).ratio()
    score = round(ratio * 100, 2)

    strengths = []
    improvements = []
    if score >= 70:
        strengths.append('Your text shows strong alignment with the reference structure/wording.')
    elif score >= 45:
        improvements.append('Increase alignment with the task reference (themes and phrasing).')
    else:
        improvements.append('Text differs substantially from the reference; review task instructions.')

    return float(score), strengths, improvements


def evaluate_writing_text(text: str, task_config: dict[str, Any]) -> dict[str, Any]:
    """
    task_config: min_words, max_words, keywords (list), reference_text (optional str)
    Returns structured evaluation for MongoDB and API.
    """
    min_w = int(task_config.get('min_words') or 100)
    max_w = int(task_config.get('max_words') or 800)
    keywords = task_config.get('keywords') or []
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(',') if k.strip()]
    reference = task_config.get('reference_text') or task_config.get('reference_passage')

    raw = text or ''
    wc = _word_count(raw)

    g_score, g_issues, g_strengths = _grammar_style_checks(raw)
    wc_score, wc_strengths, wc_improvements = _word_count_score(wc, min_w, max_w)
    kw_score, kw_strengths, kw_improvements = _keyword_score(raw, keywords)
    sim_score, sim_strengths, sim_improvements = _similarity_score(raw, reference)

    breakdown = {
        'grammar_style': round(g_score, 2),
        'word_count': round(wc_score, 2),
        'keyword_relevance': round(kw_score, 2),
        'text_similarity': round(sim_score, 2),
    }

    weights = {'grammar_style': 0.25, 'word_count': 0.25, 'keyword_relevance': 0.25, 'text_similarity': 0.25}
    overall = sum(breakdown[k] * weights[k] for k in weights)
    overall = round(min(100.0, max(0.0, overall)), 2)

    all_strengths = (
        g_strengths + wc_strengths + kw_strengths + sim_strengths
    )
    all_improvements = (
        g_issues + wc_improvements + kw_improvements + sim_improvements
    )

    # Dedupe while preserving order
    def dedupe(seq):
        seen = set()
        out = []
        for x in seq:
            if x and x not in seen:
                seen.add(x)
                out.append(x)
        return out[:12]

    strengths = dedupe(all_strengths)
    improvements = dedupe(all_improvements)

    feedback = (
        f'Overall score {overall}/100. '
        f'Grammar/style {breakdown["grammar_style"]:.0f}, '
        f'word count fit {breakdown["word_count"]:.0f}, '
        f'keywords {breakdown["keyword_relevance"]:.0f}, '
        f'similarity {breakdown["text_similarity"]:.0f}.'
    )

    return {
        'overall_score': overall,
        'score_breakdown': breakdown,
        'feedback_summary': feedback,
        'strengths': strengths if strengths else ['You submitted a complete attempt.'],
        'areas_for_improvement': improvements if improvements else ['Keep refining clarity and structure.'],
        'details': {
            'word_count': wc,
            'min_words': min_w,
            'max_words': max_w,
            'grammar_issues': g_issues,
            'keywords_required': len(keywords),
            'keywords_matched': sum(1 for k in keywords if k and k.lower() in (raw or '').lower()),
            'similarity_method': 'difflib.SequenceMatcher on normalized text vs reference' if (reference or '').strip() else 'skipped (no reference)',
        },
    }
