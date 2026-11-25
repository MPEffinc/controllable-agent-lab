# H20 — policy artifact의 완료·승인·활성화 결속

2026-11-25 UTC. **Problem:** 생성기가 policy file을 만든 상태와 승인자가 그 policy의 *의미*를 승인한 상태, 최종 PEP가 같은 bytes/hash를 활성화한 상태를 소비자가 혼동하면 승인 범위의 end-to-end 보장이 깨진다. 정상 작업은 승인된 policy의 실행이다. 공격자 없이도 CI/adapter가 프로세스 성공만 보고 배포하는 구성 오류가 가능하다.

| 증거 단계 | 확인한 내용 | 경계 |
|---|---|
| 원본 source | AutoCedar [`_authoring_completed`](../../third_party/K06-autocedar/autocedar/cli.py)는 후보 파일 존재를 완료로 보고 `_cmd_author`는 승인 false를 별도 출력하고도 완료 시 exit 0. 주석은 의도적 분리라고 명시. [`_final_user_approval_state`](../../third_party/K06-autocedar/autocedar/pipeline.py)는 명시 `intent_acknowledged_by_user`만 승인으로 취급 | 원저자 코드의 artifact 생성 API. 정책 배포 API가 아님 |
| 원본 저장 trace | [C3 archive/재실행](runs/C3_autocedar_release_gate_20261125/result.md)의 수동 AITL CyberChair 후보는 42 verifier pass, final approval false, candidate 존재 | 논문 19개 gold 불일치 후보와 동일하지 않음. 승인 false는 검토자 의미 오류 발견이 아니라 사람 승인 부재 |
| 독립 효과 대조 | 같은 후보에 completion-only 소비자는 SQLite 모의 effect +1; approval-gated 소비자는 0 | 외부 서비스·실제 배포 아님. 그 정책이 승인 의도와 틀렸다는 증거 아님 |

**가장 강한 기존 반박:** 원본이 이미 `final_user_approved`를 제공한다. 소비자가 이 필드를 fail-closed로 검사하고 policy hash/승인자를 배포 artifact에 결속하면 이 고정 위험은 해결된다. 기존 CI change approval, 서명된 artifact, K14 effective policy 검증, Cedar policy inclusion도 각각 관련 검증 수단이다. 다만 이들을 동일 활성 정책까지 묶어 실제 평가한 것은 C3가 아니다.

**기각 조건:** 원본/현행 소비자 코드가 approval false에서 후보 사용을 차단하고 승인된 exact hash만 활성화함을 확인하거나, 다른 연구의 동일한 approval→active policy attestation이 정상·안전·비용을 달성하면 넓은 H20 Need는 기각한다. 단순히 AutoCedar CLI exit 0인 사실만으로 학계 전체의 새 Gap이라고 할 수 없다.

**판정:** AutoCedar 소비자가 exit/code artifact만 배포 신호로 삼는 **조건부 인터페이스 Gap `GAP_SUPPORTED`**. 새로운 release gate 메커니즘 필요 `REJECTED_HYPOTHESIS`(이 조건). 여러 policy 생성기/PEP 사이의 승인·검증·활성본 결속 정확성과 정상성은 `UNVERIFIED`; 시스템 평가/통합 기여 후보로만 유지한다.
