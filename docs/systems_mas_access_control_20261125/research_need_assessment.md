# Research Gap / Need / Contribution 현재 판정 — 2026-11-25

## 확인된 좁은 Gap

1. **H14 공개 MAP-Graph 보조 구현:** `tool_output.derived_from`가 observed memory·agent write의 ancestry에서 빠지며 원문 tool text는 prompt에 들어간다. [원본 메서드+결정적 로컬 outbox](../access_control_empirical_20261124/runs/H11_context_path_20261125/result.md)는 부정확 계보에서 비인가 모의 effect 1, 정확 edge 또는 current service PEP에서 0/정상+1을 보였다. 저자 41건의 원인은 미확정.
2. **H17 같은 artifact의 평가 귀속:** [실제 모델 응답과 원저자 parser 재생](runs/B2_mapgraph_llm_20261125/result.md)에서 실제 JSON 제안이 parser에 안 맞으면 task oracle의 `expected_action`이 대신 gate로 들어간다. 일반 자연어 거부도 동일 fallback으로 simulated `ALLOW`가 가능함을 source-method control에서 확인했다. 실제 provider effect는 `NOT_RUN`. [공개 결과 감사](runs/A2b_mapgraph_result_audit_20261125/result.md)로 Exp-5의 41/450 결정 label은 확인했으나 원시 출력이 제외되어 그 41건에 이 경로가 얼마나 적용됐는지는 알 수 없다.
3. **H16 KubeAegis:** 논문 §VII-C가 network/system semantic conflict를 직접 한계로 밝히고 공개 `KapValidator`는 자원 존재·사전조건만 호출한다. 이 구현의 의미 충돌 검출 부족은 확인됐으나, 오래된 [통합 network+system 모델 검사](https://static.googleusercontent.com/media/research.google.com/en/us/pubs/archive/40606.pdf)가 있어 원리 부재 주장은 기각한다.
4. 기존 H1/H8/H10/H11/H12의 좁은 평가·구현 경계는 [원장](../access_control_empirical_20261124/hypotheses.md)대로 유지하되, 이번 후속 연구가 신규 Need로 승격하지 않는다.

## 강한 반박과 이번 실제 LLM 결과

[B1](runs/B1_shared_worker_llm_20261125/result.md)의 권한 A 사용자/B 요청은 원본 ALPS union allowlist 아래 로컬 비인가 row 변경을 만들었다. 같은 모델 proposal에 **독립** task grant PEP 또는 service current-grant PEP를 더하면 비인가 0, 정상 A/B 3case는 유지됐다. 그 고정 조건의 새 보안 메커니즘 필요성은 `REJECTED_HYPOTHESIS`. [Agent libOS 현행 TaskAuthorityManifest](https://github.com/yingqi-z20/Agent-libOS), [PAuth](https://arxiv.org/abs/2603.17170), [CONTINUITY](https://arxiv.org/abs/2609.05269)는 직접적인 반박 연구이며, B1의 독립 adapter가 그 원저자 성능을 재현했다는 뜻은 아니다.

[B2](runs/B2_mapgraph_llm_20261125/result.md)의 출처 소실 문제도 정확 code-owned lineage 또는 current service PEP가 **source-method decision**에서 차단할 수 있었다. 실제 모델은 외부 tool을 호출하지 않았고 공개 workflow 자체도 `simulated_no_side_effect`였다. 새 메커니즘 Need는 `UNVERIFIED`.

[ARES 원문 §III](https://cclab.info/papers/kor/2026_shin_cisc-s.pdf)는 최초 caller IAM Deny·함수 호출 관계·자원 도달성을 결합해 함수 실행 전 차단하고 caller context를 후속 함수에 전파한다. 따라서 H15에서 origin 권위 전파 기술이 없다는 주장은 성립하지 않는다. 명시 ARP 관계가 invocation별 branch의 실제 효과를 판별할 수 있는지, 정상 branch를 과차단하는지는 [B3 독립 fixture](runs/B3_ares_reachability_fixture_20261125/result.md)로 좁혀 봤다. 원본 LAM의 실제 행위는 공개 코드 없이 `UNVERIFIED`다.
[B3 결과](runs/B3_ares_reachability_fixture_20261125/result.md)는 **관계식만 적용한 경우** 정상 branch 과차단 1/1을 확인했다. 별도 origin-aware effect PEP는 정상 1/1과 금지 DB 효과 0을 함께 달성했다. ARES 원저자 구현의 정상성 실패나 새 메커니즘 Need를 이 fixture에서 도출하지 않는다.

## 아직 필요한 검증과 기각 조건

| 후보 | 필요 증거 | 기각 조건 |
|---|---|---|
| H13/H14 실제 자연어 event·출처 edge 수집 | 원본 또는 별도 실제 MAS agent의 model→tool→memory→provider trace, 정상/비인가 입력과 강한 lineage/PEP 대조 | 기존 code-owned edge/current PEP 조합이 같은 workload에서 적정 비용·정상성을 달성 |
| H16 동적 교차 계층 의미 보존 | 실제 KAP/agent policy→native active policy와 normal/unauthorized effect, old BDD/CTL·DSL/SMT 대조 | 기존 검증/컴파일로 충돌을 찾고 배포/효과까지 보존 |
| H17 평가 지표 귀속 | author 41 Exp-5의 원시 model output·fallback 여부·action/effect trace 또는 새 공개 benchmark의 paired 재채점 | explicit action/실제 effect oracle가 같은 안전·정상 판정을 내고 비용이 허용됨 |

**현재 독립 Research Need: `UNVERIFIED`.** `GAP_SUPPORTED`는 해당 논문·코드·평가 조건의 구체 한계를 뜻한다. 이번 원시 결과만으로 MAS 전체의 신규 취약성이나 보편적 해결책 부재를 주장하지 않는다. 새로운 contribution 가능성은 **동적 task authority의 여러 PEP 결속 정확성/비용**, **출처/행동/효과를 구분하는 재현 가능한 평가**, **정책 컴파일과 활성 상태의 정상·안전 동시 검증**에 있으나 기존 최강 방법의 동일 입력 비교가 선행돼야 한다.
