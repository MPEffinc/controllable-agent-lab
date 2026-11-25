# 추가 Gap 후보·강한 반박 스캔 — 2026-11-24

이 문서는 K01–K15 밖의 후속/대안 원문을 직접 읽고 **가설을 좁히거나 기각하기 위한** 기록이다. 저자 수치는 이 세션의 실행 결과가 아니다. `WATCH`는 검토 우선순위이지 `GAP_SUPPORTED`가 아니다.

| 후보 조건 | 직접 원문 근거 | 가장 강한 현재 반박 / 위협 모델 차이 | 판정·반증 조건 |
|---|---|---|---|
| 승인한 tool 호출의 **하위 프로세스 효과**가 승인 텍스트보다 넓다 | [Approval Laundering §II–V, Table II](https://arxiv.org/html/2609.38983)는 Claude Code coding harness의 Scope/Argument/Tool/Delegation/Temporal/Semantic 양식을 분리. [§VII–IX](https://arxiv.org/html/2609.38983)는 HMAC Approval Token이 Delegation 및 지정 Temporal 사례를 줄였지만 Scope와 Argument의 하위 효과는 그대로 남았다고 보고. Argument는 저자 실험에서 9/20. | Token은 **기록된 dispatch field만** 검증한다. [OpenShell](https://docs.nvidia.com/openshell/v0.1.9/how-it-works/policies/overview)의 OS/network PEP, [FORGE §4](https://arxiv.org/html/2602.16708v4)의 instrumented action PEP, [EffectBound §V/Table III](https://arxiv.org/html/2609.02866)의 provider 조건부 effect는 다른 계층에서 대응할 수 있다. 논문의 non-adversarial Claude Code 측정·특정 승인 텍스트를 일반 MAS로 전가할 수 없다. | `WATCH`: 해당 **동일 작업**의 정상 완료를 유지하면서 하위 효과를 각 기존 PEP로도 막지 못한 관측이 나오면 좁은 Gap 후보. OS/IFC/provider 집행이 막으면 기각. |
| Agent가 외부 서비스·계정·자격증명 등 **새 권한을 획득**한 뒤 활성화 | [AcquireBound §§1.1, 3–5, 7](https://arxiv.org/html/2609.14744)은 반환된 실제 capability를 provider evidence로 해석해 quarantine→현재 activation transaction→effect permit을 제안. 저자 평가는 5 resource class의 60 base fixture, 40 refinement, Docker/MCP 합성 경로를 구분. [§1.4, §10.3](https://arxiv.org/html/2609.14744)는 등록된·결정 가능한 profile, 인증된 출력, 완전 중재를 보장 전제로 명시. | **직접 해결 연구가 이미 있다.** 결핍은 특정 provider의 실제 출력·alias·effect를 인증/열거할 수 있는가라는 배포 조건. 이 조건을 명시하지 않고 “동적 capability 통제 연구 부재”라고 주장하면 기각된다. | `RESOLVED_IN_SCOPE`/실제 provider 일반화 `UNVERIFIED`. 같은 resource class에서 기존 registered profile이 요구한 evidence가 현실 API에 없고 우회 가능한 효과가 관측되면 다시 열기. |
| Planner가 보는 작업공간과 외부 승인 상태가 달라 잘못된 행동을 제안 | [From Evidence to Effect §5/Table 3](https://arxiv.org/html/2609.08472)는 128-cell 통제 평가에서 원시 권위 receipt와 typed 관계가 모두 32/32, 권위 정보가 없는 두 조건은 0/32였다고 보고. 같은 연구의 matched-intent 실행 guard가 unsafe intent 효과를 막음. | 필요한 사실을 주면 planner 성능이 개선되며, 실행 경계 guard는 planner 오류가 있어도 효과를 막는 **직접 대응**. Typed packaging 자체의 추가 효과는 원시 정보와 같은 통제 조건에서 보이지 않았다. | “모델에게 typed 권위를 보여 주면 안전” 가설은 `REJECTED_HYPOTHESIS`. 새 Need는 정보 제공/집행 guard가 같은 조건에서 모두 실패할 때만. |
| MAS 하위 에이전트가 넓은 bearer credential을 재사용 | [Delegation Without Trust §§3–7](https://arxiv.org/html/2609.00267)은 4 위협/8 요구를 정의하고 broker의 참조 평가를 제시. | [Multi-CaMeL §VI](https://arxiv.org/html/2610.05640v1#S6), [PAuth §III–IV](https://arxiv.org/html/2603.17170v2), [CONTINUITY §§3–6](https://arxiv.org/html/2609.05269)의 서로 다른 신뢰/권한 결속과 함께 **강한 선행 대안**. Broker의 성능 수치를 다른 threat model에 이식하지 않는다. | 넓은 bearer 권한의 위험은 확인된 문제지만 “해법 없음”은 `REJECTED_HYPOTHESIS`; 교차 provider·복합 위임의 미평가 조건은 `UNVERIFIED`. |

## 현재 우선순위

1. Approval Laundering의 **하위 효과**는 실제 관측과 proposed token의 음성 결과가 있어 유심히 본다. 그러나 OS·IFC·provider PEP가 같은 정상 업무를 보존하면서 해결하는지 먼저 확인한다.
2. AcquireBound는 동적으로 얻은 권한이라는 후보를 직접 해결한다. 새 Gap 주장은 등록 profile·실제 provider evidence·완전 중재가 실패하는 **구체 경로**가 있어야 가능하다.
3. K06 target mismatch는 [hypotheses.md](hypotheses.md)의 H1로 유지한다. 위 논문들의 권위 정보·effect 검사는 목표 자체가 잘못 승인된 문제를 자동 해결하지 않는다.

### H3 결합에 대한 후속 선행 대조

[개인 IETF Internet-Draft Part 10](https://datatracker.ietf.org/doc/html/draft-das-cross-device-authority-revocation-00)은 cross-provider 철회, 다중 부모 승인과 sink 검사를 한 문서에서 제안한다. Datatracker는 이 초안이 **IETF 승인/표준이 아니라고 명시**한다. [저자 연결 코드](https://github.com/sangmdas/ios-android-ai-execution-finality)는 로컬 SQLite grant/효과 모델이며, 중간 간선·OR/AND support·원격 비동기 commit의 한 평가를 제공한다는 근거는 찾지 못했다. [코드/절/라이선스 감사](deep_h3_combination.md). 따라서 조합 아이디어의 부재 주장은 기각하고, 동일 구현·효과 검증은 `UNVERIFIED`로 둔다.
