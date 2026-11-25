# 연구실 시스템 접근통제 ↔ Agent/MAS 경계 대조

2026-11-25. `논문 주장`, `고정 공개 코드`, `이번 실행`을 분리한다. 비교 대상은 동일한 보안 속성을 전제로 하지 않으며 퍼센트 성능을 직접 비교하지 않는다. [Backlog](https://docs.google.com/spreadsheets/d/1XW5u4aPcshHSyL7Z8cSQZoILxQhWkMRBKb903_aBD3Q/edit)는 연구 일정/읽기 목록 확인에만 사용했다.

| 연구 | 문제·정책 생성/표현 | 실제 집행점·신뢰 전제 | 확인된 평가/한계 | Agent/MAS 관계 |
|---|---|---|---|---|
| [ALPS](https://cclab.info/papers/2026_shin_infocom.pdf) | 함수 source/CodeQL→최소 action/resource, vendor IAM/allowlist; fine-tuned LLM은 통합 코드 생성 | 함수 내부 SDK interception `Verifier.check(permission,resource)` 및 IAM. 함수 코드·정적 분석·hook 완전성 신뢰 | 원문 §V-D 8,322 함수 중 7,891 entity-level 추출 성공. 실패 331은 동적 resource ID/wildcard. [원본 단위 12 pass](runs/A3_alps_runtime_20261125/result.md), 실제 provider effect 아님 | 함수/worker 권한은 확인; user task/root grant·delegation은 검사 키 아님. 같은 worker의 task별 scope 결속은 별도 K04/K15/Agent libOS/서비스 PEP가 가능 |
| [KubeAegis](https://cclab.info/papers/2024_kim_access_kubeaegis.pdf) | KAP로 Cilium/Calico·KubeArmor/Tetragon·Kyverno 정책을 한 operator에서 관리 | 원본 `KapValidator`는 `ValidateExistence`, `ValidatePrecondition`; adapter dispatch·상태 추적. K8s API와 adapter 신뢰 | 원문 §VII-C가 network allow와 system deny의 **의미 충돌**을 명시한 한계. 공개 코드 [kapvalidator.go](https://github.com/cclab-inu/KubeAegis/blob/79845cbcca83f12cab5cc7f6097a68dc2cb1fc5e/pkg/validator/kapvalidator.go)는 의미 충돌 검사 호출 없음. 실클러스터 재현 전 | 다중 PEP 정책 delivery/상태 추적에 유용; MAS 원천 승인→KAP 의미 보존·실행 주체 결속은 별도 문제 |
| [KubeTeus](https://cclab.info/papers/2025_kim_infocom.pdf) | 자연어 intent 또는 cluster config→LLM 네트워크 정책; BERT entity 추출 | CRD/resource/property 검증 뒤 K8s API 정책 적용. 관리자 intent·cluster state 신뢰 | 원문 §III-B/IV: 세 단계 검증은 구조·실재·속성, 사용자 의도와 생성 정책의 독립 의미 동치는 별도. 원문 F1/BLEU는 의미 보장 아님. 공식 코드 clone만, 실행 전 | agent가 생성한 task policy를 네트워크 정책으로 변환할 수 있는 기술적 출발점; origin grant/최종 서비스 행위까지의 의미는 미확인 |
| [Bambda](https://cclab.info/papers/2025_shin_access.pdf) | 함수 호출 관계·allowlist 및 입력 schema | 함수 entry에 주입한 검증과 CloudWatch 로그 관계; AWS control plane/IAM 신뢰, 한 함수 compromise 허용 | §II-C threat model, §VII-C/E는 schema가 내용 의미를 보장하지 못하며 caller spoofing·log 지연의 정량 evasion 평가를 향후 과제로 둠. 공식 코드 미확인 | inter-function call 경로는 MAS delegation의 인접 유추지만 signed user task/세부 목적 권위까지 직접 검증하지 않음 |
| [POLARIS](https://www.cclab.info/publications) | container file policy 자동 개선(출판 목록 수준) | 정확 코드·PEP 미확인 | 2026 to appear 원문 및 공개 코드 URL 재확인 필요 | 파일 효과층 후보, MAS 비교는 `UNKNOWN` |
| [ARES](https://www.cclab.info/publications) | 서버리스 agentic AI 권한 우회 방지(출판 목록 수준) | 원문 4쪽 PDF가 그림 기반이라 텍스트 추출 실패; 공식 코드 미확인 | 국내 2026 학술대회. **외부 동명 ARES 논문과 구별** | 내용 확인 전 우선대안/해결 edge 부여 불가 |
| [K03 Progent](../access_control_empirical_20261124/coverage_matrix.md) | LLM tool/arg policy, optional SMT 갱신 포함 검사 | tool wrapper before dispatch | 기존 원본 wrapper effect 대조 | 함수 내부 OS/SDK 효과와 별도 계층; downstream resource PEP 필요할 수 있음 |
| [K04 PAuth](https://arxiv.org/abs/2603.17170), [K15 CONTINUITY](https://arxiv.org/abs/2609.05269) | signed task slice/operand provenance, origin grant→delegation→effect permit | 서버 operator/operand, finality sink; 신뢰된 issuer/key/complete sink | 기존 K15 [EUR amount 원본 verifier 대조](../access_control_empirical_20261124/runs/M1_continuity_amount_20261125/result.md); 실제 공유 worker+system PEP 결합 미시험 | task authority→최종 effect의 **직접 강한 대안**. H15를 단순 ‘기법 부재’로 주장할 수 없음 |
| [K08 FORGE](https://arxiv.org/abs/2602.16708), [K13 ActPlane](https://arxiv.org/abs/2606.25189), [K14 OpenShell](https://github.com/NVIDIA/OpenShell) | 실행 event/provenance, kernel LSM, sandbox policy | event join point, OS hook, Landlock/network proxy | K14 [provider effective/audit/enforce](../access_control_empirical_20261124/runs/K14_effective_20261124/result.md) 효과 확인. K08 source build PEP 미실행 | tool 밖 파일/네트워크는 차단 가능하지만 업무 의도 정보의 생성·전달을 별도로 요구 |
| [K11 Multi-CaMeL](https://arxiv.org/abs/2610.05640), [K12 ControlValve](https://openreview.net/pdf?id=PNU9Rj5RDQ) | 위임 tree의 data/instruction 경계, agent 호출 edge | Sequrity control / orchestrator | 내부 black-box OS effect는 별도 PEP | MAS 위임·호출 topology를 검사하는 강한 경계, 시스템 effect까지의 구성은 별도 |

## 직접적인 대안과 관계

- [Agent libOS](https://os-for-agent.github.io/papers/AgenticOS_SOSP_2026_paper_8.pdf) §§1–2,5는 stable AgentProcess identity·typed capability·scoped approval·provider primitive를 결합해 **공유 프로세스 안에서도 actor authority를 자원 효과에 연결**하는 직접 대안이다. 저자 80 시나리오/720 modeled row와 24 real-model trial을 구별해야 한다. 코드 [공식 후보](https://github.com/yingqi-z20/Agent-libOS)는 이번 동일 입력에 미적용. H15의 새 메커니즘 필요성에 강한 반박.
- [Semantic Router 다중 target 논문](https://arxiv.org/html/2603.27299v1) §§3,6은 같은 DSL에서 agent gate·MCP/A2A·NetworkPolicy/Sandbox를 생성하는 **직접 교차 계층 대안**이다. §7.1은 **position paper**, production workload/실제 protocol server 통합 미평가라고 직접 말한다. 교차 계층 컴파일 원리 부재 주장은 기각되며, 의미 보존·효과·정상성의 통합 평가가 남는지 검증해야 한다.
- [GrassHopper](https://www.researchgate.net/publication/388127444_Elastic_Cross-Layer_Orchestration_of_Network_Policies_in_the_Kubernetes_Stack)는 Kubernetes NetworkPolicy→VM Security Group의 동적 변환을 다루는 인접 연구다. 논문 원문/코드 직접 재확인 전 KubeAegis의 **network↔system syscall** 의미 충돌을 해결했다는 edge는 부여하지 않는다.
- [AuthBench](https://arxiv.org/abs/2605.14859v2)는 120 coding-agent task의 사람 검토 파일 권한과 실행 validator로 안전·정상 동시 평가를 한다. H1/H15에 대한 강한 평가·정책 생성 반박이나 multi-agent delegation + service effect의 동일 조건 증거는 아직 아니다.

## 분리된 보안 질문

1. **정책 목표:** task별 승인과 function/worker union permission의 차이를 누가 정확하게 추출·검토하는가? KubeTeus/ALPS의 구조·추출 지표는 승인 의미의 oracle이 아니다.
2. **주체 결속:** 여러 Agent가 같은 worker·SDK credential을 쓰는 경우 OS/IAM subject는 worker다. K04/K15/Agent libOS/서비스 PEP가 origin authority를 결속할 수 있다. 기존 대안의 비용·정상성·완전 mediation을 동일 효과에서 비교해야 한다.
3. **교차 계층 일관성:** tool allow, network allow, OS deny, service deny는 서로 다른 결정이다. 단순 network allow+OS deny는 **정상성 실패**가 될 수 있지만 곧바로 비인가 성공은 아니다. active policy/PEP mode와 최종 효과로 판정해야 한다.
