# ALPS 공식 verifier 회귀 실행

- 2026-11-25 UTC, 연구실 공식 checkout `ace0fd2cabdc100bf5491bad3389e47bce6a37f9`, Apache-2.0. 원본 코드 수정 없음.
- 명령: `python3 -m unittest discover -s third_party/LAB_ALPS/runtime/python -p test_runtime.py -v` (repo root). [원시 stdout](stdout.txt), [stderr](stderr.txt), [exit](exit_code.txt). exit 0, **12 tests**, 0.002s. Python stdlib, 모델/API 0, USD 0.
- 공개 `Verifier.check()`는 permission/resource를 allowlist의 effective 항목과 비교한다. default `mode=enforce`의 비허용 호출은 `AlpsPermissionDenied`; `mode=monitor`는 `Decision.allowed=false` 및 violation을 기록하지만 예외를 던지지 않는다. `mode=off`는 허용한다. 공식 테스트는 정상 `dynamodb:PutItem`/`prod-Orders`와 다른 resource·action 차단, 환경변수 갱신, monitor의 decision을 포함한다 ([source](https://github.com/cclab-inu/ALPS/blob/ace0fd2cabdc100bf5491bad3389e47bce6a37f9/runtime/python/alps_runtime.py)).
- `check(permission, resource, **context)`의 `context`는 거부 기록에 포함되지만 허용 결정의 키가 아니다. 따라서 **이 함수의 허용 기준은 function allowlist의 action/resource**이며 사용자 task, origin grant, MAS 위임 토큰을 직접 평가하지 않는다. 이는 코드 경계의 정적 사실이며 ALPS 논문이 MAS task-level 보안을 주장했다는 뜻이 아니다.
- 이 실행은 **저자 단위 테스트 재실행/DECISION_ONLY**. 실제 cloud SDK hook 호출, IAM 배포, final provider effect, LLM 정책 생성, Agent/MAS 동작은 시험하지 않았다. [ALPS 원문 §V-D Table II](https://cclab.info/papers/2026_shin_infocom.pdf)의 94.8%는 8,322 함수 중 entity-level 권한 **추출 성공 범위**이지 공격 방어율이나 이 실행 결과가 아니다.

다음 질문: 동일 공유 worker에서 서로 다른 두 task의 action/resource가 union allowlist에 들어갈 때 task별 origin scope를 누가 어떻게 결속하는가? 기존 PAuth/K15/Agent libOS/서비스 PEP로 안전·정상 모두 해결되면 새 메커니즘 Need는 기각한다.
