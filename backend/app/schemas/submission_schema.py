"""MongoDB document shapes for submissions and evaluations."""

SUBMISSION_STATUS_PENDING = 'pending'
SUBMISSION_STATUS_EVALUATED = 'evaluated'
SUBMISSION_STATUS_FAILED = 'failed'

TASK_TYPE_WRITING = 'writing'
TASK_TYPE_PROGRAMMING = 'programming'
TASK_TYPE_DESIGN = 'design'

# submissions collection:
# - writing: text_content
# - programming: code_content
# - design: design_file { relative_path, original_filename, content_type, size_bytes }; optional student_notes
# shared: user_id, assignment_id, task_id, task_type, status, evaluation, created_at, updated_at
