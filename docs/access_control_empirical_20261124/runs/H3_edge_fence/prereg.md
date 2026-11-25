# H3 edge–witness–fence 최소 실험 사전등록

등록: 2026-11-24 UTC. 이 파일을 fixture 작성·실행 전에 고정한다. 허가된 로컬 메모리에서만 실행하며 유료 모델/API·실서비스 호출은 없다. 이는 **VERA 논문 전체 재현이 아니다.** 원본 artifact의 `target_set_l2`만 직접 호출하고, witness 선택·원자 provider 수락·fence·효과 정산은 별도 합성 fixture이다.

## 검증 질문과 원래 주장

질문: `A→C` 중간 위임 간선을 철회해도 독립 `X→C` 권한이 살아 있는 OR 업무는 진행되고, 철회된 A에 의존하는 단독/AND 업무의 **신규 provider 수락**은 차단되는가? 이미 수락된 provider commitment는 철회 이후 어떤 상태로 정산되는가?

원문 경계: [VERA §III–VII](https://arxiv.org/html/2608.30091)의 L2 target은 간선 삭제 전후 root reachable node의 차집합이고 대체 부모 경로가 있는 노드는 보존한다. [Authorization Revocation](https://arxiv.org/html/2609.21284)은 root-epoch, selected sufficient support, provider fence/정산을 따로 다룬다. 여기서 **중간 간선 e와 OR/AND witness를 결속하는 규칙과 sink는 우리 합성**이다.

## 고정 입력·실험 경계

- 그래프: `R→A`(`r_a`), `A→C`(`a_c`), `X→C`(`x_c`). 별도 A 경로만의 그래프에서도 `target_set_l2(a_c)`를 호출한다. e는 서명 확인이 없는 정적 fixture 간선이다.
- 요청: C가 한 추상 `write`를 sink에 제출한다. 요청마다 `request_id`, action digest, selected witness를 고정한다. OR minimal sufficient witness는 `{{a_c},{x_c}}`; AND는 `{{a_c,x_c}}`; A 단독은 `{{a_c}}`이다. `r_a`는 A의 상위 도달성 전제로만 둔다.
- sink는 한 임계구역의 `accept`에서 현재 활성 간선, 선택 witness, fence generation을 함께 검사하고 receipt를 기록한다. effect는 이 **수락된 commitment**의 나중 `settle`에서만 증가한다. 철회 뒤 최초 수락한 요청은 post-fence 신규 effect다. 철회 전 수락 뒤 늦게 정산한 effect는 `pre-fence receipt`로 별도 센다.
- `revoke(a_c)`가 fence generation을 증가시키고, 이후의 `accept`에서 해당 간선을 비활성으로 본다. 이것은 현실 provider의 원자성을 증명하지 않는 명시적 추상 계약이다. 중복 request_id 정산 방지는 로컬 ledger에서만 보인다.
- 음성 대조군은 **의도적으로** edge/fence 검사를 건너뛴 stale sink이다. 그 수락/효과는 VERA나 다른 저자 코드의 실패로 해석하지 않는다.

## 세 일정과 예상/반증 관찰

| 일정 | 순서 | 예상 관찰 | 반증 관찰 |
|---|---|---|---|
| S1 pre-fence receipt | A 단독 수락 → e 철회/fence → 그 receipt 정산 | receipt generation 0, fence generation 1, 늦은 effect 1은 `pre-fence`로 분류; 철회 뒤 새 A 수락은 0 | 철회 뒤 최초 수락을 pre-fence로 오분류하거나 이미 수락한 receipt가 출처 없이 생성됨 |
| S2 post-fence deny | e 철회/fence → A 단독·AND 수락 시도 | 두 deny, 신규 receipt 0, effect 0 | 어느 하나라도 수락·효과 발생 |
| S3 independent OR | e 철회/fence → OR의 X witness 명시 선택·수락·정산 | X 경로 정상 유지, receipt 1, effect 1; VERA의 대체 경로 있는 C target 없음 | X를 부당 거절하거나 A 경로로 암묵 승계 |

추가 음성 대조군: e 철회/fence 뒤 검사를 우회한 stale A 수락·정산은 effect 1이어야 한다. 이는 **집행 생략시 실패할 수 있음**만 보이며 신규 Gap을 입증하지 않는다.

## 완료 조건·측정·비용 상한

원본 `target_set_l2`가 A-only 그래프에서 C 포함, X 대체 그래프에서 C 미포함을 반환한다. S1–S3와 음성 대조군의 before/after ledger, active edge, generation, receipt, effect, 결정 이유, stdout JSON을 저장한다. 실행 명령·Python 버전·원본 파일과 fixture SHA256·wall time·모델/API 비용 0을 기록한다. 불일치가 나면 fixture 버그/가정 오류와 원본 함수의 실제 동작을 먼저 분리하고 동일 원인 재시도는 최대 2회. 다른 작업으로 확장하지 않는다.

## 사전 판정 규칙

S1–S3가 예상대로이면 이 **추상 원자 sink 조건**에서는 H3 조합을 해결 가능한 대조군으로 보아 “새 메커니즘 필수” 가설을 `REJECTED_HYPOTHESIS`로 판정한다. 현실 provider와 논문 전체에 대해서는 `UNVERIFIED`를 유지한다. 실패하더라도 fixture 설계/원자성 전제/권한 정보 누락 여부를 배제하기 전 `GAP_SUPPORTED`를 부여하지 않는다.
