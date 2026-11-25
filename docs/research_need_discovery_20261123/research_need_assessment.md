# AI Agent/MAS 접근통제 Research Need 평가

기준일: 2026-11-23. 이 문서는 **연구 주제 선정표가 아니라 문헌상 남은 조건의 검증 기록**이다. 문헌에 없는 통합 시스템의 실패를 상상하여 `OPEN_WITH_EVIDENCE`로 판정하지 않는다. 아래 수치는 모두 **논문 저자의 평가**이며 이번 조사에서 실험을 실행·재현하지 않았다. 논문 식별·출판 상태는 [연결 연구 지도](linked_research_map.md)의 서지표와 각 원문을 함께 보라. 별도 표기가 없는 2026년 arXiv 논문은 프리프린트다.

증거 등급: **A** 저자가 명시한 한계·미래 연구, **B** 원문 메커니즘·평가 범위에서 직접 확인한 제한, **C** 여러 원문을 비교한 연구자 추론, **D** 저자가 시험·반례에서 관측한 실패. `D`라도 그 논문의 시험 조건 밖까지 일반화하지 않는다. `PARTIALLY_RESOLVED`는 구체 조건에 기존 해법이 있고 다른 조건이 남았다는 뜻이다. `UNVERIFIED`는 남은 것처럼 보이지만 **기존 방법도 실패한다는 근거가 부족**하다는 뜻이다.

| 항목 | 현재 판정 | 문헌상 확인된 핵심 | 신규 Need 판정 |
|---|---|---|---|
| R01 지속 승인과 바뀐 실행 맥락 | `PARTIALLY_RESOLVED` | 지속 허용의 잔여 권한 재사용은 관측됨. Scoped 재사용·task 권한·commit 결속도 존재함. | 이 방법들의 조합을 넘는 실패는 `UNVERIFIED` |
| R02 자연어에서 만든 정책의 의미 | `PARTIALLY_RESOLVED` | 검토·역번역·SMT가 개선했지만 잘못된 target과 누락 조건의 실제 오류가 남음. | 자동 의미 정확성의 일반적 해결 불충분은 근거 있음. *새 방법이 필요*한지는 미확정 |
| R03 외부 자료에 위임한 민감 인자 | `PARTIALLY_RESOLVED` | 출처·인자별 권한 검사는 존재. 정당 출처의 값이 옳은지 판단하는 문제는 별개. | 정확한 위임·확인 절차가 없을 때의 신규성은 `UNVERIFIED` |
| R04 도구 승인 뒤 서비스의 실제 효과·철회 | `PARTIALLY_RESOLVED` | 특정 provider 인터페이스의 결핍과 늦은 효과가 실증됨. Native 조건부 API·commit 검사·fence가 반박. | 모든 계층을 써도 보호 불가한 일반 문제는 `UNVERIFIED` |
| R05 MAS 위임·출처·철회 | `PARTIALLY_RESOLVED` | Tree MAS의 메시지 세탁, 일부 A2A 원천 증거 오류는 시험됨. 전파·축소·fence 대안이 존재. | 비트리·영속·비동기 결합 조건의 독립 Need는 `UNVERIFIED` |
| R06 개별 허용과 전체 실행의 목적 정책 | `PARTIALLY_RESOLVED` | 거짓 양성 없는 단일 실행 검사는 일부 관계 속성을 판정 불가. 다중 실행 집행의 고전적 기술 존재. | Agent 목적 정책에 적용 후 남는 문제는 `UNVERIFIED` |
| R07 형식·포함관계·충돌 | `RESOLVED` *(지원 언어와 정해진 명세에 한정)* | Margrave, ZELKOVA, Cedar, Progent 등에서 분석 가능. | 독립적 새 Need로 제시하지 않음 |

## R01. 오래 지속되는 승인과 실행 맥락의 결속

