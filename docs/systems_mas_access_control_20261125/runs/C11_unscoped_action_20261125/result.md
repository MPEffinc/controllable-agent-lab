# C11 AutoCedar target 밖 action 검증 범위 실험

2026-11-25 UTC. [사전등록](prereg.md), [실행 코드](run.py), [원시 verifier·Cedar 출력](result.json), `plan_scope_only/`, `plan_closed_actions/`, [독립 SQLite 효과](service_state.sqlite). 공식 AutoCedar source SHA `a0cf180977d799cf943514b67ffc260fc579b9a5`. 원본 case-011 요구사항은 조건을 만족한 PR merge만 허용하고 **그 밖의 action은 허용하지 않는다**고 한다. 공식 schema에는 merge만 있어 연구자가 `deletePullRequest`를 추가한 **별도 확장 schema**를 사용했다. 원본 gold에는 손대지 않았고, 후보는 gold에 unconditional delete permit 하나만 더했다.

| 검사/요청 | Gold | 과권한 후보 |
|---|---:|---:|
| 원본 AutoCedar `verify`, merge scope만 ceiling+floor | 해당 없음 | **PASS**, loss 0 |
| 같은 `verify`에 delete candidate⇒gold ceiling 추가 | 해당 없음 | **FAIL**, loss 1, delete counterexample |
| Cedar CLI 정상 merge | ALLOW, SQLite `merged` +1 | ALLOW, `merged` +1 |
| Cedar CLI 비인가 delete | DENY, SQLite 삭제 효과 0 | **ALLOW, `deleted` +1** |

이는 [AutoCedar v2 §III-B](https://arxiv.org/html/2607.03656v2)가 직접 기술한 메커니즘 경계와 일치한다. 문서에 언급된 action만 target scope로 만들고 그 밖의 action에는 검사가 없다면, **그 범위의 정책 확대는 기존 plan 만족과 양립**한다. 원본 verifier가 비어 있는 scope를 자동으로 닫지 않는다는 점을 이 확장 schema의 원본 코드 실행으로 확인했다. 반대로 **동일 원본 verifier에 한 줄의 추가 action 포함 검사**를 주자 오류를 잡았다.

**판정:** `GAP_SUPPORTED`는 “생성/검토 target이 모든 활성 schema action을 덮지 않는 조건에서, 검증 통과 정책이 승인하지 않은 action을 허용할 수 있다”는 좁고 실증된 범위다. 연구자가 후보·스키마를 구성했으며 AutoCedar 원저자 생성기가 이 permit을 실제 만들었다는 증거는 아니다. 외부 GitHub 서비스에 삭제를 실행하지 않았고 SQLite는 모의 effect다. 기존 Cedar/AutoCedar 포함 검사로 이 고정 범위는 해결되어 **새 정형 검증 메커니즘 Need는 기각**한다. 남는 질문은 자연어의 “그 밖의 action 금지”와 확장되는 schema/tool registry에서 *어떤 action을 반드시 닫아야 하는지* target이 완전하게 판정·유지되는가이다.
