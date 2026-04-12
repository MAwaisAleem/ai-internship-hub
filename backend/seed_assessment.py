"""Seed assessment questions for MCQ test."""
import os
import sys

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend directory or project root
_backend_dir = Path(__file__).resolve().parent
_project_root = _backend_dir.parent
for _path in (_backend_dir, _project_root):
    _env_file = _path / ".env"
    if _env_file.exists():
        load_dotenv(_env_file)
        break

from pymongo import MongoClient
import certifi

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB")

if not MONGODB_URI:
    print("Error: MONGODB_URI not set. Set it in .env or the environment.")
    sys.exit(1)
if not MONGODB_DB:
    print("Error: MONGODB_DB not set. Set it in .env or the environment.")
    sys.exit(1)

# Debug: print connection (mask password in output)
_debug_uri = MONGODB_URI
if "@" in _debug_uri and "://" in _debug_uri:
    _parts = _debug_uri.split("@", 1)
    _before = _parts[0]
    if "://" in _before:
        _scheme, _rest = _before.split("://", 1)
        if ":" in _rest:
            _user, _pass = _rest.rsplit(":", 1)
            _debug_uri = f"{_scheme}://{_user}:****@{_parts[1]}"
print(f"Using MONGODB_URI: {_debug_uri}")
print(f"Using MONGODB_DB: {MONGODB_DB}")

client = MongoClient(
    MONGODB_URI,
    tls=True,
    tlsCAFile=certifi.where()
)
db = client[MONGODB_DB]
coll = db['assessment_questions']

# Sample MCQ questions across DigiSkills domains
# Format: question, options (list), correct_answer (0-based index), domain
QUESTIONS = [
    # Graphic Design
    {
        'question': 'What does RGB stand for in graphic design?',
        'options': ['Red, Green, Blue', 'Real Good Bright', 'Royal Gradient Base', 'Resolution Graphics Buffer'],
        'correct_answer': 0,
        'domain': 'Graphic Design',
    },
    {
        'question': 'Which tool is primarily used for vector graphics?',
        'options': ['Photoshop', 'Illustrator', 'InDesign', 'Premiere'],
        'correct_answer': 1,
        'domain': 'Graphic Design',
    },
    {
        'question': 'What is the purpose of a mood board in design?',
        'options': ['To store passwords', 'To inspire and define visual direction', 'To calculate budgets', 'To track time'],
        'correct_answer': 1,
        'domain': 'Graphic Design',
    },
    # Content Writing
    {
        'question': 'What does SEO stand for?',
        'options': ['Search Engine Optimization', 'Simple Editing Option', 'System Entry Order', 'Structured Export Output'],
        'correct_answer': 0,
        'domain': 'Content Writing',
    },
    {
        'question': 'What is a call-to-action (CTA) in content writing?',
        'options': ['A phone number', 'A prompt that encourages the reader to take action', 'A footnote', 'A table of contents'],
        'correct_answer': 1,
        'domain': 'Content Writing',
    },
    {
        'question': 'Which writing style is best for blog posts?',
        'options': ['Formal and academic', 'Conversational and engaging', 'Legal jargon', 'Technical manual style'],
        'correct_answer': 1,
        'domain': 'Content Writing',
    },
    # Programming
    {
        'question': 'What is a variable in programming?',
        'options': ['A constant value', 'A named container for storing data', 'A type of loop', 'An error message'],
        'correct_answer': 1,
        'domain': 'Programming',
    },
    {
        'question': 'What does API stand for?',
        'options': ['Application Programming Interface', 'Advanced Program Integration', 'Automated Process Input', 'All Purpose Internet'],
        'correct_answer': 0,
        'domain': 'Programming',
    },
    {
        'question': 'Which is a version control system?',
        'options': ['Excel', 'Git', 'Word', 'PowerPoint'],
        'correct_answer': 1,
        'domain': 'Programming',
    },
    # Freelancing
    {
        'question': 'What is a key element of a strong freelance proposal?',
        'options': ['Generic templates', 'Personalized approach addressing client needs', 'Long paragraphs', 'No pricing information'],
        'correct_answer': 1,
        'domain': 'Freelancing',
    },
    {
        'question': 'What should you do when communicating with a difficult client?',
        'options': ['Ignore them', 'Stay professional, clarify expectations, document everything', 'Refund immediately', 'Block them'],
        'correct_answer': 1,
        'domain': 'Freelancing',
    },
    {
        'question': 'What is a milestone in freelance projects?',
        'options': ['A type of stone', 'A checkpoint or deliverable with a due date', 'A payment method', 'A communication tool'],
        'correct_answer': 1,
        'domain': 'Freelancing',
    },
    # E-Commerce
    {
        'question': 'What is an e-commerce platform?',
        'options': ['A physical store', 'Software that allows online buying and selling', 'A payment gateway only', 'A shipping company'],
        'correct_answer': 1,
        'domain': 'E-Commerce',
    },
    {
        'question': 'What does conversion rate mean in e-commerce?',
        'options': ['Currency exchange rate', 'Percentage of visitors who complete a desired action (e.g., purchase)', 'Shipping speed', 'Product return rate'],
        'correct_answer': 1,
        'domain': 'E-Commerce',
    },
    {
        'question': 'Which factor is crucial for building trust in online sales?',
        'options': ['Hiding contact info', 'Clear product descriptions, reviews, and secure payment', 'No refund policy', 'Limited images'],
        'correct_answer': 1,
        'domain': 'E-Commerce',
    },
    # QuickBooks
    {
        'question': 'What is QuickBooks primarily used for?',
        'options': ['Graphic design', 'Accounting and bookkeeping', 'Video editing', 'Web development'],
        'correct_answer': 1,
        'domain': 'QuickBooks',
    },
    {
        'question': 'What is an invoice?',
        'options': ['A receipt', 'A document requesting payment for goods or services', 'A tax form', 'A budget report'],
        'correct_answer': 1,
        'domain': 'QuickBooks',
    },
    {
        'question': 'What does accounts receivable mean?',
        'options': ['Money you owe', 'Money owed to you by customers', 'Bank balance', 'Tax liability'],
        'correct_answer': 1,
        'domain': 'QuickBooks',
    },
    # AutoCAD
    {
        'question': 'What is AutoCAD used for?',
        'options': ['Writing documents', '2D and 3D computer-aided design (CAD)', 'Managing emails', 'Creating spreadsheets'],
        'correct_answer': 1,
        'domain': 'AutoCAD',
    },
    {
        'question': 'What does CAD stand for?',
        'options': ['Computer-Aided Design', 'Central Application Database', 'Code Analysis Document', 'Creative Art Development'],
        'correct_answer': 0,
        'domain': 'AutoCAD',
    },
    {
        'question': 'What is a layer in CAD software?',
        'options': ['A physical sheet', 'A way to organize and control visibility of drawing elements', 'A color palette', 'A file format'],
        'correct_answer': 1,
        'domain': 'AutoCAD',
    },
]

def main():
    coll.delete_many({})
    coll.insert_many(QUESTIONS)
    print(f'Inserted {len(QUESTIONS)} assessment questions.')

if __name__ == '__main__':
    main()