**Problem Statement / 실제 예.** 사용자가 정상 프로젝트에서 `python3 runner.py` 실행을 지속 허용했는데, 다음 프로젝트에서는 같은 argv가 다른 script·의존성·설정에 결속되어 다른 효과를 낸다. 좁은 명령 접두사나 exact-resource 규칙도 승인 당시의 *실행 의미*를 모두 보존하지 않을 수 있다. [*When Consent Outlives Context*](https://arxiv.org/html/2609.33910) §3, §5.4, Appendix E–F는 이 공격자의 통제 범위와 실제 coding-agent 사례를 기술한다.

**이미 해결한 범위.** 이 논문의 고정된 AgentDojo history 비교에서는 Progent의 현재 task 시작 정책이 영향받은 모델의 ASR을 0–0.009로 낮추고, PAuth의 *task-scoping 규칙만 따로 구현한* 조건과 no-replay가 0이었다(§5.3/Table 3, Appendix D). 따라서 해당 표를 PAuth 전체 메커니즘의 재현으로 인용하지 않는다. [ConLeash](https://arxiv.org/html/2605.11360) §§4–6은 input/output/effect/sensitivity의 경계를 사용자 승인으로 세분화하고 나중 호출에 재사용한다. §8.1은 다중 MCP 서버 상승 315/315 탐지, §8.2는 50개 실제 세션 기록의 **재생**에서 278/291 경계 초과 탐지를 보고한다. [CTA/CommitGate](https://arxiv.org/pdf/2607.10487v2) §§2–4는 선언된 정확한 효과, 현재 grant·premise·dependency를 효과 commit에서 원자적으로 검사한다. [CONTINUITY](https://arxiv.org/html/2609.05269) §§5–8은 근거 필드가 계층 사이를 거칠 때 증명과 single-use effect permit으로 묶는다.

**잔여 문제와 근거.** *When Consent Outlives Context* §5.3/Table 3은 같은 조건에서 exact-resource 지속 허용에도 영향받은 네 모델의 ASR 0.012–0.039가 남았다고 보고(**D**). §5.4는 실제 3개 coding agent·55개 사례에서 잔여 승인으로 평균 ASR이 24.9 percentage points 증가했다고 보고(**D**). §6은 이질적 도구 전반에서 재사용에 필요한 *최소* 보안 결속을 찾는 일을 미래 연구라고 밝힌다(**A**). 다만 ConLeash §9는 자신의 보장이 LLM이 만든 추상화에 상대적이고 시간·도메인 의미 제약이 부족하다고 명시(**A**); §8.1은 같은 session 안의 지속 허용을 주로 평가하므로 cross-task·cross-session 장기 승인의 완전한 반박도 아니다(**B**). CTA §2.2, §6은 정책에 필요 사실이 누락되면 실제 의도와 어긋난 효과도 통과할 수 있다고 명시(**A**). [*Earned Authority under a Fixed Ceiling*](https://arxiv.org/html/2607.23586) §VIII/Appendix A-D는 sound effect abstraction·의미 oracle을 전제하며 그 운영 비용을 평가하지 않았다(**A/B**).

**가장 강한 반박 / 신규성.** 위험에 맞게 scoped 동의를 재사용하는 ConLeash가 있고, 모든 관련 사실을 선언할 수 있다면 CTA의 원자적 effect binding 및 provider의 조건부 쓰기를 사용할 수 있다. 그러므로 “지속 승인 재사용을 안전하게 할 방법이 없다”는 주장은 **기각**한다. `PARTIALLY_RESOLVED`; *여러 도구의 맥락에서 어떤 사실을 승인에 묶어야 하는지, 정상 재사용을 유지하며 자동 검증할 수 있는가*는 아직 `UNVERIFIED`인 좁은 질문이다. 이 좁은 질문은 **C**이며 독립된 새 취약점의 관측 결과가 아니다.

**후속 연구에서 확인할 최소 증거.** 동일한 사용자 승인과 정상 작업을 유지하고 script 내용, dependency, 작업 디렉터리, 원격 리소스 버전만 바꾸는 종단 간 기록에서 ConLeash의 실제 추상화, CTA의 선언된 premise, CONTINUITY의 변환 witness, provider-native 조건부 작업을 **각각 적용한 기존 논문**이 있는지 확인한다. 실패가 있다면 필요한 사실의 선택 오류와 추출·표현·commit 경계 오류를 분리해야 한다. 신규 구현 제안은 이 조사 범위 밖이다.

**필수 7개 반박.** ① 이미 해결? ConLeash/CTA/CONTINUITY와 task-scoping이 강한 부분 해결이다. ② 구현 누락? 올바른 digest/버전 precondition을 정책·provider API에 넣으면 구체 사례가 해결될 수 있다. ③ 잘못된 정책? CTA의 “모든 필요 사실 선언”은 실제 핵심 전제다. ④ 위협 모델? ConLeash의 세션 내 MCP와 장기 cross-session 사례는 다르다. ⑤ 무엇 부족? consent에 묶을 맥락의 **선택·관측** 및 commit 시 freshness; 모든 경계에서 집행점이 없다는 주장은 아님. ⑥ 다른 분야? [UCON](https://dl.acm.org/doi/10.1145/984334.984339), 조건부 쓰기, capability expiry, TOCTOU 방어가 대안이다(CTA §7; [EffectBound](https://arxiv.org/html/2609.02866) §II/§VI). ⑦ 왜 중요? 논문 §5.4의 실제 coding-agent 관측과 ConLeash §8.3의 scoped approval 사용성은 보안·정상 작업의 동시 요구를 뒷받침한다.

## R02. 자연어 요구에서 만든 정책의 의미가 실제 승인과 같은가

**Problem Statement / 실제 예.** 사용자가 정상 항공편 취소를 요청했는데 정책 생성기가 원문에 없던 조건을 덧붙여 허용 취소를 막는다. 또는 “환자 기록”을 “환자 전체 상위 자원”으로 번역해 허용 범위를 넓힌다. 문법·충돌·SMT 검사를 통과한 규칙도 잘못된 검증 target에 충실할 수 있다. [FORGE](https://arxiv.org/html/2602.16708) Appendix H.3/Table 9의 Task 43과 [Text2NGAC](https://arxiv.org/html/2611.12572) §5.2/Table 15의 parent-resource mutation이 각각 구체 사례다.

**이미 해결한 범위.** [Cedar](https://arxiv.org/html/2403.04651) §§2.5–2.6, §4.4는 schema 검사 및 정의된 정책 간 포함·동치와 반례를 제공한다. [AutoCedar](https://arxiv.org/html/2607.03656) §§III, V-D는 검토된 target atom에 대해 후보 정책을 검증한다. [FORGE](https://arxiv.org/html/2602.16708) §3.4/Appendix H는 back-translation, trace와 judge를 이용한 확인 경로를 제시한다. [NGAC-IR](https://arxiv.org/html/2611.26941) §§3–5는 원문 문장과의 역번역 비교를 Text2NGAC의 구조 검사에 추가한다. [Reparo](https://arxiv.org/html/2610.41800) §5.2는 정책 생성기와 다른 모델을 oracle로 쓰고 저장소 코드·문서를 근거로 삼는다. 이것들이 이미 있다는 사실을 빼고 “의미 검증 연구 부재”라고 말할 수 없다.

**잔여 문제와 근거.** FORGE Appendix H.1은 자기 judge와 번역이 동일 기반 모델이고 독립 인간 명세와의 동치를 재지 않는다고 **A**로 인정한다; Appendix H.3/Table 9의 held-out 정상 작업 실패는 **D**. Text2NGAC §5.2/Table 15에서 구조 verifier의 parent abstraction 탐지는 11/120였지만 저자 heuristic이 114/120을 flag했으므로 “아무 방법도 없다”가 아니다(**D**). NGAC-IR §5.3은 실제 의미 오류 31건 중 26건 검출, **5건 미검출**; §6은 수량·delegation·중첩 obligation 표현 및 Policy Machine 조건 검사 부재를 명시(**D/A**). AutoCedar §V-D/Table VI는 검토된 target을 통과한 197개 중 19개가 독립 gold와 불일치했다고 보고하며, §VI은 target이 잘못되면 정책을 정확히 그 잘못된 target에 맞출 수 있음을 인정(**D/A**). [Intent Contracts](https://arxiv.org/pdf/2611.24025v1) §4/Table 7은 환경 대상이 모호한 DevOps 지시 96개에서 자기 구조의 비인가 행동 29개를 보고한다(**D**); 다른 방법까지 실패한다는 증거는 아니다.

**가장 강한 반박 / 신규성.** 독립적인 사용자가 정형 target을 명시·검토하면 Cedar/AutoCedar 같은 기존 도구가 정책의 형식적 정합성을 강하게 검증한다. 모호한 자연어를 사용자에게 되묻는 절차도 기존 접근통제의 유효한 해법이다. **다만** “자동 번역 뒤 검증”만으로 실제 승인 범위와 같다는 주장은 FORGE·NGAC-IR·AutoCedar의 직접 평가에서 충분히 뒷받침되지 않는다. 판정 `PARTIALLY_RESOLVED`: *평가된 자동 번역/검사 파이프라인에서 실제 오류가 남는다*는 좁은 사실은 **D**로 확인; 이를 곧 “새 프레임워크가 필요하다”로 옮기는 것은 **C**이고 보류한다.

**후속 연구에서 확인할 최소 증거.** 같은 원문과 독립 검토 target에 대해 NGAC-IR·AutoCedar·Reparo·FORGE의 실제 평가 조건 및 인간 확인 절차를 대조한다. 특히 user request, 관리자 정책, tool schema, runtime 값 중 어느 입력이 target 권위를 갖는지와 검토자가 무엇을 보았는지 확인해야 한다. 빈번한 오류율이 다른 도메인에서도 유지되는지, 이들 방법을 조합해도 동일 오류가 남는지 추가 문헌이 필요하다.

**필수 7개 반박.** ① 이미 해결? 정형 명세가 주어지면 Cedar와 AutoCedar가 상당 부분 해결한다. ② 구현 누락? 추가 테스트 trace가 Task 43을 찾을 수 있지만 가능한 모든 승인 의미를 finite trace로 보장하지는 않는다(FORGE Appendix H). ③ 잘못된 정책? 바로 그 경계가 문제이며 올바른 target을 사용자가 제공하면 해결 가능하다. ④ 위협 모델? Cedar의 논리는 *주어진 명세* 상대적; 이를 자연어 의미 증명 실패라고 비난하면 부정확하다. ⑤ 무엇 부족? 주로 **정답 target의 권위와 의미 oracle**, NGAC-IR의 일부 표현력. ⑥ 다른 분야? Margrave, ZELKOVA, Cedar의 symbolic reasoning과 인간이 검토한 명세가 강한 반박([Margrave](https://web.cs.wpi.edu/~kfisler/Pubs/icse05.pdf) §§1–3; [ZELKOVA](https://kasperluckow.com/papers/fmcad2018.pdf) §§I–IV). ⑦ 왜 중요? 과소권한은 정상 취소를 막고, 상위 자원 추상화는 과권한을 허용한다는 직접 사례가 있다.

## R03. 사용자가 외부 자료에 위임한 대상·수신자 값

**Problem Statement / 실제 예.** “청구서를 읽고 거기 있는 수취인에게 지불”이라는 정당한 요청에서 payee가 사용자 문장에는 없고 공격자 쓰기 가능한 청구서에만 있다. 모델이 보는 출처와 그 값이 사용자 승인에 *맞는 값*인지는 별개다. [ROPE](https://arxiv.org/pdf/2608.27496v2) §§2–3, §5/Table 5의 정상 bill-payment 사례가 이 차이를 보여준다.

**이미 해결한 범위.** [PAuth](https://arxiv.org/pdf/2603.17170v2) §III-C–D는 authoritative 서버가 서명한 값·계산 provenance를 통해 사용자의 task slice에 맞는 동적 인자를 검증한다. [PACT](https://arxiv.org/pdf/2605.11039v1) §3은 tool-call 전체가 아닌 argument role과 출처별 계약을 정의한다. ROPE §§2–3은 user-named trusted sender/record와 전체 값 매칭을 사용한다. [SPILLWAY](https://arxiv.org/pdf/2611.07222v3) §§2–3은 typed identity field와 제한된 위임 규칙·sanitized judge로 free text의 목적지 오염을 줄인다. [IntentCap](https://arxiv.org/html/2609.14631) §2와 [CXI](https://arxiv.org/pdf/2607.06000v1) §§2–3도 권한 필드 소유·trusted release라는 다른 계층을 제공한다.

**잔여 문제와 근거.** ROPE §5/Tables 4–5는 source-delegated 악성 대상 7건의 성공과 정상 source delegation 관련 거부 83건을 보고(**D**), §6은 올바른 출처의 *내용 적절성*을 입증하지 않는다고 인정한다(**A**). SPILLWAY §5/Tables 2–3은 자기 threat model의 2,847 attack pair에서 in-scope target 성공 0을 보고하지만, §2/§7은 typed identity field 직접 변조·도구 role 선언·적응 공격 범위를 제한한다(**A/B**). PAuth §III-A의 authoritative 서버 값 진실성, §III-E의 NonDet 인자 확인 절차도 중요하다(**A**). ROPE의 7건을 SPILLWAY나 PAuth가 동일 조건으로 모두 재검증했다고 말할 근거는 없다(**B**).

**가장 강한 반박 / 신규성.** 사용자가 신뢰할 서버·검증된 sender·typed field를 명시했거나 최종 payee를 재확인하면 기존 기법이 충분히 해결할 수 있다. 공격자가 쓸 수 있는 free text만을 승인 근거로 삼도록 사용자가 위임했는데 다른 정보가 없으면, 출처 태그만으로 참 payee를 판별할 수 없다는 것은 정보 조건에 대한 **C**이지 새로운 공격 성공의 별도 **D**가 아니다. 판정 `PARTIALLY_RESOLVED`; *확인 요청 없이 안전과 정상 지급을 모두 유지하는 일반 해법의 부재*는 `UNVERIFIED`.

**후속 연구에서 확인할 최소 증거.** 동일한 위임 문장, 동일한 공격자 제어 필드, 동일한 정상 업무를 기준으로 ROPE의 7건·83건 조건과 PAuth의 authoritative 서명, PACT의 field discharge, SPILLWAY의 typed field, CXI의 release가 실제로 동일한 값을 어떻게 판단하는지 비교한 원문을 찾는다. 사용자나 조직이 지정한 **가치 판단 근거**가 없는 조건과 있는 조건을 혼합하지 않는다.

**필수 7개 반박.** ① 이미 해결? 인증된 authoritative 값·typed field·사용자 확인 조건에서는 해결한다. ② 구현 누락? role 선언·검증 데이터가 이미 있으면 적용 문제일 수 있다. ③ 잘못된 정책? “청구서 전체를 믿는다”는 사용자 위임 자체가 과광범위하면 정책 문제다. ④ 위협 모델? PAuth는 서버 값 진실성을 가정하고 SPILLWAY는 typed field 직접 오염을 제외한다. ⑤ 무엇 부족? origin의 **진실성·내용 적합성 정보**, tool-call 집행점 부재가 아니다. ⑥ 다른 분야? 인증된 업무 원장, 서명된 invoice, 업무 규칙, 인간 이중 승인, capability field restriction을 검토한다. ⑦ 왜 중요? ROPE의 실제 정상 거부와 공격 성공은 보안뿐 아니라 청구서 지급 완수도 함께 따져야 함을 보인다.

## R04. 도구 호출 승인과 provider의 실제 효과·철회

**Problem Statement / 실제 예.** agent가 GitHub PR의 head `h1`을 검토한 뒤 merge를 승인하지만 provider 내부에서는 head가 `h2`로 바뀐다. 또는 Kafka ACL 철회가 모든 broker에 적용된 뒤에도 이전에 승인된 ProduceRequest가 append된다. 도구 호출 시점의 allow, provider 응답 성공, “철회 완료”는 서로 다른 성질이다. [EffectBound](https://arxiv.org/html/2609.02866) §§I–II, §V-B–C/Table III가 이 두 경로를 명시한다.

**이미 해결한 범위.** GitHub native API의 head SHA precondition으로 검토한 버전만 merge할 수 있다(EffectBound §I/§V-B). CTA §§2–4는 완전한 최신 근거와 exact effect binding을 atomic sink에서 재확인한다. [CONTINUITY](https://arxiv.org/html/2609.05269) §§5–6은 current policy/revocation과 single-use permit을 finality에서 검사한다. [Authorization Revocation](https://arxiv.org/html/2609.21284) §§2–5는 root epoch cut 뒤 manifested sink들의 queue/callback/provider carrier를 fence·완결하거나 exact rebind해 root-scoped quiescence를 정의한다. [HBHC](https://arxiv.org/html/2605.20704) §§3–4는 부모 heartbeat에 자식 credential의 신선도를 연결해 **새 인증**을 차단한다. 새 인증 거절과 이미 수용된 작업의 효과 폐쇄는 같지 않다.

**잔여 문제와 근거.** EffectBound §V-B/Table III의 저자 시험에서는 head 이동 뒤 기존 GitHub MCP-to-REST 경로 25/25가 다른 head를 merge했지만 `Bind SHA`를 쓰는 경로는 0/25이고 정상 25/25를 완료했다(**D**). §V-C는 Kafka 4.3.1의 고정 broker 집합·synchronous/nontransactional 경로에서 오래된 요청의 append를 재현하고 Effect Fence로 막았다(**D**, 이 경로에 국한). §VI은 provider가 필요한 제어를 **제공하지 않는 고정 인터페이스** 안에서 정상 완료와 안전을 동시에 보장하기 어려운 경우를 논한다. CTA §2.2/§6은 누락된 정책 사실과 sink 우회·issuer 오류를 보장 밖으로 둔다(**A**). CONTINUITY §12는 실제 provider 동시성·재시도·부분 실패를 구현하지 않았다고 명시(**A**). Authorization Revocation §7–8은 provider-free suite라는 평가 범위를 밝힌다(**B**).

**가장 강한 반박 / 신규성.** 정확한 provider API와 atomic precondition, transaction/fence는 이미 존재하며 EffectBound 자체가 GitHub에서 대안을 시험했다. [Linearizability](https://www.cs.columbia.edu/~wing/publications/HerlihyWing90.pdf) §1의 선형화 지점, 전통적 TOCTOU 방어, 분산 종료/취소 개념도 선행 경로다. 따라서 “agent tool을 거치면 실제 효과 집행이 원리적으로 불가능하다”는 주장은 **거짓**이다. 판정 `PARTIALLY_RESOLVED`. *고정된 좁은 provider 인터페이스가 필요한 원자 결속을 제공하지 않는 조건*은 EffectBound의 **D/형식적 경계**로 근거가 있지만, 더 낮은 서비스 계층으로 이동하면 해결될 수 있어 독립적 신규 Need로 확정하지 않는다.

**후속 연구에서 확인할 최소 증거.** 특정 provider·API 버전·정책 효과를 고정하고 효과 frontier, 조건부 API, in-flight carrier, provider-native ACL과 commit point를 원문으로 대조한다. 전체 시스템이 그 경계만 사용해야 하는지, 다른 API로 필요한 조건을 표현할 수 있는지 확인한다.

**필수 7개 반박.** ① 이미 해결? EffectBound의 Bind/Re-enter/Fence, CTA의 atomic sink, provider API가 조건부로 해결. ② 구현 누락? GitHub MCP 표면의 SHA 인자 누락은 native REST를 쓰면 해소된다. ③ 잘못된 정책? 승인 대상이 `h1`이라는 사실을 선언하지 않으면 어떤 prover도 발견 못 할 수 있다. ④ 위협 모델? HBHC는 신규 자격증명 사용, CONTINUITY prototype은 메모리 내 finality이며 provider 효과 전체 보장이 아니다. ⑤ 무엇 부족? 좁은 interface의 **제어 능력·effect frontier 관측·동시성**. ⑥ 다른 분야? CAS/ETag, transaction, linearizability, distributed fencing. ⑦ 왜 중요? 잘못된 merge와 철회 뒤 append는 서비스 상태를 실제 변경하면서 정상 merge/produce도 보존해야 한다.

## R05. MAS 위임의 권한 출처와 전달 경계

**Problem Statement / 실제 예.** 부모 agent의 도구 결과가 자식에게 `message`로 재포장되며 지시 권위로 승격되거나, A0→A1→A2 위임에서 A2가 현재 호출자 A1만 인증하고 A0의 승인 범위·축소 내역을 확인하지 않는다. 첫 문제는 [Multi-CaMeL](https://arxiv.org/html/2610.05640) §III, 두 번째는 [Donno et al.](https://arxiv.org/html/2611.07050) §§I–III의 문제 설정이다.

**이미 해결한 범위.** Multi-CaMeL §IV–V는 tree-shaped fresh child와 단방향 위임 아래 trusted `message`/untrusted `variables`를 분리하고 capability/provenance를 전파한다. Table III의 평균 공격 성공 0은 그 평가 환경에 국한한다. [ControlValve](https://openreview.net/pdf?id=PNU9Rj5RDQ) §4/Fig. 4는 opaque subagent의 허용 호출 그래프와 edge 규칙을 사전 정책으로 만들고 §6에서 CFH를 평가했다. [Progent](https://arxiv.org/html/2504.11703) §8.3은 MAS에서 global/subagent gate를 실험한다. [PAuth](https://arxiv.org/pdf/2603.17170v2) §III-D의 signed value envelope, IntentCap §2의 delegation attenuation, CONTINUITY §§5–6의 origin-to-effect witness는 위임의 서로 다른 부분을 다룬다. [RFC 8693 OAuth token exchange](https://www.rfc-editor.org/rfc/rfc8693)도 전통적인 대리 권한 전달 경로다. [ResidualAuth v2 §§4, 7–8](https://arxiv.org/html/2609.08062)은 같은 현재 reachability라도 철회 뒤 결정이 달라지는 경우를 증명하고, 논문의 제한된 위임 그래프 시험에서 신선한 인증 조회가 요약보다 정확하며 hard gate가 비인가 효과 8건을 막았다고 보고한다.

**잔여 문제와 근거.** Multi-CaMeL §VI-A “Beyond Trees”는 multi-parent, persistent child, async queue, peer cycle을 명시적으로 다음 과제로 둔다(**A**). 그러나 그 조건에서 공격이 성공했다는 **D**는 아니다. Donno et al. §V-A–B/Table II의 synthetic 4-party reimbursement에서는 isolated scope-widening 검사 하나가 통과했고, 공유 HMAC 키를 가진 정당 중간 agent가 원천 권한 증거를 다시 만들면 full application check까지 통과했다(**D**, 이 shared-key 신뢰 모델). 이 결과를 *모든* signed delegation의 실패로 일반화하면 안 된다. [Authorization Revocation](https://arxiv.org/html/2609.21284) §§7–8은 비동기 carrier를 다루지만 provider-free reference suite이고 실제 모든 A2A 네트워크의 증거가 아니다(**B**).

**가장 강한 반박 / 신규성.** origin-signed grant, per-hop attenuation, 대상 서비스의 downstream verification, token exchange와 effect fence를 조합하는 길이 이미 있다. 위임된 **내용과 승인 범위의 의미**를 무엇으로 검증할지 분리해야 한다. 판정 `PARTIALLY_RESOLVED`; 일반 그래프 MAS·장수 자식·비동기 작업을 모두 결합해도 기존 방식이 깨지는지는 `UNVERIFIED`. Multi-CaMeL의 한계를 “MAS 자체의 미해결 취약점”으로 과장하지 않는다.

**후속 연구에서 확인할 최소 증거.** A2A origin grant가 독립 키로 서명되고 각 hop의 권한 교집합이 destination에서 실제 확인되는 기존 구현/논문을 먼저 찾는다. Donno et al.의 공유 키 반례가 그 구성에서도 가능한지, parent stop 뒤 이미 수용된 effect가 어떤 provider boundary를 지나는지 별도로 확인한다. 비트리/영속 관계의 동일 공격 실증이 있는지도 확인한다.

**필수 7개 반박.** ① 이미 해결? Tree/fresh child는 Multi-CaMeL, 공개 A2A 프로토콜은 token exchange·signed hop으로 상당 부분 해결. ② 구현 누락? scope inclusion과 키 분리의 부재는 Donno et al. 사례에서 구현·설정 선택일 수 있다. ③ 잘못된 정책? 위임할 최대 scope가 잘못되면 정확한 attenuation도 과권한을 전달한다. ④ 위협 모델? opaque subagent와 shared HMAC 중간 agent는 각각 특정 모델이다. ⑤ 무엇 부족? 원천 승인 증거의 **신뢰 경로·감쇠 검증**, 오래된 carrier의 effect closure. [ResidualAuth §4](https://arxiv.org/html/2609.08062)는 현재 reachability만으로 철회 뒤 판단을 복원할 수 없음을 보인다. ⑥ 다른 분야? capability attenuation, OAuth token exchange, signed delegation, distributed fencing. ⑦ 왜 중요? 자식·서비스가 실제 외부 효과를 수행하고 부모 중단 뒤에도 작업이 남을 수 있으므로 정상 위임도 유지해야 한다.

## R06. 개별 행위의 허용과 실행 전체·관계적 목적 정책

**Problem Statement / 실제 예.** 매번 도구 호출은 특정 consent 아래 허용이지만, 두 업무의 결과를 비교하면 사용자 목적과 무관한 다른 대상에도 같은 권한이 쓰인다. 두 실행을 비교해야 정의되는 purpose/noninterference 성질은 현재 trace 하나만 보는 검사와 다르다. [*Local Allow, Global Deny*](https://arxiv.org/html/2610.27620) §§III–V의 관계적 2-safety 모델과 §VIII의 누적 consent 사례를 구별해야 한다.

**이미 해결한 범위.** [FORGE](https://arxiv.org/html/2602.16708) §§3–4의 Datalog event history, [CONTINUITY](https://arxiv.org/html/2609.05269) §§5–6의 transition/finality 계약은 단일 호출보다 많은 이력을 본다. 따라서 “기존 monitor가 모두 호출 하나만 본다”는 주장은 사실이 아니다. 관계적 속성에는 [Coenen et al., *Runtime Enforcement of Hyperproperties*](https://arxiv.org/html/2203.04146) §§3–5가 다중 trace의 HyperLTL enforcement와 안전 부분집합 해법을 이미 연구했다. Secure multi-execution도 기존 접근이며 *Local Allow, Global Deny* §IX가 이를 대안으로 인정한다.

**잔여 문제와 근거.** *Local Allow, Global Deny* §V의 정리는 **거짓 양성 없는 단일 trace 판정기**가 논문의 관계적 purpose 조건을 완전히 판별할 수 없다는 조건부 불가능성(**B: 형식 정리의 범위**). §VIII-E의 live open-weight agent 누적 consent 실패 22/60과 composition-aware guard의 0/60은 **D**이나 단일 trace 현상이고 앞의 관계적 불가능성 정리의 실증이 아니다. Coenen et al. §4는 parallel input에서 알고리즘을 제공하고 sequential input의 일반 경우는 undecidable, safety 등 제한에서 가능하다고 구별한다(**B**). 이론적 경계가 곧 agent 업무에서 정상 작업을 유지하며 쓸 수 있는 보장의 부재는 아니다(**C**).

**가장 강한 반박 / 신규성.** 단일 trace 목적 판단의 수학적 제한은 분명하지만, cross-run 비교, secure multi-execution, 기존 IFC와 formal hyperproperty enforcement가 강한 대안이다. `PARTIALLY_RESOLVED`; 특정 agent 목적 정책과 필요한 정상 사용 조건에서 기존 관계적 집행이 충분한지는 `UNVERIFIED`. “per-action 정책이 합성되지 않으므로 새로운 관계적 agent monitor가 필수”라고 결론 내리지 않는다.

**후속 연구에서 확인할 최소 증거.** 어떤 목적 정책이 정말 **둘 이상의 실행 관계**를 요구하는지 명시하고, 독립 비교 trace의 확보 가능성·결정 시점·정상 업무 허용을 기존 HyperLTL/IFC/secure multi-execution 논문과 비교한다. 단일 실행 내 누적 승인 문제와 2-safety 문제의 평가 수치를 섞지 않는다.

**필수 7개 반박.** ① 이미 해결? 단일 trace 이력 정책 및 multi-trace hyperproperty 기술이 존재한다. ② 구현 누락? 비교 trace 저장·재실행이 가능하면 기존 기법 적용 문제일 수 있다. ③ 잘못된 정책? purpose가 잘못 선언됐으면 관계적 증명도 잘못된 목표에 충실할 뿐이다. ④ 위협 모델? §V 정리는 false-alarm-free single-trace 판정기에 한정된다. ⑤ 무엇 부족? 관계 속성에 필요한 **다른 실행 관측과 정상 허용 판단**. ⑥ 다른 분야? HyperLTL/secure multi-execution/IFC가 직접 반박. ⑦ 왜 중요? 사용 목적 제한은 호출별 allow보다 강한 보안 속성이지만, 의미 있는 정상 비교 기준이 있어야 한다.

## R07. 형식 정책 검증은 이미 존재하는 해결 경로

**Problem Statement / 예.** 지정된 정책에 모순·타입 오류·예상치 못한 허용 범위가 있는지 확인한다. 예컨대 특정 데이터셋만 읽도록 만든 규칙이 전체 상위 리소스까지 허용하는지 정책 간 포함관계로 검사할 수 있다.

**이미 해결한 범위.** [Margrave](https://web.cs.wpi.edu/~kfisler/Pubs/icse05.pdf) §§1–3은 정책 속성과 변경 영향 분석을, [ZELKOVA](https://kasperluckow.com/papers/fmcad2018.pdf) §§I–IV는 IAM 정책의 SMT 분석을, [Cedar](https://arxiv.org/html/2403.04651) §§2.5–2.6/§4.4는 schema·동치·포함·반례를 제공한다. [AWS AgentCore Policy 공식 문서](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/policy-generation-validation.html) §How it works/Common findings는 생성 정책에 schema 검증과 `ALLOW_ALL`/`DENY_ALL` 류 탐지를 적용한다. [Progent](https://arxiv.org/html/2504.11703) §4.3/§6은 승인 없는 갱신이 권한을 확대하지 않는지 SMT로 검사한다. 이들은 언어·모델·정해진 명세에 대한 서로 다른 보장이다.

**잔여 문제와 근거.** Cedar policy가 사용자 승인과 의미상 일치하는지는 자동으로 나오지 않는다([AutoCedar](https://arxiv.org/html/2607.03656) §VI, **A**). FAVA의 SMT도 추출된 graph와 정책에 상대적이고 obligation 누락 시험이 있다([FAVA](https://arxiv.org/html/2607.27267) §RQ5/Fig. 5, **D**). 이것은 **R02/R04의 조건**이지 형식 포함·충돌 검사가 없다는 뜻이 아니다.

**가장 강한 반박 / 신규성.** 지원 언어와 올바르게 정형화한 요구조건에 한하여 `RESOLVED`. 새로운 형식 checker 자체가 Need라는 주장은 기존 연구가 직접 반박한다. 추가 검증은 특정 agent 정책 언어가 이 도구들로 표현 가능한지와 comparator에 주는 명세가 독립적으로 검토되었는지 확인하는 문헌 읽기면 충분하다.

**필수 7개 반박.** ① 이미 해결? 위 네 계열에서 예. ② 구현 누락? 기존 analyzer/SMT 적용으로 풀릴 수 있다. ③ 잘못된 정책? 의미가 틀리면 형식 검사는 그것을 교정하지 않는다. ④ 위협 모델? 지원 언어·모델 밖 규칙은 분석 대상 밖이다. ⑤ 무엇 부족? 이 항목에서는 보통 표현·모델링 범위이고 R02의 의미 입력과 구별한다. ⑥ 다른 분야? XACML/IAM/ABAC·SMT·symbolic reasoning이 선행. ⑦ 왜 중요? 정책 확대와 충돌은 업무와 보안에 영향이 있지만 기존 해결 경로가 충분히 성숙했다.

## 최종 판정: 확인된 잔여 조건과 아직 미확인인 신규성

**문헌상 충분히 확인:** (1) 지속 grant가 task·실행 맥락을 벗어나면 공격 성공을 높일 수 있으며 exact-resource 매칭만으로는 충분하지 않은 시험 조건이 있다(R01, **D**). (2) 자연어→정책 변환의 의미 오류는 정형 검증·역번역·검토 절차 뒤에도 평가상 남았다(R02, **D**). (3) 인증된 출처와 그 출처가 제공한 값의 적절성은 다르며 실제 보안/정상업무 양쪽 오류가 관측됐다(R03, **D**). (4) provider 인터페이스가 효과 시점의 비교·fence를 제공하지 않으면 특정 경로에서 호출 시점 승인만으로 원하는 속성을 유지할 수 없다(R04, **D**). (5) MAS의 권한 증거는 현재 caller와 원천 승인·위임 축소를 구분해야 한다(R05, **D/A**). (6) 일부 목적 정책은 단일 실행의 개별 허용으로 판별할 수 없는 관계 속성이다(R06, **형식 정리**).

**현재 확정하지 못함:** 이 조건들에 ConLeash, task-scoped authorization, PAuth/PACT/ROPE, source-authenticated evidence, Cedar/SMT, CONTINUITY, CTA, provider-native precondition/fence, 전통적 capability/IFC/hyperproperty 기술을 올바르게 조합해도 **보안과 정상 업무를 함께 만족할 수 없는** 일반적인 Agent/MAS 접근통제 문제가 무엇인지는 현재 원문 근거로 확정할 수 없다. 이번 조사에서 `OPEN_WITH_EVIDENCE`로 분류한 독립 Need는 **없다**. 이는 연구가 존재하지 않거나 향후 Need가 없다는 뜻이 아니라, 접근 제한 문헌과 동일 조건의 대안 비교를 포함한 추가 확인이 필요하다는 뜻이다. SSRN [*Authorization-Preserving Context Lifecycles*](https://papers.ssrn.com/sol3/Delivery.cfm/7580538.pdf?abstractid=7580538&mirid=1)와 ACM [*Ghost Approvals*](https://doi.org/10.1145/3847352.3848101)·[*ContractGuard*](https://doi.org/10.1145/3830454.3846789)는 본문 접근 제한으로 세부 효과·한계를 판정에 넣지 않았다.
