#!/usr/bin/env bash
# P3/P4 배치: 문제 × 반복으로 run_agent_trial.py 를 실행한다. 이미 결과가 있으면 건너뛴다.
# 사용: run_agent_batch.sh <outdir> <agent: dummy|single|split> <반복 수> <문제ID...>
# 실행 전 안전 한도(메모리 6GiB, 디스크 30GB, 노드 Ready, 밤 비용 상한)를 확인한다. 같은 오류는 1회만 재시도한다.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
PROG="$ROOT/local/overnight/progress.md"
OUT="$1"; AGENT="$2"; REPS="$3"; shift 3
mkdir -p "$OUT"
log() { echo "$(date -Is) $*" >> "$PROG"; }
spent() { python3 -c "
import json,os
f='$ROOT/local/overnight/usage.jsonl'
print(sum(json.loads(l).get('usd',0) for l in open(f)) if os.path.exists(f) else 0)"; }

for rep in $(seq 1 "$REPS"); do
  for prob in "$@"; do
    f="$OUT/p3-${prob}-${AGENT}-r${rep}__trial.json"
    [ -f "$f" ] && continue
    mem=$(free -g | awk '/^Mem:/{print $7}'); disk=$(df -BG --output=avail / | tail -1 | tr -dc 0-9)
    if [ "$mem" -lt 6 ] || [ "$disk" -lt 30 ]; then log "에이전트 배치 한도 위반(메모리 ${mem}GiB, 디스크 ${disk}GB): 중단"; exit 3; fi
    if python3 -c "import sys; sys.exit(0 if float('$(spent)')>=3.0 else 1)"; then log "에이전트 배치: 밤 비용 상한 도달, 중단"; exit 4; fi
    for n in $("$ROOT/env/sregym/run.sh" kubectl get nodes --no-headers 2>/dev/null | awk '$2!="Ready"{print $1}'); do
      log "노드 $n NotReady: kind 노드 내부 containerd 재시작"; docker exec "$n" systemctl restart containerd >/dev/null 2>&1; sleep 30; done
    for attempt in 1 2; do
      log "에이전트 시작 $prob $AGENT r$rep (시도 $attempt)"
      timeout 2400 "$ROOT/env/sregym/sregym.sh" --py "$ROOT/env/sregym/agent/run_agent_trial.py" \
        --problem "$prob" --agent "$AGENT" --rep "$rep" --outdir "$OUT" > "$OUT/log__${prob}__${AGENT}__r${rep}.txt" 2>&1
      if [ -f "$f" ] && ! grep -q '"error"' "$f"; then
        log "에이전트 종료 $prob $AGENT r$rep: $(grep -a '^RESULT' "$OUT/log__${prob}__${AGENT}__r${rep}.txt" | tail -1) | 누적비용 $(spent)"; break
      fi
      log "에이전트 오류 $prob $AGENT r$rep (시도 $attempt): $(grep -a -m1 '"error"' "$f" 2>/dev/null | cut -c1-200)"
      mv -f "$f" "$OUT/failed__${prob}__${AGENT}__r${rep}__a${attempt}.json" 2>/dev/null; sleep 20
    done
  done
done
log "에이전트 배치 종료: $AGENT $*"
