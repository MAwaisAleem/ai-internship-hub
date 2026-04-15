"""FR7: Free, lightweight career guidance chatbot (Student-focused)."""
from __future__ import annotations

import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

from bson import ObjectId

from app.extensions import mongo
from app.services.assessment_service import get_latest_result
from app.services.portfolio_service import build_portfolio


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: Any) -> str | None:
    if dt is None:
        return None
    if hasattr(dt, "isoformat"):
        return dt.isoformat()
    return str(dt)


def _oid(value: str, label: str = "id") -> ObjectId:
    try:
        return ObjectId(value)
    except Exception as e:
        raise ValueError(f"Invalid {label}") from e


STOPWORDS = {
    "the",
    "a",
    "an",
    "is",
    "am",
    "are",
    "to",
    "for",
    "and",
    "or",
    "of",
    "in",
    "on",
    "my",
    "me",
    "i",
    "you",
    "it",
    "with",
    "how",
    "what",
    "can",
    "should",
    "please",
    "help",
    "about",
    "this",
    "that",
    "from",
}


INTENT_RULES: dict[str, list[str]] = {
    "greeting": ["hi", "hello", "hey", "good morning", "good evening"],
    "freelancing_guidance": ["freelancing", "client", "gig", "upwork", "fiverr", "start"],
    "proposal_profile_advice": ["proposal", "bid", "cover letter", "profile", "headline", "bio"],
    "portfolio_improvement": ["portfolio", "project", "sample", "showcase"],
    "learning_path": ["learn", "roadmap", "plan", "improve", "study", "practice"],
    "task_help": ["task", "assignment", "submission", "deadline", "review", "score"],
}


TOPIC_MAP: dict[str, list[str]] = {
    "proposal": ["proposal", "bid", "cover", "client"],
    "portfolio": ["portfolio", "project", "sample", "showcase"],
    "learning": ["learn", "roadmap", "practice", "study", "skill"],
    "tasks": ["task", "assignment", "submission", "deadline", "review", "score"],
    "freelancing": ["freelancing", "gig", "client", "upwork", "fiverr", "profile"],
}


def ensure_chatbot_indexes() -> None:
    """Idempotent indexes for session/history reads."""
    try:
        mongo.db.chat_sessions.create_index([("user_id", 1), ("updated_at", -1)], name="chat_sessions_user_updated")
    except Exception:
        pass
    try:
        mongo.db.chat_messages.create_index([("session_id", 1), ("created_at", 1)], name="chat_messages_session_time")
    except Exception:
        pass


@lru_cache(maxsize=1)
def _load_kb() -> list[dict[str, Any]]:
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chatbot_kb.json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return [d for d in data if isinstance(d, dict)]
    except Exception:
        pass
    return []


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{1,}", (text or "").lower())


def _extract_keywords(text: str, cap: int = 8) -> list[str]:
    tokens = [t for t in _tokenize(text) if t not in STOPWORDS]
    cnt = Counter(tokens)
    return [k for k, _ in cnt.most_common(cap)]


def _detect_topics(keywords: list[str]) -> list[str]:
    topics: list[str] = []
    kw_set = set(keywords)
    for topic, words in TOPIC_MAP.items():
        if kw_set.intersection(words):
            topics.append(topic)
    return topics


def _detect_intent(message: str, keywords: list[str]) -> tuple[str, float]:
    text = (message or "").lower()
    best_intent = "fallback"
    best_score = 0
    kw_set = set(keywords)

    for intent, phrases in INTENT_RULES.items():
        score = 0
        for ph in phrases:
            if " " in ph:
                if ph in text:
                    score += 3
            else:
                if ph in kw_set:
                    score += 2
                elif ph in text:
                    score += 1
        if score > best_score:
            best_score = score
            best_intent = intent

    if best_intent == "fallback":
        return best_intent, 0.35
    confidence = min(0.95, 0.45 + 0.08 * best_score)
    return best_intent, round(confidence, 2)


