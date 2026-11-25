#!/bin/bash
# Run in the disposable 6.15 guest with compiled /work/policy.bin.
set -u
printf 'baseline\n' >/work/forbidden
for sample in 1 2 3; do
  start=$(date +%s%N)
  for ((i=0; i<5000; i++)); do : >/work/allowed; done
  end=$(date +%s%N)
  echo "baseline_${sample}_ns:$((end-start))"
done
/usr/local/bin/actplane-process --config /work/policy.bin --seed-pid "$$" --seed-label 1 >/work/perf_loader.stdout 2>/work/perf_loader.stderr &
loader_pid=$!
for ((i=0; i<150; i++)); do
  grep -q 'ActPlane: ready' /work/perf_loader.stderr && break
  kill -0 "$loader_pid" 2>/dev/null || break
  sleep 0.1
done
echo "ready_count:$(grep -c 'ActPlane: ready' /work/perf_loader.stderr)"
for sample in 1 2 3; do
  start=$(date +%s%N)
  for ((i=0; i<5000; i++)); do : >/work/allowed; done
  end=$(date +%s%N)
  echo "enforced_${sample}_ns:$((end-start))"
done
printf 'bad\n' >/work/forbidden
echo "direct_rc:$?"
/bin/bash -c 'printf child >/work/forbidden'
echo "child_rc:$?"
echo "forbidden_content:$(cat /work/forbidden)"
echo "allowed_bytes:$(wc -c </work/allowed)"
sleep 1
# Loader is protected from policy-subject signals; the disposable VM is stopped by the host.
