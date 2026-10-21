"""P2 결과 JSON(local/overnight/p2)을 문제×변형 표로 집계한다. 사용: python3 summarize.py <p2 디렉터리>"""
import json
import sys
from pathlib import Path

d = Path(sys.argv[1])
rows = {}
for f in sorted(d.glob("*__r[0-9].json")):
    r = json.loads(f.read_text())
    rows.setdefault((r["problem"], r["variant"]), {})[r["rep"]] = r


def state(r):
    a = r.get("after") or {}
    parts = []
    if a.get("networkpolicies") is not None:
        parts.append("정책 " + (",".join(a["networkpolicies"]) or "없음"))
    deps = a.get("deployments") or {}
    zero = sorted(k for k, v in deps.items() if v["spec"] == 0)
    if deps:
        parts.append("replicas=0: " + (",".join(zero) or "없음"))
    pods = a.get("pods") or {}
    if pods:
        parts.append(f"파드 Ready {sum(v['ready'] for v in pods.values())}/{len(pods)}")
    if a.get("mongo_users"):
        parts.append("mongo 사용자 " + " ".join(a["mongo_users"].split())[:160])
    if a.get("mongo_doc_counts"):
        parts.append("문서수 " + " ".join(a["mongo_doc_counts"].split())[:120])
    return "; ".join(parts)


print("| 문제 | 변형 | r1 판정 | r2 판정 | 일치 | 수리 후 상태(r1) | 오라클 reason(r1) |")
print("|---|---|---|---|---|---|---|")
for (prob, var), reps in sorted(rows.items()):
    def v(i):
        r = reps.get(i)
        if r is None:
            return "-"
        return {True: "PASS", False: "FAIL", None: "판정불가"}[r.get("mitigation_success")]
    r1 = reps.get(1, {})
    res = (r1.get("results") or {}).get("Mitigation") or {}
    same = "-" if len(reps) < 2 else ("일치" if v(1) == v(2) else "불일치")
    print(f"| {prob} | {var} | {v(1)} | {v(2)} | {same} | {state(r1)} | {res.get('reason', '')} |")