def _get_student_context(user_id: str) -> dict[str, Any]:
    uid = _oid(user_id, "user_id")

    assessment = get_latest_result(user_id)
    assignments = list(mongo.db.task_assignments.find({"user_id": uid}))
    completed = 0
    pending = 0
    for a in assignments:
        st = (a.get("status") or "").lower()
        if st == "completed":
            completed += 1
        elif st != "dropped":
            pending += 1

    portfolio_ready = False
    portfolio_summary = None
    top_domain = None
    try:
        portfolio = build_portfolio(user_id)
        readiness = portfolio.get("readiness") if isinstance(portfolio, dict) else {}
        portfolio_ready = bool(readiness.get("has_projects")) if isinstance(readiness, dict) else False
        portfolio_summary = readiness.get("summary_line") if isinstance(readiness, dict) else None
        domains = portfolio.get("domains") if isinstance(portfolio, dict) else []
        if isinstance(domains, list) and domains:
            top_domain = domains[0].get("domain")
    except Exception:
        # Keep chatbot resilient when optional data is missing.
        pass

    return {
        "assessment": {
            "recommended_domain": assessment.get("recommended_domain") if assessment else None,
            "overall_score": assessment.get("overall_score") if assessment else None,
        },
        "tasks": {
            "completed": completed,
            "pending": pending,
            "total": len(assignments),
        },
        "portfolio": {
            "ready": portfolio_ready,
            "summary_line": portfolio_summary,
            "top_domain": top_domain,
        },
    }


def _rank_kb(intent: str, keywords: list[str], topics: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    kb = _load_kb()
    kw_set = set(keywords)
    topic_set = set(topics)
    preferred_domain = (context.get("assessment") or {}).get("recommended_domain")

    scored: list[tuple[int, dict[str, Any]]] = []
    for item in kb:
        score = 0
        if item.get("intent") == intent:
            score += 6
        elif intent == "fallback":
            score += 1

        tags = set(item.get("tags") or [])
        score += 2 * len(tags.intersection(topic_set))
        item_kw = set(item.get("keywords") or [])
        score += len(item_kw.intersection(kw_set))

        if preferred_domain:
            pd = str(preferred_domain).lower()
            if pd in " ".join([str(x).lower() for x in item.get("tags") or []]):
                score += 1

        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:2]]


def _format_context_line(ctx: dict[str, Any]) -> str | None:
    parts: list[str] = []
    ass = ctx.get("assessment") or {}
    tasks = ctx.get("tasks") or {}
    port = ctx.get("portfolio") or {}

    if ass.get("recommended_domain"):
        parts.append(f"recommended domain: {ass['recommended_domain']}")
    if tasks.get("total"):
        parts.append(f"tasks completed {tasks.get('completed', 0)}/{tasks.get('total', 0)}")
    if port.get("ready"):
        parts.append("portfolio has evaluated projects")
    elif port.get("summary_line"):
        parts.append("portfolio can still be improved")

    if not parts:
        return None
    return "Based on your current progress (" + "; ".join(parts) + "), here is a focused plan:"


INTENT_OPENERS = {
    "greeting": "Hi! I can help with freelancing guidance, proposals, portfolio tips, learning plans, and task help.",
    "freelancing_guidance": "Great question about freelancing growth.",
    "proposal_profile_advice": "Let’s improve your proposal/profile quality.",
    "portfolio_improvement": "Let’s strengthen your portfolio for better client trust.",
    "learning_path": "Here’s a practical learning path you can follow.",
    "task_help": "Let’s improve your task completion and submission quality.",
    "fallback": "I can still help. Let me give you practical guidance from the project knowledge base.",
}


def _compose_reply(intent: str, kb_items: list[dict[str, Any]], context: dict[str, Any]) -> tuple[str, list[str]]:
    lines: list[str] = [INTENT_OPENERS.get(intent, INTENT_OPENERS["fallback"])]
    ctx_line = _format_context_line(context)
    if ctx_line:
        lines.append("")
        lines.append(ctx_line)

    suggestions: list[str] = []
    if kb_items:
        item = kb_items[0]
        tips = item.get("tips") or []
        checklist = item.get("checklist") or []
        lines.append("")
        lines.append(f"{item.get('title')}:")
        for t in tips[:3]:
            lines.append(f"- {t}")
        if checklist:
            lines.append("")
            lines.append("Quick checklist:")
            for c in checklist[:4]:
                lines.append(f"- {c}")
        for it in kb_items:
            for s in (it.get("suggestions") or []):
                if s not in suggestions:
                    suggestions.append(s)
    else:
        lines.append("")
        lines.extend(
            [
                "- Keep your profile focused on one service and one client outcome.",
                "- Build 1-2 focused portfolio projects before applying broadly.",
                "- Send personalized proposals with a clear delivery plan.",
            ]
        )
        suggestions = [
            "How do I improve my profile headline?",
            "Give me a proposal template for beginners.",
            "How should I plan learning for my domain?",
        ]

    return "\n".join(lines).strip(), suggestions[:4]


