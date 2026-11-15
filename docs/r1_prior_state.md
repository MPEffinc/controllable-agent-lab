# R1 선행연구 대조: 상태·provenance·중재 경계

확인일: 2026-11-15 (Asia/Seoul). 아래는 공식 arXiv HTML 원문의 R1 관련 절만 읽은 결과다. 논문을 실행한 결과가 아니며, 네 항목의 **Our validation = NOT_RUN**이다. `UNKNOWN`은 본 R1 조건에 대한 명시적 평가를 확인하지 못했다는 뜻이지 미지원·취약점 판정이 아니다.

## SoK — arXiv:2609.00595v1, 2026-09-01

- **Property / 판단 틀:** §5.1은 path target, observation, intervention, trust boundary, recovery를 분리한다. §5.3은 한 경계의 차단이 모든 경로를 닫는다는 뜻이 아니며, containment가 복사된 상태·위임 권한의 복구를 뜻하지 않는다고 설명한다. [§5 원문](https://arxiv.org/html/2609.00595v1#S5)
- **Evaluation:** §6.2.1은 single-principal 대조 또는 관계 제거 대조를 요구한다. 이는 특정 정책 구현의 안전성 정리가 아닌 문헌·평가 감사다. R1의 단일 agent/hand-off 제거 조건을 정당화하지만 새로운 gap의 증거가 아니다. [§6.2](https://arxiv.org/html/2609.00595v1#S6.SS2)
- **Taxonomy 주의:** 이 버전 SoK §5.2의 자체 control primitives는 D1–D4다. 사용자 Related Works의 **D1–D6를 대체하거나 같은 번호로 합치지 않는다**. 기존 sheet 정의가 확인될 때까지 교차 mapping은 UNKNOWN으로 둔다.

## FORGE — arXiv:2602.16708v4, 2026-10-12

- **Guarantee / mechanism:** §4.4는 모든 정책 대상 action을 effect 전에 중재하고, 정책이 사용하는 이벤트·의존성·identity를 정확히 기록한다는 두 가정 아래 배치된 Datalog policy의 denial이면 action을 실행하지 않는다고 명시한다. transitive provenance와 approval/delegation 조건은 이미 정책 표현 대상이다. [§4.4](https://arxiv.org/html/2602.16708v4#S4.SS4)
- **Evaluated:** §5의 information-flow, τ²-Bench, MALADE, AgentDojo 및 OpenClaw/Copilot case study는 compliance·task success·overhead를 평가한다. 차단 후 task completion도 연구 질문에 포함된다. **root cut 전후 queue acceptance/commit/fence의 R1 matched 조건은 UNKNOWN**이다. [§5](https://arxiv.org/html/2602.16708v4#S5)
- **Limits / R1 의미:** §7.1은 미계측 channel에 보장하지 않고 명시적 사전 정책을 요구한다. 내부 concurrent event가 atomic 관측 가정을 깨면 incomplete graph가 가능함을 이미 지적한다. 따라서 미중재 B 또는 stale authorization policy의 실패만으로 이 보장을 반증하지 못한다. [§7.1](https://arxiv.org/html/2602.16708v4#S7.SS1)
- **Code audit only:** 확보된 FORGE SHA `ecc5ff9f7576f2669249609d9002c07674947913`의 `experiments/agentdojo/sasy_agentdojo/monitor.py::SasyToolsExecutor.query`는 판정 뒤 `runtime.run_function`을 호출한다. `asked`는 현재 harness에서 실행될 수 있으므로 hard deny와 별개로 읽어야 한다. 엔진 실행·논문 재현은 NOT_RUN이다.

## Governed Shared Memory — arXiv:2606.24535v1, 2026-06-23

- **Property / mechanism:** §3.2의 Inv-Scope는 반환된 모든 memory에 대해 요청 agent가 governance에 따라 해당 scope를 읽을 권한이 있어야 한다는 조건이다. §5는 scope filtering, temporal supersession, provenance, propagation을 결합한다. 오래된 상태의 재사용과 retrieval 경로별 authorization은 이미 명시된 문제다. [§3–5](https://arxiv.org/html/2606.24535v1#S3.SS2)
- **Evaluated:** MemClaw live REST를 ArgusFleet가 leakage·contradiction·provenance·propagation 네 축으로 측정한다. §9.1은 agent-scoped GET-by-id 경계 누락을 보고하고 수정 뒤 재측정한다. tenant-key의 넓은 가시성과 agent-scope 위반을 구분한다. [§7–9](https://arxiv.org/html/2606.24535v1#S9.SS1)
- **Limits / R1 의미:** §10은 단일 tenant, focused scope probes, 부분적인 supersession/staleness 측정, 비교 baseline 부재를 명시한다. **root-task revocation, 이미 수락된 queue 작업의 commit 권리, sink fence, 타 root 지속성의 직접 평가는 UNKNOWN**이다. memory 접근 제어와 외부 effect 승인 의미를 동일시하지 않는다. [§10](https://arxiv.org/html/2606.24535v1#S10)

## Multi-CaMeL — arXiv:2610.05640v1, 2026-10-05

- **Property / mechanism:** §IV는 agent-as-tool 호출의 trusted `message`와 opaque `variables`를 분리한다. interpreter가 instruction-channel integrity와 cross-agent capability/provenance 보존을 집행하여 hierarchical CFI 및 배치한 policy S에 대한 CaMeL-security를 구성한다. 기존 plan 내부의 branch steering은 CFI 위반과 구분한다. [§IV](https://arxiv.org/html/2610.05640v1#S4)
- **Evaluated:** §V는 AssetOpsBench utility와 MultiAgentDojo utility/security를 비교한다. §IV-B는 실제 평가가 **trivial security policy**를 사용했다고 명시하므로 nontrivial root-revocation policy를 실증했다고 확대하면 안 된다. [§IV-B·V](https://arxiv.org/html/2610.05640v1#S4.SS2)
- **Limits / R1 의미:** §VI-A는 unique-parent tree와 parent-child call/response를 대상으로 하며 retained state, DAG, queue/shared memory·async·cycle의 일반화는 후속 문제로 둔다. root cut/fence·독립 root 지속성은 UNKNOWN이다. R1에서 중재된 handoff가 안전한 경우도 provenance 보존이 해결하는 기존 영역을 먼저 배제해야 한다. [§VI](https://arxiv.org/html/2610.05640v1#S6)

## 이번 비교에서 축소해야 할 후보

**문헌상 이미 제시된 해결:** 모든 효과 경계에서 현재 정책 검사, 인과 provenance 보존, 모든 retrieval 경로의 scope 검사. 위 조건이 누락된 고의적 fixture에서 효과가 남는다는 관찰은 구성·계측·정책 의미의 문제를 보여준다. 그것만으로 기존 방법들의 미해결 gap을 확정하지 않는다.

**남길 질문:** 실제 artifact에 특정 root의 cut과 sink acceptance/commit 의미를 명시했을 때, queue와 delegated state에 필요한 사실·identity·승인 근거가 faithfully 관찰되고 모든 실제 effect에 판정이 적용되는가? 이는 R1 후속 검증 질문이며 본 노트는 해당 방법들의 runtime 결과를 제공하지 않는다.
