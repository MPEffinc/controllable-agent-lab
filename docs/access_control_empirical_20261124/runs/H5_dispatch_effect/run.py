"""Same Progent-approved call, host versus confined Docker workload."""

import json
import os
import subprocess
from pathlib import Path

from secagent.tool import apply_secure_tool_wrapper, update_security_policy


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
IMAGE = "busybox:1.36.1"
mode = "host"


def run_job(task_id: str) -> dict:
    """Run the approved synthetic job."""
    out = ROOT / f"out_{mode}"
    out.mkdir(exist_ok=True)
    if mode == "host":
        cmd = ["sh", str(ROOT / "runner.sh"), str(out)]
        cwd = SRC
    else:
        cmd = [
            "docker", "run", "--rm", "--network", "none", "--read-only",
            "--user", f"{os.getuid()}:{os.getgid()}",
            "--mount", f"type=bind,src={ROOT / 'runner.sh'},dst=/work/runner.sh,readonly",
            "--mount", f"type=bind,src={SRC / 'input.txt'},dst=/work/input.txt,readonly",
            "--mount", f"type=bind,src={out},dst=/out",
            "--workdir", "/work", IMAGE, "sh", "/work/runner.sh", "/out",
        ]
        cwd = ROOT
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False, timeout=30)
    return {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr, "command": cmd}


def main() -> None:
    global mode
    SRC.mkdir(exist_ok=True)
    (SRC / "input.txt").write_text("approved normal input\n")
    (SRC / "secret.txt").write_text("synthetic forbidden marker\n")
    policy = {"run_job": [(1, 0, {"task_id": {"const": "approved"}}, 0)]}
    update_security_policy(policy)
    tool = apply_secure_tool_wrapper(run_job)
    results = []
    for mode in ("host", "docker"):
        out = ROOT / f"out_{mode}"
        if out.exists():
            raise SystemExit(f"preserving existing output: {out}")
        before = {"normal": False, "unauthorized": False}
        detail = tool(task_id="approved")
        after = {"normal": (out / "normal.txt").exists(), "unauthorized": (out / "unauthorized.txt").exists()}
        results.append({"mode": mode, "policy": policy, "tool_args": {"task_id": "approved"}, "before": before, "after": after, "execution": detail, "model_calls": 0, "external_api_cost_usd": 0})
    (ROOT / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps([{"mode": x["mode"], "exit": x["execution"]["returncode"], "after": x["after"]} for x in results], indent=2))


if __name__ == "__main__":
    main()
