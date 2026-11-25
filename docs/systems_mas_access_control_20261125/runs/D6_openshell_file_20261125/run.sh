#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
RUN="$ROOT/docs/systems_mas_access_control_20261125/runs/D6_openshell_file_20261125"
LAB="$ROOT/local/d6_openshell_file"
RELEASE="$ROOT/local/openshell-20261124/releases/v0.1.9"
CLI="$RELEASE/openshell"
GATEWAY="$RELEASE/openshell-gateway"
SANDBOX_BIN="$ROOT/local/openshell-20261124/bin/openshell-sandbox"
STATE="$LAB/gateway-state"
TLS="$STATE/tls"
export XDG_CONFIG_HOME="$LAB/cli-config" OPENSHELL_GATEWAY=d6file OPENSHELL_LOCAL_TLS_DIR="$TLS"
mkdir -p "$STATE" "$XDG_CONFIG_HOME"
chmod 700 "$STATE" "$XDG_CONFIG_HOME"
[[ ! -e "$RUN/normal.stdout" ]] || { echo 'D6 result already exists' >&2; exit 2; }
[[ -x "$CLI" && -x "$GATEWAY" && -x "$SANDBOX_BIN" ]]
[[ "$($CLI --version)" == *0.1.9* ]]
! ss -ltnH '( sport = :18084 )' | grep -q .
docker image inspect busybox:1.36.1 >/dev/null

gateway_env() {
  env OPENSHELL_BIND_ADDRESS=127.0.0.1 OPENSHELL_SERVER_PORT=18084 \
    OPENSHELL_COMPUTE_DRIVER=docker \
    OPENSHELL_GRPC_ENDPOINT=https://host.openshell.internal:18084 \
    OPENSHELL_DOCKER_SUPERVISOR_BIN="$SANDBOX_BIN" \
    OPENSHELL_DB_URL="sqlite:$STATE/openshell.db" \
    OPENSHELL_LOCAL_TLS_DIR="$TLS" \
    OPENSHELL_TLS_CERT="$TLS/server/tls.crt" \
    OPENSHELL_TLS_KEY="$TLS/server/tls.key" \
    OPENSHELL_TLS_CLIENT_CA="$TLS/ca.crt" OPENSHELL_ENABLE_MTLS_AUTH=true \
    OPENSHELL_DOCKER_TLS_CA="$TLS/ca.crt" \
    OPENSHELL_DOCKER_TLS_CERT="$TLS/client/tls.crt" \
    OPENSHELL_DOCKER_TLS_KEY="$TLS/client/tls.key" \
    "$GATEWAY" "$@"
}

gateway_pid=''
created=0
cleanup() {
  if [[ "$created" -eq 1 ]]; then
    timeout 45 "$CLI" sandbox delete d6file01 >"$RUN/delete.stdout" 2>"$RUN/delete.stderr" || true
  fi
  if [[ -n "$gateway_pid" ]]; then
    kill "$gateway_pid" 2>/dev/null || true
    wait "$gateway_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

if [[ ! -f "$TLS/ca.key" ]]; then
  "$GATEWAY" generate-certs --output-dir "$TLS" \
    --server-san 127.0.0.1 --server-san host.openshell.internal >"$RUN/certs.stdout" 2>"$RUN/certs.stderr"
fi
gateway_env config preflight >"$RUN/preflight.stdout" 2>"$RUN/preflight.stderr"
gateway_env >"$RUN/gateway.stdout" 2>"$RUN/gateway.stderr" &
gateway_pid=$!
for i in $(seq 1 60); do
  ss -ltnH '( sport = :18084 )' | grep -q . && break
  kill -0 "$gateway_pid"
  sleep 0.2
done
"$CLI" gateway add https://127.0.0.1:18084 --local --name d6file >"$RUN/gateway_add.stdout" 2>"$RUN/gateway_add.stderr"
"$CLI" status >"$RUN/status.stdout" 2>"$RUN/status.stderr"
"$CLI" profile import -f "$ROOT/local/openshell-20261124/source-v0.1.9/providers/pypi.yaml" >"$RUN/profile.stdout" 2>"$RUN/profile.stderr"
"$CLI" sandbox create --name d6file01 --from busybox:1.36.1 \
  --policy "$RUN/policy.yaml" --cpu 0.5 --memory 512Mi \
  --detach --no-auto-providers --timeout 120 -- sh -c 'sleep 3600' \
  >"$RUN/create.stdout" 2>"$RUN/create.stderr"
created=1
"$CLI" policy get d6file01 --full -o json >"$RUN/full-policy.json"
docker ps --filter 'name=openshell-d6file--d6file01-' --format '{{.Names}} {{.Status}}' >"$RUN/containers.txt"

start=$(date +%s%N)
"$CLI" sandbox exec d6file01 --no-login-shell -- sh -c \
  'printf normal > /sandbox/d6-allowed; cat /sandbox/d6-allowed' \
  >"$RUN/normal.stdout" 2>"$RUN/normal.stderr"
normal_rc=$?
normal_ns=$(($(date +%s%N)-start))

start=$(date +%s%N)
set +e
"$CLI" sandbox exec d6file01 --no-login-shell -- sh -c \
  'printf forbidden > /tmp/d6-forbidden' >"$RUN/direct.stdout" 2>"$RUN/direct.stderr"
direct_rc=$?
set -e
direct_ns=$(($(date +%s%N)-start))

start=$(date +%s%N)
set +e
"$CLI" sandbox exec d6file01 --no-login-shell -- sh -c \
  'sh -c "printf child > /tmp/d6-forbidden"' >"$RUN/child.stdout" 2>"$RUN/child.stderr"
child_rc=$?
set -e
child_ns=$(($(date +%s%N)-start))

"$CLI" sandbox exec d6file01 --no-login-shell -- sh -c \
  'printf "allowed="; cat /sandbox/d6-allowed; printf "\nforbidden_exists="; if test -e /tmp/d6-forbidden; then echo yes; else echo no; fi' \
  >"$RUN/state.stdout" 2>"$RUN/state.stderr"
"$CLI" logs d6file01 --since 10m --source sandbox >"$RUN/openshell-logs.txt" 2>"$RUN/openshell-logs.stderr" || true
supervisor=$(sed -n 's/^\([^ ]*-supervisor\) .*/\1/p' "$RUN/containers.txt" | head -1)
if [[ -n "$supervisor" ]]; then
  docker logs "$supervisor" >"$RUN/supervisor.stdout" 2>"$RUN/supervisor.stderr" || true
fi
printf 'normal_rc=%s normal_ns=%s\ndirect_rc=%s direct_ns=%s\nchild_rc=%s child_ns=%s\n' \
  "$normal_rc" "$normal_ns" "$direct_rc" "$direct_ns" "$child_rc" "$child_ns" >"$RUN/summary.txt"
cat "$RUN/summary.txt" "$RUN/state.stdout"
