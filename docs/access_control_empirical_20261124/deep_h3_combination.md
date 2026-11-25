# H3 교집합 감사: 간선 철회 × 대안·합의 승인 × 비동기 효과

검토일: 2026-11-24 UTC. **결과: 같은 세 조건을 한 보증과 한 실제 평가에서 모두 입증한 공개 연구는 이번 좁은 탐색에서 확인하지 못했다. 현실 provider에 대한 판정 `UNVERIFIED`.** 이 명제는 “그런 연구가 존재하지 않는다”는 전수 조사 결과도, 새 Research Gap의 증거도 아니다. [H3 상세 대조](deep_h3.md)의 원문 검토에 `AID-Guard`와 2026-10 개인 IETF 초안을 더했다. 유료 API·실서비스 실행 0. [로컬 최소 실험](runs/H3_edge_fence/result.md)은 조건부 합성 대조군을 통과시켰으며 원저자 재현이 아니다.

**API 버전 갱신:** EffectBound의 GitHub MCP SHA 조건 누락은 저자가 고정한 2026-08-22 revision에만 적용된다. 공식 서버는 [2026-09-01 PR #3182](https://github.com/github/github-mcp-server/pull/3182)에서 `expectedHeadSha`를 추가했다. 현재 인터페이스의 H3 Gap 근거로 재사용할 수 없다. [원본 revision 비교와 판정](h3_gap_verdict.md).

## 질문을 좁게 고정

대상은 **중간** 위임 간선 e=A→C의 철회다. C에게 X→C라는 별도 충분 경로가 있거나 A와 X가 모두 필수인 합의 조건이 있다. 철회 전 큐·콜백·provider에 도달한 작업이 이후 실제 효과 승인 경계까지 간다. 확인할 성질은 (1) e에만 의존한 후속 commit 0, (2) X의 독립 충분 승인으로 진행하는 정상 commit 허용, (3) A∧X에서 A 철회 뒤 commit 0, (4) 철회 전 **이미 수락한** provider commitment의 정산 의미를 별도 기록하는 것이다. `tool deny`, `간선 target`, `provider commit`을 한 결과로 섞지 않는다.

## 가장 가까운 원문·공식 artifact 대조

| 1차 자료 | 직접 다루는 교집합 | 빠진 필수 요소/평가 경계 |
|---|---|---|
| [VERA §III–VII, IX](https://arxiv.org/html/2608.30091), [저자 연결 artifact](https://anonymous.4open.science/r/ictai2026-agent-revocation-artifact-14BA/README.md) | 서명된 다중 부모 DAG의 **특정 간선** 철회 대상과 독립 OR 경로 보존. E16의 500 trace/500 target proof, 320/320 대안 부모 보존. | AND/threshold 승인은 원문이 명시적으로 제외. 캐시된 철회 전파·provider effect fence는 범위 밖. A2A·CrewAI 관련 추가 trace는 스키마 이식성 중심. |
| [Authorization Revocation §3–7, §10](https://arxiv.org/html/2609.21284) | 최소 충분 root 집합의 antichain으로 OR/AND, selected witness, atomic rebind, **root-epoch cut**과 비동기 provider fence/정산. 저자 구현은 provider-free 17 등록 사례·44 checker 변이. | 중간 간선 e를 독립 철회 연산으로 보증하거나 평가했다는 근거 없음. 보증의 분모는 완전 manifest와 A1–A9 성립 시의 **root** shutdown. |
| [AID-Guard §III-D–F, §VI](https://arxiv.org/html/2608.21159) | root 철회와 provider commit의 순서, 단일 예약 계보의 중복 방지·응답 손실/회복. provider 계약에 따라 원자 commit 또는 정확한 idempotency+delivery fence. Stripe test-mode 210 trial 등 실제 provider 계약 평가. | 중간 위임 간선 target, 다중 부모 OR/AND를 한 모델에서 다루지 않음. 저자는 root 철회가 **이미 제출된** 요청을 소급 취소하지 않는다고 명시한다. 구현 투영은 한 authorization/reservation lineage의 유한 일정. |
| [CTA v2 §3–6](https://arxiv.org/pdf/2607.10487v2), [EffectBound §IV–VI](https://arxiv.org/html/2609.02866) | 현재 한 승인 후보의 정확한 효과 원자 검사, 또는 provider API가 Bind/Re-enter/Fence를 제공하는지 판정. 후자는 GitHub·NATS·Kubernetes·Kafka 6경로 실험. | 둘 다 다중 부모 **중간 간선** 철회 의미 자체를 정하지 않는다. provider API가 효과 제어를 제공하면 H3의 최종 부분에 강한 기존 해법이 된다. |
| [CONTINUITY §5–8, §12](https://arxiv.org/html/2609.05269), [로컬 R2/R3](../R3_GAP_VERDICT.md) | 원본 permit의 grant/policy/revocation 재검사와 효과 결속. R2의 18조건, R3 원본 정의 범위 4조건은 별도 합성 A2A 통합 관측. | RootGrant 간 부모 간선/독립 지원/합의 승인 의미가 없음. R2/R3는 한 인메모리 effect 경로이며 실제 provider finality와 결합 실험이 아니다. |

## 새로 찾은 직접 대안: DAS 개인 IETF 초안

[Part 10 초안](https://datatracker.ietf.org/doc/html/draft-das-cross-device-authority-revocation-00) §18.35–18.36은 cross-provider 위임 철회, receiver sink fence, 다중 부모의 conjunctive/alternative/threshold 의미와 실제 sink의 현재 권한 검사를 **같은 문서에서 명시**한다. [Part 5 초안](https://datatracker.ietf.org/doc/html/draft-das-multi-agent-authority-control-00) §7.3–7.6은 위임 간선, 계보, sink의 개념 구조를 설명한다. 따라서 “문헌 어디에도 이 조합의 구상이 없다”는 주장은 **기각**한다. Datatracker는 이들이 개인 제출 Internet-Draft이며 IETF 승인·표준 지위가 없다고 명시한다. Part 10의 §18.64 Experiment 12–20(합의, 대안, 철회/commit race 등)은 **제안 실험**이며 완료 측정이 아니다.

초안이 직접 연결한 [공식 실험 동반 코드](https://github.com/sangmdas/ios-android-ai-execution-finality)를 `third_party/h3_das_finality/`에 원본 SHA `0c87d8b0c7590fef8405679501441b4e3c1ab427`로 별도 확보했다. checkout은 검사 시 clean이었다. 라이선스는 [비상업 연구·평가용 custom license](https://github.com/sangmdas/ios-android-ai-execution-finality/blob/main/LICENSE-STATUS.md)이며 patent license를 주지 않는다. 설치·실행·수정하지 않고 원본 README·`src/dasfinality/engine.py`·`docs/TEST_MATRIX.md`·`docs/LIMITATIONS.md`·tests만 정적으로 읽었다.

**코드가 실제로 보인 것:** `engine.py`의 SQLite `grants`는 한 `grant_id`와 active/generation을 저장하고 `revoke(grant_id)`로 개별 grant를 무효화한다. 부모 간선/다중 충분 witness/AND 정책/remote provider fence 데이터 모델은 이 파일에 없다. `docs/TEST_MATRIX.md`의 400 사례는 로컬 canonicalization·grant scope·nonce·quota·일회 효과·crash/ACK 등 190+210 모델 테스트다. `docs/LIMITATIONS.md`는 효과가 SQLite row이고 remote distributed atomic commit과 독립 외부 효과 증거가 없다고 명시한다. 그러므로 초안의 세 부분을 **같은 구현/평가에서 검증했다는 근거는 아직 없다.** 저자 400/400은 해당 로컬 모델 결과이지 이번 감사의 재실행 수치가 아니다.

## 문헌 부재와 Gap의 거리

현재 있는 것은 **보증의 분할**이다: VERA는 e의 정확한 대상과 OR 정상 보존, Revocation은 root 기반 OR/AND + 비동기 fence, CTA/EffectBound/AID-Guard는 실제 commit 경계의 강한 통제를 제공한다. 개별 보증을 나열해도 세 부분의 합성 정리는 나오지 않는다. 반대로 한 논문이 합성 정리를 명시하지 않았다는 사실만으로 기존 접근통제·분산 프로토콜의 올바른 조합이 실패한다는 뜻도 아니다. **증거가 필요한 잔여 명제**는 “e의 권한 의존을 selected support에 정확히 결속하고, 그 변경을 provider 수락 경계에서 원자적으로 관측하게 해도 비인가 commit이나 독립 정상 작업의 부당한 거부가 생긴다”이다. 현재 그런 실행/불가능성 증거는 `NOT_ESTABLISHED`다.

이 잔여는 세 종류로 먼저 분해해야 한다. (a) 간선 e가 실제로 **권한** 위임인지 단지 작업 전달인지 불분명하면 정책 의미 문제, (b) e→support 매핑과 정산 중재가 누락되면 계측/구현 전제 문제, (c) provider가 필요한 조건부 쓰기·fence를 제공하지 않으면 [EffectBound](https://arxiv.org/html/2609.02866)의 특정 API realizability 문제다. (b)/(c) 관측만으로 범용 MAS Gap을 주장하지 않는다.

## 가장 작은 반증 분석·실험: 로컬 추상 sink 실행, 현실 provider 미확인

1. **정형화:** DAG `R→A→C`와 `X→C`를 고정했다. 중간 간선 `a_c`에 대해 충분 witness는 OR `{{a_c},{x_c}}`, AND `{{a_c,x_c}}`, A 단독 `{{a_c}}`로 둔 **독립 합성 규칙**이다. VERA 원본 `target_set_l2(a_c)`는 A 경로만 있으면 `{C}`, X 경로가 있으면 `∅`였다. 이는 node-level target이고 selected provider witness가 아니다. [사전등록](runs/H3_edge_fence/prereg.md)과 [원시 로그](runs/H3_edge_fence/raw.json)에 입력과 결과를 고정했다.
2. **최강 추상 대조군:** C의 요청은 action digest와 selected edge witness를 포함한다. 로컬 sink의 하나의 임계구역에서 간선 상태·fence와 witness를 검사해 receipt를 원자 수락한다. 철회 뒤 A 단독/AND의 새 수락·effect는 모두 0, X를 명시 선택한 OR 정상 effect는 1이었다. 철회 전 이미 수락한 A receipt의 나중 정산 effect 1은 `pre_fence_receipt_settled_later`로 구분했다. 검사 생략 음성 대조군의 post-fence effect 1은 예상된 구현 실패다. [결과·명령·해시](runs/H3_edge_fence/result.md).
3. **판정 경계:** 위 추상 전제에서 “새 메커니즘이 반드시 필요하다”는 조건부 가설은 `REJECTED_HYPOTHESIS`다. 현실 provider에 대한 종합 판정은 `UNVERIFIED`다. fixture는 원본 VERA 대상 함수만 직접 호출했고, signer·provider 네트워크·동시 race·크래시·정산 계약은 평가하지 않았다. 초기 import는 무관한 `cryptography` 의존성 때문에 실패했고, 원본 두 모듈만 읽는 namespace shim으로 두 번째 실행에 성공했다.
4. **Gap 지지의 추가 문턱:** 최강 대조군의 전제가 실제 허가된 provider API에서 만족되는지 확인한 뒤에도 안전 또는 정상 완료가 깨져야 한다. 구현 실수·불완전한 manifest·잘못된 target의 실패라면 그 원인으로 분류한다. provider가 효과 경계의 원자 조건을 제공하지 않는다면 해당 API 제한과 [EffectBound](https://arxiv.org/html/2609.02866)의 기존 대안부터 평가한다.

**다음 문헌 확인:** DAS 초안 Part 10/5의 새 판본·artifact 시험 커버리지, Authorization Revocation의 공개 코드 출현, AID-Guard의 실행 artifact 위치를 버전 고정으로 재확인한다. 지금은 연구 Need를 선언하지 않는다.
