# C11 사전등록 — AutoCedar 검증 target 밖 action의 과권한

2026-11-25 UTC. [AutoCedar v2 §III-B](https://arxiv.org/html/2607.03656v2)는 자연어 문서가 허용/제한을 언급한 action만 target scope로 만들고, **다른 action의 새 허용을 target 검사가 거부하지 않는다**고 명시한다. 공식 `case-011` 요구사항은 merge 조건을 정하고 “no other actions are permitted”라고 한다. 공식 스키마에는 merge만 있으므로 연구자 **확장 스키마**에 같은 User/PullRequest의 `deletePullRequest` action을 하나 추가한다. 공식 gold 정책과 그 정책에 무조건 delete permit을 추가한 연구자 후보를 비교한다.

- **RQ:** merge 범위만 체크하는 AutoCedar 원본 `verify` plan이 delete 과권한 후보를 통과시키는가? delete 범위의 포함 검사를 추가하면 반례를 찾는가? 정상 merge와 비인가 delete의 실제 로컬 효과는 무엇인가?
- **고정 대조:** `plan_scope_only`는 공식 case의 merge 요청에 대해 candidate⇒gold ceiling, gold⇒candidate floor. `plan_closed_actions`는 동일 두 검사에 delete candidate⇒gold ceiling을 추가한다. gold는 delete를 허용하지 않는다. 두 plan 모두 원본 AutoCedar `verify` CLI로 실행한다. 공식 Cedar CLI는 원본 gold/과권한 후보 × 정상 merge/delete를 평가하고, 독립 SQLite PR 상태는 허용된 action 때만 변한다.
- **예상/반증:** scope-only plan이 PASS, closed-actions plan이 delete counterexample으로 FAIL, 후보의 정상 merge ALLOW·delete ALLOW, gold의 merge ALLOW·delete DENY를 예상한다. scope-only가 이미 delete를 잡으면 이 소스 경로의 gap 가설 기각. closed-actions가 찾으면 기존 추가 scope 검사로 해결돼 새 정형 verifier 메커니즘 Need는 기각. 실제 원저자 자동 생성기가 이 후보를 만들어냈다고 주장하지 않는다.
- **비용·경계:** 모델/API $0, 공식 AutoCedar verifier·Cedar CLI, 모의 SQLite 효과. 원저자 source는 수정하지 않고 별도 workspace에 스키마·후보·plan을 둔다. 실제 GitHub delete effect 없음. 확장 action은 연구자 통제 조건이며 공식 case의 원저자 gold 평가와 분리한다.
