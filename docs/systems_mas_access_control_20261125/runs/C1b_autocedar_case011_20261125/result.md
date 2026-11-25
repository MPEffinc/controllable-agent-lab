# C1b API 필드 호환성 재시도 결과

2026-11-25 UTC. [사전등록](prereg.md). 원본 source 무수정, 실험 runner가 OpenAI 요청의 unsupported `reasoning` 필드만 제거했다. CLI exit 1 (9.3초). 첫 structured model 요청에서 HTTP 400: `PropertyAtomsResponse`의 자유형 `request_dict`는 OpenAI strict response schema가 요구하는 `additionalProperties: false`를 충족하지 않는다. 성공 모델 호출 0, 기록된 사용량/비용 $0. Stage2 checkpoint까지 저장됐으나 후보·effect 없음. 별도 C1c에서 일반 JSON text와 원본 Pydantic 검증을 시도했다.
