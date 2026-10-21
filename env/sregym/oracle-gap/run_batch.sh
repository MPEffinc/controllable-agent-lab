#!/usr/bin/env bash
# P2 배치: PLAN.md 의 순서(문제별로 바퀴1 = 모든 변형, 바퀴2 = 모든 변형)대로 run_variant.py 를 실행한다.
# 이미 결과 JSON 이 있으면 건너뛴다. 실행 전 안전 한도(메모리 6GiB, 디스크 30GB, 노드 Ready)를 확인한다.
# 사용: env/sregym/oracle-gap/run_batch.sh <문제ID> <변형 목록(공백 구분)>
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
OUT="$ROOT/local/overnight/p2"; PROG="$ROOT/local/overnight/progress.md"
PROBLEM="$1"; shift; VARIANTS=("$@")
mkdir -p "$OUT"
log() { echo "$(date -Is) $*" >> "$PROG"; }

limits_ok() {
  local mem disk
  mem=$(free -g | awk '/^Mem:/{print $7}'); disk=$(df -BG --output=avail / | tail -1 | tr -dc 0-9)
  if [ "$mem" -lt 6 ] || [ "$disk" -lt 30 ]; then log "P2 한도 위반(가용메모리 ${mem}GiB, 디스크 ${disk}GB): 배치 중단"; return 1; fi
  return 0
}

nodes_ok() {
  local bad n
  bad=$("$ROOT/env/sregym/run.sh" kubectl get nodes --no-headers 2>/dev/null | awk '$2!="Ready"{print $1}')
  for n in $bad; do
    log "P2 노드 $n NotReady: kind 노드 내부 containerd 재시작 시도"
    docker exec "$n" systemctl restart containerd >/dev/null 2>&1; sleep 30
  done
  "$ROOT/env/sregym/run.sh" kubectl wait --for=condition=Ready nodes --all --timeout=120s >/dev/null 2>&1
}

for round in 1 2; do
  for v in "${VARIANTS[@]}"; do
    f="$OUT/${PROBLEM}__${v}__r${round}.json"
    [ -f "$f" ] && continue
    limits_ok || exit 3
    nodes_ok || { log "P2 노드가 Ready 가 아님: $PROBLEM $v r$round 건너뜀"; continue; }
    for attempt in 1 2; do
      log "P2 시작 $PROBLEM $v r$round (시도 $attempt)"
      timeout 1800 "$ROOT/env/sregym/sregym.sh" --py "$ROOT/env/sregym/oracle-gap/run_variant.py" \
        --problem "$PROBLEM" --variant "$v" --rep "$round" --outdir "$OUT" > "$OUT/log__${PROBLEM}__${v}__r${round}.txt" 2>&1
      rc=$?
      if [ -f "$f" ] && ! grep -q '"error"' "$f"; then
        log "P2 종료 $PROBLEM $v r$round: $(grep -a '^RESULT' "$OUT/log__${PROBLEM}__${v}__r${round}.txt" | tail -1)"; break
      fi
      log "P2 오류 $PROBLEM $v r$round rc=$rc (시도 $attempt): $(grep -a -m1 '"error"' "$f" 2>/dev/null | cut -c1-200)"
      mv -f "$f" "$OUT/failed__${PROBLEM}__${v}__r${round}__a${attempt}.json" 2>/dev/null
      sleep 20
    done
  done
done
log "P2 배치 종료: $PROBLEM"
