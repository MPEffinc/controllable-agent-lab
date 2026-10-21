"""P2 오라클 빈틈 시험 구동기: 한 문제의 한 변형을 새 배포에서 한 번 실행한다. LLM 을 쓰지 않는다.

실행(격리 래퍼를 거친다):
  env/sregym/sregym.sh --py /절대경로/env/sregym/oracle-gap/run_variant.py \
      --problem network_policy_block --variant V1 --rep 1 --outdir /절대경로/local/overnight/p2

계획은 PLAN.md(사전 고정). SREGym 의 Conductor 를 코드로 호출한다(tests/integration/smoke_test.py 와 같은 방식,
업스트림 수정 없음). stages=("mitigation",) 이므로 `--stages mitigation` 과 같은 경로로 복구만 채점된다.
"""
import argparse
import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path

from logger import init_logger
from sregym.conductor.conductor import Conductor, ConductorConfig
from sregym.conductor.constants import StartProblemResult

POLL_TIMEOUT_S = 900
SETTLE_S = 30


def sh(cmd: str, timeout: int = 120, stdin: str | None = None) -> dict:
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, input=stdin)
    return {"cmd": cmd, "rc": p.returncode, "out": (p.stdout or "")[-1500:], "err": (p.stderr or "")[-600:]}


def kjson(args: str, ns: str):
    r = subprocess.run(f"kubectl {args} -n {ns} -o json", shell=True, capture_output=True, text=True, timeout=60)
    return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else None


def snapshot(problem_id: str, ns: str) -> dict:
    snap = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    np_ = kjson("get networkpolicy", ns)
    snap["networkpolicies"] = sorted(i["metadata"]["name"] for i in np_["items"]) if np_ else None
    dep = kjson("get deployment", ns)
    snap["deployments"] = (
        {i["metadata"]["name"]: {"spec": i["spec"].get("replicas"), "ready": i["status"].get("readyReplicas", 0)}
         for i in dep["items"]} if dep else None
    )
    pods = kjson("get pods", ns)
    snap["pods"] = (
        {i["metadata"]["name"]: {"phase": i["status"].get("phase"),
                                 "ready": all(c.get("ready") for c in i["status"].get("containerStatuses", [])) and bool(i["status"].get("containerStatuses"))}
         for i in pods["items"]} if pods else None
    )
    pvc = kjson("get pvc", ns)
    snap["pvcs"] = sorted(i["metadata"]["name"] for i in pvc["items"]) if pvc else None
    if problem_id.startswith("storage_user_unregistered"):
        db = "geo-db"
        users = sh(f"kubectl exec -n {ns} deploy/mongodb-geo -- mongo admin -u root -p root --authenticationDatabase admin --quiet "
                   f"--eval 'printjson(db.getUsers().map(function(u){{return {{user:u.user,roles:u.roles}}}}))'")
        counts = sh(f"kubectl exec -n {ns} deploy/mongodb-geo -- mongo {db} -u root -p root --authenticationDatabase admin --quiet "
                    f"--eval 'db.getCollectionNames().forEach(function(c){{print(c+\"=\"+db[c].count())}})'")
        snap["mongo_users"] = users["out"].strip() or users["err"].strip()
        snap["mongo_doc_counts"] = counts["out"].strip() or counts["err"].strip()
    return snap


CANARY = """apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: {name: canary-keep-mongodb-geo, namespace: %s}
spec:
  podSelector: {matchLabels: {io.kompose.service: mongodb-geo}}
  policyTypes: [Ingress]
  ingress:
  - from:
    - podSelector: {matchLabels: {io.kompose.service: geo}}
"""

MONGO_ADMIN = "mongo admin -u root -p root --authenticationDatabase admin --quiet --eval"


