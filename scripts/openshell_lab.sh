#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LAB="$ROOT/local/openshell-20261124"
RELEASE="$LAB/releases/v0.1.9"
CLI="$RELEASE/openshell"
GATEWAY="$RELEASE/openshell-gateway"
PROVER="$RELEASE/openshell-prover"
SANDBOX_BIN="$LAB/bin/openshell-sandbox"
STATE="$LAB/gateway-state"
TLS="$STATE/tls"
FIXTURES="$ROOT/docs/experiments/20261124_openshell"
export XDG_CONFIG_HOME="$LAB/cli-config"
export OPENSHELL_GATEWAY=openshell

need_binaries() {
  for path in "$CLI" "$GATEWAY" "$PROVER" "$SANDBOX_BIN"; do
    if [[ ! -x "$path" ]]; then
      printf 'Missing executable: %s\nSee %s/README.md for setup.\n' "$path" "$FIXTURES" >&2
      exit 2
    fi
  done
  local path expected actual
  while read -r expected path; do
    actual="$(sha256sum "$path")"
    actual="${actual%% *}"
    if [[ "$actual" != "$expected" ]]; then
      printf 'SHA-256 mismatch: %s\n' "$path" >&2
      exit 2
    fi
  done <<EOF
2db8e54f63feebe9f994efaf6004bbd45c55bc70ea455eda42fe82a0ea7c7e69 $CLI
865e8c5ae15a599ca001d023efc137527ff8e102b0cccb90a85184a1c6e33978 $GATEWAY
2a79750e7cff56a4d97dfc08c8a3b069b2a2c020f527ac19b4fdf09dcbb0d8b3 $PROVER
6c3afd40f40922c9c84be19460779c951b61c6c542aaa95e4c2c8a4b0e7f48c4 $SANDBOX_BIN
EOF
  [[ "$("$CLI" --version)" == *0.1.9* ]] || { echo 'Expected OpenShell v0.1.9' >&2; exit 2; }
}

gateway_env() {
  env \
    OPENSHELL_BIND_ADDRESS=127.0.0.1 \
    OPENSHELL_SERVER_PORT=18080 \
    OPENSHELL_COMPUTE_DRIVER=docker \
    OPENSHELL_GRPC_ENDPOINT=https://host.openshell.internal:18080 \
    OPENSHELL_DOCKER_SUPERVISOR_BIN="$SANDBOX_BIN" \
    OPENSHELL_DB_URL="sqlite:$STATE/openshell.db" \
    OPENSHELL_LOCAL_TLS_DIR="$TLS" \
    OPENSHELL_TLS_CERT="$TLS/server/tls.crt" \
    OPENSHELL_TLS_KEY="$TLS/server/tls.key" \
    OPENSHELL_TLS_CLIENT_CA="$TLS/ca.crt" \
    OPENSHELL_ENABLE_MTLS_AUTH=true \
    OPENSHELL_DOCKER_TLS_CA="$TLS/ca.crt" \
    OPENSHELL_DOCKER_TLS_CERT="$TLS/client/tls.crt" \
    OPENSHELL_DOCKER_TLS_KEY="$TLS/client/tls.key" \
    "$GATEWAY" "$@"
}

serve_gateway() {
  need_binaries
  docker info >/dev/null
  docker image inspect busybox:1.36.1 >/dev/null
  mkdir -p "$STATE" "$XDG_CONFIG_HOME"
  chmod 700 "$STATE" "$XDG_CONFIG_HOME"
  if ss -ltnH '( sport = :18080 )' | grep -q .; then
    echo 'Port 18080 is in use; refusing to start another gateway.' >&2
    exit 2
  fi
  if [[ ! -f "$TLS/ca.key" ]]; then
    "$GATEWAY" generate-certs --output-dir "$TLS" \
      --server-san 127.0.0.1 --server-san host.openshell.internal
  fi
  gateway_env config preflight
  echo 'Gateway runs in this terminal. Open a second terminal for the demo.'
  gateway_env
}

register_gateway() {
  if [[ ! -f "$XDG_CONFIG_HOME/openshell/gateways/openshell/metadata.json" ]]; then
    "$CLI" gateway add https://127.0.0.1:18080 --local --name openshell
  fi
}

prover_demo() {
  need_binaries
  local run="$LAB/runs/prover-$(date -u +%Y%m%dT%H%M%SZ)"
  mkdir -p "$run"
  "$PROVER" check "$FIXTURES/candidate-contained.yaml" \
    --boundary "$FIXTURES/boundary.yaml" --output json > "$run/contained.json"
  local rc=0
  "$PROVER" check "$FIXTURES/candidate-exceeds.yaml" \
    --boundary "$FIXTURES/boundary.yaml" --output json > "$run/exceeds.json" || rc=$?
  if [[ "$rc" -ne 1 ]]; then
    echo "Expected exceeds_boundary exit code 1; got $rc" >&2
    exit 1
  fi
  cat "$run/contained.json" "$run/exceeds.json"
  echo "Prover results: $run"
}

