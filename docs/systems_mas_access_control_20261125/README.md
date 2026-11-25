# Systems & MAS Access Control — 후속 검증

기준일: 2026-11-25 UTC. 기존 `docs/access_control_empirical_20261124/`와 R1–R3를 보존하며, 별도 브랜치 `exp/20261125-systems-mas-access-control`에서 재평가한다. 이 디렉터리의 판정은 현재 확인한 범위에만 적용한다.

최신 가설 판정 및 Track 우선순위는 [H1–H19 전수 재감사](phase1_full_reassessment.md)를 먼저 읽는다. 이전 후보 순서는 당시 실행 기록으로 보존했다.

## 재개 순서

1. [STATUS.md](STATUS.md)에서 마지막 완료 단계와 Git SHA를 확인한다.
2. [QUEUE.md](QUEUE.md)의 첫 미완료 질문에 대해 기존 근거와 사전 예측을 읽는다.
3. 실행 전 `runs/<run-id>/prereg.md`를 저장하고, 원본 코드·독립 adapter·모의 서비스를 구별한다.
4. 원시 결과는 새 Run ID에만 저장한다. 키 값, 실제 서비스 데이터, 비용이 큰 호출은 원장에 넣지 않는다.
5. 검증 뒤 [hypothesis_reassessment.md](hypothesis_reassessment.md), [systems_comparison.md](systems_comparison.md), [research_need_assessment.md](research_need_assessment.md)를 갱신한다.

이번 후속 결과는 [새 가설 H15–H19](new_hypotheses.md) 및 [B1 실제 서비스 모의](runs/B1_shared_worker_llm_20261125/result.md), [B2 실제 모델·원저자 parser](runs/B2_mapgraph_llm_20261125/result.md), [B3 독립 ARES 관계식 fixture](runs/B3_ares_reachability_fixture_20261125/result.md)에 있다. B2는 모델이 tool call을 하지 않았고 저자 workflow는 simulated action을 기록하므로 두 뜻을 분리해 읽는다.

2026-11-25 Phase 2 실행은 [K06 AutoCedar full author 실패](runs/C1c_autocedar_case011_20261125/result.md), [독립 target과 원본 verifier 대조](runs/C2_target_semantics_20261125/result.md), [현행 Agent libOS 원저자 테스트](runs/A5_agent_libos_manifest_20261125/result.md), [모델 A→B write-back](runs/D1_live_writeback_20261125/result.md), [기존 restricted-context 대안](runs/D2_restricted_regeneration_20261125/result.md), [owner event 48칸 추출](runs/D3_owner_event_scope_20261125/result.md), [AutoCedar 완료·승인 소비자 경계](runs/C3_autocedar_release_gate_20261125/result.md)에 각각 원시 로그·코드·사전등록과 함께 있다. [H20 조건부 승인 경계](h20_release_contract.md)는 기존 승인 필드 gate로 해결되는 범위와 남은 검증 질문을 분리한다.

후속 C4–C10b는 공식 AutoCedar gold에 대한 **독립 전체 정책 reviewer**와 Reparo식 **독립 통제 oracle**이다. 원본 atom별 reviewer 또는 Reparo 원본 실행으로 쓰지 않는다. [H21](h21_target_review_semantics.md)에 거짓 거부, 정형 동치 정규화, Cedar 계층 의미와 강한 기존 대안을 묶었다. [C11](runs/C11_unscoped_action_20261125/result.md)은 연구자 확장 schema의 unscoped action을 **원본 AutoCedar verifier와 Cedar CLI**로 실행한 증거이며 [H22](h22_unscoped_action_closure.md)에 범위·기각 조건을 기록했다. 최초 기술적 실패와 집계 오류도 해당 run의 원시 파일·별도 정정에 보존했다.

실행 코드는 각 run의 `run.py`(C1–C1c는 `run_author.py`)다. raw 파일이 있으면 중복·덮어쓰기를 거부하므로 재실행은 **새 Run ID 복제 후** 사전등록을 갱신한다. A5의 `env/`는 `.gitignore`로 제외된 `uv.lock` 고정 환경이다. D1–D3는 키를 `local/progent-vm/.env`에서 메모리로만 읽으며 사용자 승인 $5 상한과 현재 누적액은 `STATUS.md`에 있다. C2/C3는 API 비용 0이다.

기존 공식 코드 checkout은 `third_party/`에 위치한다. 새 연구실 코드 checkout은 `third_party/LAB_*`에 고정하고 commit SHA를 [source_registry.md](source_registry.md)에 기록한다. `third_party` checkout과 환경 파일은 연구 결과가 아니다.
