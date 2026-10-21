#!/usr/bin/env bash
# SREGym 관련 모든 kubectl·SREGym 명령의 격리 래퍼.
#
# 사용: env/sregym/run.sh <명령> [인자...]
#   예: env/sregym/run.sh kubectl get nodes
#       env/sregym/run.sh bash -c 'cd third_party/SREGym && uv run main.py ...'
#
# 이유: SREGym 은 현재 kube-context 를 검증하지 않고, 문제 정리 때 베이스라인에 없는 클러스터 자원을
#       삭제한다(docs/reports/2026-10-21-precheck.md 4절 j-C). 그래서 실행 전에 아래를 모두 확인하고
#       하나라도 어긋나면 명령을 실행하지 않고 오류로 끝낸다.
#   1. KUBECONFIG 파일이 있다 (기본 local/kubeconfig-sregym)
#   2. 그 파일의 컨텍스트가 정확히 1개이고 이름이 kind-sregym-lab 이다
#   3. current-context 가 kind-sregym-lab 이다
#   4. 그 컨텍스트의 API 서버 주소가 루프백(127.0.0.1, localhost, [::1])이다 (원격 클러스터가 아님)
# 시험용으로만 SREGYM_LAB_KUBECONFIG 로 파일을 바꿀 수 있고, 검사는 그 파일에도 똑같이 적용된다.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXPECTED_CONTEXT="kind-sregym-lab"
KC="${SREGYM_LAB_KUBECONFIG:-$ROOT/local/kubeconfig-sregym}"

die() { echo "[run.sh 거부] $*" >&2; exit 78; }

[ "$#" -ge 1 ] || die "실행할 명령이 없다"
[ -f "$KC" ] || die "kubeconfig 파일이 없다: $KC"

# 다른 경로의 kubeconfig·컨텍스트가 섞이지 않게 환경을 고정한다.
export KUBECONFIG="$KC"
unset KUBECTL_CONTEXT KUBERNETES_MASTER HELM_KUBECONTEXT HELM_KUBECONFIG || true

contexts="$(kubectl config get-contexts -o name 2>/dev/null || true)"
count="$(printf '%s\n' "$contexts" | sed '/^$/d' | wc -l)"
[ "$count" -eq 1 ] || die "컨텍스트가 정확히 1개여야 한다(현재 ${count}개)"
[ "$contexts" = "$EXPECTED_CONTEXT" ] || die "컨텍스트 이름이 $EXPECTED_CONTEXT 가 아니다"

current="$(kubectl config current-context 2>/dev/null || true)"
[ "$current" = "$EXPECTED_CONTEXT" ] || die "current-context 가 $EXPECTED_CONTEXT 가 아니다(현재 '${current:-<없음>}')"

server="$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}' 2>/dev/null || true)"
case "$server" in
  https://127.0.0.1:*|https://localhost:*|https://\[::1\]:*) ;;
  *) die "API 서버 주소가 루프백이 아니다" ;;
esac

echo "[run.sh] KUBECONFIG=$KC context=$current (1개) 확인됨" >&2
exec "$@"
