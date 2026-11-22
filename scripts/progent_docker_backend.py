"""Trusted Docker controller restricted to containers created by this instance."""

from __future__ import annotations

import json
import subprocess


IMAGE = "busybox@sha256:73aaf090f3d85aa34ee199857f03fa3a95c8ede2ffd4cc2cdb5b94e566b11662"
LABEL_KEY = "org.cclab.progent.experiment"


class DockerBackendError(RuntimeError):
    pass


class DockerBackend:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.owned: dict[str, str] = {}
        self.invocations: list[dict] = []

    def _docker(self, *args: str, record: bool = True) -> str:
        command = ["docker", *args]
        try:
            process = subprocess.run(command, capture_output=True, text=True, timeout=25, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise DockerBackendError(f"Docker invocation failed: {type(exc).__name__}: {exc}") from exc
        if record:
            self.invocations.append({"argv": command, "returncode": process.returncode,
                                     "stdout": process.stdout.strip(), "stderr": process.stderr.strip()})
        if process.returncode:
            raise DockerBackendError(f"docker {args[0]} exit {process.returncode}: {process.stderr.strip()}")
        return process.stdout.strip()

    def create(self, suffix: str) -> str:
        if not suffix.isdigit() or len(suffix) > 2:
            raise ValueError("invalid experiment suffix")
        name = f"cclab-progent-exp-{self.run_id}-{suffix}"
        if name in self.owned:
            raise ValueError("resource already owned")
        container_id = self._docker("create", "--name", name, "--label", f"{LABEL_KEY}={self.run_id}",
            "--network", "none", "--memory", "128m", "--cpus", "0.5", "--pids-limit", "64",
            "--read-only", IMAGE, "sleep", "3600")
        self.owned[name] = container_id
        self._check_owned(name)
        return name

    def _inspect(self, name: str) -> dict:
        return json.loads(self._docker("inspect", "--type", "container", name, record=False))[0]

    def _check_owned(self, name: str) -> dict:
        if name not in self.owned:
            raise DockerBackendError("resource is not in this run's ownership manifest")
        info = self._inspect(name)
        if (info["Id"] != self.owned[name] or info["Name"] != "/" + name or
                info["Config"]["Labels"].get(LABEL_KEY) != self.run_id):
            raise DockerBackendError("resource ID/name/label ownership mismatch")
        return info

    def list_resources(self) -> list[str]:
        return sorted(name for name in self.owned if self._check_owned(name))

    def status(self, name: str) -> str:
        return self._check_owned(name)["State"]["Status"]

    def start(self, name: str) -> str:
        if self.status(name) not in {"created", "exited"}:
            raise DockerBackendError("start requires created or exited container")
        self._docker("start", name)
        return self.status(name)

    def stop(self, name: str) -> str:
        if self.status(name) != "running":
            raise DockerBackendError("stop requires running container")
        self._docker("stop", "--time", "2", name)
        return self.status(name)

    def restart(self, name: str) -> str:
        if self.status(name) != "running":
            raise DockerBackendError("restart requires running container")
        self._docker("restart", "--time", "2", name)
        return self.status(name)

    def cleanup(self) -> None:
        for name in list(self.owned):
            self._check_owned(name)
            self._docker("rm", "-f", name)
            del self.owned[name]
