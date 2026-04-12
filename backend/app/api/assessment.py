"""Assessment API."""
from flask import request
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.assessment_service import (
    get_questions,
    submit_assessment,
    get_latest_result,
)
from app.utils.decorators import role_required


class QuestionsView(MethodView):
    """Get assessment questions (Student only)."""

    @jwt_required()
    @role_required('Student')
    def get(self):
        questions = get_questions()
        return {'questions': questions}, 200


class SubmitView(MethodView):
    """Submit assessment answers (Student only)."""

    @jwt_required()
    @role_required('Student')
    def post(self):
        data = request.get_json() or {}
        answers = data.get('answers', [])
        if not isinstance(answers, list):
            return {'message': 'answers must be an array'}, 400

        user_id = get_jwt_identity()
        try:
            result = submit_assessment(user_id, answers)
            return {'message': 'Assessment submitted', 'result': result}, 200
        except Exception as e:
            return {'message': str(e)}, 500


class ResultView(MethodView):
    """Get latest assessment result (Student only)."""

    @jwt_required()
    @role_required('Student')
    def get(self):
        user_id = get_jwt_identity()
        result = get_latest_result(user_id)
        if not result:
            return {'message': 'No assessment result found'}, 404
        return {'result': result}, 200


from flask import Blueprint

assessment_bp = Blueprint('assessment', __name__)
assessment_bp.add_url_rule('/questions', view_func=QuestionsView.as_view('questions'))
assessment_bp.add_url_rule('/submit', view_func=SubmitView.as_view('submit'))
assessment_bp.add_url_rule('/result', view_func=ResultView.as_view('result'))
