"""Authentication service."""
import bcrypt
from bson import ObjectId

from app.extensions import mongo

ROLES = ('Student', 'Mentor', 'Administrator')


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def validate_password(password: str):
    """
    Validate password strength.
    Returns (is_valid, error_message).
    """
    if len(password) < 8:
        return False, 'Password must be at least 8 characters'
    if not any(c.isupper() for c in password):
        return False, 'Password must contain at least one uppercase letter'
    if not any(c.islower() for c in password):
        return False, 'Password must contain at least one lowercase letter'
    if not any(c.isdigit() for c in password):
        return False, 'Password must contain at least one digit'
    return True, ''


def create_user(email: str, password: str, role: str, name: str) -> dict:
    """Create a new user. Raises ValueError if email exists or invalid role."""
    if role not in ROLES:
        raise ValueError(f'Invalid role. Must be one of: {", ".join(ROLES)}')

    users = mongo.db.users
    if users.find_one({'email': email.lower()}):
        raise ValueError('Email already registered')

    user = {
        'email': email.lower().strip(),
        'password_hash': hash_password(password),
        'role': role,
        'name': name.strip(),
    }
    result = users.insert_one(user)
    user['_id'] = result.inserted_id
    user.pop('password_hash', None)
    return {
        'id': str(user['_id']),
        'email': user['email'],
        'role': user['role'],
        'name': user['name'],
    }


def authenticate_user(email: str, password: str) -> dict | None:
    """Authenticate user by email and password. Returns user dict or None."""
    users = mongo.db.users
    user = users.find_one({'email': email.lower()})
    if not user or not check_password(password, user['password_hash']):
        return None
    return {
        'id': str(user['_id']),
        'email': user['email'],
        'role': user['role'],
        'name': user.get('name', ''),
    }


def get_user_by_id(user_id: str) -> dict | None:
    """Get user by ID (without password)."""
    try:
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    except Exception:
        return None
    if not user:
        return None
    user.pop('password_hash', None)
    user['id'] = str(user['_id'])
    return user
