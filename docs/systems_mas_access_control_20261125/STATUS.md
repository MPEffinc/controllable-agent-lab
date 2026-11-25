# 상태 — 2026-11-25 UTC

## 현재 검증 질문

시스템 PEP의 자원·호출 단위 권한과 MAS의 원천 승인·위임·작업 범위가 동일 효과에 결속되는가? KubeAegis의 다중 정책 검증, ALPS의 SDK PEP, K04/K15의 서버·효과 PEP 및 기존 교차 계층 방법을 직접 비교한다.

## 기준 감사와 완료

- 기준 브랜치 `exp/20261123-progent-enforcement-usecase`는 지시서 SHA `ce8f62f41d462d62b56352454c6ee151aaa49430`와 일치했고 작업 트리는 깨끗했다. 원격 해당 브랜치 SHA도 같았다. 원격 기본 HEAD `a13622f...`는 다른 참조로, 기준 브랜치에 임의 병합하지 않았다.
- 후속 브랜치 `exp/20261125-systems-mas-access-control` 생성. 기존 R1–R3와 2026-11-24 조사 파일은 수정하지 않는다.
- 기존 STATUS의 `H14 IN_PROGRESS`는 저장된 [H11_context_path 결과](../access_control_empirical_20261124/runs/H11_context_path_20261125/result.md)와 불일치한다. 원본 공개 보조 코드 메서드+shim/결정적 fixture 8 effect row는 완료됐고, 전체 저자 workflow/LLM/원시 41행 인과 재현은 미완료다. 새 표에서는 `H14 narrow implementation observation`과 `broader Need UNVERIFIED`로 분리한다.
- 연구실 [Publications](https://www.cclab.info/publications)와 읽기 전용 [Backlog](https://docs.google.com/spreadsheets/d/1XW5u4aPcshHSyL7Z8cSQZoILxQhWkMRBKb903_aBD3Q/edit)의 메타데이터 및 관련 범위를 확인했다. Backlog `O`는 일정, `S`는 논문 읽기 기록이며 ARES 등의 원문 증거를 대체하지 않는다.
- 연구실 공식 저장소 ALPS SHA `ace0fd2cabdc100bf5491bad3389e47bce6a37f9`, KubeAegis SHA `79845cbcca83f12cab5cc7f6097a68dc2cb1fc5e`, KubeTeus SHA `d484afbfca924e68f5436a425ea0893c5346b7c0`를 격리 checkout했다. ALPS Apache-2.0, 다른 두 저장소의 최상위 LICENSE 미발견.
- [H1–H14 네 축 재평가표](hypothesis_reassessment.md) 초안을 작성했다. H14 결과 존재와 전체 LLM workflow 미검증을 분리했다. [연구실 시스템 대조](systems_comparison.md)에는 KubeAegis §VII-C의 의미 충돌, ALPS 원본 verifier, KubeTeus/Bambda 원문, K04/K15/Agent libOS/다중-target DSL의 강한 반박을 기록했다. [ARES 원문](https://cclab.info/papers/kor/2026_shin_cisc-s.pdf) §III–IV의 origin caller/ARP/인라인 차단은 H15 직접 반박으로 추가했다. [POLARIS 정식 공개 초록](https://link.springer.com/article/10.1186/s13677-026-01014-0)의 LSM-BPF·범위별 수치를 확인했고 전문·코드는 보류다.
- [ALPS 공식 Python verifier 12-test 실행](runs/A3_alps_runtime_20261125/result.md): exit 0, 결정 전용. `context`는 decision 키가 아니라 violation 기록에만 사용. 실제 클라우드/Agent effect는 미시험.
- [상위 3개 반증 후보](research_candidates.md)를 H15 공유 worker, H13/H14 event·출처, H16 교차 계층 충돌로 선정했다. B1/B2 결과로 [새 H15–H17](new_hypotheses.md)을 재구성했다. H15의 고정 메커니즘 Need는 기각. H16은 KubeAegis 구현 한정 의미 충돌 Gap이지만 [SafeConfig 2012](https://static.googleusercontent.com/media/research.google.com/en/us/pubs/archive/40606.pdf)가 교차 계층 모델 검사를 이미 구현했다. H17은 MAP-Graph 공개 보조 artifact의 평가 귀속 Gap이며 [AgentEval](https://arxiv.org/abs/2610.21177)/[SABENCH](https://arxiv.org/abs/2610.34167)가 강한 평가 대안. 독립 Need는 `UNVERIFIED`.
- `local/progent-vm/.env`의 API key는 값 출력 없이 실제 모델 endpoint로 확인했다. [B1 실제 LLM/로컬 효과](runs/B1_shared_worker_llm_20261125/result.md)는 12 calls, 비용 상한 USD 0.0007984. A→B 요청에서 ALPS-only는 합성 B row를 변경했고, task/service PEP는 차단하며 정상 A/B는 보존했다. 비신뢰 row instruction은 이번 모델 실행에서 무시됐다. 이 고정 구성의 새 메커니즘 필요 가설은 기각.
- [B2 실제 LLM+MAP-Graph 원본 메서드](runs/B2_mapgraph_llm_20261125/result.md)는 2 calls, USD 0.0003232. **누적 USD 0.0011216 / 5**, 외부 서비스 effect `NOT_RUN`. 모델은 tool call이 아니라 JSON 텍스트를 반환했다. 초기 tool-call 해석을 수정해 원저자 parser를 저장 응답에 API 없이 재생하니 둘 다 task의 `expected_action` fallback으로 gate에 들어갔고, revoked source는 정확 edge adapter에서 BLOCK, 원본 support에서는 ALLOW였다. 일반 거부 문장도 fallback simulated ALLOW인 반례 확인. 이는 저자 41건 원인이나 실제 provider effect가 아니다. [A2b 공개 CSV 감사](runs/A2b_mapgraph_result_audit_20261125/result.md)는 41/450 label을 확인했지만 원시 출력이 공개 archive에서 빠져 fallback 비율은 `NOT_ESTABLISHED`로 닫았다.
- [B3 ARES ARP 관계식 독립 fixture](runs/B3_ares_reachability_fixture_20261125/result.md)는 API 비용 0, SQLite 실제 전후 상태 6행을 남겼다. 가능 경로만으로 preflight하면 정상 branch 0/1·금지 효과 0; origin-aware effect PEP는 정상 1/1·금지 효과 0. ARES 원저자 LAM·4개 cloud 구현 재현이 아니며 그 정상성은 `UNVERIFIED`.
- **H19 정책 목표 감시:** ARES의 사용자 직접 DB Deny를 모든 대리 DB effect 금지로 해석하려면 별도 승인 의도 명세가 필요하다. [AWS Lambda 역할 문서](https://docs.aws.amazon.com/lambda/latest/dg/concepts-basics.html)는 함수가 별도 execution role로 실행됨을 확인한다. [RFC 8693](https://www.rfc-editor.org/rfc/rfc8693.html)/[RFC 9396](https://www.rfc-editor.org/rfc/rfc9396.html)과 K04/K15는 위임/세부 승인 대안이므로 새 Need는 `UNVERIFIED`.

## 다음 실행

1. H17: [A2b](runs/A2b_mapgraph_result_audit_20261125/result.md)에서 공개 archive의 한계선을 확인했다. 원시 trace가 별도 공개될 때 41건의 model response/fallback/action/effect를 paired 재채점한다. 현 자료의 `executed`는 실제 서비스 효과가 아니다.
2. H13/H14: 실제 Agent의 자연어 event·tool-output lineage 자동 수집을 같은 강한 service PEP/정상 업무에 비교한다. B1/B2의 고정 합성 사례를 일반화하지 않는다.
3. [B3](runs/B3_ares_reachability_fixture_20261125/result.md)의 실제 저자 LAM 여부는 공식 코드/세부 evaluation을 확보해야 검증 가능하다. H19의 승인된 대리 실행 oracle를 K04/K15/RFC와 대조한다. POLARIS 전문·KubeAegis cross-policy 대안, A1 표의 원문 링크를 보강한다.

Git 체크포인트: 현재 브랜치 `exp/20261125-systems-mas-access-control`. 최신 commit은 `git log -1 --oneline`, 원격 동기화는 `git ls-remote origin refs/heads/exp/20261125-systems-mas-access-control`로 확인한다. 이 세션의 각 단계는 실행 전에 사전등록 commit, 실행 뒤 결과 commit을 별도로 push했다. 이전 자료/원저자 clone은 변경하지 않았다.
