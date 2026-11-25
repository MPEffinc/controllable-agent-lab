# H3 간선 철회·selected witness·effect fence 최소 실험 결과

실행: 2026-11-24 UTC. [사전등록](prereg.md)을 먼저 저장하고 [fixture](fixture.py)를 작성했다. `python3 fixture.py > raw.json`으로 실행한 [원시 로그](raw.json)의 모든 assertion이 통과했다. **VERA 원본 논문 재현이 아니다.** VERA 원본에서 호출한 것은 `revocation.granularity.target_set_l2`와 그 DAG 자료형뿐이다. OR/AND witness, 원자적 accept/revoke/fence, receipt와 효과 정산은 우리가 작성한 독립 in-memory sink다.

## 실행 경과·재현 명령

1. `third_party/vera-artifact-anon/src/revocation/{dag,granularity}.py` 및 원본 L2 unit test를 읽었다. 원본 코드는 수정하지 않았다.
2. 첫 `python3 fixture.py > raw.json`는 원본 패키지 `__init__`가 무관한 crypto 모듈을 미리 읽어 `ModuleNotFoundError: cryptography`로 실패했다. 이때 `raw.json`에는 결과가 없었다. 원본 두 모듈만 import하도록 package namespace shim을 fixture에 추가했고, 두 번째 실행에서 exit 0이었다. 원본의 `target_set_l2` 구현은 그대로 호출했다. 외부 의존성을 설치하지 않았다.
3. 재현: `cd /home/cclab/controllable_agent/docs/access_control_empirical_20261124/runs/H3_edge_fence && python3 fixture.py > raw.json`. 결정, receipt, fence generation, effect 상태가 JSON에 저장된다. Assertion 실패는 nonzero exit다.

고정값: Python 3.12.15, Linux 6.8.0-149-generic, 모델/API 호출 0, 외부 비용 USD 0, fixture 내부 측정 5.655 ms. 원본 VERA `granularity.py` SHA256 `d762ec14a46568e3c1bd3220fd204eb149f673d3a6b0d242f361f90f44d1e039`, `dag.py` SHA256 `c0a10b038563c272be0f06fc489306164e17b34a734470903724454cf30df720`; fixture SHA256 `cc427962c93e68663d72ad6df7ddd2cbf0b78dcd9ec58b5b39958792556a31de`; prereg SHA256 `97e2d90c25fdab843f6c36d99ee78150ac10156c1c4e7543980a82afe5fb344d`; raw JSON SHA256 `0ac51fbbd76e220df4caec23872da95b299ef30706cf907bb779fe18a064e741`.

## 원본 함수와 독립 sink의 관측

원본 `target_set_l2(a_c)`는 A 경로만 있을 때 `{C}`, 독립 X 경로가 있을 때 `∅`를 반환했다. 이는 **C의 node-level 도달성 target**이다. C가 살아 있다는 정보만으로 개별 provider 요청이 철회된 `a_c` witness를 택했는지는 알 수 없다. 그 결속은 별도 fixture의 규칙이다.

| 일정 | 철회·수락 전 상태 | 정책 결정과 실제 효과 | 최종 상태 |
|---|---|---|---|
| S1 pre-fence receipt | generation 0, `a_c` 활성, receipt/effect 0 | `s1_old_A`가 generation 0에서 수락됨. `a_c` 철회로 generation 1. 기존 receipt가 나중 정산되어 effect 1; 철회 뒤 새 `s1_new_A`는 deny | `a_c` 비활성, receipt 1, `pre_fence_receipt_settled_later` effect 1, 신규 A receipt 0 |
| S2 post-fence deny | generation 1, `a_c` 비활성, receipt/effect 0 | A 단독 `{a_c}`와 AND `{a_c,x_c}` 모두 `selected_witness_revoked_at_fence`로 deny | receipt 0, effect 0 |
| S3 independent OR | generation 1, `a_c` 비활성·`x_c` 활성, receipt/effect 0 | OR의 충분 witness `{x_c}`를 명시 선택해 수락·정산 | receipt 1, 신규 정상 effect 1 |
| stale 음성 대조군 | generation 1, `a_c` 비활성, receipt/effect 0 | **의도적으로** edge/fence 검사를 생략한 sink가 `{a_c}`를 수락·정산 | 비인가 post-fence receipt 1, effect 1 |

`write:fixture_object`의 action digest는 모든 일정에서 `e5da622d5bb3e22856dd828164b8f30d8d3cfc3d3601cdc222b0c2635ff658a6`이다. JSON의 `before`, `after_accept`, `after_fence_before_settle`, `after`에 상태와 각 이벤트 순서가 들어 있다. `effect`는 추상 ledger의 실제 상태 변화이고 도구 decision만의 결과가 아니다. 그러나 외부 서비스 효과를 뜻하지 않는다.

## 판정과 적용 한계

사전 판정 규칙대로, **원자 수락·fence와 완전한 edge→selected-witness 정보가 있는 이 추상 sink**에서는 A 의존 신규 효과를 막으면서 X 독립 정상 효과를 허용했다. 따라서 “이 조합에는 무조건 새로운 보안 메커니즘이 필요하다”는 **이 조건의 가설은 `REJECTED_HYPOTHESIS`**다. stale control의 실패는 집행 검사 제거의 예상 결과이지 VERA 실패나 학계 Gap 근거가 아니다.

실제 provider·MAS 구현의 H3는 **`UNVERIFIED`**다. 여기서 accept는 한 프로세스 `RLock` 아래 원자적이며, 네트워크 지연·크래시·provider API 계약·동시 실행을 시험하지 않았다. pre-fence receipt가 철회 뒤 정산되는 의미는 “이미 provider가 수락한 commitment는 소급 취소하지 않음”이라는 **fixture의 명시적 finality 선택**이다. 철회 뒤 물리적 효과를 단 한 건도 허용하지 않아야 하는 정책이면 다른 계약/보상·취소 능력이 필요하며 이 실험은 이를 증명하지 않는다. VERA 원본의 서명 검증, 배포, trace benchmark도 재현하지 않았다. 실제 API가 같은 원자 수락·fence를 제공하는지 확인하는 것이 다음 반증 질문이다.
