# Research Gap / Need / Contribution 현재 판정 — 2026-11-25

후속 [H1–H19 전수 재감사](phase1_full_reassessment.md)에서 이전 H15/B1·H18/B3 중심 순서를 다시 평가했다. 현재 정보 가치 순서는 **정책 target 의미 정확성(C) → 자연어 event/lineage 수집(D) → 원본 위임 대안 적용(A) → 교차 계층 활성 정책(B)**이다. 이는 실증 순서이며 독립 Need 확정이 아니다.

## 확인된 좁은 Gap

1. **H14 공개 MAP-Graph 보조 구현:** `tool_output.derived_from`가 observed memory·agent write의 ancestry에서 빠지며 원문 tool text는 prompt에 들어간다. [원본 메서드+결정적 로컬 outbox](../access_control_empirical_20261124/runs/H11_context_path_20261125/result.md)는 부정확 계보에서 비인가 모의 effect 1, 정확 edge 또는 current service PEP에서 0/정상+1을 보였다. 저자 41건의 원인은 미확정.
2. **H17 같은 artifact의 평가 귀속:** [실제 모델 응답과 원저자 parser 재생](runs/B2_mapgraph_llm_20261125/result.md)에서 실제 JSON 제안이 parser에 안 맞으면 task oracle의 `expected_action`이 대신 gate로 들어간다. 일반 자연어 거부도 동일 fallback으로 simulated `ALLOW`가 가능함을 source-method control에서 확인했다. 실제 provider effect는 `NOT_RUN`. [공개 결과 감사](runs/A2b_mapgraph_result_audit_20261125/result.md)로 Exp-5의 41/450 결정 label은 확인했으나 원시 출력이 제외되어 그 41건에 이 경로가 얼마나 적용됐는지는 알 수 없다.
3. **H16 KubeAegis:** 논문 §VII-C가 network/system semantic conflict를 직접 한계로 밝히고 공개 `KapValidator`는 자원 존재·사전조건만 호출한다. 이 구현의 의미 충돌 검출 부족은 확인됐으나, 오래된 [통합 network+system 모델 검사](https://static.googleusercontent.com/media/research.google.com/en/us/pubs/archive/40606.pdf)가 있어 원리 부재 주장은 기각한다.
4. 기존 H1/H8/H10/H11/H12의 좁은 평가·구현 경계는 [원장](../access_control_empirical_20261124/hypotheses.md)대로 유지하되, 이번 후속 연구가 신규 Need로 승격하지 않는다.

## 강한 반박과 이번 실제 LLM 결과

[B1](runs/B1_shared_worker_llm_20261125/result.md)의 권한 A 사용자/B 요청은 원본 ALPS union allowlist 아래 로컬 비인가 row 변경을 만들었다. 같은 모델 proposal에 **독립** task grant PEP 또는 service current-grant PEP를 더하면 비인가 0, 정상 A/B 3case는 유지됐다. 그 고정 조건의 새 보안 메커니즘 필요성은 `REJECTED_HYPOTHESIS`. [Agent libOS 현행 TaskAuthorityManifest](https://github.com/yingqi-z20/Agent-libOS), [PAuth](https://arxiv.org/abs/2603.17170), [CONTINUITY](https://arxiv.org/abs/2609.05269)는 직접적인 반박 연구이며, B1의 독립 adapter가 그 원저자 성능을 재현했다는 뜻은 아니다.

[B2](runs/B2_mapgraph_llm_20261125/result.md)의 출처 소실 문제도 정확 code-owned lineage 또는 current service PEP가 **source-method decision**에서 차단할 수 있었다. 실제 모델은 외부 tool을 호출하지 않았고 공개 workflow 자체도 `simulated_no_side_effect`였다. 새 메커니즘 Need는 `UNVERIFIED`.

[C1–C1c AutoCedar 원본/호환성 실행](runs/C1c_autocedar_case011_20261125/result.md)은 API 필드·strict schema·필수 JSON 필드 오류로 후보 생성 전에 끝났다. 논문이 보고한 gold와 다른 19 plan이나 사용자 의도 검토의 공백을 재현한 결과가 아니다. 현재 C1은 형식·환경 재현 한계만 입증한다. [A5 Agent libOS v1.6.0 원저자 테스트](runs/A5_agent_libos_manifest_20261125/result.md)는 host가 정확한 manifest를 준 경우 자식 권한·effect ceiling을 좁히는 대안을 4/4로 확인했다. 외부 provider effect와 자연어→manifest 정확성은 시험하지 않았다.

[C2](runs/C2_target_semantics_20261125/result.md)는 case-011 gold에서 VPN 조건만 제거한 **연구자 후보**를 원본 verifier에 넣었다. 후보 자체를 target으로 주면 2/2 pass, 독립 gold target이면 `onVpn=false` 반례로 fail; 로컬 PR 효과도 off-VPN에서 gold 0/오류 후보 1, 정상 양쪽 1이었다. 이 경우 기존 verifier+정확한 독립 target이 오류를 직접 해결하므로 새 정형 메커니즘 Gap은 기각한다. 남는 좁은 평가 질문은 정확한 target의 획득·인간 검토 성능과 비용이다.

[ARES 원문 §III](https://cclab.info/papers/kor/2026_shin_cisc-s.pdf)는 최초 caller IAM Deny·함수 호출 관계·자원 도달성을 결합해 함수 실행 전 차단하고 caller context를 후속 함수에 전파한다. 따라서 H15에서 origin 권위 전파 기술이 없다는 주장은 성립하지 않는다. 명시 ARP 관계가 invocation별 branch의 실제 효과를 판별할 수 있는지, 정상 branch를 과차단하는지는 [B3 독립 fixture](runs/B3_ares_reachability_fixture_20261125/result.md)로 좁혀 봤다. 원본 LAM의 실제 행위는 공개 코드 없이 `UNVERIFIED`다.
[B3 결과](runs/B3_ares_reachability_fixture_20261125/result.md)는 **관계식만 적용한 경우** 정상 branch 과차단 1/1을 확인했다. 별도 origin-aware effect PEP는 정상 1/1과 금지 DB 효과 0을 함께 달성했다. ARES 원저자 구현의 정상성 실패나 새 메커니즘 Need를 이 fixture에서 도출하지 않는다.

**H19 감시 질문:** [ARES Fig.1/§III.2](https://cclab.info/papers/kor/2026_shin_cisc-s.pdf)는 사용자의 직접 DB Deny와 함수 호출 허용을 합쳐 DB로 도달하는 경로를 우회라고 정의한다. [AWS 실행 역할](https://docs.aws.amazon.com/lambda/latest/dg/concepts-basics.html)은 함수가 별도 권한 주체임을 분명히 한다. 따라서 `사용자 직접 DB write 불허`가 `해당 함수를 통한 승인된 대리 DB write도 불허`를 뜻하는지 **정책 의도 oracle**이 필요하다. [RFC 8693](https://www.rfc-editor.org/rfc/rfc8693.html)의 actor/subject 위임, [RFC 9396](https://www.rfc-editor.org/rfc/rfc9396.html)의 세부 승인, K04/K15가 강한 기존 해법이다. ARES가 애초 모든 간접 write 금지를 보안 요구로 둔다면 H19는 그 논문의 범위 밖이다. 현재 `UNVERIFIED`, 신규 Need 아님.

## 아직 필요한 검증과 기각 조건

| 후보 | 필요 증거 | 기각 조건 |
|---|---|---|
| H13/H14 실제 자연어 event·출처 edge 수집 | 원본 또는 별도 실제 MAS agent의 model→tool→memory→provider trace, 정상/비인가 입력과 강한 lineage/PEP 대조 | 기존 code-owned edge/current PEP 조합이 같은 workload에서 적정 비용·정상성을 달성 |
| H16 동적 교차 계층 의미 보존 | 실제 KAP/agent policy→native active policy와 normal/unauthorized effect, old BDD/CTL·DSL/SMT 대조 | 기존 검증/컴파일로 충돌을 찾고 배포/효과까지 보존 |
| H17 평가 지표 귀속 | author 41 Exp-5의 원시 model output·fallback 여부·action/effect trace 또는 새 공개 benchmark의 paired 재채점 | explicit action/실제 effect oracle가 같은 안전·정상 판정을 내고 비용이 허용됨 |
| H1/C2 승인 의미 대조 | K06 고정 case의 정책 target/후보와 독립 gold 요청 oracle·정상 서비스 효과. full author는 C1–C1c에서 후보 생성 실패 | 원본 검증기+사람/독립 oracle가 같은 입력에서 정확 정책과 정상 완료를 허용 비용으로 달성 |

**현재 독립 Research Need: `UNVERIFIED`.** `GAP_SUPPORTED`는 해당 논문·코드·평가 조건의 구체 한계를 뜻한다. 이번 원시 결과만으로 MAS 전체의 신규 취약성이나 보편적 해결책 부재를 주장하지 않는다. 새로운 contribution 가능성은 **동적 task authority의 여러 PEP 결속 정확성/비용**, **출처/행동/효과를 구분하는 재현 가능한 평가**, **정책 컴파일과 활성 상태의 정상·안전 동시 검증**에 있으나 기존 최강 방법의 동일 입력 비교가 선행돼야 한다.
