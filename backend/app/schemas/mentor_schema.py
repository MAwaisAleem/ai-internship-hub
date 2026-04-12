"""MongoDB document shapes for FR5 mentor roster and reviews."""

# mentor_roster collection:
# - mentor_id: ObjectId (users)
# - student_id: ObjectId (users)
# - active: bool
# - created_at: datetime
# Unique compound index (mentor_id, student_id)

# mentor_reviews collection:
# - submission_id: ObjectId (submissions) — one review doc per submission
# - mentor_id: ObjectId
# - student_id: ObjectId
# - feedback: str
# - status: 'pending' | 'completed'
# - created_at, updated_at, completed_at (optional until completed)
# Unique index on submission_id

MENTOR_REVIEW_STATUS_PENDING = 'pending'
MENTOR_REVIEW_STATUS_COMPLETED = 'completed'
