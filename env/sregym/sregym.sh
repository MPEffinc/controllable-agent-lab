#!/usr/bin/env bash
# SREGym 실행기: run.sh 의 격리 확인을 거친 뒤, 깨끗한 환경(env -i)으로 `uv run main.py <인자>` 를 실행한다.
# env -i 를 쓰는 이유: SREGym 은 호스트 환경의 공급자 키를 에이전트 컨테이너로 대량 전달한다
# (docs/reports/2026-10-21-precheck.md 4절 h). 필요한 변수만 명시해서 넘긴다.
# 캐시(~/cache_dir 대신)는 local/sregym-cache 로 돌린다.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
mkdir -p "$ROOT/local/sregym-cache"
exec "$ROOT/env/sregym/run.sh" bash -c '
  cd "$0/third_party/SREGym" &&
  exec env -i HOME="$HOME" PATH="$PATH" TERM=dumb KUBECONFIG="$KUBECONFIG" \
    SREGYM_CACHE_DIR="$0/local/sregym-cache" UV_CACHE_DIR="$0/local/uv-cache" \
    ${SREGYM_EXTRA_ENV:-} uv run main.py "$@"
' "$ROOT" "$@"
