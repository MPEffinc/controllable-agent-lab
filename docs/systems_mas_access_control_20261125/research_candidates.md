# Phase A-4: 반증 가능한 상위 후보 (2026-11-25)

새로운 메커니즘 필요를 가정하지 않고, 동일 입력에서 safety·normal completion·cost를 측정할 수 있는 순서로 선정했다. K01–K15 [기존 coverage](../access_control_empirical_20261124/coverage_matrix.md)와 [H1–H14 재평가](hypothesis_reassessment.md)를 바탕으로 하며, 각 후보의 `Gap`은 현재 확정 전이다.

| 순위 | RQ / 연결 | 위협·신뢰 모델 | 최강 대안 | 성공/기각 기준 | 최소 비용 |
|---|---|---|---|---|---|
| 1: H15 | **공유 worker의 정적 함수/OS allowlist와 task별 origin grant가 다를 때, 실제 LLM agent의 요청이 어떤 경계에서 효과로 이어지는가?** H5/H7/H8/H10 확장. | 공격자는 비신뢰 tool output과 자기 task 입력의 일부만 제어; worker credential/allowlist, 승인 grant, 서비스 PEP는 신뢰. 두 task가 한 worker의 허용 자원 합집합을 공유 | K04 PAuth signed task slice, K15 finality permit, Agent libOS process capability, task별 verifier, service current-state PEP | 원본 ALPS 단독 누출은 **적용 경계 관측**일 뿐. 강한 대안이 정상 task를 유지하며 비인가 effect=0이면 신규 메커니즘 Need 기각. 자동 정책/주체 mapping의 실제 오류·정상성/비용 잔여가 반복 관측되면 좁은 Need 검토 | ALPS 공식 verifier+로컬 SQLite/HTTP+gpt-4.1-mini, 목표 <$0.20 |
| 2: H13/H14 | **자연어 승인 변경과 비신뢰 tool output의 실제 파생 출처가 LLM·memory·effect까지 자동 보존되는가?** | 권한자는 자연어 scope 변경, 공격자는 tool content, source IDs는 signed/trusted ledger가 검증; 모델은 신뢰하지 않음 | code-owned event/lineage, MAP-Graph full support, WTB/CONTINUITY service PEP, human readback | 원본 H14 path 재확인+실제 모델 action+서비스 effect에서 complete support/current PEP가 정상 완료를 보존하면 새 메커니즘 Need 기각. 자동 edge 포착이 정상 합법 파생까지 과거부하면 정확성·utility 문제로 좁혀 재검토 | 기존 H14 source harness+모델 4–8회, 목표 <$0.40 |
| 3: H16 | **동적 task 정책을 tool/network/OS/service 정책으로 내릴 때 각 정책의 의미 충돌·활성 버전이 정상 업무와 안전성에 미치는 영향은 무엇인가?** KubeAegis §VII-C와 H7/H8 연결 | 관리자 root policy 신뢰, 생성기·adapter는 버그 가능, 공격자는 task/tool data만; complete PEP와 리소스 매핑 필요 | KubeAegis validation+cross-layer DSL compiler, GrassHopper network/VM, Cedar/SMT composition, effective-policy prover | 단순 allow/deny 충돌은 알려진 현상. 기존 compiler/prover가 같은 task·배포 상태에서 충돌을 검출하고 정상+안전 보존하면 새 Need 기각. 실효과·정상성의 동일 입력 평가가 부재하면 평가 Gap 후보 | 현 단계 원문/소스 감사·작은 local policy matrix, LLM 이후 필요 시 |

**우선순위의 이유:** H15는 바로 공식 런타임 verifier와 최종 effect를 연결해 기존 강한 대안을 시험할 수 있다. H13/H14는 기존 source-method 관측에 실제 LLM을 추가해야 한다. H16은 KubeAegis가 의미 충돌을 직접 인정하지만 선행 컴파일/검증 연구가 강하므로 더 엄격한 문헌·배포 조건 확인이 선행된다.

`H15`와 `H16`은 새 시스템/적용성 가설 ID이며 `GAP_SUPPORTED`가 아니다. 최종 기여는 아직 `UNVERIFIED`.
