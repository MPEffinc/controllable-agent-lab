# C1b 재시도 사전등록 — unsupported API 필드 제거

2026-11-25 UTC. C1과 동일한 case-011, gold, 모델, CLI 한도, 시간·비용 상한을 적용한다. C1은 원저자 OpenAI 어댑터가 `gpt-4.1-mini-2025-04-14`에 지원되지 않는 `reasoning.effort`를 전송해 첫 요청에서 HTTP 400으로 종료했다. C1 이벤트는 stage1 schema 작성까지이며 모델 사용량 기록은 없다.

- **검증 질문:** API 호환성 장애만 제거하면 원저자 `author`가 후보를 생성하고, gold 의미 및 정상 task와 비교할 수 있는가?
- **최소 패치:** 별도 runner에서 `autocedar.providers.openai_api._responses_kwargs` 결과의 `reasoning` 필드만 제거한다. 원저자 파일·다른 요청 인자·정책 생성 코드는 수정하지 않는다. 따라서 **원본 무수정 실행은 아니며 호환성 adapter를 쓴 재현 시도**다.
- **반증/완료:** 실행이 다시 실패하면 새 오류·호출 횟수·비용을 원시 로그로 남기고 무제한 재시도하지 않는다. 성공하면 독립 gold oracle과 local effect 검증을 별도 수행한다. 전체 API 총상한 $5, 이번 시도 목표 <$0.50, 240초 timeout.
