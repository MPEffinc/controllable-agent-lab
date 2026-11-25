# C9 사전등록 — 공식 언어 의미를 제공한 reviewer 대조

2026-11-25 UTC. C7의 두 모델은 공식 AutoCedar `case-101` gold를 원본/정규화 모두 거짓 거부했고, 이유는 Cedar `in`의 계층 의미 오해였다. C8은 2단계 자손까지 실제 ALLOW와 로컬 효과를 확인했다. [Cedar 공식 연산자 문서](https://docs.cedarpolicy.com/syntax-operators.html)에 기반한 다음 **정답이 아닌 언어 의미**만 검토 prompt에 추가한다: `A in B`는 A=B 또는 A가 B의 직접·전이적 자손이면 참이며, `!(true)`는 false다. 원문 요구사항과 두 정책은 C7과 동일하다.

- **RQ:** 공식 언어 의미를 신뢰 가능한 참고자료로 제공하면 C7의 두 모델이 정답 정책을 승인하는가?
- **입력/정답:** `case-101` 공식 요구사항, 원본 gold 및 C7에서 양방향 동치를 확인한 정규화 정책. 두 모델 × 두 정책 = 4 독립 호출. 모두 approve가 공식 gold 기준 정답. C7의 원문 결과는 각 모델 0/2 승인. 온도 0, seed 20261125, C4 system prompt 유지하고 공식 의미 문장만 추가한다.
- **반증:** 4/4 승인하면 이 case의 리뷰 오류가 기존 언어 명세 grounding으로 해결될 수 있음을 확인하고 새 reviewer 메커니즘 Need를 기각한다. 실패가 남아도 원본 AutoCedar atom reviewer/인간 전체의 실패로 확대하지 않는다. 답·C7 판정·C8 decision은 모델에 주지 않는다. 재시도·prompt 사후 수정 없음.
- **비용/효과:** `gpt-4.1-mini-2025-04-14`, `gpt-4.1-2025-04-14`, 최대 4 calls, 목표 <$0.02·전체 $5. 원시 요청·응답·토큰/비용 저장. 외부 서비스 effect 0; C8 효과를 대조로 사용.
