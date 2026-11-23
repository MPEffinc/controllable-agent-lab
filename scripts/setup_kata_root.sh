#!/usr/bin/env bash
# Reviewed Kata 4.4.0 installation and Docker runtime registration.
# Default is read-only. Never run a container, restart Docker, or change cgroups by default.
set -Eeuo pipefail
umask 077

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
CONFIG_HELPER="$PROJECT_ROOT/scripts/kata_daemon_config.py"
ARCHIVE="$PROJECT_ROOT/local/progent-vm/kata-4.4.0/kata-static-4.4.0-amd64.tar.zst"
EXPECTED_SHA256="ccbc0cbc591089d0c57012b78da64b23ef43e0bac0f869dc7bfebe8588c33986"
DAEMON_CONFIG="/etc/docker/daemon.json"
KATA_PATH="/opt/kata"
SHIM="$KATA_PATH/runtime-rs/bin/containerd-shim-kata-v2"
KATA_CONFIG="$KATA_PATH/share/defaults/kata-containers/runtime-rs/configuration-qemu-runtime-rs.toml"
STATE_DIR="/var/lib/cclab-progent-kata-setup"
LOG_DIR="/var/log/cclab-progent-kata-setup"

MODE=""
RESTART_DOCKER=false
ACCEPT_IMPACT=false
LOG_FILE=""
CANDIDATE=""
STAGING=""
BACKUP=""
ORIGINAL_CONFIG_EXISTS=false
CONFIG_MUTATED=false
APPLY_COMPLETED=false
INSTALLED_CONFIG_SHA=""

usage() {
  printf 'Usage: bash scripts/setup_kata_root.sh [--check|--dry-run|--apply|--verify] [--restart-docker --accept-container-impact]\n' >&2
}

for arg in "$@"; do
  case "$arg" in
    --check|--dry-run|--apply|--verify)
      if [[ -n "$MODE" ]]; then usage; exit 2; fi
      MODE="$arg" ;;
    --restart-docker) RESTART_DOCKER=true ;;
    --accept-container-impact) ACCEPT_IMPACT=true ;;
    *) usage; exit 2 ;;
  esac
done
MODE="${MODE:---check}"
if [[ "$RESTART_DOCKER" == true && "$MODE" != --apply ]]; then usage; exit 2; fi
if [[ "$ACCEPT_IMPACT" == true && "$RESTART_DOCKER" != true ]]; then usage; exit 2; fi

note() {
  printf '%s\n' "$*"
}

run_logged() {
  local label="$1" rc printable
  shift
  printf -v printable '%q ' "$@"
  note "[RUN] $label: $printable"
  set +e
  "$@" >> "$LOG_FILE" 2>&1
  rc=$?
  set -e
  note "[EXIT] $label: $rc"
  return "$rc"
}

cleanup() {
  local rc=$?
  trap - EXIT
  if [[ "$rc" -ne 0 && "$CONFIG_MUTATED" == true && "$APPLY_COMPLETED" == false ]]; then
    if [[ -f "$DAEMON_CONFIG" && "$(sha256sum "$DAEMON_CONFIG" | cut -d ' ' -f 1)" == "$INSTALLED_CONFIG_SHA" ]]; then
      note "[RESTORE] apply failed after daemon.json change; restoring prior configuration"
      if [[ "$ORIGINAL_CONFIG_EXISTS" == true && -f "$BACKUP" ]]; then
        cp -a -- "$BACKUP" "$DAEMON_CONFIG" || note "[RESTORE FAILED] copy backup manually: $BACKUP"
      elif [[ "$ORIGINAL_CONFIG_EXISTS" == false ]]; then
        rm -f -- "$DAEMON_CONFIG" || note "[RESTORE FAILED] remove $DAEMON_CONFIG manually"
      fi
      systemctl reload docker >> "$LOG_FILE" 2>&1 || note "[RESTORE WARNING] Docker reload failed; inspect service status"
    else
      note '[RESTORE BLOCKED] daemon.json changed after this script wrote it; manual review required'
    fi
  fi
  if [[ -n "$CANDIDATE" && "$CANDIDATE" == /etc/docker/.daemon.json-kata.* ]]; then
    rm -f -- "$CANDIDATE"
  fi
  if [[ -n "$STAGING" && "$STAGING" == /opt/.kata-stage.* ]]; then
    rm -rf -- "$STAGING"
  fi
  if [[ -n "$LOG_FILE" && -f "$LOG_FILE" ]]; then
    chgrp sudo "$LOG_FILE" 2>/dev/null || true
    chmod 0640 "$LOG_FILE" 2>/dev/null || true
    note "[LOG] $LOG_FILE"
  fi
  exit "$rc"
}
trap cleanup EXIT

