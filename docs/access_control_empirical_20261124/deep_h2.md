# H2 심층 검증: 새 실행 경로의 완전 중재와 관측 충실성

**기준일:** 2026-11-24. **판정:** `UNVERIFIED` (독립적인 Research Need 미확정). 아래의 논문 결과는 저자의 주장·평가이고, 이 세션의 새 재현 결과가 아니다. 고정한 질문은 “실행 중 추가된 tool·agent·provider가 보호 대상 *동일 효과*를 낼 때, 모든 경로가 효과 발생 전 정책 검사를 통과하고 그 검사에 필요한 사건·출처가 정확히 기록되는가?”이다. 정상 작업은 승인된 경로로 같은 효과를 성공시키는 것이다. 공격자는 agent가 사용할 새 호출 경로 또는 비신뢰 데이터를 제어할 수 있으나, 커널·관리자 정책·provider 자체를 장악하지 않는다고 둔다.

## 원문이 실제로 요구하는 조건

| 연구 | 집행·관측 지점과 보장 범위 | 동적 경로에서 남는 검증 의무 |
|---|---|---|
| [FORGE v4 §4.1, §4.4, §7.1](https://arxiv.org/html/2602.16708v4) / SASY | instrumented framework/tool dispatch와 HTTP join point가 후보 행동을 중단하고 event graph를 기록한다. 정형 보장은 **모든 정책 관련 행동의 사전 중재**와 **사실·의존관계·신원의 충실한 관측**을 전제로 한다. | 저자는 dispatch와 계측 HTTP를 모두 우회하는 raw socket·직접 stdio를 범위 밖이라고 명시한다. 계측되지 않은 채널을 추가하면 그 채널의 method/library 계측이 필요하다. 메서드 내부 동시성에서 event 기록보다 후속 인가가 앞서는 경우도 별도 전제다. 이를 관측된 공격 성공이나 모든 배포의 약점으로 확대하지 않는다. |
| [ActPlane §3.1, §4](https://arxiv.org/html/2606.25189) / [공식 코드](https://github.com/eunomia-bpf/ActPlane) | eBPF/LSM 및 tracepoint의 설정된 OS event를 process tree 전체에서 검사한다. custom Git client가 `exec git` 규칙을 피해도 `connect`/`write` syscall은 보인다는 것이 원문의 강한 반박이다. | 보장은 *설정된 hook에 전달된 event*에 한정된다. 이 계층은 provider의 비즈니스 의미와 사용자의 승인 대상까지 자동으로 식별하지 않는다. hook 목록, 커널/권한 전제, 동적 rule 적용 시점을 확인해야 한다. |
| [OpenShell v0.1.9 정책 개요](https://docs.nvidia.com/openshell/v0.1.9/how-it-works/policies/overview), [네트워크 규칙](https://docs.nvidia.com/openshell/v0.1.9/how-it-works/policies/network-rules), [prover](https://docs.nvidia.com/openshell/v0.1.9/how-it-works/policies/prover) | sandbox 파일·네트워크 경계와 optional L7 요청 규칙. provider 연결은 추가 네트워크 규칙을 **effective policy**에 보탠다. 따라서 “새 provider는 기존 정책을 그대로 우회한다”는 주장은 틀리다. | effective policy의 provider 규칙까지 검토해야 한다. inspected endpoint의 `audit`는 규칙 위반 요청을 로그만 남기고 전달하며 기본값이다. `enforce`가 차단한다. Prover는 *완전한 effective policy*를 입력받아 지원 도메인의 포함만 검사하고 GraphQL/MCP 등은 `unsupported`를 반환한다. `within_boundary`도 실행 중 서비스 효과나 승인 의도 정합성을 증명하지 않는다. |
| [CONTINUITY §3.4, §5.5(C7), §6.8, §9.7, §12](https://arxiv.org/html/2609.05269) / [공식 코드](https://github.com/zast-ai/continuity) | 같은 외부 효과를 낼 수 있는 모든 인터페이스를 effect class로 묶고 permit을 검사하는 finality sink에 연결한다. 원문의 alternate-path negative control은 정상 경로의 서명·permit 검사가 맞아도 다른 경로가 직접 효과를 내면 보호가 안 됨을 보여 준다. | 동등 효과 경로의 열거와 broker 연결은 배포자의 의무다. 저자는 모든 의미적 동등 경로를 자동 추론하지 못한다고 명시한다. 따라서 등록된 경로에 대해서는 강한 직접 해결책이며, 미등록 경로는 모델의 바깥이다. |
| [FAVA v1 §Security Assumptions, §Implementation, §Discussion](https://arxiv.org/html/2607.27267) | permission graph와 gateway-visible 후보에 대해 SMT로 인가한다. 저자는 그래프·정책 번역·gateway-visible 행동에 상대적인 soundness를 주장한다. | 모든 보안 관련 효과가 gateway를 지나고 backend가 capability-conformant여야 한다. 관측 못 한 효과, 누락된 data-flow edge, 모호한 의도가 false negative를 낼 수 있다고 인정한다. Shell은 syscall provenance가 아닌 거친 command sink이다. 논문 공개 평가 숫자를 H2의 동적 경로 완전성 수치로 사용하지 않는다. |

### 계층 간 관계와 강한 반박

FORGE/FAVA가 말하는 관측 충실성은 OS-level 차단과 다른 속성이다. ActPlane이나 OpenShell은 새 SDK·subprocess가 특정 syscall 또는 egress 경계를 지나면 여전히 중재할 수 있으므로, FORGE의 raw socket 제외만으로 *동일 배포*의 비인가 효과를 증명할 수 없다. 반대로 OS/network 계층에서 연결·파일 접근을 허용해도 그것만으로 `merge`의 정확한 repository/head 또는 `send`의 수신자와 본문에 대한 사용자 승인까지 확인되지는 않는다. CONTINUITY의 effect sink 또는 provider 자체의 조건부 API가 그 의미적 최종 효과 경계에 직접 대응한다. [EffectBound §V-B/Table III](https://arxiv.org/html/2609.02866)는 GitHub의 moved-head 사례에서 provider-native SHA binding이 같은 API 조건의 문제를 해결했다는 강한 반박이며, 다른 provider로 무조건 일반화할 수는 없다.

`provider 추가 = 정책 확대`도 항상 참이 아니다. OpenShell의 effective policy에는 provider 규칙이 합쳐지지만 [전역 정책](https://docs.nvidia.com/openshell/v0.1.9/how-it-works/policies/overview)은 provider 규칙을 억제할 수 있고, [prover](https://docs.nvidia.com/openshell/v0.1.9/how-it-works/policies/prover)는 지원 범위 안에서 그 전체 정책이 상한을 넘는지 확인한다. 반대로 prover에 *base policy만* 넣거나 `audit`를 enforce로 오해하면 실제 권한을 과소평가한다. 이는 정책 검토 절차의 검증 질문이지 OpenShell의 일반적 우회 성공 관측은 아니다.

## 가장 좁은 잠재 가설과 기각 조건

**잠재 조건:** 이미 인증된 정책과 기존 PEP가 있는 허가된 배포에서, 런타임에 추가된 provider/tool 경로가 기존의 보호된 service effect와 의미적으로 동등하지만 경로 등록·계측·sink 매핑이 갱신되지 않았다. 그 상태에서 기존 계층의 가장 강한 적용 가능한 조합까지 켜고도, 새 경로의 비인가 효과가 일어나며 정상 요청은 계속 성공한다면, “경로 변화 시 완전 중재를 검증하는 방법/증거”의 국소 gap을 지지할 수 있다. 현재는 **그런 동일 구성의 원시 로그가 없다.** 공개 논문들의 전제와 개별 negative control만 있다.

**즉시 기각:** 아래 중 하나가 같은 업무·공격자·service effect 조건에서 성립하면 이 가설을 버린다. (1) 새 경로가 default-deny OS/egress PEP에서 차단되고 정상 경로가 유지된다. (2) 경로 등록 시 effective policy 포함 검사와 event/provenance schema 검사가 실패 폐쇄로 작동한다. (3) 새 경로가 provider-native 조건부 API나 finality broker에서 승인된 효과로만 끝난다. (4) 기존 기법이 동적 registry 전체의 효과 도달성/계측 충실성을 독립적으로 증명하고 현실적 비용으로 적용된다. 완전한 경로 inventory나 provider 효과 등가관계를 구할 수 없다면 그것은 먼저 **정보의 부재**로 기록하며, 곧바로 새 프레임워크 필요성으로 판정하지 않는다.

## 최소 반증 실험의 사전 정의와 현재 상태

- **검증 질문:** 격리된 테스트 네트워크의 동일 synthetic provider에서 계측 HTTP `/approved/send`와 늦게 등록한 raw-socket `/alternate/send`가 동일한 in-memory ledger를 갱신할 때, 허용/거부 결정과 실제 ledger 변화가 각 PEP에서 일치하는가? OpenShell은 loopback 목적지를 허용하지 않으므로, 적용 대조군은 별도 비-loopback 테스트 주소·정확한 hostname 규칙을 준비할 수 있을 때만 구성한다.
- **원래 주장과 예상:** FORGE는 계측 join point에 대해서만 차단을 보장하므로 raw socket/직접 stdio로 나가는 새 경로는 FORGE 단독 범위 밖으로 예상한다. OS/egress PEP나 finality broker가 올바르게 설정되면 이 경로도 차단될 수 있어야 한다. 허용된 정상 `/approved/send`는 한 번 기록되어야 한다.
- **반증 관찰:** 모든 적용 가능한 lower-layer 및 effect-sink 통제를 켜도 비인가 ledger 변화가 발생하고, 승인된 동일 업무는 성공하며, 로그로 어느 PEP가 어떤 사실을 놓쳤는지 확인되면 잠재 gap을 지지한다. 한 통제라도 차단하거나 효과가 없으면 넓은 H2 주장을 기각 또는 축소한다. PEP 결정만 보면 `DECISION_ONLY`다.
- **최소 비용·완료 조건:** 로컬 synthetic ledger, seed 고정, API 비용 0, 전후 상태와 audit/enforce 차이를 기록한다. 같은 commit과 정책으로 정상·비인가·강한 대조군을 1회씩 실행하면 질문을 닫는다.
- **이번 세션 상태:** 실행하지 않았다. FORGE 평가가 고정한 SASY submodule은 `6dedd2bc15da491d14ec07f87c0f1ef4d339efd6`이며 더 최신 로컬 SASY `7dc9e524c5b1979b91d16b9d573219e358a6c332`와 다르다. [K08 준비·빌드 로그](runs/K08_minimal_20261124/manifest.md)의 5분 상한 Docker/Nix 빌드가 종료되어 원본 engine/PEP를 실행하지 못했다. 동일 실패 재시도와 무거운 빌드 반복을 중단한다. 따라서 현재 FORGE **실행 효과 관측 없음**, 대체 시뮬레이션을 논문 재현으로 표기하지 않는다.

## 판정과 다음 비용 효율적인 질문

1. **해결 확인 범위:** 각 연구가 직접 선언한 계측 join point, OS hook, sandbox effective policy, finality sink 안에서는 조건부 대응이 존재한다. 이것들을 하나의 “100% coverage”로 합치지 않는다.
2. **남은 조건:** 새 provider/tool의 *service effect 동등성*과 그 경로가 실제로 지나는 모든 PEP를 배포 시 어떻게 열거·검증하는지는 사례별이다. 지금 문헌만으로 일반 미해결이나 새 Need를 증명하지 못한다. `UNVERIFIED`.
3. **다음 질문:** 공식 SASY engine을 저비용으로 실행 가능한 환경이 생기는지 먼저 확인한다. 그렇지 않으면 OpenShell의 기존 격리 실험 기록에서 effective policy·audit/enforce·실제 효과를 재검토하고, CONTINUITY artifact의 alternate-path negative control을 기존 R2 기록과 구분해 확인한다. 새 실험은 동일 service effect의 강한 대조군이 준비된 경우에만 수행한다.
