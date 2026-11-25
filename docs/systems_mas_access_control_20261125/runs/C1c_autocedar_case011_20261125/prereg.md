# C1c 마지막 AutoCedar API 호환성 재시도

2026-11-25 UTC. C1/C1b와 같은 원본 case-011, gold schema, `gpt-4.1-mini-2025-04-14`, 1 map round, 16 proposal, 0 schema repair, 240초 제한. C1은 unsupported `reasoning.effort`, C1b는 `PropertyAtomsResponse.request_dict`의 strict JSON schema HTTP 400으로 종료했다. 두 번 모두 성공 모델 호출 0건.

- **RQ:** 원본 정책 파이프라인을 보존하고 API 호환성 어댑터만 바꾸면 후보·검증 결과를 얻을 수 있는가?
- **어댑터:** `compat_adapter.py`가 unsupported `reasoning` 제거, structured output을 일반 JSON text로 요청하고 원본 Pydantic type으로 로컬 검증한다. 원본 source를 수정하지 않는다. 이 변경은 model prompting과 구조화 출력 보장을 바꾸므로 논문의 원본 재현 결과라고 주장하지 않는다.
- **비용/중단:** 요청별 토큰·예상 비용을 `adapter_usage.jsonl`에 저장하고 이 run 예상 비용이 $0.50에 도달하면 추가 호출을 중지한다. 전체 상한 $5. 실패하면 원본 경로 재시도를 중단하고 다른 검증 방식으로 전환한다.
- **완료:** CLI success/failure, 원시 로그, 비용, 후보 존재 여부. 후보가 있으면 별도 독립 gold 요청 및 effect adapter를 진행한다.
