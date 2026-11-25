# H1·K07 조건부 집행 독립 반박 검토

2026-11-24. **독립 검토 단계**: 아래 선행연구와 판정은 K07 로컬 사전등록·PM 결과를 읽기 전에 원문/공식 문서로 작성했다. `H8`은 K07의 조건부 NGAC export 문제를 가리키는 편의 번호이며, 새 연구 주제 확정이 아니다.

## H1 — 자연어→검증 target 의미 오류의 사람 검토

**가장 강한 직접 선행연구.** [Prasad et al., ECOOP 2026, §2·§4.3, Table 4](https://drops.dagstuhl.de/storage/00lipics/lipics-vol372-ecoop2026/html/LIPIcs.ECOOP.2026.22/LIPIcs.ECOOP.2026.22.html)의 `pick`은 ABAC 후보 정책들이 구별되는 subject–action–resource 요청을 SAT로 만들고, 사람이 그 요청의 허용 여부를 판단하여 후보를 고른다. 이는 실제 사람을 대상으로 자연어 의도와 정책 결정의 일치를 시험한 직접 반박이다. 공식 [DARTS 승인 artifact](https://drops.dagstuhl.de/entities/document/10.4230/DARTS.12.1.7)는 0.89 GB이며, regex용 VS Code 확장과 익명화 사용자 연구 자료·인터페이스/통계 재현 Docker 이미지를 제공한다. 공개 ABAC 연구 자료가 있다는 뜻이지 ABAC 편집기가 배포됐다는 뜻은 아니다.

**정확한 분모와 과제.** ABAC 참가자는 Control(후보 목록 선택), With List(구별 요청 분류+후보 목록), Without List(구별 요청 분류·목록 미표시) 각 **50명**, 총 150명이며, 각자가 Accounting/Grading/Technology 세 문제를 푼다. Table 4 수치는 *조건별 문제별 정답 참가자 비율*이지 정책 정확도 450건의 독립 표본이나 실제 집행 성공률이 아니다. Accounting은 40/66/70% (Control/With/Without), Grading 46/68/66%, Technology 46/60/64%. Control 대비 유의한 개선은 Accounting의 두 조건과 Grading의 With List뿐이다. 저자들이 작은 교과서형 문제의 올바른 후보를 검토 후 gold로 삼고, superset/subset/overlap 후보를 **의도적으로 수정**해 만들었다(§4.3.1). 따라서 이 연구는 실제 AutoCedar 생성 target 오류 19건의 사람 수정률·비용을 측정하지 않지만, “접근정책의 의미 검토를 사람이 시험한 연구가 없다”는 넓은 H1을 기각한다.

**남는 측정 질문.** [AutoCedar v2 §V-D/Table VI](https://arxiv.org/html/2607.03656v2)의 자체 plan 통과 197개 중 독립 gold 불일치 19개에서, (a) 원문-atom/intent-map 직접 검토와 (b) `pick`식 구별 요청 판단 중 어느 쪽이 같은 실제 생성 오류를 더 적은 시간·확인 횟수로 잡고 정상 허용을 보존하는가? 원저자 19 case의 candidate/plan trace가 공개되지 않았으므로 새 generation run은 별개 cohort로 표시한다. **기각 조건**: `pick` 또는 독립 gold/검토의 현실적 조합이 같은 조건에서 오류를 충분히 제거하고 허용 가능한 비용을 보이면, 신규 메커니즘 Need를 기각한다. 지금의 엄격한 라벨은 `GAP_SUPPORTED` = *K06 특정 review mode의 동일 오류에 대한 평가 공백*만; 일반적 인간 검토 공백과 신규 Framework Need는 `REJECTED_HYPOTHESIS`/`UNVERIFIED`다.

## K07 — 조건부 권한의 export와 실제 집행

**K07 원문의 경계.** [NGAC-IR v1 §5.1](https://arxiv.org/html/2611.26941v1)은 NIST PM이 요청 시 조건을 검사하지 못해 broad export의 조건부 permission **98/715(13.7%)**가 무조건 허용됨을 보고한다. strict export는 이를 PM 그래프에서 빼고 원문/조건과 함께 앱 검사 대상으로 남긴다. PM의 **390 요청**(T2P 98, IBM 86, CC 84, ACRE 122)은 *컴파일 그래프에서 도출한 예상 결정*과 일치했다. strict export에서 23 요청의 결정이 허용→거부로 바뀌었다. 저자들이 보여준 4개 event obligation은 dataset당 1개다. 앱의 조건 검사, 조건 참일 때 정상 효과, 조건 거짓일 때 효과 차단은 §5.1에서 검증되지 않았다. 이 23건을 gold 위반/정상 업무 실패로 단정할 수 없다.

**가장 강한 기존 해결책.** [Cedar 공식 authorization 문서](https://docs.cedarpolicy.com/auth/authorization.html)는 요청마다 principal/action/resource/context를 받아 정책을 평가하고, [Cedar 조건 구문](https://docs.cedarpolicy.com/policies/syntax-policy.html)은 `when`/`unless`로 조건을 표현한다. [OASIS XACML 3.0 §3.3.1.3–4](https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-cos01-en.html)는 요청별 Boolean `Condition` 및 PDP가 PEP에 전달하는 obligation을 표준화한다. 이들은 **신뢰 가능한 조건 사실을 PEP가 제공한다는 전제**에서 조건부 결정을 이미 다룬다. 더 가까운 2026년 대안인 [Structured Decomposition §6.4/Table 3](https://arxiv.org/html/2609.24036v1)은 자연어→Rego 결과의 조건 존재를 77개 공통 출력 중 소집단인 ownership **5/5**, status **9/9**에서 보고한다. 저자도 이것이 원문과 완전한 의미 동치가 아닌 compilation/lint/test 기반 정확성이라고 밝힌다(§6.1). 공개 코드·실제 service effect는 여기서 확인하지 못했다. [NIST Policy Machine Core](https://github.com/usnistgov/policy-machine-core)의 EPP와 [NISTIR 7987r1](https://nvlpubs.nist.gov/nistpubs/ir/2015/NIST.IR.7987r1.pdf)은 event-pattern obligation으로 그래프를 갱신할 수 있다. 그러나 이것은 임의의 요청 시점 조건을 자동으로 검사한다는 뜻이 아니다. K07 strict export+앱 조건 검사도 문헌에 제시된 보수적 조합이다. 따라서 “조건부 집행 메커니즘이 없다”는 가설은 기각한다.

**남는 측정 질문.** K07의 실제 조건부 문장을 대상으로, source-faithful predicate와 신뢰 가능한 요청 context를 준비했을 때 `strict NGAC + app PEP`, `Cedar/XACML PEP`가 **조건 참에서는 정상 효과를 보존하고 거짓/정보 누락에서는 효과를 막는가**, 그리고 event obligation이 의도된 횟수/순서로 발생하는가? 동일 요청·동일 source oracle·실제 effect를 써야 한다. broad export는 과허용 대조, strict export 단독은 보수적 과거부 대조다. `NGAC_allow && condition`이라는 전체 결과의 단순 결합은 다른 독립 permission route를 잘못 거부할 수 있으므로 **규칙별 조건/route**와 forbid 우선순위를 보존해야 한다. 원자적 서비스 효과·동시성은 별도 전제다. **기각 조건**: 기존 PDP/앱 PEP 조합이 조건 참/거짓/누락·정상 업무를 충분히 처리하면 새 메커니즘 Need는 없다. 라벨은 **정적 NGAC graph-only의 조건 표현·집행 한계 `GAP_SUPPORTED`**(그 범위의 구성요소 한계), **K07 strict+app 최종 효과 `UNVERIFIED`**, 기존 조건부 집행 조합 가능성 `RESOLVED_IN_SCOPE`로 분리한다. graph-only의 한계를 접근통제 분야 전체의 신규 Need로 확대하지 않는다.

## 최소 평가 프로토콜과 중단 기준

1. K07의 공개 조건부 원문 중 의미가 분명한 1–3개를 선택하고 권한자가 참/거짓/누락 context에 대한 기대 결정을 독립 확정한다. 중복 allow route와 forbid를 최소 한 개 포함한다. K06은 생성 후보·plan·원문을 고정하고 gold는 reviewer에게 숨긴다.
2. 각 run의 policy, PEP, audit/enforce mode, context 출처, 요청, 예상·실제 결정, effect 전후 상태, obligation 사건, 실행시간/사람 검토시간을 저장한다. 외부 서비스·유료 LLM 호출 없이 로컬 mock effect로 시작한다. mock은 논문 재현이나 배포 보장을 뜻하지 않는다.
3. K07 broad/strict/strict+app/Cedar 또는 XACML을 같은 oracle에 비교한다. K06 atom review/`pick`식 구별 요청/원본 후보 직접 선택을 같은 생성 사례에 배정한다. 과허용·과거부·정상 완료·검토 질문 수·비용을 함께 측정한다. 1–3 case를 통과하면 해당 기계적 질문을 닫고, 일반성은 별도 `UNVERIFIED`로 둔다.

**독립 판정:** H1의 폭넓은 연구 공백은 `pick`이 직접 반박한다. K07 조건부 집행은 기존 정책 언어와 조합으로 가능하다. 남은 것은 두 원저자 흐름의 **같은 조건에서 실제 검토/집행 효과를 얼마나 보이는지**라는 좁은 평가 질문이다. 신규 프레임워크의 필요성은 아직 입증되지 않았다.

## 독립 초안 작성 후 K07 로컬 실험과 대조

[사전등록](runs/K07_condition_boundary/prereg.md), [결과](runs/K07_condition_boundary/result.md), [원시 6행](runs/K07_condition_boundary/decisions.jsonl)을 후순위로 읽었다. 실험은 원저자 생성기/390 replay가 아니라 NIST 소유 [Policy Machine 3.3.0 tag](https://github.com/usnistgov/policy-machine-core/tree/3.3.0)를 고정한 별도 worktree에서 원본 PM의 PAP/PDP와 인메모리 ledger를 사용했다. 같은 `read(doc)` 의도에서 상태 `registration_open=false/true`를 각 export에 적용했다.

| 대조 | false 상태: PM/최종 effect | true 상태: PM/최종 effect | 해석 |
|---|---|---|---|
| broad association | ALLOW / ledger 0→1 | ALLOW / 0→1 | 참거짓 구별 실패, 거짓에서 로컬 효과 1. |
| strict association 제외 | DENY / 0→0 | DENY / 0→0 | 차단되나 참에서도 정상 효과 없음. 원저자 strict+app 경로 전체는 미시험. |
| broad+app preguard | PM graph ALLOW, app DENY / 0→0 | PM ALLOW, app PASS / 0→1 | **이 실험의 별도 조합**에서 조건 참/거짓을 올바로 처리. false에서 PDP 자체는 미호출. |

6개 조건은 단일 테스트 메서드로 실행되어 Surefire `Tests run: 1`이고 assertion 실패는 0이다. 이를 6개의 독립 trial, 실제 외부 서비스 효과, NGAC-IR 원저자 재현으로 세지 않는다. 관측은 **정적 association에 조건 정보가 빠진 상태와, 신뢰된 app bool preguard가 붙은 상태**의 좁은 경계다. 특히 `broad+app`은 저자의 `strict+app` export를 구현한 것이 아니다. 그래서 기존 조합의 한 사례는 `RESOLVED_IN_SCOPE`, 저자 strict+app의 정상 허용·effect 및 복수 route·forbid·의무·정보 신선도는 `UNVERIFIED`로 남긴다. 새 메커니즘 Need는 관측되지 않았다.

**다음 최소 반증:** 위 6행을 되풀이하기보다, 같은 원문의 조건부 권한과 무조건 권한이 공존하는 경우에 app이 *어떤 route*의 조건을 검사하는지 추적한다. `strict+app`의 정상 허용 참 상태가 실제로 복구되고 거짓/조건 정보 누락에서 효과 0인지, 다른 무조건 route는 과거부 없이 허용되는지, forbid가 우선하는지 확인한다. 독립 oracle과 로컬 effect가 확보되지 않으면 `UNVERIFIED`에서 멈춘다. Cedar/XACML의 같은 요청 결정은 강한 기존 반박 대조다.
