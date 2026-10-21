#!/usr/bin/env bash
# run.sh 자체 시험: 가짜 kubeconfig(서버에 접속하지 않음)로 정상은 통과, 비정상은 거부되는지 확인한다.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUN="$ROOT/env/sregym/run.sh"
T="$(mktemp -d "${TMPDIR:-/tmp}/runsh-test.XXXXXX")"
trap 'rm -rf "$T"' EXIT
pass=0; fail=0

# mk <파일> <컨텍스트이름> <서버URL> [current 설정 여부: set|unset]
mk() {
  local f="$1" ctx="$2" url="$3" cur="${4:-set}"
  KUBECONFIG="$f" kubectl config set-cluster "c-$ctx" --server="$url" >/dev/null
  KUBECONFIG="$f" kubectl config set-credentials "u-$ctx" --token=fake >/dev/null
  KUBECONFIG="$f" kubectl config set-context "$ctx" --cluster="c-$ctx" --user="u-$ctx" >/dev/null
  [ "$cur" = set ] && KUBECONFIG="$f" kubectl config use-context "$ctx" >/dev/null
  return 0
}

# expect <기대: ok|reject> <이름> <kubeconfig 경로>
expect() {
  local want="$1" name="$2" kc="$3" out rc
  out="$(SREGYM_LAB_KUBECONFIG="$kc" "$RUN" echo RAN 2>&1)"; rc=$?
  if [ "$want" = ok ] && [ $rc -eq 0 ] && echo "$out" | grep -q '^RAN$'; then
    echo "PASS  [$name] 통과(기대대로)"; pass=$((pass+1))
  elif [ "$want" = reject ] && [ $rc -ne 0 ] && ! echo "$out" | grep -q '^RAN$'; then
    echo "PASS  [$name] 거부(기대대로, rc=$rc)"; pass=$((pass+1))
  else
    echo "FAIL  [$name] 기대=$want rc=$rc 출력=$out"; fail=$((fail+1))
  fi
}

mk "$T/good" kind-sregym-lab https://127.0.0.1:41234
expect ok     "정상: 컨텍스트 1개, 이름 일치, 루프백" "$T/good"

mk "$T/two" kind-sregym-lab https://127.0.0.1:41234
mk "$T/two" other-cluster https://127.0.0.1:5555
expect reject "컨텍스트 2개(다른 컨텍스트 혼입)" "$T/two"

mk "$T/wrongname" kind-kind https://127.0.0.1:41234
expect reject "컨텍스트 1개지만 이름이 다름(kind-kind)" "$T/wrongname"

mk "$T/nocur" kind-sregym-lab https://127.0.0.1:41234 unset
expect reject "current-context 미설정" "$T/nocur"

mk "$T/remote" kind-sregym-lab https://10.20.30.40:6443
expect reject "이름은 맞지만 서버가 원격 주소" "$T/remote"

expect reject "kubeconfig 파일 없음" "$T/does-not-exist"

: > "$T/empty"
expect reject "빈 kubeconfig(컨텍스트 0개)" "$T/empty"

# 인자 없이 호출
if "$RUN" >/dev/null 2>&1; then echo "FAIL  [인자 없음] 거부되지 않음"; fail=$((fail+1)); else echo "PASS  [인자 없음] 거부(기대대로)"; pass=$((pass+1)); fi

echo "결과: 통과 $pass, 실패 $fail"
[ "$fail" -eq 0 ]
