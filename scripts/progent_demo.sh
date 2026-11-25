#!/usr/bin/env bash
# One terminal, one new run. Credentials stay in the environment, never argv.
set +x
set -euo pipefail
umask 077
PROGENT_DEMO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PROGENT_DEMO_PYTHON="$PROGENT_DEMO_ROOT/local/guided-reproduction-20261117/envs/progent-agentdojo/bin/python"
export PYTHONDONTWRITEBYTECODE=1
exec "$PROGENT_DEMO_PYTHON" -B "$PROGENT_DEMO_ROOT/scripts/progent_demo.py" "$@"
