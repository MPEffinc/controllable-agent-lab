# C8 공식 Cedar 계층 검사와 로컬 서비스 효과

2026-11-25 UTC. [사전등록](prereg.md), [원본 실행 코드](run.py), [원시 8 decision/효과](result.json), [서비스 상태](service_state.sqlite), [스키마 재검사 코드](typed_recheck.py), [스키마 적용 8 decision](typed_recheck.json). 공식 AutoCedar `case-101` gold와 C7에서 정형 동치를 확인한 정규화 정책을 각각 같은 네 요청에 실행했다.

| 지역 관계 | 공식 gold | 동치 정규화 | SQLite `clear_to_close` 효과(각 정책) |
|---|---|---|---:|
| 사용자 그룹과 동일 | ALLOW | ALLOW | +1 |
| 직접 자손 | ALLOW | ALLOW | +1 |
| 2단계 자손 | **ALLOW** | **ALLOW** | +1 |
| 무관한 그룹 | DENY | DENY | 0 |

초기 `result.json`의 `matches_expected=6`은 **집계 코드 오류**다. Cedar CLI는 정상 `ALLOW`에서 exit 0, 정상 `DENY`에서 exit 2를 반환했는데 원본 점수식은 exit 0만 성공으로 셌다. 원시 `stdout`, exit code, DB는 수정하지 않았다. 별도 `typed_recheck.py`가 원시 결정을 다시 집계해 **8/8**로 확인했고, 공식 `schema.cedarschema`를 명시한 같은 8요청도 **8/8**이었다. 스키마 재검사는 effect를 추가하지 않는 읽기 전용 decision replay다.

이 결과는 [Cedar 공식 `in` 연산자 설명](https://docs.cedarpolicy.com/syntax-operators.html)의 전이적·반사적 계층 의미와 일치한다. C7의 두 모델이 `in`을 직접 일치/단순 집합 검사라고 읽어 공식 gold를 거부한 설명은 이 요청에서 **틀렸다**. C7 reviewer의 거짓 거부는 정상 승인 업무를 보류하는 위험이지만 C8의 CLI 실행 자체는 정확했다. 실제 escrow 서비스는 호출하지 않았고, SQLite 효과는 독립 모의 서비스다. 기존 Cedar 실행과 명세가 직접 반박이므로 새 Cedar 집행 메커니즘 Need가 아니다.
