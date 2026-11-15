# R1 선행연구 대조: 권한 상태·최종 효과 경계

확인일: 2026-11-15 (Asia/Seoul). 원문 HTML의 관련 본문·부록을 확인했다. 아래 문헌 수치와 보장은 **저자의 원문 주장**이며 우리 실행 결과와 구분한다. 이후 CONTINUITY 원본 quick conformance는 실제 실행했고 [별도 실행 감사](r1_continuity_artifact.md)에 기록했다. Authorization Revocation/ResidualAuth와 R1 A2A에 대한 CONTINUITY integration은 **NOT_RUN**이다. D1–D6 분류를 재정의하지 않는다.

## CONTINUITY

출처: [2609.05269v1, 2026-09-04](https://arxiv.org/html/2609.05269v1), §3, §5–7, §8, §9.6–9.7, §12. [논문이 연결한 artifact](https://github.com/zast-ai/continuity).

- **Security Property / Existing Solution:** effect와 authenticated origin·principal·task·grant·provenance·contract·현재 policy를 연결하는 ECI witness. finality sink가 subject/action/policy/revocation/expiry/replay를 효과 직전에 다시 검사한다. 이전 permit 발급만으로 효과가 허용되지 않는다.
- **Assumptions:** 신뢰된 issuers/verifier/sink와 완전 중재, context manifest의 런타임 완전성. prototype의 nonce·idempotency·finality는 in-memory atomic 모델이다.
- **Original Evaluation:** LLM 없는 결정론적 네 도메인(위임 포함), 32 fault classes, 2,560 attack/700 benign/200 ambiguous 시나리오. alternate path·revocation 재검사 제거 등을 다룬다. incomplete arms는 명명된 기존 시스템 재현이 아닌 기제 대조군이다.
- **R1 대조:** stale permit·다른 경로 효과·finality-time 재검사는 이미 직접 다룬다. 실제 A2A/provider의 동시성·partial failure·지속성은 별도 integration 검증 대상이다. R1 fixture의 단순 반례로 이 보장 실패를 주장할 수 없다.

## Authorization Revocation

출처: [2609.21284v1, 2026-09-18](https://arxiv.org/html/2609.21284v1), §3.4, §4.4–4.6, §5, §7.2–7.5, §8, §10.

- **Security Property / Existing Solution:** root cut과 provider-local fence를 구분하고, old-root pre-fence acceptance를 정확히 정산하며 post-fence acceptance를 배제한다. 독립적 충분 지원으로 exact rebind하면 작업을 보존한다.
- **Assumptions:** issuer 중재·진본 증거·durable linearization·완전 manifest/channel accounting·atomic fence/rebind. 누락/불투명 증거는 `Indeterminate`다.
- **Original Evaluation:** provider-free 17-case durable-ledger/실제 child-worker suite와 독립 checker, 44 semantic mutations. 취소-only/cut-only, cut+fence, restart/stale process, alternate-root, pre-fence accounting을 직접 비교했다. remote A2A/provider 재현은 아니다.
- **R1 대조:** cut과 fence 사이 acceptance 및 barrier 이후 기존 acceptance 정산은 논문상 허용될 수 있다. 즉시철회나 pending-effect 취소는 R1의 별도 의미다. rollback·global idleness와 구분해야 한다.

## ResidualAuth

출처: [2609.08062v2, 2026-09-30](https://arxiv.org/html/2609.08062v2), §3–8, Appendix F/G/H/I/K.9/M.

- **Security Property / Existing Solution:** 현재 permissions/reachability만 같아도 철회 이후 결정을 구분하는 history가 필요함을 formal residual-state 관점에서 분석한다. 새 보안 아키텍처를 제안하는 논문이 아니다. trusted ledger의 hard gate는 proposal과 effect를 분리한다.
- **Assumptions:** authenticated principals/events, 명시된 revocation semantics. 실험 ledger→graph 대응은 exact-coordinate·immutable selected-parent와 full selected-lineage 제한 아래 성립한다. 일반 runtime으로 무조건 확장하지 않는다.
- **Original Evaluation:** paired synthetic authorization episodes, 정보 접근/모델 memory 유지/답변 사용/실행 gate를 따로 평가. Qwen의 별도 advisory/hard 실행은 각 128 episodes에서 unauthorized attempts 8건씩, commit 8건/0건이었다. episode별 동일 proposal이라는 뜻은 아니다.
- **R1 대조:** 부정확한 proposal을 gate로 막는 기능과 권한상태 보존은 별개다. §8은 stale-state safety와 deployment architecture를 미검증으로 남긴다. R1의 root A/B 단일-grant fixture만으로 이 논문의 multi-path residual-state 요구를 재현했다고 할 수 없다.

## 이번 판단 범위

**Established prior overlap:** post-intervention stale authority, finality 재검사, root별 독립 지원 보존은 이미 연구되어 있다. **Our Validation:** CONTINUITY 원본 quick conformance 실행과 R1 Progent component/synthetic SUT를 별도로 구분한다. 다른 두 방법과 CONTINUITY의 R1 adapter는 NOT_RUN이다. **Open Question:** 동일한 명시적 acceptance/fence 의미와 실제 A2A 실행 경로에서 가장 가까운 원본 artifact의 완전 중재·상태 신선성을 검증할 수 있는가? 이 질문은 아직 gap 확정이 아니다.
