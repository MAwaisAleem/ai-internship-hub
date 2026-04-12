"""
Link a Mentor user to a Student user in mentor_roster (FR5).

Usage:
  Set MENTOR_EMAIL and STUDENT_EMAIL in .env (or environment), then:
  python seed_mentor_roster.py

Idempotent: if the pair already exists, updates active=True.
"""
import os
import sys
from datetime import datetime, timezone

from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

_backend_dir = Path(__file__).resolve().parent
_project_root = _backend_dir.parent
for _path in (_backend_dir, _project_root):
    _env_file = _path / '.env'
    if _env_file.exists():
        load_dotenv(_env_file)
        break

MONGODB_URI = os.getenv('MONGODB_URI')
MONGODB_DB = os.getenv('MONGODB_DB')
MENTOR_EMAIL = os.getenv('MENTOR_EMAIL', '').strip()
STUDENT_EMAIL = os.getenv('STUDENT_EMAIL', '').strip()

if not MONGODB_URI or not MONGODB_DB:
    print('Error: MONGODB_URI and MONGODB_DB must be set')
    sys.exit(1)

if MONGODB_URI.startswith('mongodb+srv'):
    import certifi
    client = MongoClient(MONGODB_URI, tls=True, tlsCAFile=certifi.where())
else:
    client = MongoClient(MONGODB_URI)

db = client[MONGODB_DB]
NOW = datetime.now(timezone.utc)


def main():
    if not MENTOR_EMAIL or not STUDENT_EMAIL:
        print('Set MENTOR_EMAIL and STUDENT_EMAIL in .env')
        sys.exit(1)

    mentor = db.users.find_one({'email': MENTOR_EMAIL.lower()})
    if not mentor:
        print(f'No user with email {MENTOR_EMAIL}')
        sys.exit(1)
    if mentor.get('role') != 'Mentor':
        print(f'User {MENTOR_EMAIL} is not a Mentor (role={mentor.get("role")})')
        sys.exit(1)

    student = db.users.find_one({'email': STUDENT_EMAIL.lower()})
    if not student:
        print(f'No user with email {STUDENT_EMAIL}')
        sys.exit(1)
    if student.get('role') != 'Student':
        print(f'User {STUDENT_EMAIL} is not a Student')
        sys.exit(1)

    mid = mentor['_id']
    sid = student['_id']

    db.mentor_roster.create_index(
        [('mentor_id', 1), ('student_id', 1)],
        unique=True,
        name='mentor_student_unique',
    )

    existing = db.mentor_roster.find_one({'mentor_id': mid, 'student_id': sid})
    if existing:
        db.mentor_roster.update_one(
            {'_id': existing['_id']},
            {'$set': {'active': True, 'updated_at': NOW}},
        )
        print('Updated existing mentor_roster link (active=True).')
    else:
        db.mentor_roster.insert_one(
            {
                'mentor_id': mid,
                'student_id': sid,
                'active': True,
                'created_at': NOW,
                'updated_at': NOW,
            }
        )
        print('Inserted mentor_roster link.')

    print(f'Mentor: {MENTOR_EMAIL} ({mid})')
    print(f'Student: {STUDENT_EMAIL} ({sid})')


if __name__ == '__main__':
    main()
