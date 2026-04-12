"""
Design / creative task evaluator — automated validation only.

No AI aesthetic scoring. Valid files are accepted for mentor review (FR5).
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple

# Pillow optional for dimension checks; graceful fallback if missing
try:
    from PIL import Image
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False


def _normalize_ext(filename: str) -> str:
    if not filename:
        return ''
    return os.path.splitext(filename)[1].lower()


def _pdf_magic_ok(path: str) -> bool:
    try:
        with open(path, 'rb') as f:
            return f.read(5).startswith(b'%PDF')
    except OSError:
        return False


def _image_magic_ok(path: str, ext: str) -> bool:
    try:
        with open(path, 'rb') as f:
            head = f.read(16)
    except OSError:
        return False
    if ext == '.png':
        return head.startswith(b'\x89PNG\r\n\x1a\n')
    if ext in ('.jpg', '.jpeg'):
        return len(head) >= 3 and head[:3] == b'\xff\xd8\xff'
    return False


def _png_ihdr_size(path: str) -> Tuple[Optional[int], Optional[int]]:
    """Read width/height from PNG IHDR without Pillow (optional dependency)."""
    try:
        with open(path, 'rb') as f:
            if f.read(8) != b'\x89PNG\r\n\x1a\n':
                return None, None
            _length = int.from_bytes(f.read(4), 'big')
            if f.read(4) != b'IHDR':
                return None, None
            w = int.from_bytes(f.read(4), 'big')
            h = int.from_bytes(f.read(4), 'big')
            return w, h
    except OSError:
        return None, None


def _image_dimensions(path: str, ext: str) -> Tuple[Optional[int], Optional[int], Optional[str]]:
    if _HAS_PIL:
        try:
            with Image.open(path) as img:
                return img.width, img.height, None
        except Exception as e:
            return None, None, f'Could not read image dimensions: {e}'
    if ext == '.png':
        w, h = _png_ihdr_size(path)
        if w is not None and h is not None:
            return w, h, None
        return None, None, 'Could not read PNG dimensions (IHDR)'
    return None, None, 'Install pillow for JPEG dimension limits, or use PNG'


def evaluate_design_file(
    file_path: str,
    original_filename: str,
    task_config: Optional[Dict[str, Any]] = None,
    *,
    relative_path_for_details: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run automated checks on a design upload. Returns a structure aligned with
    writing/programming evaluators for frontend reuse.

    task_config keys (optional):
      - allowed_extensions: list of strings e.g. ['.png', '.jpg', '.jpeg', '.pdf']
      - max_file_mb: float
      - max_image_width / max_image_height / min_image_width / min_image_height: int
    """
    tc = task_config or {}
    allowed = tc.get('allowed_extensions') or ['.png', '.jpg', '.jpeg', '.pdf']
    allowed = [a.lower() if a.startswith('.') else f'.{a.lower()}' for a in allowed]
    max_mb = float(tc.get('max_file_mb') or tc.get('max_file_size_mb') or 16)

    checks: List[Dict[str, Any]] = []
    issues: List[str] = []
    ext = _normalize_ext(original_filename)

    # 1) File present
    present = bool(file_path and os.path.isfile(file_path))
    checks.append({
        'name': 'file_present',
        'passed': present,
        'detail': 'File exists on server' if present else 'File missing or not saved',
    })
    if not present:
        issues.append('Uploaded file was not found on the server.')

    size_bytes = 0
    if present:
        try:
            size_bytes = os.path.getsize(file_path)
        except OSError:
            size_bytes = 0

    max_bytes = int(max_mb * 1024 * 1024)
    size_ok = present and size_bytes > 0 and size_bytes <= max_bytes
    checks.append({
        'name': 'file_size',
        'passed': size_ok,
        'detail': f'{size_bytes} bytes (max {max_mb} MB)' if present else 'N/A',
    })
    if present and size_bytes > max_bytes:
        issues.append(f'File exceeds maximum size ({max_mb} MB).')
    if present and size_bytes == 0:
        issues.append('File is empty.')

    # 2) Extension / type
    ext_ok = ext in allowed
    checks.append({
        'name': 'file_extension',
        'passed': ext_ok,
        'detail': f'{ext or "(none)"} — allowed: {", ".join(allowed)}',
    })
    if present and not ext_ok:
        issues.append(f'Extension {ext or "missing"} is not allowed for this task.')

    # 3) Content sanity (PDF magic or image openable)
    content_ok = False
    content_detail = 'N/A'
    if present and ext_ok:
        if ext == '.pdf':
            content_ok = _pdf_magic_ok(file_path)
            content_detail = 'PDF header %PDF verified' if content_ok else 'File does not look like a valid PDF'
        elif ext in ('.png', '.jpg', '.jpeg'):
            w, h, dim_err = _image_dimensions(file_path, ext)
            if w is not None and h is not None:
                content_ok = True
                content_detail = f'Image readable ({w}×{h} px)'
            elif _image_magic_ok(file_path, ext):
                content_ok = True
                content_detail = 'Image header OK' + (
                    f' ({dim_err})' if dim_err else ''
                )
            else:
                content_ok = False
                content_detail = dim_err or 'File does not look like a valid PNG/JPEG'
        else:
            content_ok = True
            content_detail = 'Extension allowed; no extra content check'
    checks.append({
        'name': 'file_content',
        'passed': content_ok if (present and ext_ok) else False,
        'detail': content_detail,
    })
    if present and ext_ok and not content_ok:
        issues.append('File content does not match expected format (corrupt or wrong type).')

    # 4) Optional dimension bounds (images only)
    dim_ok = True
    dim_detail = 'N/A'
    if present and ext_ok and ext in ('.png', '.jpg', '.jpeg'):
        w, h, err = _image_dimensions(file_path, ext)
        max_w = tc.get('max_image_width')
        max_h = tc.get('max_image_height')
        min_w = tc.get('min_image_width')
        min_h = tc.get('min_image_height')
        has_limits = any(x is not None for x in (max_w, max_h, min_w, min_h))
        if not _HAS_PIL and has_limits and ext in ('.jpg', '.jpeg'):
            dim_ok = True
            dim_detail = 'JPEG dimension limits need Pillow (pip install pillow) or convert to PNG'
        elif w is not None and h is not None:
            if max_w is not None and w > int(max_w):
                dim_ok = False
                issues.append(f'Image width {w}px exceeds maximum {max_w}px.')
            if max_h is not None and h > int(max_h):
                dim_ok = False
                issues.append(f'Image height {h}px exceeds maximum {max_h}px.')
            if min_w is not None and w < int(min_w):
                dim_ok = False
                issues.append(f'Image width {w}px is below minimum {min_w}px.')
            if min_h is not None and h < int(min_h):
                dim_ok = False
                issues.append(f'Image height {h}px is below minimum {min_h}px.')
            dim_detail = f'{w}×{h} px'
            if has_limits:
                dim_detail += f' (limits: max {max_w}×{max_h}, min {min_w}×{min_h})'
        elif err:
            dim_detail = err
            dim_ok = False
    checks.append({
        'name': 'image_dimensions',
        'passed': dim_ok if ext in ('.png', '.jpg', '.jpeg') and present and ext_ok else True,
        'detail': dim_detail,
    })

    all_passed = all(c['passed'] for c in checks)
    validation_score = 100.0 if all_passed else 0.0

    # Mentor review: required when file is valid (passes checks) for qualitative grading.
    # If validation failed, mentor review is not the primary next step.
    mentor_required = bool(all_passed)
    mentor_reason = (
        'Automated checks passed. Design quality and brief alignment will be reviewed by your mentor (FR5).'
        if all_passed
        else 'Fix validation issues and resubmit. Mentor review applies after a valid upload.'
    )

    feedback = (
        'All automated checks passed. Your submission is queued for mentor review.'
        if all_passed
        else 'Some automated checks failed. Please fix the issues and resubmit.'
    )

    return {
        'overall_score': None,
        'score_breakdown': {
            'automated_validation': round(validation_score, 2),
        },
        'automated_checks_passed': all_passed,
        'automated_checks': checks,
        'validation_issues': issues,
        'mentor_review_required': mentor_required,
        'mentor_review_reason': mentor_reason,
        'feedback_summary': feedback,
        'strengths': ['File submitted successfully.'] if all_passed else [],
        'areas_for_improvement': issues if issues else (['None — awaiting mentor feedback.'] if all_passed else []),
        'details': {
            'original_filename': original_filename,
            'relative_path': relative_path_for_details or '',
            'size_bytes': size_bytes,
            'extension': ext,
            'task_limits': {
                'allowed_extensions': allowed,
                'max_file_mb': max_mb,
            },
        },
    }
