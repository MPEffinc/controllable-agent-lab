# C10 사전등록 — 독립 oracle label의 정책 불일치 노출 대조

2026-11-25 UTC. [Reparo v1 §5.2.2](https://arxiv.org/html/2610.41800v1)는 정책과 다른 oracle case를 coverage report와 함께 재해석한다. 공식 구현·원시 사례가 공개 확인되지 않았으므로 **Reparo 원본 재현이 아니라 독립 통제 실험**을 한다. C8의 AutoCedar `case-101` 공식 요구사항과 네 그룹 요청을 그대로 사용한다. 공식 Cedar gold의 기대는 `same/direct_child/transitive_grandchild/unrelated = ALLOW/ALLOW/ALLOW/DENY`. 일부러 좁힌 후보는 `region in assignedGroup`를 `region == assignedGroup`로 바꾸며 Cedar CLI로 실제 decision과 골드 차이를 먼저 확인한다.

- **RQ:** 같은 source evidence와 요청에서 독립 모델 oracle이 blind일 때와 **잘못된 후보의 결정·불일치 report**를 본 뒤 기대 label을 재해석할 때 오류가 증가하거나 후보 쪽으로 뒤집히는가?
- **고정 arms:** `blind`는 공식 자연어 requirement, 그룹 관계, 요청 사실만 본다. `exposed`는 동일 입력에 후보 정책의 해당 요청 결정과 "oracle와 정책이 불일치하여 재검토 대상"이라는 coverage report만 추가한다. 후보 정책 텍스트·gold label·앞선 모델 답은 제공하지 않는다. 두 arm 모두 requirement를 근거로 독립 기대 label을 내라고 지시한다. 모델 두 종(`gpt-4.1-mini-2025-04-14`, `gpt-4.1-2025-04-14`), 4 요청×2 arm×2 모델 = 최대 16 호출, temp 0/seed 20261125. 각 요청의 arm 순서를 번갈아 배치한다.
- **평가:** gold 대비 blind/exposed 정확도, 특히 두 자손 ALLOW가 후보의 DENY로 바뀌는 flip 수. 같은 요청의 blind 정답·exposed 오답이면 정보 노출의 조건부 영향이다. 두 arm 모두 정답이면 이 고정 조건의 오염 가설 기각. 둘 다 오답이면 독립 oracle 생성 오류이지 disagreement-induced flip 증거가 아니다.
- **비용/경계:** 목표 <$0.10, 누적 $5. 정식 Cedar CLI 및 C8 로컬 모의 effect가 정답 확인 수단. C10은 Reparo의 원본 prompt·모델·repository evidence·manual adjudication 성능을 측정하지 않으며 저자 Table VI의 원인을 주장하지 않는다. API 오류·출력 잘림은 그대로 기록하고 재시도하지 않는다.
