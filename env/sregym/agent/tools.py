"""P3/P4 에이전트의 도구. 임의 셸 실행 도구가 아니다.

- 모든 명령은 인자 목록으로 subprocess 에 넘긴다(shell=True 없음, 파이프·리다이렉션 불가).
- kubectl 은 동사 허용 목록, 네임스페이스는 문제 네임스페이스 하나로 고정(없으면 자동으로 붙이고, 다르면 거부).
- --kubeconfig/--context/--server/--token/--as 등 접속 대상을 바꾸는 플래그와 -A/--all-namespaces 는 거부.
- 노드·네임스페이스·PV·CRD·클러스터 역할 삭제는 거부.
- kubectl_exec 는 파드 안에서 `mongo`/`mongosh` 실행 파일만 허용한다(셸 아님).
모든 호출은 이벤트 로그(JSONL)에 남긴다. 게이트는 아직 없다(P4 의 "기록만 하고 통과" 방식은 gate_log 로 대신한다).
"""
import json
import subprocess
import time
from pathlib import Path

READ_VERBS = {"get", "describe", "logs", "top", "explain", "api-resources"}
WRITE_VERBS = {"delete", "scale", "patch", "rollout", "label", "annotate", "set", "create"}
FORBIDDEN_FLAGS = {"--kubeconfig", "--context", "--server", "-s", "--token", "--as", "--as-group", "--cluster",
                   "--user", "--insecure-skip-tls-verify", "--certificate-authority", "--client-certificate",
                   "--client-key", "-A", "--all-namespaces"}
FORBIDDEN_DELETE_KINDS = {"namespace", "namespaces", "ns", "node", "nodes", "no", "pv", "persistentvolume",
                          "persistentvolumes", "crd", "crds", "customresourcedefinition", "customresourcedefinitions",
                          "clusterrole", "clusterroles", "clusterrolebinding", "clusterrolebindings", "storageclass",
                          "storageclasses", "sc", "validatingwebhookconfiguration", "mutatingwebhookconfiguration"}
EXEC_BINARIES = {"mongo", "mongosh"}
MAX_OUT = 6000


class ToolBox:
    def __init__(self, namespace: str, events_path: Path, *, allow_exec: bool):
        self.ns = namespace
        self.events_path = events_path
        self.allow_exec = allow_exec
        self.calls: list[dict] = []

    # ---- 기록 ----
    def _log(self, tool: str, role: str, args, result: str, ok: bool) -> None:
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "tool": tool, "role": role, "args": args,
               "ok": ok, "result": result[:1500]}
        self.calls.append(rec)
        with self.events_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def _run(self, argv: list[str], stdin: str | None = None, timeout: int = 90) -> tuple[bool, str]:
        try:
            p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, input=stdin)
        except subprocess.TimeoutExpired:
            return False, f"시간 초과({timeout}초)"
        out = (p.stdout or "") + (("\n[stderr]\n" + p.stderr) if p.stderr.strip() else "")
        if len(out) > MAX_OUT:
            out = out[:MAX_OUT] + f"\n...(잘림, 전체 {len(out)}자)"
        return p.returncode == 0, out.strip() or "(출력 없음)"

    # ---- 검증 ----
    def _check_args(self, args: list[str], verbs: set[str]) -> str | None:
        if not args or not isinstance(args, list) or not all(isinstance(a, str) for a in args):
            return "args 는 문자열 목록이어야 한다 (예: [\"get\", \"pods\"])"
        if args[0] not in verbs:
            return f"허용되지 않은 동사 '{args[0]}'. 허용: {sorted(verbs)}"
        for i, a in enumerate(args):
            flag = a.split("=")[0]
            if flag in FORBIDDEN_FLAGS:
                return f"허용되지 않은 플래그 {flag}"
            if flag in ("-n", "--namespace"):
                val = a.split("=", 1)[1] if "=" in a else (args[i + 1] if i + 1 < len(args) else "")
                if val != self.ns:
                    return f"네임스페이스는 '{self.ns}' 만 쓸 수 있다"
        if args[0] == "delete":
            for a in args[1:]:
                kind = a.split("/")[0].lower() if not a.startswith("-") else ""
                if kind in FORBIDDEN_DELETE_KINDS:
                    return f"'{kind}' 삭제는 허용되지 않는다"
        return None

    def _with_ns(self, args: list[str]) -> list[str]:
        has_ns = any(a in ("-n", "--namespace") or a.startswith("--namespace=") for a in args)
        return ["kubectl", *args] if has_ns else ["kubectl", *args, "-n", self.ns]

    # ---- 도구 본체 ----
    def kubectl_read(self, args: list[str], role: str = "agent") -> str:
        err = self._check_args(args, READ_VERBS)
        if err:
            self._log("kubectl_read", role, args, "거부: " + err, False)
            return "거부: " + err
        argv = ["kubectl", *args] if args[0] == "api-resources" or args[0] == "explain" else self._with_ns(args)
        ok, out = self._run(argv)
        self._log("kubectl_read", role, args, out, ok)
        return out

    def kubectl_write(self, args: list[str], role: str = "agent") -> str:
        err = self._check_args(args, WRITE_VERBS)
        if err:
            self._log("kubectl_write", role, args, "거부: " + err, False)
            return "거부: " + err
        ok, out = self._run(self._with_ns(args))
        self._log("kubectl_write", role, args, out, ok)
        return out

    def kubectl_apply_manifest(self, manifest: str, role: str = "agent") -> str:
        ok, out = self._run(["kubectl", "apply", "-n", self.ns, "-f", "-"], stdin=manifest)
        self._log("kubectl_apply_manifest", role, {"manifest": manifest[:800]}, out, ok)
        return out

    def kubectl_exec(self, deployment: str, command: list[str], role: str = "agent") -> str:
        if not self.allow_exec:
            self._log("kubectl_exec", role, {"deployment": deployment, "command": command}, "거부: 이 구성에서는 비활성", False)
            return "거부: 이 실험 구성에서는 kubectl_exec 가 비활성이다"
        if not command or command[0] not in EXEC_BINARIES or not deployment.replace("-", "").isalnum():
            msg = f"거부: 실행 파일은 {sorted(EXEC_BINARIES)} 만 허용, deployment 는 이름만"
            self._log("kubectl_exec", role, {"deployment": deployment, "command": command}, msg, False)
            return msg
        ok, out = self._run(["kubectl", "exec", "-i", "-n", self.ns, f"deploy/{deployment}", "--", *command], timeout=120)
        self._log("kubectl_exec", role, {"deployment": deployment, "command": command}, out, ok)
        return out
