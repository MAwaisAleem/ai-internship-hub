"""FR5 Mentor dashboard API (Mentor role only)."""
from flask import request
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services import mentor_service as mentor_svc
from app.utils.decorators import role_required

from flask import Blueprint


def _parse_limit(default=50, cap=100):
    try:
        n = int(request.args.get('limit', default))
        return max(1, min(cap, n))
    except (TypeError, ValueError):
        return default


def _parse_skip():
    try:
        return max(0, int(request.args.get('skip', 0)))
    except (TypeError, ValueError):
        return 0


class MentorStudentsView(MethodView):
    """GET /mentor/students — students on this mentor's roster."""

    @jwt_required()
    @role_required('Mentor')
    def get(self):
        mentor_id = get_jwt_identity()
        try:
            students = mentor_svc.list_assigned_students(mentor_id)
            return {'students': students}, 200
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Failed to load roster', 'detail': str(e)}, 500


class MentorStudentProgressView(MethodView):
    """GET /mentor/students/<student_id>/progress"""

    @jwt_required()
    @role_required('Mentor')
    def get(self, student_id):
        mentor_id = get_jwt_identity()
        try:
            summary = mentor_svc.get_student_progress_summary(mentor_id, student_id)
            return {'progress': summary}, 200
        except PermissionError as e:
            return {'message': str(e)}, 403
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Failed to load progress', 'detail': str(e)}, 500


class MentorPendingSubmissionsView(MethodView):
    """GET /mentor/submissions/pending — evaluated submissions awaiting mentor review."""

    @jwt_required()
    @role_required('Mentor')
    def get(self):
        mentor_id = get_jwt_identity()
        limit = _parse_limit(default=50, cap=100)
        try:
            items = mentor_svc.list_pending_submissions_for_mentor(mentor_id, limit=limit)
            return {'submissions': items, 'count': len(items)}, 200
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Failed to load pending submissions', 'detail': str(e)}, 500


class MentorSubmissionDetailView(MethodView):
    """GET /mentor/submissions/<submission_id> — full submission + evaluation + existing review."""

    @jwt_required()
    @role_required('Mentor')
    def get(self, submission_id):
        mentor_id = get_jwt_identity()
        try:
            detail = mentor_svc.get_submission_detail_for_mentor(mentor_id, submission_id)
            if not detail:
                return {'message': 'Submission not found'}, 404
            return detail, 200
        except PermissionError as e:
            return {'message': str(e)}, 403
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Failed to load submission', 'detail': str(e)}, 500


class MentorSubmissionFeedbackView(MethodView):
    """POST /mentor/submissions/<submission_id>/feedback — submit or update mentor feedback."""

    @jwt_required()
    @role_required('Mentor')
    def post(self, submission_id):
        mentor_id = get_jwt_identity()
        data = request.get_json() or {}
        feedback = data.get('feedback')
        try:
            review = mentor_svc.submit_mentor_feedback(mentor_id, submission_id, feedback)
            return {'message': 'Feedback saved', 'mentor_review': review}, 200
        except PermissionError as e:
            return {'message': str(e)}, 403
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Failed to save feedback', 'detail': str(e)}, 500


class MentorFeedbackHistoryView(MethodView):
    """GET /mentor/reviews/history — completed mentor reviews with pagination."""

    @jwt_required()
    @role_required('Mentor')
    def get(self):
        mentor_id = get_jwt_identity()
        limit = _parse_limit(default=50, cap=100)
        skip = _parse_skip()
        try:
            items, total = mentor_svc.list_feedback_history(mentor_id, limit=limit, skip=skip)
            return {'reviews': items, 'total': total, 'limit': limit, 'skip': skip}, 200
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Failed to load history', 'detail': str(e)}, 500


mentor_bp = Blueprint('mentor', __name__)

mentor_bp.add_url_rule('/students', view_func=MentorStudentsView.as_view('students'), methods=['GET'])
mentor_bp.add_url_rule(
    '/students/<student_id>/progress',
    view_func=MentorStudentProgressView.as_view('student_progress'),
    methods=['GET'],
)
mentor_bp.add_url_rule(
    '/submissions/pending',
    view_func=MentorPendingSubmissionsView.as_view('pending_submissions'),
    methods=['GET'],
)
mentor_bp.add_url_rule(
    '/submissions/<submission_id>',
    view_func=MentorSubmissionDetailView.as_view('submission_detail'),
    methods=['GET'],
)
mentor_bp.add_url_rule(
    '/submissions/<submission_id>/feedback',
    view_func=MentorSubmissionFeedbackView.as_view('submission_feedback'),
    methods=['POST'],
)
mentor_bp.add_url_rule(
    '/reviews/history',
    view_func=MentorFeedbackHistoryView.as_view('feedback_history'),
    methods=['GET'],
)