def _get_or_create_session(user_oid: ObjectId, session_id: str | None, first_message: str) -> tuple[ObjectId, bool]:
    if session_id:
        sid = _oid(session_id, "session_id")
        s = mongo.db.chat_sessions.find_one({"_id": sid, "user_id": user_oid})
        if not s:
            raise ValueError("Chat session not found")
        return sid, False

    now = _utcnow()
    title = (first_message or "").strip()[:80] or "Career guidance chat"
    doc = {
        "user_id": user_oid,
        "title": title,
        "created_at": now,
        "updated_at": now,
    }
    ins = mongo.db.chat_sessions.insert_one(doc)
    return ins.inserted_id, True


def _serialize_message(m: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(m["_id"]),
        "session_id": str(m["session_id"]),
        "role": m.get("role"),
        "content": m.get("content"),
        "intent": m.get("intent"),
        "confidence": m.get("confidence"),
        "keywords": m.get("keywords") or [],
        "created_at": _iso(m.get("created_at")),
    }


def get_chat_history(user_id: str, session_id: str, limit: int = 30) -> dict[str, Any]:
    ensure_chatbot_indexes()
    uid = _oid(user_id, "user_id")
    sid = _oid(session_id, "session_id")
    s = mongo.db.chat_sessions.find_one({"_id": sid, "user_id": uid})
    if not s:
        raise ValueError("Chat session not found")

    cur = (
        mongo.db.chat_messages.find({"session_id": sid})
        .sort("created_at", 1)
        .limit(max(1, min(100, int(limit or 30))))
    )
    return {
        "session_id": session_id,
        "title": s.get("title"),
        "messages": [_serialize_message(m) for m in cur],
    }


def get_quick_suggestions(user_id: str) -> dict[str, Any]:
    context = _get_student_context(user_id)
    suggestions = [
        "How can I start freelancing with my current skill level?",
        "Help me improve my portfolio for clients.",
        "Give me a better proposal structure.",
        "Create a weekly learning plan for me.",
        "How can I improve my task scores?",
    ]
    rec_dom = (context.get("assessment") or {}).get("recommended_domain")
    if rec_dom:
        suggestions.insert(0, f"What should I learn next for {rec_dom}?")
    return {"suggestions": suggestions[:6], "context_used": context}


def respond_to_message(user_id: str, message: str, session_id: str | None = None) -> dict[str, Any]:
    """Main chatbot entrypoint."""
    ensure_chatbot_indexes()
    text = (message or "").strip()
    if not text:
        raise ValueError("message is required")
    if len(text) > 2000:
        raise ValueError("message is too long")

    uid = _oid(user_id, "user_id")
    sid, _created = _get_or_create_session(uid, session_id, text)
    now = _utcnow()

    keywords = _extract_keywords(text)
    topics = _detect_topics(keywords)
    intent, confidence = _detect_intent(text, keywords)
    context = _get_student_context(user_id)
    kb_items = _rank_kb(intent, keywords, topics, context)
    reply, suggestions = _compose_reply(intent, kb_items, context)

    mongo.db.chat_messages.insert_one(
        {
            "session_id": sid,
            "user_id": uid,
            "role": "user",
            "content": text,
            "created_at": now,
        }
    )
    assistant_doc = {
        "session_id": sid,
        "user_id": uid,
        "role": "assistant",
        "content": reply,
        "intent": intent,
        "confidence": confidence,
        "keywords": keywords,
        "topics": topics,
        "created_at": _utcnow(),
    }
    ins = mongo.db.chat_messages.insert_one(assistant_doc)
    mongo.db.chat_sessions.update_one(
        {"_id": sid, "user_id": uid},
        {
            "$set": {
                "updated_at": _utcnow(),
                "last_intent": intent,
                "last_keywords": keywords[:8],
            }
        },
    )

    return {
        "session_id": str(sid),
        "message_id": str(ins.inserted_id),
        "intent": intent,
        "confidence": confidence,
        "keywords": keywords,
        "topics": topics,
        "reply": reply,
        "suggestions": suggestions,
        "context_used": {
            "assessment_used": bool((context.get("assessment") or {}).get("recommended_domain")),
            "task_progress_used": bool((context.get("tasks") or {}).get("total")),
            "portfolio_used": bool((context.get("portfolio") or {}).get("summary_line") or (context.get("portfolio") or {}).get("ready")),
        },
    }
