#!/usr/bin/env bash
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILDER_HOME="${HOME}/NewbieProjectBuilder"
LOG_DIR="${BUILDER_HOME}/logs"
mkdir -p "$LOG_DIR"
BOOTSTRAP_LOG="${LOG_DIR}/bootstrap-linux-$(date +%Y%m%d-%H%M%S).log"

log() {
  printf '%s %s\n' "$(date --iso-8601=seconds 2>/dev/null || date)" "$*" | tee -a "$BOOTSTRAP_LOG"
}

printf '%s\n' '============================================================'
printf '%s\n' ' NEWBIE PROJECT BUILDER'
printf '%s\n' ' Safe setup for people with no computer experience'
printf '%s\n' '============================================================'
printf '\nNothing will be published or deleted without your permission.\n'
printf 'Bootstrap log: %s\n\n' "$BOOTSTRAP_LOG"
log "Launcher root: $ROOT"

PYTHON=""
if command -v python3 >/dev/null 2>&1; then
  if python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)'; then
    PYTHON="python3"
  fi
fi

if [[ -z "$PYTHON" ]]; then
  printf 'Python 3.11 or newer was not found.\n'
  distro_id=""
  if [[ -r /etc/os-release ]]; then
    distro_id="$(awk -F= '$1 == "ID" {value=$2; gsub(/[\"\047]/, "", value); print tolower(value); exit}' /etc/os-release)"
  fi
  case "$distro_id" in
    ubuntu|debian|kali) ;;
    *)
      log "ERROR NPB-001: Unsupported automatic install target: ${distro_id:-unknown}."
      printf 'ERROR NPB-001: Automatic installation supports Ubuntu, Debian, and Kali Linux.\n'
      printf 'Nothing was changed. Read docs/START_HERE_LINUX.md.\n'
      exit 1
      ;;
  esac
  if ! command -v apt-get >/dev/null 2>&1; then
    log 'ERROR NPB-011: APT is unavailable.'
    printf 'ERROR NPB-011: Automatic installation supports Ubuntu, Debian, and Kali Linux.\n'
    printf 'Nothing was changed. Read docs/START_HERE_LINUX.md.\n'
    exit 11
  fi
  read -r -p 'Install Python, Git, and required basics with APT? Type YES to continue: ' answer
  if [[ "$answer" != "YES" ]]; then
    log 'Package installation declined.'
    printf 'No software was installed.\n'
    exit 0
  fi
  log 'Running approved APT prerequisite installation.'
  if ! sudo apt-get update 2>&1 | tee -a "$BOOTSTRAP_LOG"; then
    log 'ERROR NPB-011: apt-get update failed.'
    exit 11
  fi
  if ! sudo apt-get install -y python3 python3-venv python3-pip git curl ca-certificates 2>&1 |
      tee -a "$BOOTSTRAP_LOG"; then
    log 'ERROR NPB-103: prerequisite installation failed.'
    exit 103
  fi
  PYTHON="python3"
fi

export PYTHONPATH="${ROOT}/src"
log "Starting shared Python builder with $PYTHON."
"$PYTHON" -m newbie_project_builder --home "$BUILDER_HOME" menu
exit_code=$?
log "Builder exit code: $exit_code"
if [[ $exit_code -ne 0 ]]; then
  printf 'The builder stopped safely. Review the message above and logs in %s.\n' "$LOG_DIR"
fi
exit "$exit_code"
