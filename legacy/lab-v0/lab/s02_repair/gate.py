"""행동 도구 앞의 게이트. 모든 호출을 기록한다. 정책은 S3 에서 붙인다.

이 모듈은 판정기·정답 모듈을 import 하지 않는다(게이트에는 실험 정답을 주지 않는다).
"""


class Gate:
    """조건 0: 모든 호출을 기록하고 통과시킨다."""

    def __init__(self):
        self.log: list[dict] = []

    def __call__(self, call: dict) -> dict:
        """call = {"tool": 이름, "args": 인자}. 로그 항목(allowed, reason 포함)을 돌려준다."""
        entry = {"seq": len(self.log) + 1, "call": call, "allowed": True, "reason": "조건 0: 정책 없음"}
        self.log.append(entry)
        return entry
