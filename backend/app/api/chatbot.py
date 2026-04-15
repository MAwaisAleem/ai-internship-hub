"""FR7: Student-focused career guidance chatbot API."""
from __future__ import annotations

from flask import Blueprint, request
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.services import chatbot_service as chatbot_svc
from app.utils.decorators import role_required


def _parse_limit(default: int = 30, cap: int = 100) -> int:
    try:
        n = int(request.args.get("limit", default))
        return max(1, min(cap, n))
    except (TypeError, ValueError):
        return default


class ChatbotMessageView(MethodView):
    """POST /chatbot/message — send one message and receive one response."""

    @jwt_required()
    @role_required("Student")
    def post(self):
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        message = data.get("message")
        session_id = data.get("session_id")
        try:
            result = chatbot_svc.respond_to_message(user_id, str(message or ""), session_id=session_id)
            return result, 200
        except ValueError as e:
            return {"message": str(e)}, 400
        except Exception as e:
            return {"message": "Failed to generate chatbot response", "detail": str(e)}, 500


class ChatbotHistoryView(MethodView):
    """GET /chatbot/history?session_id=...&limit=..."""

    @jwt_required()
    @role_required("Student")
    def get(self):
        user_id = get_jwt_identity()
        session_id = (request.args.get("session_id") or "").strip()
        if not session_id:
            return {"message": "session_id is required"}, 400
        limit = _parse_limit(default=30, cap=100)
        try:
            result = chatbot_svc.get_chat_history(user_id, session_id, limit=limit)
            return result, 200
        except ValueError as e:
            return {"message": str(e)}, 400
        except Exception as e:
            return {"message": "Failed to load chat history", "detail": str(e)}, 500


class ChatbotSuggestionsView(MethodView):
    """GET /chatbot/suggestions — starter prompts personalized by student context."""

    @jwt_required()
    @role_required("Student")
    def get(self):
        user_id = get_jwt_identity()
        try:
            result = chatbot_svc.get_quick_suggestions(user_id)
            return result, 200
        except ValueError as e:
            return {"message": str(e)}, 400
        except Exception as e:
            return {"message": "Failed to load chatbot suggestions", "detail": str(e)}, 500


chatbot_bp = Blueprint("chatbot", __name__)
chatbot_bp.add_url_rule("/message", view_func=ChatbotMessageView.as_view("message"), methods=["POST"])
chatbot_bp.add_url_rule("/history", view_func=ChatbotHistoryView.as_view("history"), methods=["GET"])
chatbot_bp.add_url_rule("/suggestions", view_func=ChatbotSuggestionsView.as_view("suggestions"), methods=["GET"])
