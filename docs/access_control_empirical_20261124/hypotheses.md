# 반박 가능한 가설과 현재 판정

## H1 — 생성 정책의 target 오류

- 속성: 사용자/조직이 승인한 허용 집합과 생성된 정책의 허용 집합이 같은가. 정상 요청이 통과하고 비인가 요청은 차단되어야 한다.
- 근거: [AutoCedar v2 §V-D/Table VI](https://arxiv.org/html/2607.03656v2)는 자체 plan을 통과한 197개 중 19개가 독립 gold와 다름을 저자가 보고. [FORGE v4 Appendix H.3/Table 9](https://arxiv.org/html/2602.16708v4)에는 생성 trace의 judge 합의 뒤에도 held-out 정상 취소 거부가 있음. 이번 Progent 실험의 과권한 정책은 잘못된 정책이 올바르게 집행될 수 있음을 **구성적으로만** 보임.
- 가장 강한 반박: K06의 사람 검토 atom, 독립 gold, Cedar의 형식 포함·동치, Reparo의 별도 행동 oracle, NGAC-IR/Text2NGAC의 출처·역번역·전문가 검토. 승인 목표를 정형·정확하게 제공한다면 속성은 기존 방법으로 검사 가능. [원문 심층 대조](deep_h1.md).
- 기각 조건: 같은 입력·review 조건에서 독립 gold/사용자 확인으로 target 오류가 모두 검출되고 정상 task completion이 유지되면 독립 Gap 주장을 버린다.
- 판정: **K06 한정 사람 검토 효과의 평가 지식 공백 `GAP_SUPPORTED`**; 독립 신규 메커니즘 Need `UNVERIFIED`. [좁은 판정](h1_gap_verdict.md). 제공 workspace의 정형 검증은 이번에 정상 6 PASS/과권한 ceiling FAIL·반례로 확인했다. Gold dataset 200건의 저장 policy/schema/AST가 structured 입력에서 재컴파일되는 것도 확인했다. [공식 trace 탐색](deep_h1_trace.md)은 dataset 200건, 공개 experiments/branch/release에 후보·plan·19건 case ID가 연결되지 않음을 기록했다. 따라서 Table VI의 19건은 저자 결과로만 보존하며 임의 LLM 재생성을 동일 후보 재현으로 바꾸지 않는다. 다음: 동일 문서의 독립 oracle·검토 대조를 구성할 때만 의미 실험.

## H2 — 동적으로 변하는 효과 경로의 완전 중재

- 속성: 보호 대상 effect로 가는 모든 실행 경로가 정책 결정을 통과하고, 새로운 tool/agent/provider 경로도 누락 없이 등록되는가.
- 근거: Progent 로컬 실험은 wrapper 경로에서만 효과 차단을 관측. OpenShell 기존 v0.1.9 실행은 파일/네트워크 계층의 효과를 관측. [FORGE §4.4](https://arxiv.org/html/2602.16708v4)는 완전 중재·충실한 관측을 보장 전제로 두고 [§7.1](https://arxiv.org/html/2602.16708v4)는 미계측 raw socket/direct stdio를 범위 밖이라고 명시한다. [Authorization Revocation §3.4 A6](https://arxiv.org/html/2609.21284)는 manifest completeness를 명시적 가정으로 둔다. 이는 서로 다른 PEP의 범위 확인이지 동일 업무에서 기존 조합이 실패했다는 증거는 아니다.
- 가장 강한 반박: OS/네트워크 PEP(OpenShell), event instrumentation(FORGE), provider-native conditional effect(EffectBound), sink permit(CONTINUITY)의 각 적절한 조합. 특정 도구가 누락돼도 해당 계층을 통과하면 차단할 수 있다.
- 기각 조건: 하나의 정의된 업무·effect 집합에서 새 경로까지 신뢰된 계측/OS/sink가 완전하게 포착하고 정상 요청을 유지하면 버린다. 반대로 **같은 구성**에서 효과는 발생했으나 모든 적절한 PEP가 놓쳤다는 원시 로그가 필요. FORGE 미계측 raw socket 한 개만으로 충분하지 않다. lower-layer PEP 대조가 필요하다.
- 판정: 일반 동적 effect 경로는 `UNVERIFIED`; [원문 대조](deep_h2.md)와 [K14 공식 v0.1.9 실제 대조](runs/K14_effective_20261124/result.md) 완료. OpenShell은 profile 규칙을 effective policy에 추가하고, 이번 L7 `enforce`는 동일 비인가 synthetic 요청의 downstream effect를 0으로 만들면서 정상 요청을 유지했다. 따라서 ‘provider 추가가 항상 우회’는 이 범위에서 기각. 다음: 해당 제품의 실제 effect-equivalent 경로 목록을 고정하고 FORGE PEP가 저비용 실행 가능할 때만 별도 시험.

## H3 — 승인 당시 상태와 provider 최종 effect 불일치

- 속성: 정확히 승인한 대상/버전만 provider에서 최종 확정되고, 철회 후 기존 carrier로부터 새 effect가 생기지 않는가.
- 근거: [EffectBound §V-B/Table III](https://arxiv.org/html/2609.02866)의 저자 GitHub **native REST replay 25쌍**에서 기본 경로 moved-head 25/25→SHA binding 후 0/25, 공식 MCP server end-to-end는 **별도 1회** 확인. 기존 R1의 stale-policy 결과는 인위적 구성; R2의 current-grant permit은 지정 조건에서 차단.
- 가장 강한 반박: 같은 EffectBound의 native SHA binding REST replay 0/25, [Authorization Revocation §3.4 A5–A9](https://arxiv.org/html/2609.21284)의 sink fence/채널 accounting, CONTINUITY의 permit. 각각 승인 목표·최신 상태·API 원자성·완전 manifest를 요구.
- 기각 조건: 해당 provider가 요청 digest/SHA 또는 CAS/If-Match와 fence를 제공하며 이를 실제 승인과 결속해 정상 완료를 유지하면 범용 Gap 주장을 버린다.
- 판정: 지원 provider/API에서는 `RESOLVED_IN_SCOPE`; 다른 provider 일반화는 `UNVERIFIED`. [위임·철회·finality 원문 대조](deep_h3.md)에서 VERA 간선 철회, Authorization Revocation의 support antichain·fence, CTA 원자 commit도 확인. [이번 합성 3일정 실험](runs/H3_edge_fence/result.md)은 원본 VERA target 함수와 **별도 작성** 원자 sink에서 A 단독/AND 신규 effect 0, X OR 정상 effect 1을 관측해 ‘추상적으로 조합 불가능’ 주장을 기각했다. 실제 provider 조건은 여전히 `UNVERIFIED`.

## H4 — 하위 위임 계보 철회가 새로운 MAS Gap

- 근거/반박: [기존 R3 판정](../R3_GAP_VERDICT.md)의 CONTINUITY 모델 밖 G3–G5를 이번 [H3 원문 대조](deep_h3.md)에서 VERA의 disjunctive 간선 철회와 Authorization Revocation의 root support antichain·sink fence로 다시 확인했다. 두 논문은 같은 종합 보장을 단독 증명하지 않는다.
- 기각 조건: 기존 해법이 같은 계보·독립 지원·합의 승인 의미를 각 정의한 범위에서 다루면 버린다.
- 판정: 기존 R3의 ‘CONTINUITY의 기능 부재 = 새 Gap’ 주장은 `REJECTED_HYPOTHESIS`; 간선 철회+provider finality의 **동시 결합**은 H3a `UNVERIFIED`.

## H5 — 승인된 호출 내부의 하위 효과가 승인 범위를 벗어남

- 보안/정상 속성: 사람은 특정 명령/도구를 승인하고 정상 coding task는 계속 완료해야 한다. 그 호출이 읽거나 쓰는 **실제 자원과 외부 효과**는 승인 범위를 넘지 않아야 한다.
- 직접 근거: [Approval Laundering §V, §VII–IX](https://arxiv.org/html/2609.38983)의 저자 Claude Code 실험은 기록된 명령 인자가 변하지 않아도 `npm` 하위 프로세스 파일 읽기 또는 Git hook 효과가 발생했고, 기록 필드에 결속한 Approval Token으로 Scope/Argument 양식이 해결되지 않았다고 보고한다. 해당 논문이 문제를 명명·측정했으므로 관측 자체를 새 발견으로 주장하지 않는다.
- 가장 강한 반박: [OpenShell](https://docs.nvidia.com/openshell/v0.1.9/how-it-works/policies/overview)의 파일/네트워크 PEP, [FORGE §4.4](https://arxiv.org/html/2602.16708v4)의 계측된 action 집행, [EffectBound §V](https://arxiv.org/html/2609.02866)의 provider-native 결속. 특정 정상 업무가 하위 자원을 필요로 하는지, PEP가 그 자원을 차단해도 completion이 유지되는지 같은 조건에서 봐야 한다.
- 기각 조건: 승인된 호출과 동일한 정상 작업에서 기존 OS/IFC/provider PEP가 하위 비인가 효과를 막고 정상 완료를 유지하면 독립 Gap 주장을 버린다.
- 판정: 실제 한계 사례는 `OBSERVED_IN_PRIOR_WORK`; 새로운 독립 Need는 `UNVERIFIED`. 이번 [동일 호출 대조](runs/H5_dispatch_effect/result.md)는 정상 업무에 필요 없는 합성 파일에 한해 host 하위 효과를 확인하고 Docker 파일 경계로 정상 출력 유지·비인가 효과 0을 관측했다. 따라서 **이 특정 자원 조건의 신규 Gap은 `REJECTED_HYPOTHESIS`**. 동적/필수 자원과 실제 provider 효과에 대한 일반화는 보류. [추가 대조표](expanded_candidate_scan.md) 참조.

## H6 — 획득한 새 권한의 활성화가 기존 MAS 방법 밖의 새 Gap

- 직접 근거: 새 계정/credential/resource의 capability는 사전 tool 호출 승인만으로 정해지지 않을 수 있다.
- 가장 강한 반박: [AcquireBound §§3–5, 7](https://arxiv.org/html/2609.14744)은 인증된 provider 실제 결과, quarantine, 최신 activation, 관계형 한계와 effect permit으로 이 전이를 **직접** 모델링·검증한다. 단 [§1.4, §10.3](https://arxiv.org/html/2609.14744)는 등록된 profile·완전 중재에 상대적이다.
- 기각 조건: 구체 provider가 authenticated capability description과 activation PEP를 제공하고 정상 task를 완료하면 버린다. 자료가 없는 provider에서는 먼저 필요한 evidence가 **실제 불가능한지**와 그 영향까지 입증해야 한다.
- 판정: 일반적 “방법 부재” 가설은 `REJECTED_HYPOTHESIS`; 특정 provider 적용성은 `UNVERIFIED`.

## H7 — 검토·증명된 정책과 실제 활성 effective policy의 불일치

- 보안/정상 속성: 배포 시점의 전체 effective policy가 승인된 상한을 넘지 않으며, 보호 대상 경로의 PEP가 실제 `enforce` 모드여야 한다. 정상 요청은 유지해야 한다.
- 직접 근거: K03 원본 갱신 subset gate는 `SECAGENT_ONLY_ALLOW_NARROW=True` 옵션이고 기본 False(`secagent/tool.py:465–482`). 이번 [수동 구성 효과](runs/progent_manual_boundary/results.json)는 정책 `None`일 때 경고만 후 로컬 비인가 effect 1건. K14 [공식 정책 문서](https://docs.nvidia.com/openshell/v0.1.9/how-it-works/policies/overview)는 provider 규칙을 effective policy에 합치고 inspected endpoint `audit`와 `enforce`를 구분한다. 이것들은 각각 다른 제품·설정의 조건이다.
- 가장 강한 반박: 전체 effective policy에 대한 [OpenShell prover](https://docs.nvidia.com/openshell/v0.1.9/how-it-works/policies/prover), fail-closed deployment/config gate, 정책 해시·서명·활성 PEP 모드 검사. `None`/`audit`가 의도된 관측 설정인지도 구별해야 한다.
- 기각 조건: 동일 배포에서 전체 정책의 포함 검사와 enforce 상태 확인이 정상 업무를 유지하면서 잘못된 활성 정책을 차단하면 신규 Gap 주장을 버린다. `None` 하나를 보편적 연구 미해결로 승격하지 않는다.
- 판정: 실무상 유심히 볼 `WATCH`, 독립 신규 Need `UNVERIFIED`. [K14 새 실행](runs/K14_effective_20261124/result.md)은 provider attach 이후 base/effective 차이와 audit/enforce effect 차이를 확인했다. 이어 [공식 prover 대조](runs/H7_policy_gate_20261124/result.md)는 base 후보를 `within_boundary`, provider 규칙 포함 후보를 `exceeds_boundary`로 검출했다. 따라서 **이번 policy 형상에서 전체 확대를 검사할 수 없다는 가설은 `REJECTED_HYPOTHESIS`**. 자동 배포 gate의 실제 적용은 시험하지 않았다. 기본 shorthand audit 로그는 `/blocked`를 `ALLOWED`로 보여 별도 원본 telemetry 없이는 would-deny를 판독하기 어렵다. 이 로깅 제한을 독립 학술 Gap으로 승격하지 않는다. [감시표](gap_watchlist.md)의 4번.

## H8 — 조건부 권한의 graph export와 실제 효과

- 속성: 같은 `read(doc)`는 trusted `registration_open=false`에서 effect 0, `true`에서 effect 1. K07의 자연어 IR에 조건을 기록한 것과 실제 PM/app PEP 집행을 분리한다.
- 근거: [NGAC-IR v1 §5.1](https://arxiv.org/html/2611.26941v1)은 broad export의 조건부 권한 98/715 무조건화, strict export의 23/390 추가 PM 거부를 저자가 보고한다. [공식 NIST PM 3.3.0 독립 6조건](runs/K07_condition_boundary/result.md)에서 broad false 로컬 effect 1, strict true effect 0을 관측했다. 원저자 생성기/strict+app 배포 재현은 아니다.
- 가장 강한 반박: [같은 PM의 broad+앱 사전 guard](runs/K07_condition_boundary/result.md)와 [Cedar 공식 CLI의 `when` 조건 PDP](runs/K05_conditional_alternative_20261124/result.md)는 이 고정 조건에서 false effect 0/true effect 1. [독립 복수 route PM 7조건](runs/K07_route_composition_20261125/result.md)은 전역 gate의 정상 과거부와 conditional prohibition 상시 export의 PM 과거부를 구별했다. [Cedar 규칙별 조건 6조건](runs/K05_route_composition_20261125/result.md)은 같은 작은 의미를 모두 맞췄다. XACML request attributes 및 NIST 동적 graph도 대안. condition 값의 신뢰·최신성·commit 원자성이 추가 전제다.
- 기각 조건: 원저자 strict export+앱 목록의 조건 검사가 PM의 다른 prohibit/obligation 의미를 보존하며 동일 안전·정상 effect를 낸다면 K07 평가 공백을 닫는다. 일반 새 메커니즘 주장에는 기존 앱/Cedar/XACML 조합이 합리적 비용에서 같은 목표를 해결하면 즉시 기각한다.
- 판정: **정적 NGAC graph-only 한계 `GAP_SUPPORTED`**, K07의 strict+앱 통합 effect 평가 공백도 확인. 그러나 이미 있는 조건 PDP/앱 PEP가 단순 고정 조건을 해결했으므로 **독립 신규 Research Need `UNVERIFIED`**. [상세](h8_conditional_gap_verdict.md).

## H9 — 조건의 두 단계 손실이 같은 요청의 효과로 이어지는가

- 고정 질문: 자연어 조건이 IR 추출에서 누락되거나, IR에는 남지만 export된 PEP에서 검사되지 않으면 동일한 비인가 `read` 효과가 나는가. 두 단계를 **서로 다른 원인**으로 기록하고 같은 case ID/조건/최종 효과로 연결할 수 있는가.
- 직접 원문: [NGAC-IR v1 §§3.3, 5.1–5.3](https://arxiv.org/html/2611.26941v1)은 714문장 중 의미 오류 31개에서 조건 누락 4개를 보고하며, back-translation flag가 놓친 오류 5개 중 3개가 조건 누락이다. 별도로 broad export는 조건부 허용 98/715개를 무조건화한다. **이 두 집합의 교집합·요청 효과는 논문에서 확인되지 않았으므로 수치를 더하거나 동일 사건으로 취급하지 않는다.**
- 가장 강한 반박: 권한자의 source-aware 조건 검토, [ECOOP 2026 `pick`](https://drops.dagstuhl.de/storage/00lipics/lipics-vol372-ecoop2026/html/LIPIcs.ECOOP.2026.22/LIPIcs.ECOOP.2026.22.html)의 구별 요청, K06 검토 target/독립 gold, 조건식 Cedar/XACML PDP와 route-aware 앱 PEP. 각각 원문 정확성·정책 조건·집행 연결에 다른 신뢰를 요구한다.
- 기각 조건: 같은 원문 조건에서 독립 사람/정형 oracle이 누락을 발견하고, route-aware 조건 PDP/앱이 false effect 0과 true 정상 effect 1을 유지하면 독립 메커니즘 Need를 버린다. 공개 K07 생성 trace나 승인된 별도 생성 run이 없으면 단계를 연결한 신규 실패로 주장하지 않는다.
- 판정: 두 단계의 **개별 저자 관측은 있음**, 같은 요청의 합성 effect 및 기존 결합 대응 실패는 `UNVERIFIED`. 지금은 `WATCH`이며 `GAP_SUPPORTED`로 합산하지 않는다.

## H10 — 권한 있는 출처의 승인 변경이 지속 메모리에 잘못 반영됨

- 고정 속성: 권한자의 자연어 grant/revoke/scope 변경이 여러 session을 지나도 **현재 승인 상태**로 정확히 남고, executor의 해당 tool 요청은 그 상태에 맞게 처리돼야 한다. 잘못된 권한은 차단하고 정상 허용도 보존해야 한다. 원점 신원·문장 내용·업데이트 적용·최종 effect를 분리한다.
- 저자 관측: [EAL-Bench v2 §4.2/4.6, Appendix C.1–C.4](https://arxiv.org/html/2609.01836v2)에서 source-authority filter 뒤에도 메모리의 false authority 149/2772 비인가 probe, 선택된 잔여 오류에서 58/60 비인가 tool 행동. 동일 typed-incremental paired comparison에서 filter UA 23.5%→7.3% / LA 93.1%→53.2%; event 방식 UA 23.4%→9.3% / LA 93.0%→68.6%. **저자 원시 trial을 이번에 재실행한 수치가 아니다.** [공식 코드 오프라인 감사](runs/EAL_offline_20261125/result.md)는 200 보존 자료 해시·파생 CSV 재계산만 확인하고 raw trial 부재를 기록한다.
- 가장 강한 반박: EAL 내부의 3-block 재구축 UA 4.9%/LA 95.2%, oracle-exact memory의 선택된 오류 1/390 비인가 행동; [PLACE](https://arxiv.org/html/2610.25179)의 trusted event+physical readback, [MemTxn](https://arxiv.org/html/2607.27834)의 ordered source support, [AuthMem-Bench](https://arxiv.org/html/2608.01679)의 source role metadata, [MAP-Graph](https://arxiv.org/html/2608.10509)의 명시 revoke action gate, [Revoked but Still Authoritative](https://arxiv.org/html/2609.08258)의 retrieval validity guard. 각자 **이미 정확한 event/status/정형 근거를 받는지**가 H10과의 핵심 차이. [같은 조건 반박 조사](h10_memory_counterreview_20261125.md).
- 기각 조건: 같은 36 synthetic case/승인 history와 두 executor에서 기존 정확 event ledger·권한자 검토·재구축·source support 조합이 현재 상태 오류와 비인가 행동을 충분히 줄이면서 정상 행동 및 입력/검토 비용을 유지하면 새 메커니즘 Need 가설을 버린다. raw v2 trial/원시 writer state가 공개되지 않으면 저자 결과를 복제한 실험으로 부르지 않는다.
- 판정: **source-only 충분 가설 `REJECTED_HYPOTHESIS`**, EAL 테스트 범위에서 현재 대책의 의미 오류·안전/정상 잔여 **좁은 `GAP_SUPPORTED`**. 다른 대안의 같은 입력 성능·독립 신규 Research Need `UNVERIFIED`. 실제 provider 효과는 평가되지 않음.
- 2026-11-25 추가 직접 대조: [원본 EAL source gate/정책 함수 + 공식 procurement case 6입력](runs/H10_source_scope_20261125/result.md)에서 CFO 최신 상한 9,500의 정확 상태는 정상 9,000 effect +1/비인가 10,000 effect 0. **독립 조작**으로 같은 CFO 인용을 유지하고 memory 상한만 15,000으로 넓히자 gate Pass/비인가 로컬 effect +1. 비권한자 인용은 gate가 막지만 정상도 거부. 저자 자체 contract self-check 통과. 이 고정 조건의 정확 event ledger/서비스 현재 상한 대안은 동작하므로 **새 메커니즘 필수성 `REJECTED_HYPOTHESIS`**, 자연어 event 추출의 비용·정확성은 `UNVERIFIED`.

## H12 — 철회된 출처가 새 current journal로 재기록될 때 status-only 검색 필터가 남기는 권위

- 속성·정상 업무: 오래된 권한/운영 규칙에서 파생한 journal은 그 원본이 철회되면 후속 판단 근거가 되지 않아야 한다. 별도로 작성된 실제 최신 journal은 검색되고 정상 업무를 계속 지원해야 한다. 공격자 주입뿐 아니라 agent 자신의 잘못된 결론 재기록도 범위에 넣는다.
- 직접 근거: [Shen et al. Appendix C.1/Table 14](https://arxiv.org/html/2609.08258)는 Graphiti의 hop-0 unsafe 결정 이후, direct write-back의 current journal이 남을 때 필터 뒤 hop1 unsafe 255/356, natural ingestion에서 active journal 22/358 및 해당 active 조건 19/22 hop1 unsafe를 보고한다. 전체 natural filtered hop1은 27/358이다. 조건부 분모·ingestion 모드를 혼동하지 않는다. [원저자 guard 원본 함수에 대한 독립 합성 대조](runs/M4_guard_boundary_20261125/result.md)는 원본 `expired_at`만 있으면 새 `j`가 `kept`, 외부에서 `j.revoked_at`을 정확히 주면 `withheld`임을 관측했다. 실제 Graphiti/LLM/provider 재현은 아니다.
- 가장 강한 반박: [MAP-Graph §§3.2–3.4](https://arxiv.org/html/2608.10509v1)의 trusted `derived_from`/recursive ancestry와 명시 revoke, Audience-Bound Persistent Memory의 currentness cascade, 출처/변경의 code-owned event ledger, 최종 effect의 CONTINUITY sink. 각 기법은 정확한 원점·파생·철회 정보와 모든 관련 경로 매개를 요구한다. [동일 문제 반박](m4_alternatives_note_20261125.md).
- 기각 조건: **같은 실제 write-back trace**에서 신뢰된 파생 계보+철회 이벤트를 가진 기존 방법이 새 journal을 정확히 제외하고 정상 최신 journal과 업무 성공을 보존하면 독립 메커니즘 Need를 기각한다. status-only가 표지 없는 journal도 정확히 제외하는 반례가 나오면 좁은 실패 판정도 재검토한다. 계보가 누락/오인된 조건은 별도의 수집 정확성 질문이다.
- 초기 판정(함수 입력 시험 당시): Graphiti/write-back의 **status-only 검색 경계는 `GAP_SUPPORTED`**. 원문은 후속 **결정**을 측정했고 초기 함수 실험은 실제 protected service effect를 관측하지 않았다. 아래 추가 로컬 모의 서비스 효과 대조가 이 범위를 넓힌다.
- 2026-11-25 효과 대조: [원본 guard+독립 loopback HTTP/SQLite 모의 서비스 6조건](runs/M4_live_20261125/result.md)에서 bad journal은 비인가 1-reviewer effect +1을 구성적으로 만들었다. **정확한 외부 계보** 또는 서비스의 현재 2-reviewer PEP는 비인가 0·정상 +1을 동시에 달성했다. 따라서 이 고정 effect 구성에서 **새 메커니즘 필수성 `REJECTED_HYPOTHESIS`**. 자연 Graphiti/LLM write-back과 자동 계보 수집·정상 사용성은 여전히 `UNVERIFIED`.

## H11 — action risk의 모델 제안 metadata가 신뢰된 task risk보다 gate를 낮춤

- 속성·정상 업무: 허용 가능한 증거 trust threshold는 실제 실행할 action의 trusted type/risk에 맞아야 하고, 정상 high-risk action은 증거가 부족할 때 확인 요청으로 진행할 수 있어야 한다. 모델이 자기 action을 낮은 type/risk로 적어 기준을 우회해서는 안 된다.
- 근거: [MAP-Graph §3.4/§4.4/Appendix F.6](https://arxiv.org/html/2608.10509v1)은 risk-sensitive gate와 Exp-5의 41/450 impermissible Allow를 저자가 보고한다. first author의 공개 보조 artifact 후보 commit `d94b0bf3c73efdb60fcc08014989b44ce8eae99d`에서 [저장 결과 41건 재집계](runs/H11_risk_metadata_20261125/result.md)는 모두 Exp-5, public risk high→제안 medium 13/41. 원본 `gate_action()`의 [독립 4조건 함수 시험](runs/H11_risk_metadata_20261125/result.md)은 같은 `send_email/high` task와 trust .76에서 제안 `send_email/high`→`ASK_USER`(.85), `answer/medium`→`ALLOW`(.30), `send_email/medium`→`ALLOW`(.60), revoked ancestor→`BLOCK`을 관측했다. 실제 tool/provider effect는 없음.
- 가장 강한 반박: trusted public task type/risk에 제안 metadata를 재결속하거나 불일치 거부, typed effect policy/PEP, 원본 MAP-Graph의 **정확한** revoked ancestry hard rule. [H11 자세한 source·평가 감사](h11_mapgraph_risk_gate_20261125.md). 41건 중 public medium 28건은 올바른 .60 threshold도 trust .76으로 통과하므로 metadata 수정만으로 전체 오류 해결이라는 주장은 성립하지 않는다.
- 기각 조건: 같은 450 Exp-5와 정상 task에서 trusted action metadata 재결속+정확한 supporting lineage+effect PEP가 비허용 Allow를 제거하고 정상 completion을 보존하면 독립 메커니즘 Need를 기각한다. 공개 raw trace가 없어 **41건의 인과 기여**와 실제 외부 효과는 판정하지 않는다. 구현 코드가 논문 평가에 쓰인 정확한 commit인지도 미확정이다.
- 초기 판정(함수 입력 시험 당시): 보조 공개 코드의 제안 metadata 우선순위 **구체 구현 경계 `GAP_SUPPORTED`**; 논문 41건의 원인 귀속·새 독립 Need는 `UNVERIFIED`. 아래 추가 로컬 모의 효과 대조와 구별한다.
- 2026-11-25 효과·반사실 대조: [원본 gate+별도 trusted binding/mock outbox와 저장 지표 900행](runs/H11_counterfactual_20261125/result.md)은 같은 `send_email/high`의 합성 제안 medium에서 원본 ALLOW/로컬 +1, trusted binding ASK_USER/0; 정상 high trust .95 둘 다 +1, revoked ancestor 둘 다 0. 그러므로 **이 구성의 새 메커니즘 필수성 `REJECTED_HYPOTHESIS`**. 저장된 Exp-5 unsafe 41건 중 threshold-only 교차는 11건뿐이며 그 11건 제안 type은 모두 `answer`; 전체 저장 run의 counterfactual 결과는 raw support/graph 부재로 UNKNOWN. 남은 30건과 context-support 누락 경계는 별도 가설로 확인한다.

## H13 — 자연어 승인 event와 실제 파생 계보를 얻는 과정의 공동 평가 공백

- 고정 문제: 인증된 권한자가 자연어로 grant/narrow/revoke하고 Agent A가 후속 memory를 쓰며 Agent B가 정상/비인가 요청을 처리한다. `source identity` 진위, 그 문장의 승인 **의미**, 실제 읽은 source→write edge, 현재 grant, effect sink를 서로 다른 입력으로 기록한다. 목표는 비인가 effect 0과 정상 effect 보존을 동시에 측정하는 것이다.
- 현재 근거: [EAL 원본 source-only gate 직접 대조](runs/H10_source_scope_20261125/result.md)는 정확 actor citation에도 잘못된 scope와 로컬 비인가 effect가 남음을 보였고, [M4 원본 guard+서비스 모의](runs/M4_live_20261125/result.md)는 unmarked write-back과 계보/최종 PEP 반박을 구별했다. [문헌 교차검증](h13_hard_counter_20261125.md)은 WTB v4·CONTINUITY·Epistemic Guard·MAP-Graph·PLACE·PACMI의 **이미 확보된 메커니즘**과 event/edge 정확성 전제를 기록한다. 서로 다른 저자 결과를 동일 공격 체인의 성공률로 합산하지 않는다.
- 가장 강한 반박: 인증된 정책 event의 구조화 수집·권한자 readback, code-owned actual-consumption lineage, 현재 승인 상태를 확인하는 WTB/CONTINUITY/일반 ABAC·provider PEP, 정확 ledger 또는 3-block rebuild. 정확한 정보가 주어진 이번 최소 조건에서는 기존 대안이 정상 요청을 유지하며 비인가 효과를 막았다.
- 기각 조건: 같은 자연어 변경/실제 write-back/동일 모의 서비스에서 강한 기존 조합이 추출·계보 오류를 허용 가능한 비용으로 줄이거나, 오류가 남아도 현재 authority effect PEP가 비인가 효과를 막고 정상 완료를 유지하면 새로운 메커니즘 Need 가설을 버린다. 정보가 원천적으로 없는 경우와 provider 원자성 부재는 다른 문제다.
- 판정: “해결 메커니즘 전무”는 `REJECTED_HYPOTHESIS`. **자동 event/실제 edge 수집의 안전·정상 공동 평가**는 [범위가 좁은 평가 Gap 후보](h13_hard_counter_20261125.md)이며 아직 같은 입력 강한 조합 결과가 없어 `WATCH/UNVERIFIED`. 
