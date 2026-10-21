"""runs/usage.jsonl 을 UTC 날짜별로 묶어 호출 수, 토큰 합계, usd_estimate 합계를 출력한다.

OpenAI 대시보드와 비교용이다. 날짜 기준은 UTC 이고 대시보드의 기준과 다를 수 있다.
usd_estimate 가 없는 옛 줄은 가격 상수(lab/common.py)로 토큰에서 계산하며(캐시 없음 가정) 별도 열로 센다.
실행: python scripts/usage_by_day.py
"""
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lab.common import USAGE_LOG, _usd  # noqa: E402


def main() -> None:
    days = defaultdict(lambda: {"calls": 0, "input": 0, "output": 0, "reasoning": 0, "usd": 0.0, "legacy": 0})
    for line in USAGE_LOG.read_text(encoding="utf-8").splitlines():
        rec = json.loads(line)
        day = datetime.fromisoformat(rec["ts"]).astimezone(timezone.utc).date().isoformat()
        d = days[day]
        d["calls"] += 1
        d["input"] += rec["input_tokens"]
        d["output"] += rec["output_tokens"]
        d["reasoning"] += rec.get("reasoning_tokens") or 0
        if "usd_estimate" in rec:
            d["usd"] += rec["usd_estimate"]
        else:
            d["usd"] += _usd(rec["input_tokens"], 0, rec["output_tokens"])
            d["legacy"] += 1
    print("날짜 기준: UTC (OpenAI 대시보드의 날짜 기준과 다를 수 있음)")
    print("| 날짜(UTC) | 호출 수 | 입력 토큰 | 출력 토큰 | 그중 추론 | 토큰 합계 | usd_estimate | usd 없는 옛 줄 |")
    print("|---|---|---|---|---|---|---|---|")
    total = defaultdict(float)
    for day in sorted(days):
        d = days[day]
        print(f"| {day} | {d['calls']} | {d['input']} | {d['output']} | {d['reasoning']} | "
              f"{d['input'] + d['output']} | {d['usd']:.6f} | {d['legacy']} |")
        for k, v in d.items():
            total[k] += v
    print(f"| 합계 | {int(total['calls'])} | {int(total['input'])} | {int(total['output'])} | {int(total['reasoning'])} | "
          f"{int(total['input'] + total['output'])} | {total['usd']:.6f} | {int(total['legacy'])} |")
    print("\n주의: 이 표는 call_llm() 을 거친 호출만 센다. call_llm() 이 생기기 전의 시험 호출(S0 환경 점검, 임시 도구 호출 시험 등)은 포함되지 않는다.")


if __name__ == "__main__":
    main()
