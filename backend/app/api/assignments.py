"""Student task assignments (read-only) for FR3/FR4 UI."""
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.assignment_service import get_assignment_for_student, list_assignments_for_student
from app.utils.decorators import role_required

from flask import Blueprint


class AssignmentListView(MethodView):
    """GET /assignments — current student's assignments with task summary."""

    @jwt_required()
    @role_required('Student')
    def get(self):
        user_id = get_jwt_identity()
        items = list_assignments_for_student(user_id)
        return {'assignments': items}, 200


class AssignmentDetailView(MethodView):
    """GET /assignments/<assignment_id>"""

    @jwt_required()
    @role_required('Student')
    def get(self, assignment_id):
        user_id = get_jwt_identity()
        row = get_assignment_for_student(user_id, assignment_id)
        if not row:
            return {'message': 'Assignment not found or access denied'}, 404
        return {'assignment': row}, 200


assignments_bp = Blueprint('assignments', __name__)
assignments_bp.add_url_rule('', view_func=AssignmentListView.as_view('list'), methods=['GET'])
assignments_bp.add_url_rule(
    '/<assignment_id>',
    view_func=AssignmentDetailView.as_view('detail'),
    methods=['GET'],
)
