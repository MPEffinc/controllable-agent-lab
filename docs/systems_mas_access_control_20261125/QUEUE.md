# 검증 큐

순서는 증거 확보 비용과 의존 관계다. Gap 중요도 순위가 아니다.

| ID | 질문·사전 예측 | 완료 기준 | 상태 |
|---|---|---|---|
| A1 | H1–H14의 안전성·적용성·정확성/정상성·시스템 기여를 각각 다시 판정. 좁은 구현 실패와 신규 Need를 분리할 것으로 예상 | 각 가설에 최초 근거, 직접 관측, 최강 반박, 미검증 조건, 기각 조건을 기입 | [초안 완료](hypothesis_reassessment.md), 원문 행별 재검증 진행 |
| A2 | K01–K15 밖의 강한 해결책이 H13/H14와 시스템 계층 문제를 이미 해결하는가 | 원문 절·코드·평가 경계와 같은 문제 여부 기록 | Agent libOS/DSL/AuthBench/GrassHopper 1차 대조, 추가 검증 진행 |
| A3 | 연구실 ALPS/KubeAegis/KubeTeus/Bambda/POLARIS/ARES의 실제 PEP·정책·한계를 MAS 연구와 비교 | 원문·공식 코드 여부·제약을 source registry 및 비교표에 기입 | ALPS 공식 12 test·주요 원문 대조 완료, POLARIS/ARES 세부 보류 |
| A4 | 안전·정상·비용을 같은 입력에서 측정할 후보가 무엇인가 | RQ/위협/최강 대안/성공·실패 기준을 가진 상위 2–3개 선택 | [3개 조건부 선정](research_candidates.md) |
| B1 | 실제 LLM이 공유 worker의 다른 task 권한 아래 어떤 policy 초안·tool proposal을 내는가 | [사전등록](runs/B1_shared_worker_llm_20261125/prereg.md), 원시 요청/응답·토큰·비용, 정상/비인가·강한 PEP, 로컬 서비스 전후 상태 | [12 calls·4case×3arm 완료](runs/B1_shared_worker_llm_20261125/result.md); 고정 구성 신규 메커니즘 Need 기각 |
| B2 | H14 원본 provenance 소실 경로에서 **같은 visible text**의 revoked/current 출처가 실제 LLM proposal→gate→outbox에 어떤 차이를 주는가 | [사전등록](runs/B2_mapgraph_llm_20261125/prereg.md), 원본 메서드·model raw·같은 support의 4arm·정상/비인가 effect | 실행 대기 |

각 실험의 실패가 기존 방법으로 해결되면 그 조건의 Need를 기각한다. 저자 코드와 독립 adapter를 혼동하지 않는다.
