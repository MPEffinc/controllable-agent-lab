# 2026-11-25 MAS 권한 출처·위임·효과의 잔여 Gap 재검색

검토 기준: 2026-11-25 UTC. 이 문서는 [현재 상태](STATUS.md)와 [H3 판정](h3_gap_verdict.md)을 재검토하고, **MAS에서 서로 다른 주체의 승인·데이터·효과가 합쳐지는 경우**를 원문과 고정 소스로 좁혀 본 추가 조사다. 기존 H1/H8 판정과 문서는 수정하지 않았다. [M1의 CONTINUITY 원본 함수 독립 대조](runs/M1_continuity_amount_20261125/result.md)는 실행했으나 유료 API·운영 서비스 호출은 0. 아래의 저자 실험 결과를 우리 재현으로 표시하지 않는다.

## 결론과 판정 경계

| 후보 | 같은 조건의 직접 관측 | 강한 기존 대응 | 현재 판정 |
|---|---|---|---|
| M1: A2A 중간자가 원점 승인을 대체 | Donno 등 §V-B: 공유 증거 HMAC 키를 가진 정당한 Hospital이 승인 상한 EUR 120→9000을 바꾸고 하위 Insurer 검사를 통과 | [Lineage](https://ieeexplore.ieee.org/abstract/document/11589226)의 resource-server 서명 체인·범위 단조성, [CONTINUITY](https://arxiv.org/html/2609.05269)의 서명 root·위임 축소·finality; [원본 함수 독립 대조](runs/M1_continuity_amount_20261125/result.md) | **구현 약점은 관측; 서버 측 검증 가능한 범위 `RESOLVED_IN_SCOPE`, 독립 새 Need `UNVERIFIED`** |
| M2: 여러 부모가 재사용하는 child의 이전 출처가 새 부모의 승인으로 격상 | [Multi-CaMeL §VI-A](https://arxiv.org/html/2610.05640)는 tree·unique parent·fresh child로 제한하고 retained history/DAG/queue를 평가하지 않음. 이것은 **관측 실패가 아님** | 새 parent마다 fresh episode, 출처 보존, sink 검사; [MAP-Graph](https://arxiv.org/html/2608.10509)는 task 내 shared memory 계보·action gate, [Audience-Bound](https://arxiv.org/html/2609.36373)는 context 전 audience gate; [Authorization Succession](https://arxiv.org/html/2610.00347)은 단일 부모 fork/cut 보장 | **`UNVERIFIED`** |
| M3: child가 요청 범위 대신 가까운 범위 결과를 반환하고 parent가 계속 실행 | [Multi-CaMeL §V-C.2](https://arxiv.org/html/2610.05640)는 AssetOpsBench의 여러 정상 task에서 이 **업무 실패를 직접 관찰** | 검증 가능한 결과 metadata와 effect 전 exact-scope 확인, [CONTINUITY](https://arxiv.org/html/2609.05269)의 field/action 결속 | **업무 실패 관측; 비인가 provider 효과·새 보안 Need는 `UNVERIFIED`** |

특히 M2는 기존 논문이 다루지 않은 *평가 조건*으로는 명확하다. 그러나 미평가를 공격 성공 또는 독립 Research Need라고 부를 수 없다. M1의 실패도 이미 저자들이 파악했고, 다른 신뢰 경계가 같은 원점 보존 문제를 직접 다룬다. 세 후보 모두 **일반적인 신규 MAS Research Need는 아직 `UNVERIFIED`**다.

## M1 — 정당한 중간자의 원점 승인 대체

**고정 조건·속성.** 사용자/Patient의 상한 EUR 120 승인으로 Hospital에 위임하고, Hospital은 자신의 합법적 Ed25519 호출키와 *공유된* authorization-evidence HMAC 키를 가진다. Insurer가 현재 호출자와 C2 증거를 확인해도, 최종 청구/지급 수락은 사용자가 승인한 금액·수혜자·행동 범위에 묶여야 한다. 이는 단순 prompt injection이 아니라 **승인 자료를 다시 서명할 수 있는 정당한 중간자의 오용**이다.

**원문에서 직접 관측한 사실.** [Donno 등, arXiv:2611.07050v1 §II-C, §III-B, §V-A–B, Table II](https://arxiv.org/html/2611.07050): C1은 현재 caller의 서명을, C2는 원점 정보·승인 세부정보의 hash와 **참여자 간 공유 HMAC**을, C3은 현재 hop의 서명을 확인한다. 경로 검사는 주체 순서와 목적지의 구조를 보지만 scope의 의미상 축소를 확인하지 않는다. Table II의 scope widening 수락 1건은 *isolated path-layer test*이고, 키 없는 공격자의 end-to-end 성공이 아니다. 별도 §V-B에서는 Hospital이 EUR 120을 EUR 9000으로 바꾸고 hash/HMAC을 다시 만들며 현재 hop을 서명하자 C3·C1·C2 및 Insurer application check가 통과했다. 저자 평가 분모는 서로 다른 층을 포함한 적대 조건 15개 중 14개 차단, 정상 400/400 수락, 지정한 적대 조건 반복 500/500 차단이다. 반복 500은 이 합법적 중간자 사례의 일반 공격 성공률 추정이 아니다. 보험 서비스의 외부 지급 상태나 분산 provider commit은 측정하지 않았다. 원문에서 원저자 공개 코드 링크는 확인되지 않아 구현 재현 가능성은 `NOT_ESTABLISHED`다.

**가장 강한 반박.** Donno §V-B 자신이 원점 서명 보존, per-hop 서명 위임, 축소만 가능한 capability와 [Lineage](https://ieeexplore.ieee.org/abstract/document/11589226)를 대응으로 제시한다. Lineage의 IEEE 원문 초록은 **resource server가 제어하는 서명 위임 체인**, scope 단조성, 깊이 제한, server에서 전체 조상 검사를 주장하며 live LLM reference implementation의 prompt-injection 사례 1건 차단을 보고한다. 그 평가는 Donno의 악성 Hospital과 동일 입력·키 배포·실제 보험 효과를 직접 비교한 것은 아니다. [CONTINUITY §5.1–5.4](https://arxiv.org/html/2609.05269)도 서명된 root, authority/delegation scope 축소, action·subject·정책 epoch·철회에 묶인 최종 permit을 둔다. 고정 코드 `third_party/continuity` SHA `59cfe60930d247d1890b366ded686c718020a11e`의 `src/continuity/core.py:1204-1220`은 위임 범위의 subset을 검사하고 `:1411-1485`는 메모리 FinalitySink에서 permit 결속과 철회를 검사한다. 이는 원점 신뢰와 최종 중재를 **다른 구성으로 구현할 수 있다는 강한 반박**이지 Donno 배포의 원저자 재현이나 실제 보험 지급 보장이 아니다. [Macaroons](https://www.ndss-symposium.org/ndss2014/ndss-2014-programme/macaroons-cookies-contextual-caveats-decentralized-authorization-cloud/)의 제한 caveat도 고전적 대안이다.

**2026-11-25 독립 실행 대조.** [사전등록·명령·원시 효과·판정](runs/M1_continuity_amount_20261125/result.md)을 보존했다. CONTINUITY의 **원본** `verify_bundle → issue_permit → FinalitySink`를 호출한 finance 적응에서 signed root max EUR 120/액션 EUR 120은 로컬 effect 1, 같은 max/액션 EUR 9000은 `E_ROOT_FIELD_CONSTRAINT`와 effect 0이었다. 사후 별도 등록한 위임 scope 확대는 `E_ROOT_SCOPE_EXCEEDED`/effect 0, 정말 넓은 signed root EUR 9000은 effect 1이었다. 네 입력은 동일 `SimulatedWorld`/`NonceLedger`를 공유했다. 이는 원본 verifier를 활용한 **독립 synthetic 대조**이며 Donno의 HMAC 신뢰 모델, A2A 원래 코드, 실제 보험 provider의 수락을 재현하지 않는다. 새 Gap을 입증하지도 않는다.

**판정·기각 조건.** Donno가 고정한 공유키 설계에서 *원점 승인 불변* 성질의 실패는 **직접 관측된 구현 약점**이며 이미 해당 논문이 설명한다. 서버가 서명 체인을 통제하고 매 hop 축소를 확인할 수 있는 범위는 Lineage 등에 의해 `RESOLVED_IN_SCOPE`로 보는 것이 타당하다. 따라서 이 실패를 곧바로 독립적 `GAP_SUPPORTED`로 세지 않는다. “이를 해결할 새 MAS 권한 기법이 필요하다”는 Need는 `UNVERIFIED`; 서버 보유 키/원점 서명과 per-hop 축소, 최종 효과 중재가 같은 4자 요청에서 EUR 9000을 거절하고 EUR 120 정상 요청을 성공시키면 그 Need 가설은 기각한다. 새 연구 가능성은 **서버 측 검증을 배치할 수 없는 실제 A2A/provider 계약**이 고정되고 기존 대안도 실패할 때만 다시 평가한다. 그 계약은 아직 찾지 못했다.

**다음 최소 반증 실험.** CONTINUITY의 원본 함수 로컬 대조는 완료했다. 공개 Donno 코드가 확보되면 원저자 4자 synthetic workflow의 정상 EUR 120과 변조 EUR 9000을 같은 입력으로 재생하고, 원점 서명/per-hop subset 대조를 **같은 신뢰 키 소유와 최종 효과 경계**에 붙인다. 외부 보험 서비스 effect는 현재 범위 밖이다. 코드가 없으면 계속 `NOT_ESTABLISHED`로 둔다. 비용: 로컬 CPU, 외부 API 0. 완료: 원본과 강한 대조의 동일 입력·정상 완료·효과가 모두 기록됨.

## M2 — 복수 부모·지속 child에서 출처와 권한의 교차

**고정 조건·속성.** 부모 A의 데이터 또는 위임은 나중에 부모 B가 같은 지속 child에 내리는 *신뢰된 새 task*를 수정하거나 B의 provider 효과를 승인하는 근거가 되어서는 안 된다. A의 유해 데이터가 이력을 통해 B의 task/effect로 흘러가는지, 반대로 B의 정상 업무를 필요 이상으로 거절하는지를 함께 평가한다. 이는 A→child, B→child라는 복수 유입과 retained memory, 가능한 비동기 응답을 포함한다.

**원문·소스 범위.** [Multi-CaMeL §III, §IV, §V-B, §VI-A](https://arxiv.org/html/2610.05640)에서 단일 agent 보호를 이어 붙일 때 untrusted 결과가 child의 trusted `task`로 승격되는 공격을 저자들이 보여주고, `task`/`variables` 분리로 tree agent-as-tool 구성의 CFI를 보장한다. MultiAgentDojo에서는 모델·구성당 주입 task 949개, Multi-CaMeL의 보고 ASR 0%이며 이는 그 벤치마크의 결과다. §VI-A는 각 non-root agent가 **고유 부모 하나**, 호출 시 새 child를 갖는 tree라고 명시한다. DAG에서는 부모마다 별도 fresh episode가 가능하나 이전 이력을 유지하면 불신 데이터의 재승격을 막아야 한다고 명시하고, queue/shared state/cycle까지 미래 과제로 둔다. 고정 `third_party/multiagentdojo` SHA `e71647382155dc6949d6ccf9a9d7ec7cf429b856`의 `src/agentdojo/agent_pipeline/multi_agent.py:583-596`은 tool 유래 `task.producers`에 대한 hard deny 정책을 만들고 `:645`에서 Sequrity에 보낸다; `:655-685`는 각 호출마다 child를 새로 만든다. 현재 로컬 fake-client 시험은 실제 Sequrity hard deny를 관측하지 않았으므로 이 경계의 집행을 우리 실험으로 증명하지 않는다.

**가장 강한 반박.** Multi-CaMeL 저자가 제시한 *부모별 새 episode와 provenance 보존*이 바로 이 위협을 피하는 간단한 배포 선택이다. [Authorization Succession §4.5, §5.5–5.9, §7–8](https://arxiv.org/html/2610.00347)은 변화하는 agent population의 fork·조상 cut·rollback과 원자 effect admission을 다루며 32 등록 결정 × 2 logical mapping = 64/64 재생 등을 보고한다. 그러나 저자도 executable profile을 **single-parent forest**, unique parent, no multi-parent merge라고 제한하고 두 logical mapping은 provider-free라고 한다. [Authorization Revocation](https://arxiv.org/html/2609.21284)의 OR/AND 선택 witness와 [CTA v2](https://arxiv.org/pdf/2607.10487v2)의 원자 sink 후보 재선택은 복수 승인 측면의 대안이다. 이 조합들이 같은 지속 child의 이전 자연어·도구 데이터 출처까지 추적했다는 근거는 없지만, 별도 episode/출처 분리/최종 gate의 조합이 충분할 수 있다.

**판정·기각 조건.** 제한된 평가 지형은 명확하나 같은 강한 대안에서의 비인가 effect 관측이 없어 `UNVERIFIED`다. fresh episode 또는 이력 전체의 taint 보존에 최종 sink 결속을 더한 대조군이 B 정상 effect를 유지하고 A 유래 비인가 effect를 0으로 만들면 독립 Need는 기각한다. 다른 agent의 권한을 합쳐야 하는 실제 업무가 없으면 단순히 상태를 분리하는 것으로 충분하므로 연구 필요성도 약하다.

**최소 안전 반증 실험.** 로컬 한 child/두 부모/메모리 sink로 (1) A의 오염된 응답을 child history에 넣고, (2) B가 독립적인 정상 task를 보낸 뒤, (3) child가 B task 외 효과를 제안하는지 관찰한다. **동일 입력**에서 retained history baseline, 부모별 fresh episode, provenance-labeled retained history+effect gate를 비교한다. 로그에는 정확한 신뢰 채널·history bytes의 해시·B 정상 완료·provider 전후 state를 저장한다. 관측 실패가 특정 fixture의 구현 실수인지 별도로 감사한다. 원본 Multi-CaMeL의 지원 토폴로지 밖이므로 저자 공격 성공률로 표시하지 않는다. 비용: 로컬 결정적 fixture, API 0. 완료: 세 조건의 효과와 B 정상성 기록.

## M3 — child 결과의 범위 치환과 후속 효과

**고정 조건·속성.** 부모는 `asset=x, 기간=t`의 결과만 근거로 후속 write를 승인한다. child가 `x′/t′`의 근접 결과를 반환하면 trusted `task`가 바뀌지 않았어도 write가 원래 승인 범위를 벗어날 수 있다. `task` CFI와 **응답의 업무상 정확성·효과 결속**은 다른 성질이다.

**직접 근거와 한계.** [Multi-CaMeL §V-C.2](https://arxiv.org/html/2610.05640)는 AssetOpsBench의 여러 trajectory에서 child가 정확한 asset/time을 얻지 못해 인접 범위를 반환하고 부모가 사전 생성된 plan대로 진행한 **정상 task utility failure**를 보고한다. 그 몇 건의 분모, 공격자 제어, 비인가 provider write의 상태 변화는 이 절에서 제시되지 않는다. 소스 `third_party/multiagentdojo/src/agentdojo/agent_pipeline/multi_agent.py:655-685`의 해당 tool은 마지막 child 답변을 문자열로 반환한다. 이 함수 자체에는 원래 요청 범위와 child 결과 범위를 비교하는 구조화 검사가 없다. 그것만으로 전체 응용의 모든 effect 경로가 미보호라고 추론하지 않는다.

[공식 MultiAgentDojo checkout의 공개 trace 감사](m3_assetops_trace_audit_20261125.md)에서는 네 AgentDojo suite와 36,679개 tracked run 파일에서 AssetOpsBench 특정 실패 궤적을 찾지 못했다. 논문 부록 A의 task 609는 IoT child가 원 요청 site `MAIN`이 없을 때 첫 site로 대체하도록 작성된 **잠재적 코드 경로**를 보이지만 실제 tool 반환값/분기 실행이 없으므로 저자 관측 실패의 재현으로 세지 않는다.

**가장 강한 반박·판정.** 정확한 범위를 붙인 구조화 결과/typed schema를 parent가 확인하고 최종 효과 gate가 요청의 asset/time과 비교하면 될 수 있다. [CONTINUITY §5.2–5.4](https://arxiv.org/html/2609.05269)는 field provenance와 action digest를 effect permit에 묶는 직접 대안이지만 해당 AssetOpsBench task를 실행한 것은 아니다. PAuth의 server-side task slice도 실제 도구 인자에 범위를 붙이는 대안이다. 현재 **업무 실패는 관측**, 보안 Gap과 새 Need는 `UNVERIFIED`. 정확한 metadata 대조가 정상 작업을 유지하며 근접 범위를 거절하면 새 메커니즘 필요 가설을 기각한다.

**최소 안전 반증 실험.** 저자 공개 AssetOpsBench trajectory 하나에서 원 요청 asset/time, child 반환 asset/time, parent 후속 호출을 추출한다. 동일 fixture에 구조화 result metadata와 sink exact-match를 넣어 정확한 결과는 effect 1, 치환 결과는 effect 0인지 확인한다. 원시 trace가 없으면 synthetic fixture로만 기록하며 저자 실패 재현으로 부르지 않는다. 비용: 로컬 trace/fixture, API 0. 완료: 동일 요청에서 범위·효과·정상 완료가 모두 관측됨.

## 다음 실행 순서

1. **M1 자료 확보:** Donno 원저자 코드/원시 4자 입력 공개 여부를 확인하되, 없으면 더 이상 저자 재현을 주장하지 않는다. Lineage의 공개 full text/코드가 확보되면 공유키 보유 악성 중간자와 같은 금액·수혜자 조건의 server-side 반증을 우선한다.
2. **M3 저자 trace:** Multi-CaMeL의 AssetOpsBench 범위 치환 사례가 공개 데이터/로그에서 식별되는지 확인한다. 정확한 instance가 없으면 자체 사례는 별도 synthetic 결과로 둔다.
3. **M2는 낮은 비용으로 조건 고정:** 재사용 child가 실제로 필수인 업무와 provider effect를 먼저 정한다. fresh child가 허용되면 강한 기존 대안으로 즉시 기각한다. 별도 retained-state 효과 실험은 그 후에만 사전등록한다.

**최종 Need 판정:** 보안 영향의 직접 관측은 M1의 특정 shared-HMAC A2A 프로토타입에 한정되며 이미 원저자와 대안이 설명한다. M2/M3의 추가 MAS 조건은 현재 미평가 또는 업무 실패 수준이다. 따라서 2026-11-25 시점의 **독립적으로 새로운 Research Need = `UNVERIFIED`**다.
