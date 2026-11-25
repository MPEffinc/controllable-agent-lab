# K07 독립 최소 실험 사전 등록 — 다중 허용 경로와 조건부 금지

기록 시점: 2026-11-25 UTC. 이 문서는 실행 전에 작성한다. 대상은 공식 NIST Policy Machine core 3.3.0 고정 commit `7cc6b615354c871099d84bab8ec6667ef7c3e417`의 `MemoryPAP`/`PDP`이고, **NGAC-IR 저자 코드·생성기·평가 재현이 아니다**. 원본은 수정하지 않고 격리 worktree `env/K07_pm_worktree`에 새 JUnit test 하나만 둔다.

## 검증 질문

동일 `alice/read/doc`에 (1) `registration_open`일 때만 유효한 허용 경로와 (2) 상시 유효한 별도 허용 경로가 있다. 전자를 PM에 무조건 association으로 export하고, 조건은 앱의 전역 preguard `registration_open`으로 검사하면, 후자의 정상 권한도 거부하는가? `embargo_active`일 때만 유효한 금지를 PM에 상시 prohibition으로 export하면, embargo가 꺼진 정상 허용도 거부하는가? PM query 결정, 실제 PDP 호출, 메모리 effect를 분리한다.

## 정책 의미와 구현 모델

- 의도된 최종 허용: `(registration_open || alternate_allow) && !(conditional_prohibition_rule && embargo_active)`.
- PM graph: `ua_cond -> oa_doc : read` association은 모든 case에 존재한다. `alternate_allow=true`면 별도 `ua_alt -> oa_doc : read` association을 추가한다. 유저는 두 UA에 속한다. 그래프 association은 조건을 평가하지 않는다.
- `conditional_prohibition_rule=true`와 `export_prohibition=true`면 `alice`의 `oa_doc`에 대한 `read` prohibition을 추가한다. NIST 원본 테스트의 `createNodeProhibition(..., Set.of(oa), Set.of(), true)` 사례를 따른다. `embargo_active`는 독립 신뢰 bool이며 PM은 읽지 못한다. `export_prohibition=false`는 조건을 평가할 수 있는 *가상 외부 구성*에서 inactive 금지를 PM에 넣지 않은 반사실 대조군이며, 저자 strict export의 실행이 아니다.
- `naive`: 앱 전역 gate=`registration_open`; 통과하면 원본 PDP `adjudicateOperation` 호출. `route_aware`: 앱 gate=`registration_open || alternate_allow`; 통과하면 **같은 PM PDP** 호출. 따라서 두 앱 variant 모두 PM prohibition을 우회할 수 없다. route metadata와 bool은 실험이 신뢰 공급한다. 각각 별도 메모리 effect ledger를 쓰고 각 case마다 새 PAP를 만든다.

## 사전 정의한 7개 case와 기대

| case | alternate | open | conditional prohibition rule | embargo active | export prohibition | PM 예상 | naive effect | route-aware effect | 의도 effect |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| conditional_only_closed | 0 | 0 | 0 | 0 | 0 | ALLOW | 0 | 0 | 0 |
| conditional_only_open | 0 | 1 | 0 | 0 | 0 | ALLOW | 1 | 1 | 1 |
| alternate_closed | 1 | 0 | 0 | 0 | 0 | ALLOW | 0 | 1 | 1 |
| alternate_open | 1 | 1 | 0 | 0 | 0 | ALLOW | 1 | 1 | 1 |
| embargo_inactive_always_export | 1 | 0 | 1 | 0 | 1 | DENY | 0 | 0 | 1 |
| embargo_active_always_export | 1 | 0 | 1 | 1 | 1 | DENY | 0 | 0 | 0 |
| embargo_inactive_aware_export | 1 | 0 | 1 | 0 | 0 | ALLOW | 0 | 1 | 1 |

반증 관찰: `alternate_closed`에서 naive effect가 발생하거나 route-aware effect가 없으면 첫 가설이 틀리거나 구현 오류다. `embargo_inactive_always_export`에서 PM이 ALLOW하면 둘째 가설이 틀리거나 prohibition 구성이 잘못됐다. `embargo_active_always_export`에서 PM이 ALLOW/effect가 나면 강제 금지 실패다. 어떤 결과도 일반 연구 Gap의 증거로 자동 승격하지 않는다.

## 비용·완료 기준

기존 Maven cache만 사용, 네트워크 API·모델 호출 없음, JUnit test 1개, 각 case의 PM 결정·앱 gate·PDP 호출·두 effect 전후 출력. `timeout 180s`, Maven heap 1 GiB; 최초 실행 + 원인 확인 후 **최대 재실행 1회**. 빌드 실패 시 실패 로그와 원인만 기록. 원시 JSONL, 명령, source hash, commit과 결과를 이 디렉터리에 보존. 실제 서비스 effect·동시성·조건 신뢰성은 평가하지 않는다.

## 일차 근거와 강한 대안

- [NGAC-IR v1 §5.1](https://arxiv.org/html/2611.26941v1): PM이 조건을 검사하지 못하며, strict export는 조건부 허용을 제외하지만 조건부 금지는 남겨 상시 적용한다고 설명한다. 이는 원문의 저자 보고이고 여기서는 저자 생성기 실행을 하지 않는다.
- [NIST PM core 3.3.0의 원본 prohibition test](https://github.com/usnistgov/policy-machine-core/blob/7cc6b615354c871099d84bab8ec6667ef7c3e417/src/test/java/gov/nist/csd/pm/core/pap/query/AccessQuerierTest.java): static prohibition이 association보다 우선하는 테스트.
- [Cedar 공식 authorization semantics](https://docs.cedarpolicy.com/auth/authorization.html): 조건식이 각 policy별로 평가되고, 만족된 `forbid`가 모든 `permit`보다 우선한다. 신뢰 가능한 context를 공급한다는 전제에서 같은 조합의 직접 대안이다.
