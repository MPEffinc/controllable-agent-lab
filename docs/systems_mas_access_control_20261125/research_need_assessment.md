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

[D1 실제 모델 A→B write-back](runs/D1_live_writeback_20261125/result.md)은 정확한 최신 journal을 생성했다. 보수적 code-owned 전체 입력 ancestry는 폐기 `r1`까지 묶어 정상 2명 요청을 1/1 과차단했지만, 현재 승인에 대한 로컬 service PEP는 정상 1/1·비인가 0을 달성했다. 따라서 **fine-grained support의 자동 획득·정상성 비용은 감시할 만한 좁은 조건**이며, 이 고정 입력의 새 effect admission 메커니즘 Need는 기각한다. 모델의 `support_ids`는 자기 보고로 신뢰 근거가 아니며 WTB 원본 실행도 아니다.

[D2](runs/D2_restricted_regeneration_20261125/result.md)에서 [Permissive IFC의 제한 context 재생성](https://arxiv.org/html/2410.03055v2)이라는 기존 직접 대안을 D1 동일 입력에 적용했다. A가 폐기 `r1`을 받지 않게 하고 새 journal을 만들자 code-owned 출처가 `r2`만 남아 정상 1/1·비인가 0이었다. **D1 과차단의 새로운 메커니즘 Gap 가설은 기각**한다. [LMLineage](https://arxiv.org/html/2611.22511v1)는 sentence-span attribution을 하지만 §6에서 보안 적용은 범위 밖이라 명시한다. [NeuroTaint](https://arxiv.org/html/2604.23374v1)는 실행 후 source-to-sink audit이며 [A³Bench](https://arxiv.org/html/2609.33676v1)는 action attribution 평가를 제공한다. 이들은 출처 관측의 직접 대안/평가 기준이지 D2의 online 승인 집행과 동일 보장은 아니다. 남는 질문은 제한할 입력을 고르기 위한 신뢰된 owner event·scope의 자동 획득이며 `UNVERIFIED`다.

[D3](runs/D3_owner_event_scope_20261125/result.md)에서는 명료한 여섯 합성 owner history의 scope/철회/시점 48칸을 실제 모델이 모두 정확히 구조화했고, 로컬 service 효과도 정상 48/48·비인가 0/48이었다. D2의 'event를 골라야 한다'는 전제를 **이 조건에서는** 충족했다. 이 실패 가설도 범위 한정 기각. 실제 권한자 식별·긴 승인 이력의 상충·모호한 조직 언어·공격자 제어 문서에 대한 새 Need는 여전히 `UNVERIFIED`다.

[C3](runs/C3_autocedar_release_gate_20261125/result.md)는 AutoCedar의 저장된 **수동 AITL CyberChair** 저자 trace에서 candidate 42 verifier pass·CLI 완료 true와 최종 human semantic approval false의 분리를 확인했다. 완료만 소비하는 독립 로컬 서비스는 후보를 적용했으며 명시 승인 gate는 보류했다. 이것은 **승인 확인 없이 CLI 완료를 배포 허가로 쓰는 소비자 조건의 `GAP_SUPPORTED`**다. 원본 코드가 이 분리를 의도적으로 문서화하고 approval 필드를 제공하므로, 그 필드를 검사하는 기존 간단한 gate가 고정 문제를 해결한다. **신규 메커니즘 Need는 이 조건에서 기각**하고, 여러 생성기와 활성 PEP에 걸쳐 검증 대상·승인자·정책 hash를 결속하는 시스템 문제가 남는지 H20으로 감시한다. 실제 저자 무승인 배포나 19개 gold 오류의 원인으로 확대하지 않는다.

[C4](runs/C4_blind_policy_review_20261125/result.md)와 [C5](runs/C5_stronger_review_20261125/result.md)는 공식 case-011 정답+여섯 연구자 단일 조건 변이를 동일 블라인드 prompt로 검토했다. `gpt-4.1-mini`와 `gpt-4.1` 모두 **6/7**, 정답 정책을 거짓 거부했다. 두 모델 모두 `!(true) || principal != author`를 잘못 읽었다. 원본 verifier+독립 gold는 7/7이고 Cedar 로컬 효과가 정상 허용·비인가 차단을 확인했다. 따라서 **자연어 독립 검토 단독의 조건부 정상성 실패는 `GAP_SUPPORTED`**, 독립 gold가 있는 동일 조건의 새 검증 메커니즘 Need는 `REJECTED_HYPOTHESIS`다. Human atom review·저자 실제 오류 후보에 대한 검토 성능은 아직 `UNVERIFIED`다.

[C6](runs/C6_normalized_review_20261125/result.md)는 바로 그 7개 정책을 공식 verifier의 양방향 포함으로 동치 확인한 뒤 간단히 정규화했다. 두 모델 모두 7/7로 거짓 거부를 없앴다. 따라서 C4/C5의 표기 민감성은 **실제로 관측됐으나 기존 정형 검증을 활용한 의미 보존 정규화로 해결되는 범위**다. 이를 신규 메커니즘 Need로 올리지 않는다. 공식 gold 200개 중 184개에 동일 `(!(true) ||` 형태가 있으므로 유사 실패의 범위를 C7에서 사전 선택한 다른 case로 확인한다. 184/200은 표기 빈도일 뿐 오류율이 아니다.

[C7](runs/C7_cross_case_review_20261125/result.md)은 네 구간 사전 선택 공식 gold의 원본/동치 정규화를 두 모델에 블라인드 검토시켰다. `001`에서 강한 모델의 원본 표기 오거부는 정규화로 해결됐지만 `101`에서는 두 모델 모두 원본·정규화를 오거부했다. 두 모델은 Cedar `in`이 직접 그룹만 검사한다고 설명했으나 [공식 언어 명세](https://docs.cedarpolicy.com/syntax-operators.html)는 전이적·반사적 계층 검사를 명시한다. 따라서 **모델 기반 전체 정책 reviewer가 도메인 연산자 의미를 오해해 정상 정책을 보류하는 조건부 평가 Gap**이 추가로 관측됐다. 실제 정책의 계층 요청 허용은 C8에서 검증했다. 기존 Cedar 실행·동치 verifier·사람 전문 검토가 직접 대안이므로 새로운 메커니즘 Need는 여전히 `UNVERIFIED`. 이 실험은 원본 AutoCedar atom reviewer 성능이 아니다.

[C8](runs/C8_cedar_hierarchy_effect_20261125/result.md)은 `case-101`의 공식 gold와 동치 정규화가 동일·직접 자손·2단계 자손을 허용하고 무관 그룹을 차단하는 **실제 Cedar decision 8/8** 및 독립 SQLite 효과를 확인했다. 공식 schema 적용 재검사도 8/8. 이에 C7의 `in` 오해는 정책 gold 오류가 아니라 모델 설명 오류라는 결론이 강화됐다. 최초 집계 6/8은 정상 DENY의 CLI exit2를 잘못 센 코드 오류이며 원시 결과와 정정 기록을 모두 보존했다. C9에서 명세 grounding이라는 기존 간단한 대조를 시험했다.

[C9](runs/C9_grounded_review_20261125/result.md)는 공식 연산자 의미만 추가했지만 두 모델×원본/정규화에서 승인 **1/4**였다. 두 응답은 자연어 설명에서 승인해야 한다고 결론 내리면서 기계 판정 `approve=false`를 냈다. 따라서 단순 문서 grounding도 고정 입력의 reviewer 오류를 안정적으로 해결하지 못했다. [H21](h21_target_review_semantics.md)의 좁은 독립 전체 정책 reviewer Gap은 유지하되, 실제 AutoCedar atom reviewer·human review의 오류라고 확대하지 않는다. [AutoCedar v2](https://arxiv.org/html/2607.03656v2)는 197개 완료 중 19개 target plan이 gold와 달랐고, 14명 연구는 artifact 선호도이며 실제 사람 atom review를 평가하지 않았다고 명시한다. [Reparo](https://arxiv.org/html/2610.41800v1)는 독립 요청 oracle과 사람 표본 검토의 강한 대안이므로 **독립 신규 Need는 여전히 `UNVERIFIED`**다.

[C10](runs/C10_oracle_refinement_bias_20261125/result.md)은 Reparo식 독립 oracle의 한 위험을 저자 원본이 아닌 통제 fixture에서 반박했다. 공식 gold는 `case-101` 자손 두 요청을 허용하지만 equality-only 후보는 거부했다. 모델 oracle은 blind와 잘못된 후보의 decision/불일치 정보를 본 arm에서 **같은 자손 기대 ALLOW**를 유지해, 정책 노출로 gold label을 지우는 실패는 이 조건에서 없었다. 다른 무관 그룹의 강한 모델 ALLOW 2건은 입력이 부모 간선 목록의 완전성을 명시하지 않아 모델 오류와 정보 누락을 구별할 수 없다. C10b에서 그 사실만 보충한다. Reparo의 실제 oracle refinement 결과가 아님.

[C10b](runs/C10b_complete_hierarchy_20261125/result.md)는 부모 부재·간선 목록 완전성만 명시하자 무관 그룹의 두 모델 blind/exposed가 모두 **4/4 DENY**로 바뀌었다. 이 고정 조건에서 잘못된 후보 결정 노출이 oracle을 오염시킨다는 가설과, 충분한 사실을 받은 model oracle이 필연적으로 틀린다는 가설을 기각한다. 실제 저장소에서 관계 증거 누락을 찾아내는 문제는 별도로 남지만 이 입력만으로 새 Need를 주장하지 않는다.

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
