"""Pure, strict Docker daemon.json merge for the reviewed Kata root setup."""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path


KATA_RUNTIME = {
    "runtimeType": "/opt/kata/runtime-rs/bin/containerd-shim-kata-v2",
    "options": {
        "ConfigPath": "/opt/kata/share/defaults/kata-containers/runtime-rs/configuration-qemu-runtime-rs.toml"
    },
}


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate daemon.json key: {key}")
        result[key] = value
    return result


def read_config(path: Path) -> dict:
    if path.is_symlink():
        raise ValueError("daemon.json symlink requires manual review")
    if not path.exists():
        return {}
    result = json.loads(path.read_text(), object_pairs_hook=unique_pairs)
    if not isinstance(result, dict):
        raise ValueError("daemon.json must contain a JSON object")
    return result


def merge_config(existing: dict) -> tuple[dict, bool]:
    merged = deepcopy(existing)
    runtimes = merged.setdefault("runtimes", {})
    if not isinstance(runtimes, dict):
        raise ValueError("daemon.json runtimes must be a JSON object")
    if "kata" in runtimes:
        if runtimes["kata"] != KATA_RUNTIME:
            raise ValueError("existing kata runtime differs; manual review required")
        return merged, False
    runtimes["kata"] = deepcopy(KATA_RUNTIME)
    return merged, True


def summary(config: dict, exists: bool) -> dict:
    runtimes = config.get("runtimes", {})
    return {
        "exists": exists,
        "top_level_keys": sorted(config),
        "runtime_names": sorted(runtimes) if isinstance(runtimes, dict) else "invalid",
        "kata_matches_proposed": isinstance(runtimes, dict) and runtimes.get("kata") == KATA_RUNTIME,
        "live_restore": config.get("live-restore", "unset"),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("inspect", "render"))
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path, nargs="?")
    args = parser.parse_args()
    config = read_config(args.source)
    if args.action == "inspect":
        print(json.dumps(summary(config, args.source.exists()), sort_keys=True))
        return
    if args.destination is None:
        parser.error("render requires destination")
    merged, changed = merge_config(config)
    if args.destination.is_symlink():
        raise ValueError("render destination must not be a symlink")
    args.destination.write_text(json.dumps(merged, indent=2, sort_keys=True) + "\n")
    print("changed" if changed else "unchanged")


if __name__ == "__main__":
    main()
