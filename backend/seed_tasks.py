"""Seed sample tasks for FR3 task allocation (run once after assessment seed)."""
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

sys.path.insert(0, str(_backend_dir))

MONGODB_URI = os.getenv('MONGODB_URI')
MONGODB_DB = os.getenv('MONGODB_DB')

if not MONGODB_URI or not MONGODB_DB:
    print('Error: MONGODB_URI and MONGODB_DB must be set in .env')
    sys.exit(1)

# Match connection style: Atlas needs TLS; local Docker often does not
if MONGODB_URI.startswith('mongodb+srv'):
    import certifi
    client = MongoClient(MONGODB_URI, tls=True, tlsCAFile=certifi.where())
else:
    client = MongoClient(MONGODB_URI)

db = client[MONGODB_DB]
tasks_coll = db['tasks']

NOW = datetime.now(timezone.utc)

SAMPLE_TASKS = [
    {
        'title': 'Design a social media banner set',
        'description': 'Create three banner sizes for a fictional coffee shop brand using consistent typography and color.',
        'domain': 'Graphic Design',
        'difficulty': 'beginner',
        'tags': ['design', 'branding'],
        'keywords': ['Graphic Design', 'visual', 'layout'],
        'status': 'open',
        'estimated_hours': 4,
        'created_at': NOW,
        'updated_at': NOW,
        'created_by': None,
    },
    {
        'title': 'Write a 800-word blog post on remote work',
        'description': 'Research and write an SEO-friendly article with headings and meta description.',
        'domain': 'Content Writing',
        'difficulty': 'intermediate',
        'tags': ['writing', 'seo'],
        'keywords': ['Content Writing', 'blog', 'SEO'],
        'status': 'open',
        'estimated_hours': 6,
        'created_at': NOW,
        'updated_at': NOW,
        'created_by': None,
    },
    {
        'title': 'Implement a REST API endpoint with validation',
        'description': 'Build a Flask endpoint with JSON validation and error handling for a user profile update.',
        'domain': 'Programming',
        'difficulty': 'intermediate',
        'tags': ['python', 'flask', 'api'],
        'keywords': ['Programming', 'Flask', 'API'],
        'status': 'open',
        'estimated_hours': 8,
        'created_at': NOW,
        'updated_at': NOW,
        'created_by': None,
    },
    {
        'title': 'Freelancing: client proposal template',
        'description': 'Draft a reusable proposal template covering scope, timeline, and pricing sections.',
        'domain': 'Freelancing',
        'difficulty': 'beginner',
        'tags': ['proposal', 'client'],
        'keywords': ['Freelancing', 'proposal', 'pricing'],
        'status': 'open',
        'estimated_hours': 3,
        'created_at': NOW,
        'updated_at': NOW,
        'created_by': None,
    },
    {
        'title': 'E-Commerce: product page checklist',
        'description': 'Create a checklist for optimizing a product page (images, trust signals, CTA).',
        'domain': 'E-Commerce',
        'difficulty': 'beginner',
        'tags': ['shopify', 'conversion'],
        'keywords': ['E-Commerce', 'product', 'conversion'],
        'status': 'open',
        'estimated_hours': 2,
        'created_at': NOW,
        'updated_at': NOW,
        'created_by': None,
    },
    {
        'title': 'QuickBooks: categorize sample transactions',
        'description': 'Given a list of transactions, assign categories and note any anomalies.',
        'domain': 'QuickBooks',
        'difficulty': 'intermediate',
        'tags': ['accounting', 'bookkeeping'],
        'keywords': ['QuickBooks', 'transactions', 'categories'],
        'status': 'open',
        'estimated_hours': 5,
        'created_at': NOW,
        'updated_at': NOW,
        'created_by': None,
    },
    {
        'title': 'AutoCAD: simple floor plan sketch',
        'description': 'Draw a basic two-room floor plan with dimensions and one door/window.',
        'domain': 'AutoCAD',
        'difficulty': 'advanced',
        'tags': ['cad', 'drafting'],
        'keywords': ['AutoCAD', 'floor plan', 'dimensions'],
        'status': 'open',
        'estimated_hours': 10,
        'created_at': NOW,
        'updated_at': NOW,
        'created_by': None,
    },
]


def ensure_indexes():
    tasks_coll.create_index([('status', 1), ('domain', 1)])
    tasks_coll.create_index([('created_at', -1)])
    db['task_assignments'].create_index([('user_id', 1), ('task_id', 1)], unique=True)
    db['task_assignments'].create_index([('user_id', 1), ('status', 1)])
    db['student_progress'].create_index('user_id', unique=True)


def main():
    ensure_indexes()
    existing = tasks_coll.count_documents({})
    if existing > 0:
        print(f'Tasks collection already has {existing} document(s). Skipping insert.')
        print('To re-seed, delete documents from "tasks" in MongoDB and run again.')
        return
    tasks_coll.insert_many(SAMPLE_TASKS)
    print(f'Inserted {len(SAMPLE_TASKS)} sample tasks.')
    print('Indexes ensured for tasks, task_assignments, student_progress.')


if __name__ == '__main__':
    main()
