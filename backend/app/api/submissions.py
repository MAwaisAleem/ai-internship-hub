"""Submissions and automated evaluation API (Student): writing, programming, design."""
from flask import request
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required

from bson import ObjectId
from bson.errors import InvalidId

from app.services import submission_service as sub_svc
from app.utils.decorators import role_required


def _validate_oid(value, label='id'):
    try:
        ObjectId(value)
    except Exception:
        return {'message': f'Invalid {label} format'}, 400
    return None


class WritingSubmissionView(MethodView):
    """POST /submissions/writing — body: assignment_id, text_content"""

    @jwt_required()
    @role_required('Student')
    def post(self):
        data = request.get_json() or {}
        assignment_id = (data.get('assignment_id') or '').strip()
        text_content = data.get('text_content')

        if not assignment_id:
            return {'message': 'assignment_id is required'}, 400
        err = _validate_oid(assignment_id, 'assignment_id')
        if err:
            return err

        if text_content is None:
            return {'message': 'text_content is required'}, 400
        if not isinstance(text_content, str):
            return {'message': 'text_content must be a string'}, 400

        user_id = get_jwt_identity()
        try:
            submission = sub_svc.create_writing_submission(user_id, assignment_id, text_content)
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Failed to create submission', 'detail': str(e)}, 500

        return {'message': 'Submission saved', 'submission': submission}, 201


class ProgrammingSubmissionView(MethodView):
    """POST /submissions/programming — body: assignment_id, code_content"""

    @jwt_required()
    @role_required('Student')
    def post(self):
        data = request.get_json() or {}
        assignment_id = (data.get('assignment_id') or '').strip()
        code_content = data.get('code_content')

        if not assignment_id:
            return {'message': 'assignment_id is required'}, 400
        err = _validate_oid(assignment_id, 'assignment_id')
        if err:
            return err

        if code_content is None:
            return {'message': 'code_content is required'}, 400
        if not isinstance(code_content, str):
            return {'message': 'code_content must be a string'}, 400

        user_id = get_jwt_identity()
        try:
            submission = sub_svc.create_programming_submission(user_id, assignment_id, code_content)
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Failed to create submission', 'detail': str(e)}, 500

        return {'message': 'Submission saved', 'submission': submission}, 201


class DesignSubmissionView(MethodView):
    """POST /submissions/design — multipart: assignment_id, file; optional student_notes"""

    @jwt_required()
    @role_required('Student')
    def post(self):
        assignment_id = (request.form.get('assignment_id') or '').strip()
        if not assignment_id:
            return {'message': 'assignment_id is required'}, 400
        err = _validate_oid(assignment_id, 'assignment_id')
        if err:
            return err

        f = request.files.get('file')
        if not f or not getattr(f, 'filename', None):
            return {'message': 'file is required (multipart field name: file)'}, 400

        notes = request.form.get('student_notes')
        if notes is not None and not isinstance(notes, str):
            return {'message': 'student_notes must be a string'}, 400

        user_id = get_jwt_identity()
        try:
            submission = sub_svc.create_design_submission(
                user_id,
                assignment_id,
                f,
                student_notes=notes,
            )
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Failed to create submission', 'detail': str(e)}, 500

        return {'message': 'Submission saved', 'submission': submission}, 201


class SubmissionDetailView(MethodView):
    """GET /submissions/<submission_id>"""

    @jwt_required()
    @role_required('Student')
    def get(self, submission_id):
        err = _validate_oid(submission_id, 'submission_id')
        if err:
            return err
        user_id = get_jwt_identity()
        sub = sub_svc.get_submission(submission_id, user_id)
        if not sub:
            return {'message': 'Submission not found'}, 404
        return {'submission': sub}, 200


class LatestSubmissionForAssignmentView(MethodView):
    """GET /submissions/assignment/<assignment_id>/latest"""

    @jwt_required()
    @role_required('Student')
    def get(self, assignment_id):
        err = _validate_oid(assignment_id, 'assignment_id')
        if err:
            return err
        user_id = get_jwt_identity()
        sub = sub_svc.get_latest_submission_for_assignment(assignment_id, user_id)
        if not sub:
            return {'message': 'No submission found for this assignment'}, 404
        return {'submission': sub}, 200


from flask import Blueprint

submissions_bp = Blueprint('submissions', __name__)

submissions_bp.add_url_rule(
    '/writing',
    view_func=WritingSubmissionView.as_view('writing'),
    methods=['POST'],
)
submissions_bp.add_url_rule(
    '/programming',
    view_func=ProgrammingSubmissionView.as_view('programming'),
    methods=['POST'],
)
submissions_bp.add_url_rule(
    '/design',
    view_func=DesignSubmissionView.as_view('design'),
    methods=['POST'],
)
submissions_bp.add_url_rule(
    '/assignment/<assignment_id>/latest',
    view_func=LatestSubmissionForAssignmentView.as_view('latest_for_assignment'),
    methods=['GET'],
)
submissions_bp.add_url_rule(
    '/<submission_id>',
    view_func=SubmissionDetailView.as_view('detail'),
    methods=['GET'],
)
