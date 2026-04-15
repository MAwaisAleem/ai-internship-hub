<<<<<<< HEAD
"""Submission status and task type constants (aligned with FR4).

Imported by submission_service, evaluation_service, portfolio, mentor, analytics.
"""

# Submission lifecycle (MongoDB `submissions.status`)
SUBMISSION_STATUS_PENDING = "pending"
SUBMISSION_STATUS_EVALUATED = "evaluated"
SUBMISSION_STATUS_FAILED = "failed"

# Task / submission kind (must match task documents and API validation)
TASK_TYPE_WRITING = "writing"
TASK_TYPE_PROGRAMMING = "programming"
TASK_TYPE_DESIGN = "design"
=======
"""Submission status and task type constants (aligned with FR4)."""



SUBMISSION_STATUS_PENDING = 'pending'

SUBMISSION_STATUS_EVALUATED = 'evaluated'

SUBMISSION_STATUS_FAILED = 'failed'



TASK_TYPE_WRITING = 'writing'

TASK_TYPE_PROGRAMMING = 'programming'

TASK_TYPE_DESIGN = 'design'
>>>>>>> a36fdcbf362d96dd9834ae691373adf330fa6c4b
