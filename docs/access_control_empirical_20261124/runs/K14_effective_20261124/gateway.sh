#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
LAB="$ROOT/local/openshell-h2-effective-20261124"
OLD_LAB="$ROOT/local/openshell-20261124"
GATEWAY="$OLD_LAB/releases/v0.1.9/openshell-gateway"
SANDBOX_BIN="$OLD_LAB/bin/openshell-sandbox"
STATE="$LAB/gateway-state"
TLS="$STATE/tls"

mkdir -p "$STATE"
chmod 700 "$STATE"
if ss -ltnH '( sport = :18081 )' | rg -q .; then
  echo 'Port 18081 already in use' >&2
  exit 2
fi
docker image inspect busybox:1.36.1 >/dev/null
if [[ ! -f "$TLS/ca.key" ]]; then
  "$GATEWAY" generate-certs --output-dir "$TLS" \
    --server-san 127.0.0.1 --server-san host.openshell.internal
fi
export OPENSHELL_BIND_ADDRESS=127.0.0.1
export OPENSHELL_SERVER_PORT=18081
export OPENSHELL_COMPUTE_DRIVER=docker
export OPENSHELL_GRPC_ENDPOINT=https://host.openshell.internal:18081
export OPENSHELL_DOCKER_SUPERVISOR_BIN="$SANDBOX_BIN"
export OPENSHELL_DB_URL="sqlite:$STATE/openshell.db"
export OPENSHELL_LOCAL_TLS_DIR="$TLS"
export OPENSHELL_TLS_CERT="$TLS/server/tls.crt"
export OPENSHELL_TLS_KEY="$TLS/server/tls.key"
export OPENSHELL_TLS_CLIENT_CA="$TLS/ca.crt"
export OPENSHELL_ENABLE_MTLS_AUTH=true
export OPENSHELL_DOCKER_TLS_CA="$TLS/ca.crt"
export OPENSHELL_DOCKER_TLS_CERT="$TLS/client/tls.crt"
export OPENSHELL_DOCKER_TLS_KEY="$TLS/client/tls.key"
"$GATEWAY" config preflight
exec "$GATEWAY"
