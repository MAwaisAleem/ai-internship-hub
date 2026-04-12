"""
Insert a sample Python programming task (sum two integers from stdin) + optional assignment.
Usage:
  python seed_programming_task.py
  Set STUDENT_EMAIL in .env for auto task_assignment.
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

TASK_DOC = {
    'title': 'Read two integers and print their sum',
    'description': 'Read two lines from stdin, each containing one integer. Print the sum.',
    'domain': 'Programming',
    'difficulty': 'beginner',
    'task_type': 'programming',
    'language': 'python',
    'status': 'open',
    'timeout_seconds': 5,
    'test_cases': [
        {
            'name': 'Small numbers',
            'stdin': '2\n3\n',
            'expected_stdout': '5',
        },
        {
            'name': 'Larger numbers',
            'stdin': '10\n20\n',
            'expected_stdout': '30',
        },
    ],
    'created_at': NOW,
    'updated_at': NOW,
    'created_by': None,
}


def main():
    tid = db.tasks.insert_one(TASK_DOC).inserted_id
    print(f'Inserted programming task _id: {tid}')

    email = os.getenv('STUDENT_EMAIL', '').strip()
    if not email:
        print('Set STUDENT_EMAIL in .env to auto-create task_assignment.')
        return

    user = db.users.find_one({'email': email.lower()})
    if not user:
        print(f'No user with email {email}')
        return

    uid = user['_id']
    adoc = {
        'user_id': uid,
        'task_id': tid,
        'status': 'in_progress',
        'claimed_at': NOW,
        'started_at': NOW,
        'completed_at': None,
        'recommendation_snapshot': None,
    }
    aid = db.task_assignments.insert_one(adoc).inserted_id
    print(f'Created task_assignment _id: {aid}')
    print('POST /api/submissions/programming with assignment_id and code_content')


if __name__ == '__main__':
    main()
