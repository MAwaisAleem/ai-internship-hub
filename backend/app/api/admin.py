"""FR8 Admin API (Administrator role only)."""
from flask import Blueprint, request
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required

from bson import ObjectId
from bson.errors import InvalidId

from app.services import admin_service as admin_svc
from app.services.auth_service import get_user_by_id
from app.utils.decorators import role_required


def _parse_pagination():
    try:
        page = int(request.args.get('page', 1))
        page = max(1, page)
    except (TypeError, ValueError):
        page = 1
    try:
        limit = int(request.args.get('limit', 20))
        limit = max(1, min(100, limit))
    except (TypeError, ValueError):
        limit = 20
    skip = (page - 1) * limit
    return skip, limit, page


def _validate_oid(value, label='id'):
    try:
        ObjectId(value)
    except Exception:
        return {'message': f'Invalid {label} format'}, 400
    return None


class AdminOverviewView(MethodView):
    """GET /admin/overview"""

    @jwt_required()
    @role_required('Administrator')
    def get(self):
        try:
            data = admin_svc.get_overview()
            return data, 200
        except Exception as e:
            return {'message': 'Failed to load overview', 'detail': str(e)}, 500


class AdminReportsSummaryView(MethodView):
    """GET /admin/reports/summary"""

    @jwt_required()
    @role_required('Administrator')
    def get(self):
        try:
            data = admin_svc.get_reports_summary()
            return data, 200
        except Exception as e:
            return {'message': 'Failed to load report', 'detail': str(e)}, 500


class AdminUsersListView(MethodView):
    """GET /admin/users — filter by role, search q."""

    @jwt_required()
    @role_required('Administrator')
    def get(self):
        role = request.args.get('role') or None
        q = request.args.get('q') or None
        skip, limit, page = _parse_pagination()
        try:
            items, total = admin_svc.list_users(role=role, q=q, skip=skip, limit=limit)
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Failed to list users', 'detail': str(e)}, 500
        return {'users': items, 'total': total, 'page': page, 'limit': limit}, 200


class AdminUserDetailView(MethodView):
    """GET/PATCH /admin/users/<user_id>"""

    @jwt_required()
    @role_required('Administrator')
    def get(self, user_id):
        err = _validate_oid(user_id, 'user_id')
        if err:
            return err
        user = get_user_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        user.pop('_id', None)
        return {'user': user}, 200

    @jwt_required()
    @role_required('Administrator')
    def patch(self, user_id):
        err = _validate_oid(user_id, 'user_id')
        if err:
            return err
        data = request.get_json() or {}
        try:
            updated = admin_svc.update_user(user_id, data)
            return {'message': 'User updated', 'user': updated}, 200
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Failed to update user', 'detail': str(e)}, 500


class AdminRosterListView(MethodView):
    """GET /admin/roster — optional mentor_id, student_id, active."""

    @jwt_required()
    @role_required('Administrator')
    def get(self):
        mentor_id = request.args.get('mentor_id') or None
        student_id = request.args.get('student_id') or None
        active_raw = request.args.get('active')
        active = None
        if active_raw is not None:
            active = active_raw.lower() in ('1', 'true', 'yes')
        skip, limit, page = _parse_pagination()
        try:
            items, total = admin_svc.list_roster(
                mentor_id=mentor_id,
                student_id=student_id,
                active=active,
                skip=skip,
                limit=limit,
            )
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Failed to list roster', 'detail': str(e)}, 500
        return {'roster': items, 'total': total, 'page': page, 'limit': limit}, 200


class AdminRosterCreateView(MethodView):
    """POST /admin/roster — mentor_id, student_id."""

    @jwt_required()
    @role_required('Administrator')
    def post(self):
        data = request.get_json() or {}
        mentor_id = (data.get('mentor_id') or '').strip()
        student_id = (data.get('student_id') or '').strip()
        if not mentor_id or not student_id:
            return {'message': 'mentor_id and student_id are required'}, 400
        err = _validate_oid(mentor_id, 'mentor_id')
        if err:
            return err
        err = _validate_oid(student_id, 'student_id')
        if err:
            return err
        try:
            row = admin_svc.create_roster_link(mentor_id, student_id)
            return {'message': 'Roster link created', 'roster': row}, 201
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Failed to create roster link', 'detail': str(e)}, 500


