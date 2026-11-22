#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"
PYTHON=local/guided-reproduction-20261117/envs/progent-agentdojo/bin/python
export PYTHONPATH=.
case "${1:-}" in
  manual) exec "$PYTHON" -m scripts.progent_vm_manual ;;
  live) shift; exec "$PYTHON" -m scripts.progent_vm_live "$@" ;;
  system-live) shift; exec "$PYTHON" -m scripts.progent_system_live "$@" ;;
  agentdojo) shift; exec "$PYTHON" -m scripts.progent_agentdojo_evaluation "$@" ;;
  *) printf 'Usage: bash scripts/progent_vm.sh manual | live [options] | system-live --backend mock|docker --case A|B|C|D|E [options] | agentdojo --backend mock|docker --case A|B|C|D [--offline-ground-truth]\n' >&2; exit 2 ;;
esac
