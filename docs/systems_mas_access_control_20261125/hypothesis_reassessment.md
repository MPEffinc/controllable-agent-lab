# H1–H14 독립 재평가 — 2026-11-25

증거 단위: [기존 가설 원장](../access_control_empirical_20261124/hypotheses.md), [K01–K15 coverage](../access_control_empirical_20261124/coverage_matrix.md), [H14 저장 결과](../access_control_empirical_20261124/runs/H11_context_path_20261125/result.md). 아래 `S/A/C/U/X`는 각각 **Security Gap / Agent·MAS 적용성 / 안전·정상 Correctness & Utility / System Contribution / 가장 강한 반박**이다. `관측`은 이번 또는 원저자 결과 중 명시된 범위만 뜻한다. 이 표는 최초 원문·공식 코드와 전수 재대조의 진행 원장이며, 재확인 전 `UNVERIFIED`를 유지한다.

| ID | 최초 주장·직접 증거 / 상태 | S: 안전 | A: 적용성 | C: 정확성·정상성 | U: 시스템 기여 가능성 | X: 최강 반박·기각 조건 |
|---|---|---|---|---|---|---|
| H1 | K06 AutoCedar 저자 19 target 오류 보고, 공식 gold 200 재컴파일·형식 검사 직접 확인. 사람 atom 검토 효과의 같은 후보 trace 미공개 | **좁은 평가 Gap**; 공격 성공 증거 아님 | 자연어→정형 요구에서 중요 | 독립 의도 oracle/검토 시간 미측정 | 동일 후보에 blind reviewer·gold·정상 task 비교 | K06 자체 review, ECOOP `pick`, Cedar. 동일 후보의 독립 검토가 정상성을 유지하고 수정하면 Need 기각 |
| H2 | 동적 효과 경로 완전 중재 미증명; OpenShell v0.1.9 L7 enforce 직접 차단 | 일반 우회 `UNVERIFIED` | tool 밖 효과에 적용성 질문 | 정상 경로 포함한 effect set 미고정 | effect 경로 discovery·PEP mapping 평가 가능 | OpenShell OS/network, FORGE event, provider PEP, K15 sink의 같은 경로 조합이 차단하면 기각 |
| H3 | provider commit 시점과 승인 시점. VERA+독립 원자 sink A/AND 차단, X OR 정상 보존 | 원자 sink 지원 조건 해결 | 비원자 provider는 별도 | 실제 provider 미시험 | provider별 원자성·fence 비용 측정 | CTA/EffectBound/Authorization Revocation/K15가 같은 API에서 안전·정상 달성하면 기각 |
| H4 | R3 하위 위임 철회 계보. VERA와 기존 철회 연구가 직접 모델링 | 신규 메커니즘 부재 가설 **기각** | 다중 agent 핵심이나 신뢰된 grant 계보 필요 | 실제 provider 결합 미시험 | 계보→effect fence 통합 비용 가능 | 기존 VERA+finality 조합이 동일 위임 경로에서 달성하면 기각 |
| H5 | R1/Progent 같은 허용 tool 아래 추가 파일 effect 구성; Docker 제한 시 정상 보존·추가 effect 차단 | 해당 파일 조건 **기각** | 필수·동적 자원 미검증 | 정상 workload 자원 요구가 관건 | 동적 최소 자원 policy 생성의 정확·비용 | OpenShell/FORGE/ALPS 등 동일 필수 자원에 정상+안전 달성하면 기각 |
| H6 | 획득한 권한 활성화의 모델링; AcquireBound가 직접 다룸 | 일반 부재 가설 **기각** | provider별 적용 미검증 | acquire quarantine·fresh activation 비용 미평가 | provider adapter 검증 가능 | AcquireBound의 등록 profile/완전 PEP가 같은 획득 경로를 처리하면 기각 |
| H7 | base 정책과 effective 정책 차이 K14 실행 확인; 공식 prover가 full 확대 반례 검출 | 현재 형상에서 검사 부재 가설 **기각** | 동적 provider attach 시 중요 | 자동 배포 gate·mode 회귀 미평가 | 활성 hash·mode 검증 운영 비용 | full-effective prover+fail-closed gate가 배포와 효과를 동기화하면 기각 |
| H8 | K07 static graph만으로 조건부 허용 불충분; NIST PM 6조건, Cedar 6조건 독립 effect 대조 | graph-only **좁은 Gap**; 기존 조건 PDP 해결 | 조건 값 출처·commit 결속 필요 | broad unsafe/strict 과거부, Cedar 조건 대조 정상 | IR→조건 PDP·graph 자동 합성 검증 | 정확 조건·trusted context·앱/서비스 PEP가 같은 업무를 처리하면 신규 Need 기각 |
| H9 | K07 저자의 별도 조건 누락 4/714과 무조건화 98/715; 동일 사례 교집합 불명 | 같은 요청 실패 `UNVERIFIED` | 생성/집행 양단 연결 | 평가 분모·정상 조건 미연결 | 단계별 손실을 같은 case에서 추적 | 원본 paired trace에서 교집합 0 또는 강한 review+조건 PEP로 해결되면 기각 |
| H10 | EAL 원본 gate+조달 의미 6입력. 같은 권한자 인용에 잘못된 15k scope면 비인가 10k 로컬 effect 1 | source-only 경계 **관측** | 지속 memory가 MAS에 재사용될 때 확대 가능 | 정확 event 대안 정상 9k+1/비인가 0 | 자연어 승인 변경→typed event의 안전·정상·비용 평가 | EAL rebuild/PLACE 등 정확 event 수집+현재 서비스 PEP가 같은 자연어 입력에서 달성하면 Need 기각 |
| H11 | MAP-Graph 공개 후보 원본 gate의 model-risk 우선순위; 구성적 outbox effect, 저장 41건 인과 미확정 | 구현 경계 **관측** | MAS action metadata 신뢰 문제 | trusted binding 정상 high-trust 보존·비인가 차단 | action type/risk 결속의 평가 | 기존 typed effect policy/PEP가 실제 archived 입력에서도 41건과 정상 task 처리하면 Need 기각 |
| H12 | M4 status-only guard에 무표지 재기록 통과, 원본 guard+로컬 HTTP/SQLite 비인가 effect 1 | 구현 경계 **관측** | 다중 agent memory writeback에 적용 | 정확 lineage 또는 current service PEP는 정상 보존·비인가 차단 | 실제 자동 lineage capture·writeback 평가 | MAP-Graph식 code-owned lineage 또는 service PEP가 자연 writeback에서 달성하면 Need 기각 |
| H13 | H10/H12 잔여를 묶은 자연어 event·실제 파생 edge 수집 공동 평가 | 메커니즘 부재 가설 **기각**, 새 안전 실패 `UNVERIFIED` | MAS 승인 변화와 파생 memory에 중요 | 같은 입력의 safety+utility 측정 없음 | 정확 수집·검토·비용의 end-to-end 실증 가능 | WTB v4/Epistemic Guard/PLACE/CONTINUITY 조합이 같은 입력에서 적정 비용으로 달성하면 기각 |
| H14 | [원본 MAP-Graph 보조 메서드 결과](../access_control_empirical_20261124/runs/H11_context_path_20261125/result.md): tool output의 `derived_from` 소실, prompt raw output은 가시, `write()` support IDs 누락. 결정적 local outbox A/A2 비인가+1; 정확 edge 또는 current service PEP 0/정상+1 | **좁은 공개 구현 Gap** | raw tool output→MAS memory→action 경로 | 전체 LLM workflow·41건 인과 미평가 | 영향 받은 prompt context의 정확 support 수집·오탐·비용 실증 | 완전 context-support adapter 또는 service PEP가 실제 LLM·정상 task에서 달성하면 새 Need 기각 |

## 이번 재해석

이전 `REJECTED_HYPOTHESIS`는 위 표의 고정 구성/효과에만 적용한다. H13/H14의 핵심은 새 방어 원리 부재 주장이 아니라 **자동 권한 의미/출처 수집과 여러 PEP의 결속을 실제 Agent/MAS workload에서 안전·정상·비용으로 함께 검증했는가**다. 이것도 아직 연구 Need로 확정되지 않았다.

## 추가 원문 재감사 필요

H1 K06 Table VI 후보 trace, H9 K07 두 실패 집합의 교집합, H11 MAP-Graph 논문 평가 commit과 raw trace, H14 전체 workflow, H13 강한 기존 조합의 동일 입력 성능은 미확정. 각 항목은 해당 원시 자료 또는 별도 신규 실험으로만 승격한다.
