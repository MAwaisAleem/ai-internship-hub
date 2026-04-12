"""
Backfill missing or invalid task_type on documents in the tasks collection.

Valid task_type values: writing | programming | design (matches FR4 frontend + backend).

Usage:
  python migrate_task_types.py           # apply updates
  python migrate_task_types.py --dry-run # print planned changes only

Requires MONGODB_URI and MONGODB_DB (same as other seed scripts). Idempotent: safe to re-run;
tasks that already have a valid task_type are skipped.
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient

VALID_TYPES = frozenset({'writing', 'programming', 'design'})

_backend_dir = Path(__file__).resolve().parent
_project_root = _backend_dir.parent
for _path in (_backend_dir, _project_root):
    _env_file = _path / '.env'
    if _env_file.exists():
        load_dotenv(_env_file)
        break

MONGODB_URI = os.getenv('MONGODB_URI')
MONGODB_DB = os.getenv('MONGODB_DB')


def _connect():
    if not MONGODB_URI or not MONGODB_DB:
        print('Error: MONGODB_URI and MONGODB_DB must be set', file=sys.stderr)
        sys.exit(1)
    if MONGODB_URI.startswith('mongodb+srv'):
        import certifi
        return MongoClient(MONGODB_URI, tls=True, tlsCAFile=certifi.where())
    return MongoClient(MONGODB_URI)


def _existing_type(doc: dict) -> str | None:
    raw = (doc.get('task_type') or doc.get('type') or '').strip().lower()
    if raw in VALID_TYPES:
        return raw
    return None


def infer_task_type(doc: dict) -> tuple[str, str]:
    """
    Return (task_type, reason_short) using domain, title, and description heuristics.
    """
    domain = (doc.get('domain') or '').strip().lower()
    title = (doc.get('title') or '').strip().lower()
    desc = (doc.get('description') or '').strip().lower()
    blob = f'{domain} {title} {desc}'

    # -------------------------------------------------------------------------
    # Priority buckets (run before scored heuristics so domain/title mismatches
    # are fixed: e.g. Graphic Design domain + QuickBooks title -> writing;
    # Content Writing domain + AutoCAD floor plan -> design.)
    # -------------------------------------------------------------------------

    # Accounting / bookkeeping / finance-style practical tasks -> writing (3-type model)
    _accounting_finance = (
        'quickbooks',
        'quick book',
        'xero',
        'sage',
        'bookkeeping',
        'bookkeeper',
        'accounting',
        'transaction',
        'transactions',
        'invoice',
        'invoices',
        'payroll',
        'ledger',
        'reconcile',
        'reconciliation',
        'finance',
        'financial',
        'expense',
        'expenses',
        'tax prep',
        'tax preparation',
        'general ledger',
        'accounts payable',
        'accounts receivable',
        'journal entry',
        'journal entries',
        'categorize',
        'categorise',
        'bank feed',
        'bank reconciliation',
        'double-entry',
        'double entry',
        'balance sheet',
        'profit and loss',
        'p&l',
        'pl statement',
    )
    if any(p in blob for p in _accounting_finance):
        return 'writing', 'bucket_accounting_finance'

    # CAD / drafting / architectural drawing -> design (includes AutoCAD, floor plans, blueprints)
    _cad_drafting = (
        'autocad',
        'auto cad',
        'cad ',
        ' cad',
        'floor plan',
        'floorplan',
        'drafting',
        'draftsman',
        'blueprint',
        'blueprints',
        'technical drawing',
        'civil 3d',
        'revit',
        'sketchup',
        'sketch-up',
        'solidworks',
        'architectural drawing',
        'site plan',
        'elevation',
        'dwg',
        'bim',
    )
    if any(p in blob for p in _cad_drafting):
        return 'design', 'bucket_cad_drafting'
    # "sketch" only when clearly drafting / spatial (avoids stealing pure writing briefs)
    if 'sketch' in blob and any(
        x in blob
        for x in (
            'floor',
            'plan',
            'cad',
            'autocad',
            'draft',
            'blueprint',
            'architect',
            'engineering',
            'site ',
            'elevation',
            'drawing',
        )
    ):
        return 'design', 'bucket_cad_sketch_context'

    scores = {'design': 0, 'writing': 0, 'programming': 0}

    # --- Strong domain signals (DigiSkills / internship style) ---
    if any(
        x in domain
        for x in (
            'graphic design',
            'graphic',
            'ui/ux',
            'ux design',
            'visual design',
            'creative design',
        )
    ):
        scores['design'] += 12
    if any(x in domain for x in ('content writing', 'copywriting', 'technical writing')) or domain in (
        'writing',
        'blogging',
    ):
        scores['writing'] += 12
    if any(
        x in domain
        for x in (
            'programming',
            'software development',
            'web development',
            'development',
        )
    ):
        scores['programming'] += 12

    # Broad domain hints
    if 'design' in domain and 'writing' not in domain and 'content writing' not in domain:
        scores['design'] += 4
    if any(x in domain for x in ('content', 'writing', 'marketing')) and 'programming' not in domain:
        scores['writing'] += 3
    if any(x in domain for x in ('programming', 'coding', 'software')):
        scores['programming'] += 4

    # --- Keyword signals (title + description + domain blob) ---
    design_kw = [
        'graphic',
        'banner',
        'logo',
        'wireframe',
        'mockup',
        'figma',
        'branding',
        'poster',
        'illustration',
        'photoshop',
        'canva',
        'typography',
        'creative brief',
        'visual',
        'ui ',
        ' ux',
        'color palette',
        'layout design',
    ]
    writing_kw = [
        'blog',
        'article',
        'proposal',
        'checklist',
        'essay',
        'paragraph',
        'newsletter',
        'seo',
        'proofread',
        'copy',
        'product page',
        'press release',
        'white paper',
        'documentation',  # user-facing docs; may overlap — tempered by scores
        'content strategy',
        'landing page copy',
    ]
    programming_kw = [
        'python',
        'javascript',
        'java ',
        'typescript',
        'code',
        'coding',
        'program',
        'bug fix',
        'script',
        'algorithm',
        'api',
        'backend',
        'frontend',
        'debug',
        'git',
        'sql',
        'react',
        'node.js',
        'stdin',
        'stdout',
        'test case',
        'refactor',
        'subprocess',
        'repository',
        'pull request',
    ]

    for kw in design_kw:
        if kw in blob:
            scores['design'] += 2
    for kw in writing_kw:
        if kw in blob:
            scores['writing'] += 2
    for kw in programming_kw:
        if kw in blob:
            scores['programming'] += 2

    best = max(scores, key=lambda k: scores[k])
    max_score = scores[best]

    if max_score == 0:
        # Last-resort inference from domain words
        if any(x in domain for x in ('design', 'creative', 'visual', 'ui', 'ux')):
            return 'design', 'fallback_domain_creative'
        if any(x in domain for x in ('writing', 'content', 'blog', 'copy')):
            return 'writing', 'fallback_domain_writing'
        if any(x in domain for x in ('program', 'dev', 'software', 'code')):
            return 'programming', 'fallback_domain_dev'
        # Default: writing (most generic internship task style)
        return 'writing', 'fallback_default_writing'

    return best, f'scores={scores}'


def main() -> None:
    parser = argparse.ArgumentParser(description='Backfill task_type on tasks collection')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Print planned updates without writing to MongoDB',
    )
    args = parser.parse_args()

    client = _connect()
    db = client[MONGODB_DB]
    coll = db.tasks

    cursor = coll.find({})
    total = coll.count_documents({})
    skipped_ok = 0
    planned: list[tuple[ObjectId, str | None, str, str, str]] = []

    for doc in cursor:
        oid = doc['_id']
        current = _existing_type(doc)
        raw = (doc.get('task_type') or doc.get('type') or '')
        if current:
            skipped_ok += 1
            continue

        inferred, reason = infer_task_type(doc)
        planned.append((oid, raw or None, inferred, reason, doc.get('title', '')[:60]))

    print(f'Tasks in database: {total}')
    print(f'Already valid task_type: {skipped_ok}')
    print(f'Need update: {len(planned)}')
    print()

    if not planned:
        print('Nothing to do.')
        return

    now = datetime.now(timezone.utc)
    for oid, old_raw, new_type, reason, title_preview in planned:
        print(f'  _id={oid}')
        print(f'    title: {title_preview!r}...')
        print(f'    old task_type/type: {old_raw!r}')
        print(f'    -> task_type: {new_type!r} ({reason})')

    if args.dry_run:
        print('\nDry run: no writes performed.')
        return

    updated = 0
    for oid, _old_raw, new_type, _reason, _tp in planned:
        result = coll.update_one(
            {'_id': oid},
            {'$set': {'task_type': new_type, 'updated_at': now}},
        )
        if result.modified_count:
            updated += 1

    print(f'\nUpdated {updated} document(s).')
    print('Re-run this script anytime; valid tasks are skipped.')


if __name__ == '__main__':
    main()
