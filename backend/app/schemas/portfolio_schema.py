"""FR6: Portfolio read-model — response shape documentation (MongoDB remains schemaless).

GET /api/portfolio/me returns a single JSON object:

{
  "profile": { "id", "name", "email", "role" },
  "readiness": {
    "summary_line": str,
    "domains": [{ "domain", "completed_count", "avg_score" | null }],
    "skill_tags": [str],
  },
  "assessment": { ... } | null,   # latest MCQ summary (optional)
  "highlights": [{ "text": str }],
  "projects": [
    {
      "assignment_id": str,
      "assignment_status": str | null,
      "submission_id": str,
      "task": { "id", "title", "domain", "task_type", "difficulty" },
      "completed_at": str | null,
      "evaluation": {
        "overall_score": float | null,
        "feedback_summary": str | null,
        "score_breakdown": object,
        "strengths": [str],
        "areas_for_improvement": [str],
      } | null,
      "mentor_feedback": {
        "has_feedback": bool,
        "feedback": str | null,
        "completed_at": str | null,
      } | null,
    }
  ],
  "meta": { "generated_at": ISO8601, "version": int },
}

Projects are derived from evaluated submissions (latest per assignment). No separate portfolios collection in v1.
"""

PORTFOLIO_RESPONSE_VERSION = 1
