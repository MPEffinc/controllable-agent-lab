#!/bin/bash
printf 'baseline\n' >/work/allowed
printf 'baseline\n' >/work/forbidden
/usr/local/bin/actplane-process --config /work/policy.bin --seed-pid "$$" --seed-label 1 >/work/loader.stdout 2>/work/loader.stderr &
loader_pid=$!
for i in $(seq 1 150); do
  grep -q 'ActPlane: ready' /work/loader.stderr && break
  kill -0 "$loader_pid" 2>/dev/null || break
  sleep 0.1
done
echo "ready_count:$(grep -c 'ActPlane: ready' /work/loader.stderr)"
printf 'normal\n' >/work/allowed
echo "allowed_rc:$?"
printf 'bad\n' >/work/forbidden 2>/work/direct_error
echo "direct_rc:$?"
/bin/bash -c 'printf child >/work/forbidden' 2>/work/child_error
echo "child_rc:$?"
echo "allowed_content:$(cat /work/allowed)"
echo "forbidden_content:$(cat /work/forbidden)"
sleep 1
kill "$loader_pid" 2>/dev/null
wait "$loader_pid" 2>/dev/null
echo "loader_exit:$?"
