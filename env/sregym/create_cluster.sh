#!/usr/bin/env bash
# kind 클러스터 `sregym-lab` 생성(SREGym 의 kind/setup_kind_cluster.sh 와 같은 단계, 다른 점만 아래).
#  - 클러스터 이름 sregym-lab, 전용 kubeconfig local/kubeconfig-sregym (기본 ~/.kube/config 는 건드리지 않음)
#  - 저장소 밖 ~/cache_dir 을 지우지 않는다(SREGym 캐시는 sregym.sh 가 local/sregym-cache 로 돌린다)
# 사용: env/sregym/create_cluster.sh        삭제: kind delete cluster --name sregym-lab --kubeconfig local/kubeconfig-sregym
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
KC="$ROOT/local/kubeconfig-sregym"; NAME=sregym-lab; CALICO=v3.29.3
if kind get clusters 2>/dev/null | grep -qx "$NAME"; then echo "이미 있음: $NAME" >&2; exit 1; fi
if [ -e "$KC" ]; then   # kind delete 뒤에 빈 파일이 남는다. 컨텍스트가 0개일 때만 재사용한다.
  [ "$(KUBECONFIG="$KC" kubectl config get-contexts -o name 2>/dev/null | wc -l)" -eq 0 ] \
    || { echo "kubeconfig 에 컨텍스트가 남아 있음: $KC" >&2; exit 1; }
  rm -f "$KC"
fi
echo "사전 상태: KUBECONFIG='${KUBECONFIG:-<미설정>}', 기본 컨텍스트 $(kubectl config get-contexts -o name 2>/dev/null | wc -l)개"
kind create cluster --name "$NAME" --config "$ROOT/third_party/SREGym/kind/kind-config.yaml" --kubeconfig "$KC"
for n in $(kind get nodes --name "$NAME"); do   # 호스트 DNS search 도메인 제거(SREGym 스크립트 1b 단계)
  docker exec "$n" sh -c 'awk "!/^search /" /etc/resolv.conf > /tmp/resolv.conf.sregym && cat /tmp/resolv.conf.sregym > /etc/resolv.conf'
done
for a in 1 2 3; do
  "$ROOT/env/sregym/run.sh" kubectl apply -f "https://raw.githubusercontent.com/projectcalico/calico/$CALICO/manifests/calico.yaml" && break
  [ "$a" = 3 ] && { echo "Calico 설치 실패" >&2; exit 1; }; sleep 5
done
"$ROOT/env/sregym/run.sh" kubectl rollout status daemonset/calico-node -n kube-system --timeout=300s
"$ROOT/env/sregym/run.sh" kubectl wait --for=condition=Ready nodes --all --timeout=180s
echo "완료: $NAME"
