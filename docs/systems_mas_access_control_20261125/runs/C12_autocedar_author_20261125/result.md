# C12 원본 파이프라인 + API 호환 어댑터 결과

2026-11-25 UTC. [사전등록](prereg.md), [runner](run_author.py), [API 어댑터](compat_adapter.py), [원시 session](session/C12_case011_extended), [사용량](adapter_usage.jsonl), [모델 원문](adapter_raw.jsonl), [stderr](stderr.txt), [실행 메타](run_meta.json). AutoCedar 원본 source SHA `a0cf180977d799cf943514b67ffc260fc579b9a5` 무수정. API adapter가 prompting/structured parse를 변경했으므로 완전한 원본 provider 재현은 아니다.

확장 schema의 `mergePullRequest`와 `deletePullRequest`, 공식 case-011 요구로 원본 author CLI를 실행했다. C1c의 필수 `rationale` 누락은 반복되지 않았다. Structured 응답 6건은 모두 첫 출력에서 원본 Pydantic 검증을 통과하여 형식 재요청 0회였다. Stage 0 intent map, Stage 1 schema, Stage 2 원본 atom 제안/모델 리뷰와 target 작성까지 진행했다. Stage 3는 원본 syntax verifier에서 실패한 후보를 세 번 반복해 **원본의 oscillation 중단 규칙**으로 종료(exit 1, 42.9초). 후보는 `resource.targetBranch[0] == "h"` 등 문자열 인덱싱을 사용했는데 Cedar 구문 오류다. 또한 `action.onVpn`은 schema의 `context.onVpn`과 맞지 않으나 첫 syntax 오류 뒤 실제 검증 결과는 미관측이다.

원시 usage는 총 19 API calls, 추정 **$0.0287864**. 이전 누적 $0.0754388와 합한 누적 추정 **$0.1042252/$5**. 반복 모델 호출은 종료했다. Stage 3의 후보는 유효한 활성 정책이 아니며 실제 서비스 효과 `NOT_RUN`이다. 저장된 후보에 `deletePullRequest` Permit은 없지만 **유효한 최종 정책까지 도달하지 못했으므로 H22의 원본 생성 빈도/안전성 판정은 유보**한다. 이 실패는 AutoCedar의 일반 보안 실패나 원저자 평가 재현 결과가 아니다. 더 작은 접두사 없는 요구에서 Authoring을 별도 Run ID로 시도한다.
