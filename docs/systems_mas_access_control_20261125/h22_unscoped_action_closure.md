# H22 — target에 빠진 action의 정책 확대

2026-11-25 UTC. **Problem:** 검증 대상 target이 언급된 action만 덮는다면, 같은 스키마의 다른 action을 candidate policy가 허용해도 모든 target 검사가 통과할 수 있다. **보안 속성:** 사용자 의도 “명시한 merge 외 action은 허용하지 않는다”가 정책 생성·검증·집행까지 유지된다. **정상 작업:** 조건부 PR merge. **비인가 작업:** PR delete. 공격자 없이 생성 정책 오류만으로도 성립하며, 악의적 후보 주입은 시험하지 않았다.

## 원문→구현→효과의 증거 체인

1. [AutoCedar v2 §III-B](https://arxiv.org/html/2607.03656v2) 문단은 문서가 허용/제한을 언급한 action만 intent-map scope로 만들고, **그 밖의 action에 추가 permit이 생겨도 target 검사가 거부하지 않는다**고 직접 설명한다. 형식 성질은 각 scope의 floor/ceiling 포함이며 전역 “모든 schema action” 보장이 아니다.
2. [C11](runs/C11_unscoped_action_20261125/result.md)은 공식 `case-011`의 “no other actions” 요구와 gold를 유지하고, 연구자 확장 schema에 `deletePullRequest` action을 넣었다. gold+delete permit 후보는 원본 AutoCedar `verify`의 merge 전용 plan 2/2 PASS/loss0이다.
3. 같은 원본 verifier에 delete scope의 candidate⇒gold 검사를 더하면 FAIL/loss1 및 delete counterexample. Cedar CLI/독립 SQLite는 정상 merge를 두 정책 모두 실행하고, 비인가 delete를 gold 0/후보 +1로 보여 준다. 정책 표현 범위, 검사 범위, 실제 로컬 효과를 분리했다.

## 가장 강한 기존 반박

- **기존 원본 verifier 자체가 해결 도구:** 활성 schema action 전체에 대해 닫힌 target이나 gold의 전역 inclusion을 추가하면 C11의 과권한이 검출된다. 공식 Cedar의 default-deny도 정책이 delete permit을 생성하지 않는 동안에는 보호한다. 본 실험은 **생성 candidate에 permit이 이미 들어간 경우**다.
- AutoCedar는 atom/intent-map을 사람이나 모델이 검토하고 문서에서 허용한 action만 map scope로 삼는다. 따라서 실제 generator가 C11의 추가 permit을 만들 가능성과 빈도는 이 실험에서 측정하지 않았다. 원저자 자동 완주·사람 리뷰 효과도 미평가다.
- Progent의 동적 tool 정책 갱신, Agent libOS의 host-authored manifest/effect ceiling, PAuth/CONTINUITY의 범위 위임은 다른 층에서 무허가 동작을 막는 직접 대안이지만, C11에 그 원본 구현을 연결해 시험하지 않았다.

## 판정과 반증 조건

**`GAP_SUPPORTED` (AutoCedar target coverage, 조건부):** active schema에 문서에 안 나온 action이 있고 verifier plan이 그 action을 덮지 않으면, plan PASS와 비인가 로컬 효과가 동시에 가능하다. [C11 원시 로그](runs/C11_unscoped_action_20261125/result.json)는 재현 가능한 반례다. **`REJECTED_HYPOTHESIS` (새 정형 메커니즘 Need):** 같은 verifier에 action 포함 검사를 한 개 더 추가하자 해결됐다. **`UNVERIFIED` (넓은 시스템 Need):** 실제 자연어 “그 밖의 action 금지”를 현재·미래 tool/schema action의 닫힌 범위로 변환하고, 생성/갱신된 정책의 활성본까지 어떤 비용으로 유지하는가.

**가설 기각 조건:** AutoCedar의 실제 authoring 경로 또는 다른 현행 시스템이 입력 문서·schema/tool registry 변화에도 모든 unmentioned action을 명시적으로 닫고, 정상 action의 성공을 유지하면서 과권한 추가를 검출/차단한다는 원본 코드·실험이 나오면 넓은 Need를 기각한다. 스키마 확장만으로 비인가 효과가 자동 발생한다는 주장도 하지 않는다. 후보가 delete permit을 추가한 **조건**이 필요하다.

**후속 원본 실행:** [C12](runs/C12_autocedar_author_20261125/result.md)는 API 호환 어댑터로 공식 case-011 확장 schema의 원본 Stage 2 atom/target과 Stage 3 후보까지 진행했으나 `hotfix/` Cedar 문자열 인덱싱 구문 반복으로 원본 oscillation gate에서 중단됐다. [C13](runs/C13_autocedar_minimal_20261125/result.md)는 접두사 없는 최소 소유자 읽기 + 미언급 삭제 schema에서 원본 author가 완주했다. 최종 후보는 read만 permit하고 delete는 Cedar/SQLite에서 DENY·효과0, 정상 read 효과1이었다. 원본 Atom Reviewer 1개 승인과 verifier 3/3 PASS를 확인했지만 사용자 최종 승인 `false`이며 실제 활성화 없음. 이 1회 결과는 **미승인 action 생성 가설을 지지하지 않으며** C11의 조건부 target coverage Gap이나 더 넓은 action-registry 변경 시 문제를 일반적으로 기각하지 않는다. 현재 추가 유사 변이보다 승인·활성본 결속과 다른 Track의 미검증 효과 경계를 우선한다.