demo() {
  need_binaries
  register_gateway
  "$CLI" status >/dev/null
  docker image inspect busybox:1.36.1 >/dev/null
  for name in oslab-default oslab-ro; do
    if "$CLI" sandbox get "$name" >/dev/null 2>&1; then
      echo "Sandbox $name already exists; run 'stop' before repeating the demo." >&2
      exit 2
    fi
  done
  local run="$LAB/runs/sandbox-$(date -u +%Y%m%dT%H%M%SZ)"
  mkdir -p "$run"
  echo "Local run log: $run/terminal.log"
  {
    echo '[DEFAULT POLICY: /tmp write]'
    "$CLI" sandbox create --name oslab-default --from busybox:1.36.1 \
      --cpu 0.5 --memory 512Mi --detach --no-auto-providers --timeout 120 \
      -- sh -c 'sleep 3600'
    "$CLI" sandbox exec oslab-default --no-login-shell -- sh -c \
      'id; printf allowed > /tmp/openshell-demo.txt; cat /tmp/openshell-demo.txt; printf "\n"'
    echo '[CUSTOM POLICY: /tmp read-only, /sandbox writable]'
    "$CLI" sandbox create --name oslab-ro --from busybox:1.36.1 \
      --policy "$FIXTURES/readonly_tmp.yaml" --cpu 0.5 --memory 512Mi \
      --detach --no-auto-providers --timeout 120 -- sh -c 'sleep 3600'
    "$CLI" sandbox get oslab-ro --policy-only
    echo
    "$CLI" sandbox exec oslab-ro --no-login-shell -- sh -c \
      'id; printf allowed > /sandbox/openshell-demo.txt; cat /sandbox/openshell-demo.txt; printf "\n"'
    local rc=0
    "$CLI" sandbox exec oslab-ro --no-login-shell -- sh -c \
      'printf denied > /tmp/openshell-demo.txt' || rc=$?
    echo "Denied write exit code: $rc"
    [[ "$rc" -eq 1 ]] || { echo 'Unexpected deny result' >&2; exit 1; }
    echo '[NETWORK: no endpoint allow rule]'
    rc=0
    "$CLI" sandbox exec oslab-default --timeout 12 --no-login-shell \
      -- wget -T 4 -O - http://example.com/ || rc=$?
    echo "Default network request exit code: $rc"
    [[ "$rc" -eq 1 ]] || { echo 'Unexpected network result' >&2; exit 1; }
    echo '[OWNED DOCKER CONTAINERS]'
    docker ps --filter 'name=openshell-default--oslab-' \
      --format '{{.Names}} {{.Status}}'
    local ro_container net_supervisor landlock_line net_line
    ro_container="$(docker ps --format '{{.Names}}' \
      | rg '^openshell-default--oslab-ro-' | rg -v -- '-supervisor$' | head -1)"
    net_supervisor="$(docker ps --format '{{.Names}}' \
      | rg '^openshell-default--oslab-default-.*-supervisor$' | head -1)"
    echo "[DOCKER OUTER FENCE] $(docker inspect --format 'readonly_rootfs={{.HostConfig.ReadonlyRootfs}} network_mode={{.HostConfig.NetworkMode}} user={{.Config.User}}' "$ro_container")"
    landlock_line="$(docker logs --since 5m "$ro_container" 2>&1 \
      | rg 'OCSF CONFIG:APPLYING.*Landlock filesystem sandbox' | tail -1 || true)"
    [[ -n "$landlock_line" ]] || { echo 'Missing Landlock application log' >&2; exit 1; }
    echo "[LANDLOCK] $landlock_line"
    net_line=''
    for _ in {1..5}; do
      net_line="$(docker logs --since 5m "$net_supervisor" 2>&1 \
        | rg 'OCSF NET:OPEN.*DENIED.*example.com:80' | tail -1 || true)"
      [[ -n "$net_line" ]] && break
      sleep 1
    done
    [[ -n "$net_line" ]] || { echo 'Missing supervisor network deny log' >&2; exit 1; }
    echo "[SUPERVISOR] $net_line"
  } 2>&1 | tee "$run/terminal.log"
  echo "Inspect supervisor OCSF logs with: docker logs <the oslab-default supervisor name>"
}

stop_lab() {
  need_binaries
  register_gateway
  if "$CLI" status >/dev/null 2>&1; then
    for name in oslab-default oslab-ro; do
      if "$CLI" sandbox get "$name" >/dev/null 2>&1; then
        "$CLI" sandbox delete "$name"
      fi
    done
  fi
  echo 'Lab sandboxes removed. Stop the foreground gateway with Ctrl-C in the first terminal.'
}

case "${1:-help}" in
  serve) serve_gateway ;;
  status) need_binaries; register_gateway; "$CLI" status; "$CLI" sandbox list ;;
  prover) prover_demo ;;
  demo) demo ;;
  stop) stop_lab ;;
  *) echo 'Usage: bash scripts/openshell_lab.sh {serve|status|prover|demo|stop}' ;;
esac
