"""
MongoDB document shapes for FR3: tasks, assignments, and student progress.

These are documentation constants — MongoDB is schemaless; validate in services/APIs.

--- Collection: tasks ---
{
  "title": str,
  "description": str,
  "domain": str,              # Must align with assessment_service.DOMAINS where possible
  "difficulty": str,          # TASK_DIFFICULTY_* below
  "tags": [str],              # optional
  "keywords": [str],          # optional, for light content-based matching
  "status": str,              # TASK_STATUS_* below
  "estimated_hours": int,     # optional
  "created_at": datetime (UTC),
  "updated_at": datetime (UTC),
  "created_by": ObjectId | null,  # admin user id if applicable
}

--- Collection: task_assignments ---
{
  "user_id": ObjectId,
  "task_id": ObjectId,
  "status": str,              # ASSIGNMENT_STATUS_* below
  "claimed_at": datetime,
  "started_at": datetime | null,
  "completed_at": datetime | null,
  "recommendation_snapshot": {   # filled at claim time from recommendation engine
    "score": float,
    "reasons": [{ "code": str, "message": str }]
  } | null,
}

Index (recommended): unique compound on (user_id, task_id) for active uniqueness checks.

--- Collection: student_progress ---
{
  "user_id": ObjectId,        # unique per student
  "weak_domains": [str],      # derived from latest assessment
  "strong_domains": [str],
  "completed_count_by_domain": { str: int },
  "total_completed": int,
  "last_recommendation_at": datetime | null,
  "last_recommendation_items": [   # snapshot from last GET /tasks/recommended
    {
      "task_id": str,
      "score": float,
      "reasons": [{ "code": str, "message": str }]
    }
  ],
  "updated_at": datetime,
}
"""

# Task lifecycle in catalog
TASK_STATUS_OPEN = 'open'
TASK_STATUS_CLOSED = 'closed'

# Assignment lifecycle
ASSIGNMENT_CLAIMED = 'claimed'
ASSIGNMENT_IN_PROGRESS = 'in_progress'
ASSIGNMENT_SUBMITTED = 'submitted'
ASSIGNMENT_COMPLETED = 'completed'
ASSIGNMENT_DROPPED = 'dropped'

TASK_DIFFICULTY_BEGINNER = 'beginner'
TASK_DIFFICULTY_INTERMEDIATE = 'intermediate'
TASK_DIFFICULTY_ADVANCED = 'advanced'
