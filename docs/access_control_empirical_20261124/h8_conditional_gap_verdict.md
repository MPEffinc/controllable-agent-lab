# H8 좁은 판정: 자연어 조건부 권한의 NGAC export와 실제 effect

2026-11-24 UTC. **`GAP_SUPPORTED`의 정확한 범위:** K07 NGAC-IR의 정적 Policy Machine graph export만으로는 조건부 허용을 안전성과 정상 완료 양쪽을 만족하게 집행할 수 없다. 논문은 이 차이를 스스로 인정한다. **평가 지식 공백:** 논문이 권하는 strict export→애플리케이션 조건 검사를 실제 서비스 effect와 정상 업무로 검증하지 않았다. 우리의 공식 NIST PM 최소 실험은 정적 graph의 tradeoff를 독립 재확인했지만 **NGAC-IR 생성기 재현은 아니다**. 새 보안 메커니즘 Need는 기존 대안이 있어 `UNVERIFIED`다.

## 고정 조건과 직접 증거

`read(doc)`는 신뢰된 `registration_open=true`에만 effect 1, false에는 effect 0이어야 한다. [NGAC-IR v1 §5.1](https://arxiv.org/html/2611.26941v1)은 broad export가 조건부 허용 98/715개를 무조건화한다고 보고하고, strict export는 조건부 허용을 PM에서 제외해 390 graph 요청 중 23개를 더 거부한다고 보고한다. 저자는 **조건부 prohibition은 strict에도 항상 적용**되어 정상 허용을 더 거부할 수 있다고 명시한다. 390은 **컴파일된 graph에 대한 결정 replay**이며 자연어 의도나 앱 PEP effect가 아니다.

| 동등한 작은 요청 | [공식 NIST PM 3.3.0 독립 실행](runs/K07_condition_boundary/result.md) | 실제 로컬 effect |
|---|---|---|
| broad graph / false | PM Allow, PDP 실행 | **1**: 정의된 조건의 과허용 |
| broad graph / true | PM Allow, PDP 실행 | 1: 정상 완료 |
| strict graph / false | PM Deny | 0: 안전 |
| strict graph / true | PM Deny | **0**: 정상 거부 |
| broad graph + 앱 사전 조건 / false | PM graph는 Allow지만 앱이 PDP 호출 전 차단 | 0: 안전 |
| broad graph + 앱 사전 조건 / true | 앱 통과, PM Allow | 1: 정상 완료 |

각 행은 새 in-memory graph와 ledger로 실행했다. 앱 사전 조건 구성은 **우리의 별도 대안**이며, 논문이 제시한 `strict export + 조건부 허용 목록을 앱이 처리` 구현을 그대로 시험한 것이 아니다. 원본 K07 저자 코드는 확인한 공개 경로에서 미확보. Policy Machine 자체는 주어진 graph를 충실히 집행했다. [원시 결정 6행](runs/K07_condition_boundary/decisions.jsonl), [명령·고정 코드·해시](runs/K07_condition_boundary/result.md).

**고정 graph-only 경계의 이유:** 동일한 graph와 동일한 사용자·행동·자원 요청을 PM에 주면 외부 `registration_open` 값은 PM 입력에 없으므로 두 상태의 PM 결정은 같다. 원래 의도는 두 상태의 결정이 달라야 한다. 따라서 graph를 상태에 맞춰 신뢰되게 갱신하거나, 조건을 검사하는 다른 PEP를 결합하지 않는 한 이 고정 구조로 두 상태를 동시에 만족할 수 없다. 이는 동적 graph 갱신이나 조건식 PDP의 불가능을 주장하는 증명이 아니다.

### 2026-11-25: 여러 허용 경로·조건부 금지로 넓힌 독립 대조

[사전 등록한 공식 NIST PM 3.3.0의 7조건](runs/K07_route_composition_20261125/result.md)은 의도를 `(registration_open OR alternate_allow) AND NOT embargo_active`로 고정했다. `registration_open=false`여도 별도 `alternate_allow=true`인 정상 요청에서 **전역 앱 gate는 effect 0**, 경로별 gate는 effect 1이었다. 조건부 금지가 `embargo_active=false`인데도 PM graph에 항상 export되면 **PM이 Deny해 경로별 gate 뒤에도 effect 0**이었다. 금지가 실제 활성일 때의 Deny/effect 0은 맞았다. 이는 저자 K07 생성기나 저자 strict+앱 adapter의 실행이 아닌 **독립 구성 실험**이며 7개 설계 행은 발생률이 아니다.

같은 의미를 규칙별 permit 두 개와 조건부 forbid로 쓴 [공식 Cedar CLI 6조건 대조](runs/K05_route_composition_20261125/result.md)는 비인가 false/no-alternate와 활성 embargo effect 0, 독립 경로·조건 참 정상 effect 1로 6/6 기대와 일치했다. 따라서 **전역 앱 gate의 과거부와 정적 금지 상시 export의 과거부**는 구체적으로 관측됐지만, 이 작은 조건을 해결할 기존 정책 언어/방법 부재 주장은 기각된다. Cedar도 신뢰된 최신 context와 실제 effect PEP 연결을 전제한다.

## 같은 조건의 강한 기존 반박

- [Cedar의 request context와 `when`](https://docs.cedarpolicy.com/auth/authorization.html)은 조건을 PDP 안에서 평가한다. [조건부 permit 공식 CLI 독립 대조](runs/K05_conditional_alternative_20261124/result.md)에서 같은 `read(doc)`의 false는 Deny/effect 0, true는 Allow/effect 1이었다. [조건부 prohibition 대조](runs/K05_conditional_prohibition_20261125/result.md)는 무조건 permit과 조건부 forbid가 함께 있어도 false에서 Deny/effect 0, true에서 Allow/effect 1을 확인했다. 조건값을 앱이 정확히 공급하고 결정을 effect 전에 적용하는 것이 전제다.
- [OASIS XACML 3.0](https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html)은 environment/request attributes로 조건을 표현한다. 이는 문서상의 표현·평가 대안이며 이번에 XACML engine을 실행한 것은 아니다.
- K07 자체도 strict export와 앱 조건 검사를 제안한다. 원문이 `app check`의 효과를 측정하지 않았다는 사실은 그 경로가 실패했다는 관측이 아니다. NGAC의 event obligation으로 상태 변경에 맞춰 graph를 갱신하는 설계 역시 검토할 수 있지만, 신뢰된 이벤트 전달·결정과 효과의 시점 관계를 따로 검증해야 한다.

## 남은 Research Need와 기각 조건

**실증 평가 Need:** 동일 자연어 원문을 조건이 포함된 IR, graph, 앱에 전달되는 조건부 허용 목록으로 추적하고, true/false와 조건 전환을 모두 포함해 **최종 effect/정상 완료/false denial/검토 비용**을 측정해야 한다. 특히 strict export에서 PM Deny를 앱이 어떻게 정상 조건 Allow로 합성하되 기존 prohibitions를 우회하지 않는지, 반대로 **조건이 거짓인 prohibition의 항상 적용으로 생기는 과거부를 어떻게 처리할지** 명시해야 한다. 별도 무조건 허용 route는 전역 gate에 눌리지 않아야 한다. 이 결합 semantics는 현재 K07 논문 390 graph replay나 우리의 **저자 구현과 다른** PM 대조로는 입증되지 않았다. 원저자 코드 공개 시 같은 case ID·판본으로 재검증한다.

**신규 메커니즘 Need 기각 조건:** 권한의 정확한 조건과 신뢰된 최신 상태를 가진 Cedar/XACML PDP, 제대로 합성한 앱 PEP, 또는 NGAC의 안전한 동적 graph 갱신이 동일 정상 task와 비인가 효과를 합리적 비용에서 처리하면 “새 집행 방법이 필요하다”는 주장을 버린다. 이번 Cedar 및 broad+앱 대조는 고정 bool 조건에서는 이미 그 반례다. 조건의 출처가 거짓이거나 효과 시점에 상태가 바뀌는 문제는 별도 정보 신뢰·원자성 문제로 구분한다.