archive_check() {
  if [[ ! -f "$ARCHIVE" || -L "$ARCHIVE" ]]; then
    note "[FAIL] expected regular official archive is missing: $ARCHIVE"
    return 1
  fi
  local actual
  actual="$(sha256sum -- "$ARCHIVE" | cut -d ' ' -f 1)"
  if [[ "$actual" != "$EXPECTED_SHA256" ]]; then
    note "[FAIL] Kata archive SHA-256 mismatch: expected $EXPECTED_SHA256; got $actual"
    return 1
  fi
  note "[PASS] Kata 4.4.0 archive SHA-256 matches official release: $actual"
}

runtime_active() {
  docker info --format '{{json .Runtimes}}' 2>/dev/null |
    python3 -c 'import json,sys; sys.exit(0 if "kata" in json.load(sys.stdin) else 1)'
}

impact_report() {
  local count live policy id
  count="$(docker ps -q | wc -l | tr -d ' ')"
  live="$(docker info --format '{{.LiveRestoreEnabled}}')"
  note "[IMPACT] running Docker containers=$count; live-restore=$live"
  if [[ "$count" -gt 0 ]]; then
    # Print policy totals only; no existing container IDs, names or config values.
    while IFS= read -r id; do
      [[ -n "$id" ]] || continue
      policy="$(docker inspect --format '{{.HostConfig.RestartPolicy.Name}}' "$id")"
      note "[IMPACT] one running container has restart-policy=${policy:-no}"
    done < <(docker ps -q)
  fi
}

check_status() {
  local os_info
  os_info="$(python3 -c 'from pathlib import Path; lines=Path("/etc/os-release").read_text().splitlines(); d=dict(x.split("=",1) for x in lines if "=" in x and not x.startswith("#")); print(d.get("ID","unknown").strip(chr(34)),d.get("VERSION_ID","unknown").strip(chr(34)))')"
  note "[MODE] $MODE; effective_uid=$EUID; user=$(id -un); host_kernel=$(uname -r)"
  note "[OS] $os_info"
  note "[Docker] client/server: $(docker version --format '{{.Client.Version}}/{{.Server.Version}}')"
  note "[containerd] $(containerd --version)"
  if [[ -r /dev/kvm && -w /dev/kvm ]]; then note '[KVM] readable and writable'; else note '[KVM] inaccessible'; fi
  if [[ -e "$KATA_PATH" || -L "$KATA_PATH" ]]; then
    if [[ -f "$KATA_PATH/VERSION" ]]; then
      note "[Kata] /opt/kata present, version=$(cat "$KATA_PATH/VERSION")"
    else
      note '[Kata] /opt/kata exists without VERSION; apply will refuse to overwrite'
    fi
  else
    note '[Kata] /opt/kata absent'
  fi
  if [[ -e "$DAEMON_CONFIG" && ! -r "$DAEMON_CONFIG" ]]; then
    note '[Docker config] daemon.json is root-readable only; use sudo for detailed key-name inspection'
  else
    note "[Docker config] $(python3 "$CONFIG_HELPER" inspect "$DAEMON_CONFIG")"
  fi
  if runtime_active; then note '[Docker runtime] kata registered and active'; else note '[Docker runtime] kata not active'; fi
  impact_report
  archive_check
}

