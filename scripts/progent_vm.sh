#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"
PYTHON=local/guided-reproduction-20261117/envs/progent-agentdojo/bin/python
export PYTHONPATH=.
case "${1:-}" in
  manual) exec "$PYTHON" -m scripts.progent_vm_manual ;;
  check-env) shift; exec "$PYTHON" -m scripts.progent_api_env_check "$@" ;;
  budget) shift; exec "$PYTHON" -m scripts.progent_budget_status "$@" ;;
  live) shift; exec "$PYTHON" -m scripts.progent_vm_live "$@" ;;
  system-live) shift; exec "$PYTHON" -m scripts.progent_system_live "$@" ;;
  agentdojo) shift; exec "$PYTHON" -m scripts.progent_agentdojo_evaluation "$@" ;;
  docker) shift; exec "$PYTHON" -m scripts.progent_docker_experiment --runtime runc "$@" ;;
  kata) shift; exec "$PYTHON" -m scripts.progent_docker_experiment --runtime kata "$@" ;;
  view-run) shift; exec "$PYTHON" -m scripts.progent_log_view "$@" ;;
  show-bc) shift; exec "$PYTHON" -m scripts.progent_bc_evidence "$@" ;;
  *) printf 'Usage: bash scripts/progent_vm.sh check-env [--env-file PATH] | budget | view-run RUN_ID [--section source|trace] [--color auto|always|never] | show-bc [--case B|C|both] [--verbose] | manual | live [options] | docker | kata | system-live --backend mock|docker|kata --case A|B|C|D|E [options] | agentdojo --backend mock|docker|kata --case A|B|C|D [--offline-ground-truth]\n' >&2; exit 2 ;;
esac
