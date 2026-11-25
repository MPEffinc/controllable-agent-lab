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

기존 공식 코드 checkout은 `third_party/`에 위치한다. 새 연구실 코드 checkout은 `third_party/LAB_*`에 고정하고 commit SHA를 [source_registry.md](source_registry.md)에 기록한다. `third_party` checkout과 환경 파일은 연구 결과가 아니다.
