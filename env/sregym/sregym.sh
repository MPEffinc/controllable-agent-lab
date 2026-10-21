#!/usr/bin/env bash
# SREGym 실행기: run.sh 의 격리 확인을 거친 뒤, 깨끗한 환경(env -i)으로 SREGym 가상환경에서 실행한다.
#   env/sregym/sregym.sh <main.py 인자...>            -> uv run main.py <인자>
#   env/sregym/sregym.sh --py <스크립트> [인자...]     -> uv run python <스크립트> [인자]  (PYTHONPATH=SREGym 루트)
# env -i 를 쓰는 이유: SREGym 은 호스트 환경의 공급자 키를 에이전트 컨테이너로 대량 전달한다
# (docs/reports/2026-10-21-precheck.md 4절 h). 필요한 변수만 명시해서 넘긴다.
# 캐시(~/cache_dir 대신)는 local/sregym-cache 로 돌린다. 추가 환경 변수는 SREGYM_EXTRA_ENV="A=1 B=2" 로 넘긴다.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
mkdir -p "$ROOT/local/sregym-cache"
exec "$ROOT/env/sregym/run.sh" bash -c '
  root="$1"; shift
  cd "$root/third_party/SREGym" || exit 1
  if [ "${1:-}" = "--py" ]; then
    shift
    exec env -i HOME="$HOME" PATH="$PATH" TERM=dumb KUBECONFIG="$KUBECONFIG" PYTHONPATH="$PWD" \
      SREGYM_CACHE_DIR="$root/local/sregym-cache" UV_CACHE_DIR="$root/local/uv-cache" \
      ${SREGYM_EXTRA_ENV:-} uv run python "$@"
  fi
  exec env -i HOME="$HOME" PATH="$PATH" TERM=dumb KUBECONFIG="$KUBECONFIG" \
    SREGYM_CACHE_DIR="$root/local/sregym-cache" UV_CACHE_DIR="$root/local/uv-cache" \
    ${SREGYM_EXTRA_ENV:-} uv run main.py "$@"
' _ "$ROOT" "$@"