if [[ "$MODE" == --check ]]; then
  check_status
  exit 0
fi
if [[ "$MODE" == --dry-run ]]; then
  check_status
  note "[PLAN] sha256sum $ARCHIVE (must equal $EXPECTED_SHA256)"
  note "[PLAN] python3 $CONFIG_HELPER render $DAEMON_CONFIG /etc/docker/.daemon.json-kata.<mktemp> (merge runtimes.kata only)"
  note "[PLAN] tar -I zstd -xf $ARCHIVE -C /opt/.kata-stage.<mktemp>; mv extracted /opt/kata only if absent"
  note "[PLAN] back up existing daemon.json under $STATE_DIR; dockerd --validate --config-file <candidate>"
  note '[PLAN] atomically replace daemon.json; systemctl reload docker; docker info runtime verification'
  note '[PLAN] Docker restart is excluded from --apply. An explicit --restart-docker option also requires --accept-container-impact when containers run.'
  note "[PLAN] Root log directory: $LOG_DIR (root:sudo, mode 0640 files)"
  exit 0
fi
if [[ "$MODE" == --verify ]]; then
  [[ -x "$SHIM" && -f "$KATA_CONFIG" && -f "$KATA_PATH/share/kata-containers/vmlinux.container" && -f "$KATA_PATH/share/kata-containers/kata-containers.img" ]] || {
    note '[FAIL] Kata shim, configuration, guest kernel or image missing'; exit 1;
  }
  note "[PASS] installed Kata version=$(cat "$KATA_PATH/VERSION")"
  "$SHIM" --version
  if [[ -r "$DAEMON_CONFIG" ]]; then
    python3 "$CONFIG_HELPER" inspect "$DAEMON_CONFIG"
    dockerd --validate --config-file "$DAEMON_CONFIG"
  else
    note '[SKIP] daemon.json is not readable here; sudo --verify performs config validation'
  fi
  if runtime_active; then note '[PASS] Docker reports active kata runtime'; else note '[FAIL] Docker does not report active kata runtime'; exit 1; fi
  exit 0
fi

if [[ "$EUID" -ne 0 ]]; then
  note '[FAIL] --apply requires root; run sudo bash scripts/setup_kata_root.sh --apply'
  exit 2
fi
install -d -m 0750 -o root -g sudo "$LOG_DIR"
LOG_FILE="$(mktemp "$LOG_DIR/setup-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX.log")"
exec > >(tee -a "$LOG_FILE") 2>&1
note "[LOG] $LOG_FILE"
note "[MODE] --apply; project=$PROJECT_ROOT; restart_option=$RESTART_DOCKER"
check_status
[[ "$(uname -m)" == x86_64 ]] || { note '[FAIL] archive is amd64 but host architecture differs'; exit 1; }
[[ -d /etc/docker && ! -L /etc/docker ]] || { note '[FAIL] /etc/docker missing or symlinked'; exit 1; }
[[ ! -L "$DAEMON_CONFIG" ]] || { note '[FAIL] daemon.json symlink requires manual review'; exit 1; }

# Render before installing, so conflicts in an existing configuration cause no installation.
CANDIDATE="$(mktemp /etc/docker/.daemon.json-kata.XXXXXX)"
change="$(python3 "$CONFIG_HELPER" render "$DAEMON_CONFIG" "$CANDIDATE")" || exit 1
note "[CONFIG] Kata runtime merge: $change; other keys and runtimes preserved"
if [[ -e "$KATA_PATH" || -L "$KATA_PATH" ]]; then
  [[ ! -L "$KATA_PATH" && -f "$KATA_PATH/VERSION" && "$(cat "$KATA_PATH/VERSION")" == 4.4.0 && -x "$SHIM" && -f "$KATA_CONFIG" && -f "$KATA_PATH/share/kata-containers/vmlinux.container" && -f "$KATA_PATH/share/kata-containers/kata-containers.img" ]] || {
    note '[FAIL] existing /opt/kata is not the matching 4.4.0 installation; refusing overwrite'; exit 1;
  }
  note '[INSTALL] matching Kata 4.4.0 already present; no extraction'
