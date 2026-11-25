# C12 사전등록 — AutoCedar 원본 Authoring 최소 재실행

2026-11-25 UTC. C1c가 원본 Stage 2의 `PropertyAtomsResponse.atoms.0.rationale` 누락으로 멈춘 뒤의 **새 사용자 지시**에 따른 별도 실험이다. 공식 K06 source SHA `a0cf180977d799cf943514b67ffc260fc579b9a5`는 수정하지 않는다. 공식 case-011 자연어 요구와 C11의 `deletePullRequest` 추가 스키마를 사용한다. 독립 원본 저자 생성 성공이라고 부르려면 원본 pipeline이 원시 atom, plan, candidate를 작성해야 한다. 모델 호출 API 호환 어댑터가 관여하면 원본 provider의 완전한 재현은 아니다.

## 질문·예측·기각

1. C1c와 같은 `gpt-4.1-mini-2025-04-14`로 Responses API의 unsupported reasoning을 제거하고 JSON text를 원본 Pydantic으로 검증한다. ValidationError일 때는 **같은 structured call당 최대 1회** 누락 필드만 지적해 재요청한다. 원본 pipeline의 의미·스키마·검증기는 바꾸지 않는다. 비용·형식 오류·재시도·원시 모델 응답을 저장한다.
2. 실행이 후보까지 도달하면, 원본 author가 확장 schema의 미언급 `deletePullRequest` Permit을 실제 생성하는지 확인한다. 이 Permit이 없으면 H22의 생성기 실증 가설은 이 사례에서 기각한다. 후보가 있어도 Gold Target/Cedar 정상·비인가 요청으로 효과를 확인하기 전에는 안전성 결론을 내리지 않는다.
3. 후보 전에 다시 실패하면 구체적 단계, 원본/어댑터 오류, 성공 호출 수를 보고하고 H22를 `NOT_RUN`으로 남긴다. 호환 어댑터의 형식 문제를 정책 오류로 귀속하지 않는다.

최대 240초, 이번 run 예상 API 비용 $0.35에서 추가 호출 중지, 기존 누적 $0.0754388와 합쳐 $5 상한 유지. 새 session ID를 사용하고 기존 원시 기록은 보존한다. 모델 reviewer는 원본 CLI `--model-review` 경로로 실행하되 인간 검토 성능으로 해석하지 않는다. 정책 생성 실패 시 동일 입력의 반복 모델 호출을 하지 않는다.
