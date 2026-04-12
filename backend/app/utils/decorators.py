"""Role-based access control decorators."""
from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.services.auth_service import get_user_by_id


def role_required(*allowed_roles):
    """Decorator to require specific role(s) for a route."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = get_user_by_id(user_id)
            if not user:
                return {'message': 'User not found'}, 404
            if user.get('role') not in allowed_roles:
                return {'message': 'Forbidden: insufficient permissions'}, 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