else
  STAGING="$(mktemp -d /opt/.kata-stage.XXXXXX)"
  run_logged 'extract official Kata archive to private staging' tar -I zstd -xf "$ARCHIVE" -C "$STAGING" || exit 1
  [[ -x "$STAGING/opt/kata/runtime-rs/bin/containerd-shim-kata-v2" && -f "$STAGING/opt/kata/share/defaults/kata-containers/runtime-rs/configuration-qemu-runtime-rs.toml" && -f "$STAGING/opt/kata/share/kata-containers/vmlinux.container" && -f "$STAGING/opt/kata/share/kata-containers/kata-containers.img" ]] || {
    note '[FAIL] extracted release lacks required shim/config/kernel/image'; exit 1;
  }
  [[ "$(cat "$STAGING/opt/kata/VERSION")" == 4.4.0 ]] || { note '[FAIL] extracted version mismatch'; exit 1; }
  run_logged 'install Kata into /opt/kata' mv -- "$STAGING/opt/kata" "$KATA_PATH" || exit 1
  printf 'Installed by scripts/setup_kata_root.sh from SHA-256 %s\n' "$EXPECTED_SHA256" > "$KATA_PATH/.cclab-progent-setup"
fi

run_logged 'validate merged Docker configuration' dockerd --validate --config-file "$CANDIDATE" || exit 1
if [[ "$change" == changed ]]; then
  run_logged 'create root-owned backup directory' install -d -m 0700 -o root -g root "$STATE_DIR" || exit 1
  if [[ -e "$DAEMON_CONFIG" ]]; then
    ORIGINAL_CONFIG_EXISTS=true
    BACKUP="$STATE_DIR/daemon.json.before-$(date -u +%Y%m%dT%H%M%SZ)-$$"
    run_logged 'back up existing daemon.json' cp -a -- "$DAEMON_CONFIG" "$BACKUP" || exit 1
    note "[BACKUP] $BACKUP"
  else
    note '[BACKUP] prior daemon.json absent; rollback removes script-created file'
  fi
  INSTALLED_CONFIG_SHA="$(sha256sum "$CANDIDATE" | cut -d ' ' -f 1)"
  run_logged 'install merged daemon.json atomically' mv -- "$CANDIDATE" "$DAEMON_CONFIG" || exit 1
  CANDIDATE=""
  CONFIG_MUTATED=true
  run_logged 'reload Docker without restart' systemctl reload docker || exit 1
  APPLY_COMPLETED=true
else
  note '[CONFIG] existing kata entry already matches; no daemon.json rewrite'
  if ! runtime_active; then run_logged 'reload existing Docker config without restart' systemctl reload docker || exit 1; fi
  APPLY_COMPLETED=true
fi

for attempt in 1 2 3; do
  if runtime_active; then note '[PASS] kata runtime active after reload'; exit 0; fi
  sleep 1
done
note '[PENDING] valid configuration installed but kata runtime not active after reload'
if [[ "$RESTART_DOCKER" != true ]]; then
  note '[PENDING] no restart was performed; inspect log and use explicit --apply --restart-docker only after reviewing impact'
  exit 3
fi
count="$(docker ps -q | wc -l | tr -d ' ')"
if [[ "$count" -gt 0 && "$ACCEPT_IMPACT" != true ]]; then
  note '[BLOCKED] running containers exist; explicit --accept-container-impact is required for restart'
  exit 4
fi
impact_report
run_logged 'explicitly requested Docker service restart' systemctl restart docker || exit 1
if runtime_active; then note '[PASS] kata runtime active after explicit restart'; else note '[FAIL] kata runtime still inactive after restart'; exit 1; fi
