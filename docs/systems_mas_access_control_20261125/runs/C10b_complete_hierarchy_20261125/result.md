# C10b 완전한 그룹 관계 입력 대조

2026-11-25 UTC. [사전등록](prereg.md), [실행 코드](run.py), [원시 요청/응답](raw.jsonl), [전체 결과](result.json). C10에서 `unrelated/south`의 부모가 없다는 사실과 나열한 그룹 간선이 완전하다는 사실만 추가했다. 이전 모델 답·gold label은 제공하지 않았다.

두 모델의 blind/exposed 네 verdict가 모두 **DENY (4/4)**였다. C10에서 강한 모델이 같은 요청을 양 arm 모두 ALLOW로 본 것은 불완전한 관계 입력에 따른 오해로 좁혀진다. 4 calls, 추정 **$0.0039552**. 이 결과는 단순 입력 보완으로 고정 오류가 해결될 수 있음을 보여 준다. Reparo의 원본 oracle/refinement·실제 repository 증거 검색 성능은 시험하지 않았다.

**판정:** C10과 C10b를 함께 보면 잘못된 후보의 결정 노출이 정답 oracle label을 지운 증거는 없고, 모델에 전달하는 **신뢰된 관계 그래프의 완전성**이 정상·비인가 판정에 중요했다. 이 조건의 신규 oracle 메커니즘 Need는 `REJECTED_HYPOTHESIS`; 실제 저장소에서 누락된 관계를 어떻게 신뢰 있게 찾는지는 `UNVERIFIED`다.
