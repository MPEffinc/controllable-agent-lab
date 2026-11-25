# K07 독립 경로 조합 실험 결과

**판정:** 정적 PM graph 위에 조건부 허용을 broad association으로 두고 단일 전역 app gate를 적용하면, 별도 무조건 허용 경로가 있는 정상 요청도 차단됐다. 경로별 app gate로 이 과차단은 회복됐지만, 조건이 꺼진 금지를 PM에 상시 export한 경우에는 PM 자체가 거부하므로 경로별 app gate만으로 회복하지 못했다. 이는 **이 실험에서 구성한 조합의 한계**이며 NGAC-IR 저자 생성기/배포 재현, PM 구현 결함, 일반 Research Gap의 증거가 아니다.

[사전 등록](prereg.md)은 실행 전인 00:30:31 UTC에 작성했다. [보존한 소스](K07RouteCompositionTest.java), [원시 로그](build-attempt1.log), [7행 JSONL](decisions.jsonl), [명령·환경·hash](commands.md)를 참조한다.

## 관측

매 case마다 새 NIST `MemoryPAP`와 두 개의 0으로 시작하는 effect ledger를 만든다. PM graph 질의 `computePrivileges(alice, doc)`를 기록하고, 앱 gate가 통과하면 실제 원본 `PDP.adjudicateOperation`으로 `read_naive` 또는 `read_route` 연산의 `RequiredPrivilegeOnParameter(read)`를 검사한다. 허용 때만 custom in-memory `ResourceOperation.execute`가 해당 ledger를 증가시킨다. 따라서 효과는 **메모리 상태 0→1**이며 실제 서비스의 commit/transaction은 아니다. 두 앱 variant는 같은 PM 정책과 금지를 사용하고, `route-aware`가 PM 금지를 우회하지 않는다.

| Case | PM `read` | 의도 효과 | 전역 gate 최종/효과 | 경로별 gate 최종/효과 | 해석 |
|---|---|---:|---|---|---|
| 조건부 허용만, 조건 닫힘 | ALLOW | 0 | 앱 DENY / 0→0 | 앱 DENY / 0→0 | broad PM graph alone은 과권한이나 두 앱 gate가 막음 |
| 조건부 허용만, 조건 열림 | ALLOW | 1 | ALLOW / 0→1 | ALLOW / 0→1 | 정상 요청 |
| 무조건 허용 경로 추가, 조건 닫힘 | ALLOW | 1 | 앱 DENY / 0→0 | ALLOW / 0→1 | 전역 gate의 정상 업무 과차단; 경로별 복구 |
| 무조건 허용 경로 추가, 조건 열림 | ALLOW | 1 | ALLOW / 0→1 | ALLOW / 0→1 | 두 경로 모두 유효 |
| 조건부 금지 inactive, 상시 export | **DENY** | 1 | 앱 DENY / 0→0 | **PM DENY / 0→0** | 정적 금지 export의 정상 업무 과차단 |
| 조건부 금지 active, 상시 export | **DENY** | 0 | 앱 DENY / 0→0 | **PM DENY / 0→0** | 금지 우선 적용은 의도와 일치 |
| 금지 inactive라 export 제외한 반사실 대조 | ALLOW | 1 | 앱 DENY / 0→0 | ALLOW / 0→1 | 신뢰된 조건에 따라 policy를 구성할 수 있으면 복구 가능; 동적 배포 안전성은 미평가 |

원시 7행의 `pm_allow`, `intended_allow`, `naive_*`, `route_*` 값을 JSON으로 파싱하고 각 effect와 최종 결정의 일치를 확인했다. 전역 gate는 의도와 다른 정상 거부가 3/7개 구성 행, 경로별 gate는 1/7개 구성 행이다. **이 분모는 설계된 소규모 반례 묶음**이고 발생률/성능 수치가 아니다. `embargo_inactive_always_export`에서는 PM graph `DENY`, 경로별 앱은 PDP를 호출했고 PDP `DENY`, 효과 0→0이라 decision-only 관찰이 아니다. `embargo_active_always_export`에서도 PM `DENY`가 별도 무조건 허용 association보다 우선했다.

## 주장·구현·대안의 경계

[NGAC-IR v1 §5.1](https://arxiv.org/html/2611.26941v1)은 PM이 조건을 직접 검사하지 못하고, strict export에서 조건부 허용은 PM에서 제외해 앱에 넘기지만 조건부 금지는 PM에 남아 상시 적용되므로 과차단할 수 있다고 **저자가 직접 설명**한다. 여기서는 저자 strict export를 실행하지 않았다. 실험은 조건부 허용을 PM에 broad association으로 넣은 채 두 앱 gate를 비교했다. 다만 금지 case에는 별도 무조건 허용 association이 있으므로, 저자 strict export처럼 조건부 허용 association만 제거해도 PM의 금지 우선 결과는 같을 것으로 **추론**된다. 이를 저자 시스템의 관측 결과라고 쓰지 않는다.

공식 NIST PM core 3.3.0의 [AccessQuerierTest](https://github.com/usnistgov/policy-machine-core/blob/7cc6b615354c871099d84bab8ec6667ef7c3e417/src/test/java/gov/nist/csd/pm/core/pap/query/AccessQuerierTest.java)와 이 실행 모두 prohibition이 association보다 우선함을 확인한다. [NIST SP 800-178 §4.3](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-178.pdf)은 결정 함수에서 deny가 privilege보다 우선한다고 정의한다. 같은 문서 §4.2.3–4.2.4는 obligation 이벤트에 따른 동적 prohibition 생성도 기술한다. 따라서 이 정적 export 사례를 NGAC 전체의 조건 표현 불능이라고 일반화할 수 없다. PM은 입력된 정적 graph를 충실히 집행했다. 의도·정적 graph 사이의 차이와 app 조합 방식이 문제다.

[Cedar 공식 authorization semantics](https://docs.cedarpolicy.com/auth/authorization.html)는 각 permit/forbid를 조건식과 request context로 평가하고, 만족된 forbid가 permit보다 우선한다고 명시한다. 조건부 `permit`과 독립 허용 `permit`, 조건부 `forbid`를 조합한 **별도 [공식 Cedar CLI 6조건 대조](../K05_route_composition_20261125/result.md)**에서 의도 결정·로컬 효과가 6/6 맞았다. 이 K07 PM 실험 자체가 Cedar 엔진을 실행한 것은 아니며, context 공급의 신뢰성·최신성·effect 시점 원자성은 별도 질문이다. 기존 조건부 PDP 대안이 있으므로 이 반례만으로 새 Research Need를 확정하지 않는다.

**범위:** 공격자 없음, local trusted booleans와 경로 metadata, 단일 요청·단일 프로세스, in-memory effect, 경쟁 상태/철회/원격 provider 없음. 모델·seed·temperature 사용 없음. 원본 NIST repo는 clean; 새 test는 격리 worktree만 수정. `mvn -o` 1회 성공, 외부 API 비용 0.
