#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

python_bin="${PYTHON:-python3}"

printf '%s\n' '[1/7] Compiling Python files...'
"$python_bin" -m compileall -q src
printf '%s\n' '[2/7] Running Ruff...'
"$python_bin" -m ruff check .
printf '%s\n' '[3/7] Running mypy...'
"$python_bin" -m mypy src
printf '%s\n' '[4/7] Running tests and coverage...'
"$python_bin" -m pytest
printf '%s\n' '[5/7] Running Bandit...'
"$python_bin" -m bandit -r src -ll
printf '%s\n' '[6/7] Auditing dependencies...'
"$python_bin" -m pip_audit
printf '%s\n' '[7/7] Building packages...'
"$python_bin" -m build
printf '%s\n' 'All required checks passed.'
