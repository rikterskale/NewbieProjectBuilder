#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${root}/src"
python3 -m newbie_project_builder --home "${HOME}/NewbieProjectBuilder" diagnose
