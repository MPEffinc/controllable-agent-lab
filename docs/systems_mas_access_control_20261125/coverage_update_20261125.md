# Phase 2 coverage 갱신 — 생성 / 정책 정확성 / 집행

2026-11-25 UTC. 이 표는 새 실행으로 **추가 확인된 범위**만 다룬다. K01–K15 원문 전체의 10개 필드는 기존 [coverage matrix](../access_control_empirical_20261124/coverage_matrix.md)와 [H1–H19 재감사](phase1_full_reassessment.md)에 있다. `UNKNOWN`은 0이 아니고, 로컬 adapter의 effect는 저자 시스템의 실제 provider effect가 아니다.

| 연구·run | 정책 생성/표현 | 정책 정확성 검사 | 집행 경로/실제 효과 | 평가 위협·정상 분모 / 미확인 |
|---|---|---|---|---|
| K06 AutoCedar [C1–C1c](runs/C1c_autocedar_case011_20261125/result.md) | 공식 case-011 자연어→target/후보 full author 시도; 후보 전 종료 | Stage1 schema까지, 최종 형식/의미 검사 미도달 | 없음 | API 호환성·출력 형식 실패; 보안 ASR/정상률 `NOT_ESTABLISHED` |
| K06 [C2](runs/C2_target_semantics_20261125/result.md) | 연구자 작성 VPN 누락 후보와 target 두 개 | 원본 `verify`: 자기 target 2/2 pass, gold target 포함 반례 1 | 독립 Cedar CLI+모의 PR: 정상 2 policy allow, off-VPN gold deny/오류 allow | 1 source case×2 target×3 request. **원저자 생성 오류 재현 아님** |
| K06 [C3](runs/C3_autocedar_release_gate_20261125/result.md) | 저자 공개 manual-AITL CyberChair 후보 | 원본 42/42 pass, human semantic approval false | 독립 소비자 완료만 검사 시 SQLite +1, 승인 gate 시 0 | 1 정상 요청×2 소비자, 외부 배포 `NOT_RUN`. 승인 false는 의미 오류 판정 아님 |
| 현행 Agent libOS [A5](runs/A5_agent_libos_manifest_20261125/result.md) | trusted host가 manifest 작성, child attenuation | 원저자 단위 테스트 4/4: hash·parent ceiling·effect ceiling | runtime decision/SQLite 영속화. 외부 provider effect `DECISION_ONLY` | 현재 v1.6.0, 논문 평가판 동일성 `UNKNOWN` |
| M4 guard + 독립 A→B [D1](runs/D1_live_writeback_20261125/result.md) | 실제 모델 journal, claimed support 비신뢰 | 원본 status guard는 revoked `r1` 제외, new `j1` 유지 | 독립 local effect: conservative lineage 정상 0/1, current PEP 정상 1/1·비인가 0 | 1 owner update, 2 B 요청, 3 model calls. M4 원저자 Graphiti 실행 아님 |
| Permissive IFC 아이디어 [D2](runs/D2_restricted_regeneration_20261125/result.md) | r1 제외 후 재생성된 journal | code-owned ancestry `r2`만, 모델 support claim 불필요 | 독립 local effect: 정상 1/1·비인가 0 | 원문 아이디어 독립 적용, 원저자 코드 재현 아님. r2 정확 식별 전제 |
| 독립 owner event extractor [D3](runs/D3_owner_event_scope_20261125/result.md) | 모델이 6 history→48 policy cells | 사전 gold 48/48 일치 | SQLite 모의 service: 정상 48/48·비인가 0/48 | 명료한 합성 history, 공격/긴 이력/실서비스 `NOT_ESTABLISHED` |

**Coverage 결론:** Policy language가 표현한 범위(Cedar/manifest), 실제 PEP를 지나는 범위(원본 verifier·runtime decision vs 독립 SQLite gate), 평가에서 시험한 요청 수, 형식 도구가 검사한 포함/ceiling 성질을 서로 바꾸어 말하지 않는다. H20의 승인 결속은 기존 필드가 있어도 소비자가 반드시 검사해야 한다는 **인터페이스 조건**이다.
