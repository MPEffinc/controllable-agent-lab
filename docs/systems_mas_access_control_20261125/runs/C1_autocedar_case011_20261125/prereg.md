# C1 사전등록: AutoCedar target·gold 의미·정상성

2026-11-25 UTC. [공식 AutoCedar 코드](https://github.com/neselab/cedar-synthesis-engine) 고정 `a0cf180977d799cf943514b67ffc260fc579b9a5`, [공식 gold case-011](https://github.com/neselab/cedar-synthesis-engine/tree/a0cf180977d799cf943514b67ffc260fc579b9a5/dataset/gold-reference-dataset/cases/case-011). 원본 논문 평가의 19개 plan 오류와 이 실행의 case ID 대응은 **없다**.

- **RQ:** 같은 자연어 승인에서 원본 모델 검토·symbolic target/후보 검증이 gold의 의미와 어느 정도 맞고, 정상 `mergePullRequest`를 과거부하지 않는가?
- **신뢰/공격:** gold `requirement.md`를 승인 의도의 독립 oracle로, gold `schema.cedarschema`를 고정 vocabulary로 사용. 모델의 atom/map/후보는 오류 가능. 이 실험에는 공격자 주입 없음. 모델 reviewer는 같은 모델이므로 사람 검토/독립 gold가 아니다.
- **정답:** maintainer role, PR author가 아님, VPN, approvalCount≥1, targetBranch가 `hotfix/`로 시작할 때만 merge 허용. 각 필수 조건 하나씩 거짓인 요청과 unrelated action은 거부. gold 정책·schema를 모델 호출에는 주지 않고 schema만 준다.
- **원본/대안 경계:** `autocedar.cli author --schema ... --provider openai --model-review`를 고정 원본에서 호출. 기존 격리 Python 3.11 venv와 공식 Cedar v4.12.0/CVC5 v1.4.2를 재사용한다(논문 당시 toolchain과 동일성 `UNKNOWN`). 별도 gold 요청 oracle/로컬 효과 검증은 이 연구의 독립 adapter이며 원본 저자 실험이 아니다.
- **예상/반증:** 형식 target을 통과해도 gold 요청 하나 이상과 다르면 H1 의미 오류의 별도 사례. 모두 일치하고 정상 완료·비인가 차단을 유지하면 이 사례의 H1은 기존 방법으로 해결. 생성이 실패하면 실패 원인과 비용을 기록하고 성공률로 해석하지 않는다.
- **모델/비용:** `gpt-4.1-mini-2025-04-14`, AutoCedar 원본 CLI에는 seed·temperature 제어가 없어 `NOT_SET_BY_CLI`; map round 1, proposal step 16, schema repair 0, 실행 시간 상한 240초. 입력/출력 토큰은 저자 `llm_calls.jsonl`에서 확인하고 공식 가격으로 누적한다. 이 run의 목표 비용 <$0.50, 전체 $5 상한 유지. 키 값/헤더는 저장하지 않는다.
- **완료:** 원본 session의 prompt/response·review·plan·candidate/실패 사유, token/time/cost와 gold request 대조(가능할 때), 정상/비인가 로컬 effect 상태를 각각 기록하면 닫는다. 원본 실행 단계와 독립 effect adapter를 혼동하지 않는다.
