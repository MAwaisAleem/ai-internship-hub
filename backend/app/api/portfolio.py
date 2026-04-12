"""FR6: Student portfolio (read-only aggregate)."""
from flask import Blueprint
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services.portfolio_service import build_portfolio
from app.utils.decorators import role_required


class PortfolioMeView(MethodView):
    """GET /portfolio/me — portfolio for the authenticated student only."""

    @jwt_required()
    @role_required('Student')
    def get(self):
        user_id = get_jwt_identity()
        try:
            payload = build_portfolio(user_id)
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Failed to build portfolio', 'detail': str(e)}, 500
        return payload, 200


portfolio_bp = Blueprint('portfolio', __name__)
portfolio_bp.add_url_rule('/me', view_func=PortfolioMeView.as_view('portfolio_me'), methods=['GET'])
