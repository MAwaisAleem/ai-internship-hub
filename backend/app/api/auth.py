"""Authentication API."""
from flask import request
from flask.views import MethodView
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
)

from app.services.auth_service import (
    create_user,
    authenticate_user,
    validate_password,
    get_user_by_id,
)


class RegisterView(MethodView):
    """User registration."""

    def post(self):
        data = request.get_json() or {}
        email = data.get('email', '').strip()
        password = data.get('password', '')
        role = data.get('role', 'Student')
        name = data.get('name', '').strip() or email.split('@')[0]

        if not email:
            return {'message': 'Email is required'}, 400
        if not password:
            return {'message': 'Password is required'}, 400

        valid, msg = validate_password(password)
        if not valid:
            return {'message': msg}, 400

        try:
            user = create_user(email, password, role, name)
            return {'message': 'Registration successful', 'user': user}, 201
        except ValueError as e:
            return {'message': str(e)}, 400


class LoginView(MethodView):
    """User login."""

    def post(self):
        data = request.get_json() or {}
        email = data.get('email', '').strip()
        password = data.get('password', '')

        if not email or not password:
            return {'message': 'Email and password are required'}, 400

        user = authenticate_user(email, password)
        if not user:
            return {'message': 'Invalid email or password'}, 401

        access_token = create_access_token(identity=user['id'])
        return {
            'access_token': access_token,
            'user': user,
        }, 200


class LogoutView(MethodView):
    """User logout (client should discard token)."""

    @jwt_required()
    def post(self):
        # JWT is stateless; client discards token. Optionally use a blocklist.
        return {'message': 'Logged out successfully'}, 200


class ProfileView(MethodView):
    """Get current user profile."""

    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        return {'user': user}, 200


# Blueprint setup
from flask import Blueprint

auth_bp = Blueprint('auth', __name__)
auth_bp.add_url_rule('/register', view_func=RegisterView.as_view('register'))
auth_bp.add_url_rule('/login', view_func=LoginView.as_view('login'))
auth_bp.add_url_rule('/logout', view_func=LogoutView.as_view('logout'))
auth_bp.add_url_rule('/profile', view_func=ProfileView.as_view('profile'))
