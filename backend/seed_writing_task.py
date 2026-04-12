"""
Insert a sample writing task and optional task_assignment for a student user.
Usage:
  python seed_writing_task.py
  set STUDENT_EMAIL=you@example.com   (optional — links assignment to first matching user)
"""
import os
import sys
from datetime import datetime, timezone

from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

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
    'title': 'Sample writing task (blog intro)',
    'description': 'Write an introduction paragraph for a blog about remote work.',
    'domain': 'Content Writing',
    'difficulty': 'intermediate',
    'task_type': 'writing',
    'status': 'open',
    'min_words': 80,
    'max_words': 250,
    'keywords': ['remote', 'productivity', 'team', 'communication'],
    'reference_text': (
        'Remote work has reshaped how teams collaborate. Strong communication and clear '
        'expectations help distributed teams stay productive and engaged.'
    ),
    'created_at': NOW,
    'updated_at': NOW,
    'created_by': None,
}


def main():
    db.submissions.create_index([('user_id', 1), ('assignment_id', 1)])
    db.submissions.create_index([('task_id', 1)])

    tid = db.tasks.insert_one(TASK_DOC).inserted_id
    print(f'Inserted writing task _id: {tid}')

    email = os.getenv('STUDENT_EMAIL', '').strip()
    if not email:
        print('Set STUDENT_EMAIL in .env to auto-create a task_assignment for testing.')
        print('Or insert task_assignments manually with task_id above and your user _id.')
        return

    user = db.users.find_one({'email': email.lower()})
    if not user:
        print(f'No user with email {email}; skip assignment.')
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
    print('Use assignment_id in POST /api/submissions/writing')


if __name__ == '__main__':
    main()
