"""FR9: Analytics API (Student, Mentor, Administrator)."""
from flask import Blueprint
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services import analytics_service as analytics_svc
from app.utils.decorators import role_required


class StudentAnalyticsView(MethodView):
    """GET /analytics/me — current student's analytics only."""

    @jwt_required()
    @role_required('Student')
    def get(self):
        user_id = get_jwt_identity()
        try:
            data = analytics_svc.get_student_analytics(user_id)
            return data, 200
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Failed to load analytics', 'detail': str(e)}, 500


class MentorAnalyticsView(MethodView):
    """GET /analytics/mentor — roster-scoped analytics for the current mentor."""

    @jwt_required()
    @role_required('Mentor')
    def get(self):
        mentor_id = get_jwt_identity()
        try:
            data = analytics_svc.get_mentor_analytics(mentor_id)
            return data, 200
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Failed to load analytics', 'detail': str(e)}, 500


class AdminAnalyticsSummaryView(MethodView):
    """GET /analytics/admin/summary — platform-wide summary."""

    @jwt_required()
    @role_required('Administrator')
    def get(self):
        try:
            data = analytics_svc.get_admin_analytics_summary()
            return data, 200
        except Exception as e:
            return {'message': 'Failed to load analytics', 'detail': str(e)}, 500


analytics_bp = Blueprint('analytics', __name__)

analytics_bp.add_url_rule('/me', view_func=StudentAnalyticsView.as_view('student_me'), methods=['GET'])
analytics_bp.add_url_rule('/mentor', view_func=MentorAnalyticsView.as_view('mentor'), methods=['GET'])
analytics_bp.add_url_rule(
    '/admin/summary',
    view_func=AdminAnalyticsSummaryView.as_view('admin_summary'),
    methods=['GET'],
)