class AdminRosterDetailView(MethodView):
    """PATCH /admin/roster/<roster_id> — active."""

    @jwt_required()
    @role_required('Administrator')
    def patch(self, roster_id):
        err = _validate_oid(roster_id, 'roster_id')
        if err:
            return err
        data = request.get_json() or {}
        try:
            row = admin_svc.update_roster_link(roster_id, data)
            return {'message': 'Roster link updated', 'roster': row}, 200
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Failed to update roster link', 'detail': str(e)}, 500


class AdminTasksListView(MethodView):
    """GET /admin/tasks — optional status, domain."""

    @jwt_required()
    @role_required('Administrator')
    def get(self):
        status = request.args.get('status') or None
        domain = request.args.get('domain') or None
        skip, limit, page = _parse_pagination()
        try:
            items, total = admin_svc.list_tasks_admin(status=status, domain=domain, skip=skip, limit=limit)
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Failed to list tasks', 'detail': str(e)}, 500
        return {'tasks': items, 'total': total, 'page': page, 'limit': limit}, 200

    @jwt_required()
    @role_required('Administrator')
    def post(self):
        data = request.get_json() or {}
        admin_id = get_jwt_identity()
        try:
            task = admin_svc.create_task(data, created_by_id=admin_id)
            return {'message': 'Task created', 'task': task}, 201
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Failed to create task', 'detail': str(e)}, 500


class AdminTaskDetailView(MethodView):
    """PATCH /admin/tasks/<task_id>"""

    @jwt_required()
    @role_required('Administrator')
    def patch(self, task_id):
        err = _validate_oid(task_id, 'task_id')
        if err:
            return err
        data = request.get_json() or {}
        try:
            task = admin_svc.update_task(task_id, data)
            return {'message': 'Task updated', 'task': task}, 200
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Failed to update task', 'detail': str(e)}, 500


class AdminSubmissionsListView(MethodView):
    """GET /admin/submissions — optional user_id, status, task_type."""

    @jwt_required()
    @role_required('Administrator')
    def get(self):
        user_id = request.args.get('user_id') or None
        status = request.args.get('status') or None
        task_type = request.args.get('task_type') or None
        if user_id:
            err = _validate_oid(user_id, 'user_id')
            if err:
                return err
        skip, limit, page = _parse_pagination()
        try:
            items, total = admin_svc.list_submissions_admin(
                user_id=user_id,
                status=status,
                task_type=task_type,
                skip=skip,
                limit=limit,
            )
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Failed to list submissions', 'detail': str(e)}, 500
        return {'submissions': items, 'total': total, 'page': page, 'limit': limit}, 200


class AdminSubmissionDetailView(MethodView):
    """GET /admin/submissions/<submission_id>"""

    @jwt_required()
    @role_required('Administrator')
    def get(self, submission_id):
        err = _validate_oid(submission_id, 'submission_id')
        if err:
            return err
        detail = admin_svc.get_submission_detail_admin(submission_id)
        if not detail:
            return {'message': 'Submission not found'}, 404
        return detail, 200


admin_bp = Blueprint('admin', __name__)

admin_bp.add_url_rule('/overview', view_func=AdminOverviewView.as_view('overview'), methods=['GET'])
admin_bp.add_url_rule(
    '/reports/summary',
    view_func=AdminReportsSummaryView.as_view('reports_summary'),
    methods=['GET'],
)
admin_bp.add_url_rule('/users', view_func=AdminUsersListView.as_view('users_list'), methods=['GET'])
admin_bp.add_url_rule(
    '/users/<user_id>',
    view_func=AdminUserDetailView.as_view('users_detail'),
    methods=['GET', 'PATCH'],
)
admin_bp.add_url_rule('/roster', view_func=AdminRosterListView.as_view('roster_list'), methods=['GET'])
admin_bp.add_url_rule('/roster', view_func=AdminRosterCreateView.as_view('roster_create'), methods=['POST'])
admin_bp.add_url_rule(
    '/roster/<roster_id>',
    view_func=AdminRosterDetailView.as_view('roster_detail'),
    methods=['PATCH'],
)
admin_bp.add_url_rule('/tasks', view_func=AdminTasksListView.as_view('tasks_list'), methods=['GET', 'POST'])
admin_bp.add_url_rule(
    '/tasks/<task_id>',
    view_func=AdminTaskDetailView.as_view('tasks_detail'),
    methods=['PATCH'],
)
admin_bp.add_url_rule(
    '/submissions',
    view_func=AdminSubmissionsListView.as_view('submissions_list'),
    methods=['GET'],
)
admin_bp.add_url_rule(
    '/submissions/<submission_id>',
    view_func=AdminSubmissionDetailView.as_view('submissions_detail'),
    methods=['GET'],
)
