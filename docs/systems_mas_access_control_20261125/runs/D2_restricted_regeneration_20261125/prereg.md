# D2 사전등록 — 기존 permissive IFC restricted-context regeneration 반박

2026-11-25 UTC. [Permissive IFC v2 §3.4](https://arxiv.org/html/2410.03055v2)는 덜 제한적인 context로 모델을 다시 실행하고 **새 출력**만 사용해 제거된 입력 의존성을 차단한다. [Fides v2 Appendix E](https://arxiv.org/html/2505.23643v2)는 전체 메시지 taint의 정상성 과차단과 이 방법의 적용 가능성을 명시한다. D1의 과차단을 새 Gap으로 선언하기 전에 이 강한 대안을 대조한다.

- **RQ:** 동일 Agent A/B 정책 업무에서 폐기 `r1`을 A 재생성 context에서 제외하고 trusted owner `r2`만 주면, 출력의 code-owned ancestry를 `{r2}`로 한정하면서 1명 요청 거부·2명 요청 정상 완료를 유지하는가?
- **고정 조건:** D1과 같은 model `gpt-4.1-mini-2025-04-14`, seed 20261125, temperature 0, A/B system instruction, trusted `r2`, 두 B 요청. 유일한 의미 변경은 A user input에서 `tool_record=r1` 제거. A journal은 새 호출의 output만 사용한다. `support_ids`는 자기 보고이며 보증 근거가 아니다.
- **대조/반증:** D1 conservative lineage의 정상 0/1, current service PEP 정상 1/1·비인가 0과 비교. 새 context에서 A가 현재 규칙을 잘못 쓰거나 B가 정상 2명을 거부하면 이 대안의 **이 고정 조건** 정상성 실패. 정상 1/1·비인가 0이면 D1 과차단의 새 메커니즘 Need를 기각한다.
- **범위/비용:** 논문 방법을 원문에 따라 만든 독립 adapter이며 원저자 코드/평가 재현은 아니다. 신뢰된 r2 식별과 제거 가능한 prompt context가 전제다. 로컬 SQLite 효과만. 모델 호출 3회, 비용 목표 <$0.05/전체 $5, 키 비기록. 원시 요청·응답·전후 상태·토큰 기록.
