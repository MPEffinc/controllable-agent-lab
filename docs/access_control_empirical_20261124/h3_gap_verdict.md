# H3 좁은 Gap 판정: provider API 제약 × 중간 간선 철회 × OR/AND

검토 기준일: 2026-11-24 UTC. 결론: **새롭고 독립적인 Research Gap/Need는 `UNVERIFIED`**. 실제로 관측·증명된 좁은 API 제약은 있지만 [EffectBound](https://arxiv.org/html/2609.02866) 자체가 이미 설명했고, 가장 구체적인 GitHub MCP 제약은 공식 서버의 이후 변경으로 수정되었다. 세 조건의 결합에서 강한 기존 해법이 실패한다는 관측은 없다. 이번 조사는 원문·공식 소스 read-only 비교이며 provider 서비스 호출, 유료 API, 공격 실험은 0이다.

## 고정할 보안 속성

중간 위임 간선 `e=A→C`와 독립 `X→C`가 있다. 한 효과의 최소 충분 승인 집합은 OR `{{e},{x}}`, AND `{{e,x}}`처럼 명시한다. `e` 철회 뒤 **새 provider 수락**은 e 의존 witness로 0이어야 하고, 독립 X만 충분한 정상 업무는 허용되어야 한다. 철회 전에 provider가 이미 수락한 commitment는 별도 receipt로 정산한다. **물리적 효과 발생 시각 기준 즉시 철회**를 요구한다면 이는 더 강한 다른 계약이며, pre-fence 수락의 소급 취소 능력을 따로 확인해야 한다. [Authorization Revocation §4.4](https://arxiv.org/html/2609.21284)의 sink-local fence/receipt 정의와 [AID-Guard §III-D](https://arxiv.org/html/2608.21159)의 제출 선형화·비소급 의미가 이 구분을 요구한다.

## 가장 강한 반박과 버전 교정

| 자료 | 실제 해결 범위 | 이 질문에서 남는 전제 |
|---|---|---|
| [EffectBound §III–V, Table III](https://arxiv.org/html/2609.02866) | provider 인터페이스의 모든 노출 제어를 둔 유한 계약에서 안전·필수 정상 완료 동시 가능성을 검사한다. GitHub의 **당시 고정 MCP 서버**는 reviewed head SHA를 merge와 원자 결속하지 못했고, 25/25 moved-head 재생에서 비인가 head merge, SHA Bind 대조 0/25·정상 25/25였다. 공식 MCP end-to-end 확인은 별도 1회다. 이 계약은 안전한 merge이지 철회 lineage closure 주장은 아니다. | 분석자가 effect frontier, 제어 inventory, 정상 workload를 정확히 제공해야 한다. 외부 e의 승인 상태를 GitHub merge에서 원자 검사하는지는 이 사례의 검증 목표가 아니다. |
| [GitHub MCP PR #3182](https://github.com/github/github-mcp-server/pull/3182), [현재 공식 소스](https://github.com/github/github-mcp-server/blob/b8f107b9ceb0cfeef8f22f629e39c15bb27522c4/pkg/github/pullrequests.go#L1516), [REST 문서](https://docs.github.com/en/rest/pulls/pulls#merge-a-pull-request) | **2026-09-01 13:12 UTC 병합**된 공식 수정이 optional `expectedHeadSha`를 MCP `merge_pull_request`에 추가하고 REST `sha`로 전달한다. REST는 head 불일치 시 409다. 이 필드를 **실제로 전달하는** 현행 클라이언트는 EffectBound의 동일한 moved-head 조건에 대한 제어를 얻는다. | optional이라 생략하면 이전 위험이 남는다. SHA는 PR head identity를 묶을 뿐 `e`의 현재 권한이나 OR/AND 선택을 공급하지 않는다. 실 배포 버전·tool schema·클라이언트가 필드를 쓰는지 확인 필요. |
| [CTA v2 §3–4, Table 20](https://arxiv.org/pdf/2607.10487v2) | 하나의 완전한 승인 후보를 효과 원자 sink에서 재선택하고, stale 후보 대신 독립 current 후보를 허용한다. 정책 필수 claim에 AND 조건을 담을 수 있고, multi-agent branch epoch도 예시다. | 모든 보호 효과의 원자 sink 중재와 올바른 policy/evidence 필드가 전제. 외부 provider가 해당 조건을 원자 지원하지 않으면 이 증명은 바로 적용되지 않는다. 파생 lease는 source 철회 뒤 만료까지 유효할 수 있다. |
| [AID-Guard §III-D, §IV, §VII-B](https://arxiv.org/html/2608.21159) | H3/D2에서 현재 authority graph·정확한 request·provider precondition을 재검사한다. 본문은 checked-edge mutation이 durable submission보다 앞서면 거절, 뒤면 기존 제출은 비소급 정산이라고 한다. atomic 또는 scoped idempotency·terminal query·delivery fence가 있는 provider 계약에서 retry/복구를 제한한다. | 저자 평가의 unit은 하나의 reservation lineage와 선언한 provider 경로다. VERA식 특정 중간 간선의 OR/AND selected witness 및 X rebind가 같은 provider 평가에서 검증됐다는 근거는 찾지 못했다. 약한 provider는 모호 상태를 charged/uncertain으로 유지하며 자동 재시도하지 않는다. |
| [Authorization Revocation §4–7](https://arxiv.org/html/2609.21284), [VERA §III–VII](https://arxiv.org/html/2608.30091) | 전자는 OR/AND 충분 root support antichain·selected witness·atomic X rebind·provider leaf fence/receipt의 조건부 보증; 후자는 특정 중간 간선 삭제 때 대안 경로를 보존하는 target을 계산한다. | 전자의 cut 원자는 **root epoch**, 후자의 target은 **node reachability**이며 서로 곧바로 동치가 아니다. e→요청별 selected support 매핑과 provider receipt를 합쳐 증명한 공개 평가가 필요하다. |
| [DAS Part 10 개인 Internet-Draft §18.35–18.36](https://datatracker.ietf.org/doc/html/draft-das-cross-device-authority-revocation-00), [공식 동반 저장소](https://github.com/sangmdas/ios-android-ai-execution-finality) | 중간 위임·대안/합의 승인·sink fence 조합을 **개념적으로 명시**한다. 따라서 “조합 자체를 누구도 제안하지 않았다”는 주장은 기각한다. | 개인 I-D이며 IETF 승인·표준 지위가 없다. 동반 저장소의 400 로컬 테스트는 단일 grant/SQLite 효과 중심이고 이 결합의 원격 provider 실행 근거는 아니다. [코드·평가 감사](deep_h3_combination.md). |
| [우리 H3 fixture](runs/H3_edge_fence/result.md) | VERA 원본 `target_set_l2` 호출 + **독립** 원자 메모리 sink: e 철회 후 A 단독/AND 신규 효과 0, X OR 정상 효과 1, pre-fence receipt의 늦은 정산 별도 1. | 네트워크 provider, 동시 race, 크래시, 실제 e→support attestation을 시험하지 않았다. 따라서 가능한 조합의 대조군이지 실제 provider 보증이나 저자 재현이 아니다. |

### GitHub MCP 시간축을 재검증한 방법

[EffectBound가 고정한 공식 소스 `64a49f34`](https://github.com/github/github-mcp-server/blob/64a49f34/pkg/github/pullrequests.go#L1487)의 `MergePullRequest` 함수에는 `expectedHeadSha`가 없었다. 공식 GitHub API에서 [PR #3182](https://github.com/github/github-mcp-server/pull/3182)의 `merged=true`, `merged_at=2026-09-01T13:12:27Z`, merge SHA `b8f107b9ceb0cfeef8f22f629e39c15bb27522c4`를 읽었다. 그 merge SHA의 같은 함수에는 `expectedHeadSha` 입력과 `PullRequestOptions.SHA` 전달이 있다. 두 revision의 원본 `pullrequests.go`를 **실행 없이** read-only로 비교했다. 현재 `main`에도 필드가 있다는 [공식 소스](https://github.com/github/github-mcp-server/blob/main/pkg/github/pullrequests.go)와 README를 확인했다. 따라서 “2026-11-24 GitHub MCP는 SHA 조건을 노출하지 않는다”는 판정은 **`REJECTED_HYPOTHESIS`**이고, 당시 고정 버전에 대한 EffectBound의 결과는 그대로 유효하다. 현행 release binary/연동별 배포 버전은 검사하지 않았다.

## 좁은 후보의 현재 판정

| 가설 | 강한 반박 / 실험 근거 | 판정과 기각 조건 |
|---|---|---|
| H3-P1: GitHub MCP에는 reviewed-head 원자 조건이 없어 현재도 어떤 mediator도 안전·정상 merge를 동시에 보장할 수 없다. | 당시 pinned 버전은 EffectBound가 이미 이 인터페이스 제약을 입증했다. 현행 공식 PR #3182는 `expectedHeadSha`를 제공한다; REST 원래 `sha`를 지원한다. | **당시 버전에서 알려진 API 한계 `GAP_SUPPORTED`(이미 선행연구가 설명); 현행 일반화 `REJECTED_HYPOTHESIS`**. 현행에서도 이 필드가 실제 작동하지 않거나 특정 배포가 구버전을 강제한다는 버전 고정 관측이 있어야 다시 열 수 있다. |
| H3-P2: e 철회·OR/AND·실 provider 결합에는 새로운 메커니즘이 반드시 필요하다. | CTA의 전체 후보 재선택, Revocation의 antichain/rebind, AID의 현재 그래프·제출 선형화, EffectBound의 Bind/Re-enter/Fence가 강한 조합이다. 우리 메모리 sink는 올바른 edge→witness mapping 아래 안전과 X 정상성을 동시에 보였다. DAS 초안도 결합을 제안한다. | **추상 원자 sink 조건에서는 `REJECTED_HYPOTHESIS`; 현실 provider 범위 `UNVERIFIED`**. 강한 조합이 같은 승인 의미·실 provider 계약에서 e 의존 post-fence 수락 또는 X의 필수 정상 완료 거절을 보이면 다시 연다. |
| H3-P3: 특정 고정 provider 도구가 외부 `e`의 현재 상태를 effect frontier에서 확인할 수 없고, 이미 내보낸 e 의존 요청을 구별·fence/정산할 수도 없어, 안전한 e 철회와 X 정상 완료를 **동시에** 보장할 수 없다. | `expectedHeadSha`는 head만 묶고 e epoch은 묶지 않는다. 그러나 trusted gateway의 제출 선형화, pre-fence receipt, bounded drain, provider-native 조건/credential 분리/서버 규칙이 이 조건을 해결할 수 있다. 그 모든 실제 제어를 배제한 provider 계약은 아직 고정하지 않았다. | **`UNVERIFIED`, 아직 `GAP_SUPPORTED` 아님.** 한 provider·고정 revision·효과·정상 workload에 대해 모든 노출 제어와 frontier를 확인하고, 서로 구별할 수 없는 안전/정상 world 및 강한 대안 실패를 보여야 한다. provider-native rule/조건, 정확한 receipt+drain 또는 분리 credential이 안전과 X 완료를 함께 달성하면 기각한다. |

**Need 판정:** 특정 구버전 MCP에서의 head Bind는 이미 [공식 수정](https://github.com/github/github-mcp-server/pull/3182)이 있고, 중간 간선 e를 추가해도 그 기존 문제를 새 MAS Need로 바꾸지 않는다. H3-P3이 실제 계약에서 성립한다면 Need는 “간선 철회 일반 프레임워크”가 아니라 **그 고정 provider 효과 경계에서 권한 witness를 수락·fence·정산할 수 있는 제어 또는 검증 가능한 불가능 판정**으로 한정한다. 현재 보안 영향과 정상 X 완료의 충돌을 실 provider에서 관측하지 않았으므로 이 Need 역시 `UNVERIFIED`다.

## 다음 반증 질문과 최소 비용

1. **버전·제어 목록:** 연구용으로 허가된 provider **한 개의 고정 API revision**을 선택해 e의 상태를 수락 지점에서 무엇이 원자 검사할 수 있는지, 요청별 receipt/terminal query/cancel/fence/credential scope/서버 규칙이 있는지 공식 문서와 실제 schema로 열거한다. GitHub라면 current MCP `expectedHeadSha`를 반드시 대조군에 넣는다. 읽기 전용 조사 비용 0.
2. **승인 시간 의미:** `provider accept` 전 e 철회인지, 뒤 e 철회인지 따로 사전등록한다. 늦은 물리적 효과만 보고 위반으로 부르지 않는다. 정상 X 요청·A 단독·AND·pre-fence receipt·post-fence 신규 수락의 동일 effect state를 비교한다.
3. **도구 제약의 실제성:** MCP-only를 강제하는 조직 요구와 native REST/서버 rule 사용 불가가 실제 배포 조건인지 기록한다. 제약이 없으면 REST/CTA/AID식 adapter를 최강 대조군으로 실행한다. 외부 provider는 허가된 test mode/격리 repo만 사용하며 별도 승인 없이 운영 서비스에 effect를 내지 않는다.
4. **판정 중단:** 강한 대조군이 A/AND 0과 X 정상 1 및 pre-fence 정산을 달성하면 후보를 기각한다. 제공자 내부 경로의 완전성을 확인하지 못하면 `UNVERIFIED`/`Unsupported`로 둔다. 특정 API 계약의 불가능이 입증되더라도 기존 EffectBound의 범위와 겹치는지 먼저 판단한다.
