"""
Python programming evaluation: run student code against stdin/stdout test cases.
Uses subprocess + temp directory + per-test timeout — no network, no heavy sandbox.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from typing import Any


def _normalize_output(s: str) -> str:
    if s is None:
        return ''
    return s.replace('\r\n', '\n').strip()


def _run_python_file(workdir: str, code: str, stdin_text: str, timeout_sec: float) -> tuple[str, str, str | None]:
    """Write solution.py, run with stdin. Returns (stdout, stderr, error_message_or_none)."""
    path = os.path.join(workdir, 'solution.py')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)

    try:
        proc = subprocess.run(
            [sys.executable, 'solution.py'],
            input=(stdin_text or ''),
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            cwd=workdir,
            env={**os.environ, 'PYTHONUNBUFFERED': '1'},
        )
        out = proc.stdout or ''
        err = proc.stderr or ''
        if proc.returncode != 0:
            return out, err, f'Process exited with code {proc.returncode}'
        return out, err, None
    except subprocess.TimeoutExpired:
        return '', '', f'Execution exceeded {timeout_sec}s timeout'
    except Exception as e:
        return '', '', str(e)


def evaluate_python_code(code: str, task_config: dict[str, Any]) -> dict[str, Any]:
    """
    task_config:
      - test_cases: list of { "name": optional str, "stdin": str, "expected_stdout": str }
        (alias: expected_output for expected_stdout)
      - timeout_seconds: float (default 5)
    """
    code = (code or '').strip()
    if not code:
        return _empty_eval('No code submitted.')

    test_cases = task_config.get('test_cases') or []
    if not isinstance(test_cases, list):
        test_cases = []

    timeout_sec = float(task_config.get('timeout_seconds') or 5)
    timeout_sec = max(1.0, min(30.0, timeout_sec))

    if not test_cases:
        return _empty_eval('No test cases configured for this task.')

    test_results: list[dict[str, Any]] = []
    passed = 0
    failed = 0

    tmp_root = tempfile.mkdtemp(prefix='eval_py_')
    try:
        for i, tc in enumerate(test_cases):
            if not isinstance(tc, dict):
                failed += 1
                test_results.append({
                    'index': i,
                    'name': f'Test {i + 1}',
                    'passed': False,
                    'expected': '',
                    'actual': '',
                    'error': 'Invalid test case entry (must be an object)',
                })
                continue

            name = (tc.get('name') or f'Test {i + 1}').strip()
            stdin_text = tc.get('stdin')
            if stdin_text is None:
                stdin_text = ''
            if not isinstance(stdin_text, str):
                stdin_text = str(stdin_text)

            expected = tc.get('expected_stdout')
            if expected is None:
                expected = tc.get('expected_output')
            if expected is None:
                expected = ''
            if not isinstance(expected, str):
                expected = str(expected)

            subdir = os.path.join(tmp_root, f't{i}')
            os.makedirs(subdir, exist_ok=True)
            stdout, stderr, run_err = _run_python_file(subdir, code, stdin_text, timeout_sec)

            actual = _normalize_output(stdout)
            exp = _normalize_output(expected)
            ok = run_err is None and actual == exp

            if ok:
                passed += 1
            else:
                failed += 1

            entry: dict[str, Any] = {
                'index': i,
                'name': name,
                'passed': ok,
                'expected': exp,
                'actual': actual,
            }
            if stderr and stderr.strip():
                entry['stderr'] = stderr.strip()[:2000]
            if run_err:
                entry['error'] = run_err
            test_results.append(entry)
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

    total = passed + failed
    overall = round(100.0 * passed / total, 2) if total > 0 else 0.0
    breakdown = {'correctness': overall}

    strengths: list[str] = []
    improvements: list[str] = []
    if passed == total and total > 0:
        strengths.append(f'All {passed} test case(s) passed.')
    elif passed > 0:
        strengths.append(f'{passed} of {total} test case(s) passed.')
        improvements.append(f'{failed} test case(s) failed; compare expected vs actual output.')
    else:
        improvements.append('No tests passed; check logic, I/O format, and edge cases.')

    feedback = (
        f'Score {overall}/100. Passed {passed}/{total} tests.'
    )

    return {
        'overall_score': overall,
        'score_breakdown': breakdown,
        'passed_tests': passed,
        'failed_tests': failed,
        'test_results': test_results,
        'feedback_summary': feedback,
        'strengths': strengths if strengths else ['Your code was received and executed against the test suite.'],
        'areas_for_improvement': improvements if improvements else ['Review failing tests below.'],
        'details': {
            'language': 'python',
            'timeout_seconds': timeout_sec,
            'tests_configured': len(test_cases),
            'tests_run': len(test_results),
        },
    }


def _empty_eval(reason: str) -> dict[str, Any]:
    return {
        'overall_score': 0.0,
        'score_breakdown': {'correctness': 0.0},
        'passed_tests': 0,
        'failed_tests': 0,
        'test_results': [],
        'feedback_summary': reason,
        'strengths': [],
        'areas_for_improvement': [reason],
        'details': {'language': 'python', 'tests_run': 0},
    }
