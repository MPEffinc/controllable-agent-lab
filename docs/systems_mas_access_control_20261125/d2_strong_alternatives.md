# D2 출처 세분화의 강한 기존 반박 — 2026-11-25

| 연구 | 원문이 직접 다루는 성질·근거 | D1/D2와 다른 보장·전제 |
|---|---|---|
| [Fides v2 §4/Appendix E](https://arxiv.org/html/2505.23643v2) | 전체 입력 label 전파의 soundness와 과보수성, 정보 숨김/선택적 노출. Appendix E는 permissive propagation 및 2–3× token 증가를 명시 | trusted label·planner 구조 전제. D1의 `r1`까지 붙는 결과는 설계상 예상된 utility 비용; 이 자체로 미해결 원리 증거 아님 |
| [Permissive IFC v2 §3.4/§6.2](https://arxiv.org/html/2410.03055v2) | 덜 제한적인 context로 **재생성된 출력**만 반환해 제거된 입력에 대한 의존을 차단. §6.2는 추가 호출·adversarial distraction의 서비스 저하 가능성을 인정 | D2는 이 아이디어의 독립 최소 적용. 원저자 prototype/평가 재현 아님. 어떤 입력을 제거할지 trusted label 및 context 제어 필요 |
| [NeuroTaint v1 §4–5](https://arxiv.org/html/2604.23374v1) | semantic/implicit/cross-session source→sink를 **offline audit**. TaintBench 400 시나리오, 저자 13 FN·16 FP를 보고 | 완료 후 전파 발견은 online effect 허가와 다름. D1의 정상 과차단을 해결할 가능성은 있으나 동일 요청의 runtime 정상·안전 보장으로 환산 불가 |
| [LMLineage v1 §5–6](https://arxiv.org/html/2611.22511v1) | sentence-to-span attribution; 71 중국어 gold sentence, 멀티세션 fine accuracy 0.55–0.63. §6은 security implication을 범위 밖으로 명시 | 모델 자기 보고보다 독립 attribution 대안이지만 이 수치를 승인 증명·PEP 정확성으로 쓰지 않음 |
| [A³Bench v1 §3/§5](https://arxiv.org/html/2609.33676v1) | policy basis/parameter provenance 등 1,396 audit 질문, end-to-end source accuracy 64.5% | action 원인 audit benchmark. online 승인/최종 effect 집행 자체는 평가 목표 아님 |

**현재 판정:** D1의 전체 입력 taint 과차단은 Permissive IFC 방식의 restricted-context regeneration과 current service PEP라는 기존 대안으로 고정 조건에서 해결됐다. 남는 검증 질문은 자연어 owner event의 **주체·scope·철회·현재성**을 신뢰할 수 있는 구조화 입력으로 전환하는 정확성/비용이다. 기존 대안의 전제를 빼고 새 Need라고 할 수 없으므로 D3에서 독립 gold와 실제 정상·비인가 효과를 함께 측정한다.