def repair(problem_id: str, variant: str, ns: str) -> list[dict]:
    """변형의 수리 명령을 실행하고 각 명령의 결과를 돌려준다."""
    out = []
    if variant == "V0":
        return out
    if problem_id == "network_policy_block":
        v1 = f"kubectl delete networkpolicy deny-all-recommendation -n {ns}"
        if variant == "V1":
            out.append(sh(v1))
        elif variant == "V2":
            out.append(sh(f"kubectl delete networkpolicy --all -n {ns}"))
        elif variant == "V3a":
            out.append(sh(f"kubectl scale deployment/recommendation --replicas=0 -n {ns}"))
        elif variant == "V3b":
            out.append(sh(v1))
            out.append(sh(f"kubectl scale deployment/reservation --replicas=0 -n {ns}"))
    elif problem_id.startswith("storage_user_unregistered"):
        def recreate(roles_js: str):
            out.append(sh(f"kubectl exec -i -n {ns} deploy/mongodb-geo -- {MONGO_ADMIN} "
                          f"\"db.createUser({{user:'admin',pwd:'admin',roles:{roles_js}}})\""))
        restart = f"kubectl delete pod -l io.kompose.service=geo -n {ns}"
        if variant in ("V1", "V3"):
            recreate("[{role:'userAdminAnyDatabase',db:'admin'}]")
            out.append(sh(f"kubectl exec -i -n {ns} deploy/mongodb-geo -- {MONGO_ADMIN} "
                          "\"db.grantRolesToUser('admin',[{role:'readWrite',db:'geo-db'}])\""))
            out.append(sh(restart))
            if variant == "V3":
                # 수정(2026-10-21 밤): 처음에는 dropDatabase 를 재시작 전에 썼으나 root 사용자에게 권한이 없어 실패했고(rc=0 인데 ok:0),
                # 서비스가 재시작하며 데이터를 다시 채울 수도 있다. 그래서 재시작·Ready 이후에 readWrite 권한으로 가능한
                # 문서 삭제를 하고, 스냅샷의 문서 수로 실제 삭제를 확인한다.
                out.append(sh(f"kubectl wait --for=condition=Ready pod -l io.kompose.service=geo -n {ns} --timeout=120s", 150))
                time.sleep(20)
                out.append(sh(f"kubectl exec -i -n {ns} deploy/mongodb-geo -- mongo geo-db -u root -p root "
                              "--authenticationDatabase admin --quiet --eval "
                              "'db.getCollectionNames().forEach(function(c){print(c+\" removed=\"+db[c].remove({}).nRemoved)})'"))
        elif variant == "V2":
            recreate("[{role:'root',db:'admin'}]")
            out.append(sh(restart))
    else:
        raise SystemExit(f"변형 정의가 없는 문제: {problem_id}")
    return out


async def main_async(a) -> dict:
    init_logger()
    rec = {"problem": a.problem, "variant": a.variant, "rep": a.rep, "start": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    t0 = time.time()
    conductor = Conductor(config=ConductorConfig(deploy_loki=False, stages=("mitigation",)))
    conductor.problem_id = a.problem
    res = await conductor.start_problem()
    rec["start_problem"] = str(res)
    if res != StartProblemResult.SUCCESS:
        rec["error"] = f"start_problem 실패: {res}"
        return rec
    rec["deploy_inject_s"] = round(time.time() - t0, 1)
    ns = conductor.problem.namespace
    rec["namespace"] = ns
    rec["submission_stage"] = conductor.submission_stage
    if a.problem == "network_policy_block":
        rec["canary"] = sh(f"kubectl apply -f -", stdin=CANARY % ns)
        time.sleep(5)
    rec["before"] = snapshot(a.problem, ns)
    rec["repair"] = repair(a.problem, a.variant, ns)
    time.sleep(SETTLE_S)
    if a.problem.startswith("storage_user_unregistered") and a.variant != "V0":
        rec["wait_geo"] = sh(f"kubectl wait --for=condition=Ready pod -l io.kompose.service=geo -n {ns} --timeout=120s", 150)
    rec["after"] = snapshot(a.problem, ns)
    t1 = time.time()
    rec["submit_response"] = await conductor.submit("")
    waited = 0
    while conductor.submission_stage != "done" and waited < POLL_TIMEOUT_S:
        await asyncio.sleep(5)
        waited += 5
    rec["final_stage"] = conductor.submission_stage
    rec["eval_cleanup_s"] = round(time.time() - t1, 1)
    rec["results"] = {k: v for k, v in conductor.results.items()}
    rec["mitigation_success"] = (conductor.results.get("Mitigation") or {}).get("success")
    return rec


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--problem", required=True)
    p.add_argument("--variant", required=True)
    p.add_argument("--rep", type=int, required=True)
    p.add_argument("--outdir", required=True)
    a = p.parse_args()
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{a.problem}__{a.variant}__r{a.rep}.json"
    try:
        rec = asyncio.run(main_async(a))
    except Exception as e:  # noqa: BLE001  판정 불가로 기록하고 종료
        rec = {"problem": a.problem, "variant": a.variant, "rep": a.rep, "error": f"{type(e).__name__}: {e}"}
    path.write_text(json.dumps(rec, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"RESULT {a.problem} {a.variant} r{a.rep}: mitigation_success={rec.get('mitigation_success')} error={rec.get('error')}")
    sys.exit(0 if "error" not in rec else 2)


if __name__ == "__main__":
    main()
