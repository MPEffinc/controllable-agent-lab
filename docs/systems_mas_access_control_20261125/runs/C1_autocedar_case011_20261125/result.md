# C1 원본 AutoCedar CLI 결과

2026-11-25 UTC. 공식 source SHA `a0cf180977d799cf943514b67ffc260fc579b9a5`, case-011 gold schema, `gpt-4.1-mini-2025-04-14`. [사전등록](prereg.md), `run_author.py`, `run_meta.json`, 원시 stdout/stderr 및 `session/` 보존.

CLI exit 1 (5.3초). Stage0 source 4개와 Stage1 schema 작성 뒤 첫 모델 요청에서 HTTP 400: `reasoning.effort`가 이 모델에 지원되지 않는다. 성공 모델 호출 0, 기록된 사용량/비용 $0. **정책 후보·실제 effect 없음.** 정책의 의미 오류나 원저자 평가 실패로 해석하지 않는다. 별도 호환성 재시도 C1b/C1c로 이어졌다.
