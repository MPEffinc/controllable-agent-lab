# K07 route-aware 조건 합성에 대한 Cedar 직접 대안 — 사전 등록

등록일 2026-11-25 UTC. **질문:** K07 독립 PM route 시험과 동일한 의도 `(registration_open || alternate_allow) && !embargo_active`를 Cedar의 규칙별 조건 두 permit과 한 forbid로 표현하면, 독립 허용 경로를 전역 조건 gate처럼 과거부하지 않으면서 embargo의 금지는 우선 적용하는가?

- **정책/위협/신뢰:** 동일 `User::"student" / Action::"read" / Document::"doc"`. 신뢰된 세 Boolean context를 요청마다 공급하고 CLI 결정을 효과 직전 독립 ledger에 적용한다. 이번 실험은 상태 source를 공격자가 변경하지 않는다.
- **예상:** `closed,no alternate,no embargo` Deny/effect0; `open,no alternate,no embargo` Allow/effect1; `closed,alternate,no embargo` Allow/effect1; `open,alternate,no embargo` Allow/effect1; `closed,alternate,embargo` Deny/effect0; `open,alternate,embargo` Deny/effect0. 어떤 조건이 뒤집히면 정책/요청/CLI 해석을 먼저 점검한다.
- **대조와 의미:** [NGAC-IR §5.1](https://arxiv.org/html/2611.26941v1)은 strict export가 조건부 금지를 항상 적용한다고 인정한다. [Cedar 공식 authorization semantics](https://docs.cedarpolicy.com/auth/authorization.html)는 만족된 forbid 우선과 규칙별 `when`을 정의한다. 공식 Cedar CLI v4.12.0 실험 binary로 이 기존 대안을 **독립 실행**한다. PM 원저자/NGAC-IR 생성기 재현이 아니다.
- **비용/완료:** 모델/API/실서비스 0, Python wrapper와 CLI 요청 6건, seed 해당 없음. 정책·context·binary SHA-256, 정확 argv, 결정, effect 전후, 정상/비인가 분모를 raw에 보존한다. context 신뢰·실서비스 finality·동시 전환은 미검증으로 남긴다.
