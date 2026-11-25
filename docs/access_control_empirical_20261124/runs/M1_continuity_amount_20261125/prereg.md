# M1 CONTINUITY 원본 함수 부분 호출 — 사전등록

등록 시점: 2026-11-25 UTC, **코드 실행 전**. Donno 논문 재현이 아닌 독립 대조. 외부 API·실서비스 호출 0.

## 검증 질문과 원래 주장

- 질문: 원점 RootGrant의 finance 금액 상한이 **EUR 120**(12,000 cents)일 때, 서명된 후속 provenance/context/transition이 **EUR 9000**(900,000 cents) 액션을 담아도 CONTINUITY 원본 verifier와 FinalitySink를 거쳐 동일한 로컬 service ledger에 효과를 남길 수 있는가?
- 원래 주장: [CONTINUITY §5.1–5.4](https://arxiv.org/html/2609.05269)는 root/field/transition/finality 결속을 주장한다. [Donno §V-B](https://arxiv.org/html/2611.07050)의 악성 Hospital은 *공유 HMAC* 증거를 다시 만들어 원점 승인 상한을 바꿨다. 두 논문의 신뢰 모델은 다르므로 여기서는 **원점 서명·필드 상한이라는 기존 대응의 최소 동작**만 검사한다.
- 호출 대상: 고정 원저자 소스 `third_party/continuity` commit `59cfe60930d247d1890b366ded686c718020a11e`, `experiment.make_scenario/materialise/_verifier`와 `core.ContinuityVerifier.verify_bundle/issue_permit`, `FinalitySink/EffectBroker` 원본 함수를 사용한다. 원저자 파일은 수정하지 않는다.

## 세 입력과 예상·반증 관찰

| 순서 | RootGrant 한도 | 제시 액션 | 예상 verifier/효과 | 반증 관찰 |
|---|---:|---:|---|---|
| N: 정상 | 12000 cents | 12000 cents | allow, 효과 +1 | 거절 또는 효과 0 |
| A: 악성 중간자에 대응하는 범위 확대 | 12000 cents | 900000 cents | deny, 효과 +0, `E_ROOT_FIELD_CONSTRAINT` | allow 및 효과 +1 |
| W: 원점이 **실제로** 넓게 서명한 정책 대조 | 900000 cents | 900000 cents | allow, 효과 +1 | 거절/효과 0 |

동일 `SimulatedWorld`와 `NonceLedger`를 유지해 전후 effect count/상태 digest와 receipt를 기록한다. EUR 9000을 거절하는 것이 올바른 정책 goal 때문인지 확인하기 위해 W를 포함한다. 두 benign grant/요청은 서로 다른 ID로 만들어 idempotency 충돌을 피한다.

## 적응 방법과 해석 제한

원저자 finance scenario의 기본 금액·상한은 이 금액이 아니다. 로컬 harness가 **메모리 안에서만** `experiment._params`, `_root_constraints`, `_malicious_value`의 결과를 EUR 120/9000으로 바꾼 뒤 원저자 `make_scenario`로 서명 객체를 생성한다. A에서 `ROOT_FIELD_CONSTRAINT_BYPASS` fault를 사용한다. 즉 A는 root issuer가 EUR 120 한도를 서명하되 EUR 9000의 action/provenance를 담은 **저자 시나리오 빌더의 변형**이다. 이것은 Donno의 공유키 보유 Hospital·A2A 4자 경로·외부 보험 지급의 재현이 아니다. 공격자가 root signer까지 얻은 경우도 시험하지 않는다. 이 fixture의 승패는 새 MAS Gap의 증명이나 기각으로 일반화하지 않는다.

최소 비용: 기존 `.venv` Python, 결정적 3입력, 모델/API 0, 추가 설치 0. 완료 조건: `commands.md`, `raw.json`, `result.md`에 입력·원본 함수 경로·verifier 이유·sink 결과·전후 state·한계를 기록. 오류가 나면 최대 2회 원인별 수정 후 중단한다.
