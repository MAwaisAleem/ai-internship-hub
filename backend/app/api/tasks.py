"""FR3 Task allocation & recommendation API (Student)."""
from flask import request
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from bson import ObjectId
from bson.errors import InvalidId

from app.services.recommendation_service import (
    persist_recommendation_snapshot,
    rank_tasks_for_student,
)
from app.services import task_service as task_svc
from app.utils.decorators import role_required


def _parse_limit(default=10, cap=50):
    try:
        raw = request.args.get('limit', default)
        n = int(raw)
        return max(1, min(cap, n))
    except (TypeError, ValueError):
        return default


def _validate_task_id(task_id):
    """Return None if valid ObjectId string, else an error response tuple (body, status)."""
    if not task_id or not isinstance(task_id, str):
        return ({'message': 'Invalid task id'}, 400)
    try:
        ObjectId(task_id)
    except InvalidId:
        return ({'message': 'Invalid task id format'}, 400)
    return None


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


class RecommendedTasksView(MethodView):
    """GET /tasks/recommended — ranked tasks with reasons; stores snapshot on student_progress."""

    @jwt_required()
    @role_required('Student')
    def get(self):
        user_id = get_jwt_identity()
        limit = _parse_limit(default=20, cap=30)
        try:
            ranked, ctx = rank_tasks_for_student(user_id, limit=limit)
        except Exception as e:
            return {'message': 'Failed to build recommendations', 'detail': str(e)}, 500

        items_for_store = []
        for row in ranked:
            t = row.get('task') or {}
            items_for_store.append({
                'task_id': t.get('id'),
                'score': row.get('score'),
                'reasons': row.get('reasons'),
            })

        try:
            persist_recommendation_snapshot(user_id, items_for_store)
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Failed to store recommendation snapshot', 'detail': str(e)}, 500

        return {
            'recommendations': ranked,
            'has_assessment_context': ctx is not None,
        }, 200


class TaskListView(MethodView):
    """GET /tasks — browse open tasks (optional filters)."""

    @jwt_required()
    @role_required('Student')
    def get(self):
        domain = request.args.get('domain') or None
        difficulty = request.args.get('difficulty') or None
        skip, limit, page = _parse_pagination()
        try:
            items, total = task_svc.list_open_tasks(
                domain=domain,
                difficulty=difficulty,
                skip=skip,
                limit=limit,
            )
        except Exception as e:
            return {'message': 'Failed to list tasks', 'detail': str(e)}, 500

        return {
            'tasks': items,
            'total': total,
            'page': page,
            'limit': limit,
        }, 200


class TaskDetailView(MethodView):
    """GET /tasks/<task_id>"""

    @jwt_required()
    @role_required('Student')
    def get(self, task_id):
        invalid = _validate_task_id(task_id)
        if invalid:
            return invalid[0], invalid[1]
        t = task_svc.get_task_by_id(task_id)
        if not t:
            return {'message': 'Task not found'}, 404
        return {'task': t}, 200


class ClaimTaskView(MethodView):
    """POST /tasks/<task_id>/claim — start task; stores recommendation snapshot on assignment."""

    @jwt_required()
    @role_required('Student')
    def post(self, task_id):
        invalid = _validate_task_id(task_id)
        if invalid:
            return invalid[0], invalid[1]
        user_id = get_jwt_identity()
        try:
            result = task_svc.claim_task(user_id, task_id)
        except ValueError as e:
            msg = str(e)
            code = 400
            if 'not found' in msg.lower():
                code = 404
            return {'message': msg}, code
        except Exception as e:
            return {'message': 'Failed to claim task', 'detail': str(e)}, 500

        return {'message': 'Task started', 'assignment': result}, 201


class MyAssignmentsView(MethodView):
    """GET /tasks/assignments/me — student's assignments."""

    @jwt_required()
    @role_required('Student')
    def get(self):
        user_id = get_jwt_identity()
        try:
            rows = task_svc.get_user_assignments(user_id)
        except Exception as e:
            return {'message': 'Failed to load assignments', 'detail': str(e)}, 500
        return {'assignments': rows}, 200


from flask import Blueprint

tasks_bp = Blueprint('tasks', __name__)

# Register specific paths before /<task_id> routes
tasks_bp.add_url_rule(
    '/recommended',
    view_func=RecommendedTasksView.as_view('recommended'),
    methods=['GET'],
)
tasks_bp.add_url_rule(
    '/assignments/me',
    view_func=MyAssignmentsView.as_view('my_assignments'),
    methods=['GET'],
)
tasks_bp.add_url_rule(
    '/',
    view_func=TaskListView.as_view('list'),
    methods=['GET'],
)
tasks_bp.add_url_rule(
    '/<task_id>/claim',
    view_func=ClaimTaskView.as_view('claim'),
    methods=['POST'],
)
tasks_bp.add_url_rule(
    '/<task_id>',
    view_func=TaskDetailView.as_view('detail'),
    methods=['GET'],
)
