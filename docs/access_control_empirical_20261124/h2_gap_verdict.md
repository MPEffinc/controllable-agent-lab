# H2/H7 좁은 Gap 재심사: 동적 경로, 동시성, 실제 활성 정책

**2026-11-24 판정:** 이번 자료에서 `GAP_SUPPORTED` **0건**. H2의 메서드 내부 동시성은 `UNVERIFIED`; H7의 “전체 policy를 검증할 방법 부재” 가설은 이번 정책 형상에서 `REJECTED_HYPOTHESIS`, 자동 배포 gate의 다른 배포 일반화는 `UNVERIFIED`다. 어느 조건도 독립적인 Research Need로 승격하지 않는다.

## 비교할 속성과 같은 조건

- **보호할 효과:** 승인된 `GET /ok`만 synthetic upstream ledger에 기록한다. `GET /blocked`는 기록되면 안 된다. 새 provider 규칙은 승인 상한을 넘지 않아야 한다.
- **정상 작업:** 같은 `/bin/wget`와 같은 local upstream에서 `/ok`가 성공해야 한다.
- **공격자/관리 범위:** agent가 요청 경로를 선택하거나 새 provider/tool을 사용할 수 있다. Gateway 관리자·커널·정책 상한·upstream은 신뢰한다. 관리자가 의도적으로 `audit`를 선택하거나 상한 검사를 생략한 경우는 **설정·운영 조건**으로 따로 기록한다.
- **서로 다른 검증 대상:** FORGE의 event/provenance 충실성, OpenShell의 OS/network/L7 집행, provider의 최종 서비스 효과 의미는 같은 숫자로 합치지 않는다. [FORGE v4 §4.4](https://arxiv.org/html/2602.16708v4)의 완전 중재/충실한 관측 전제와 [CONTINUITY §6.8](https://arxiv.org/html/2609.05269)의 동등 효과 경로 sink 전제도 구별한다.

## 이번 실행에서 실제로 발생한 것

| 관찰 | 같은 조건의 강한 반박 | 판정 |
|---|---|---|
| [K14 원시 실험](runs/K14_effective_20261124/result.md): provider attach 뒤 base network rule은 0, effective에 `_provider_h2pypi`가 추가됐다. Receipt `ready`와 Supervisor `CONFIG:LOADED`로 활성 상태를 확인했다. | v0.1.9의 [합성 코드](https://github.com/ai-openshell/openshell/blob/ce58cf8e9b953281352d98a637e41616295b1318/crates/openshell-policy/src/compose.rs#L59)와 [공식 문서](https://docs.nvidia.com/openshell/v0.1.9/how-it-works/policies/overview)가 바로 이 동작을 설명한다. provider 생성만으로 attach되지 않고, global policy는 provider 기여를 억제한다. | “provider 추가가 감지되지 않는 숨은 변화”라는 넓은 주장은 **기각**. 검토자가 base만 보면 놓치는 것은 사실이다. |
| 동일 synthetic `/blocked`: `audit`에서 HTTP 200, upstream ledger +1. `enforce`에서 HTTP 403, ledger +0. 동일 enforce에서 정상 `/ok`는 HTTP 200, ledger +1. | [공식 `audit`/`enforce` 정의](https://docs.nvidia.com/openshell/v0.1.9/how-it-works/policies/network-rules)와 [v0.1.9 PEP 분기](https://github.com/ai-openshell/openshell/blob/ce58cf8e9b953281352d98a637e41616295b1318/crates/openshell-supervisor-network/src/proxy.rs#L6450)가 결과를 설명한다. | audit의 효과 발생은 **의도된 모드**다. 차단 의도인데 audit 배포했다면 설정 오류. 같은 경로에서 enforce 보호는 `RESOLVED_IN_SCOPE`. |
| 사전 등록한 [H7 공식 prover 대조](runs/H7_policy_gate_20261124/result.md): base만 넣으면 `within_boundary`/exit 0, provider 포함 full을 넣으면 `exceeds_boundary`/exit 1, `pypi.org:443` network 반례. | [공식 prover 지침](https://docs.nvidia.com/openshell/v0.1.9/how-it-works/policies/prover)은 provider 규칙이 포함된 *전체 effective policy*를 넣도록 한다. `unsupported`는 통과로 취급하지 않는다. | 이 정책 형상에서 **기존 검사로 확대 검출 가능**. `8.8.8.8`은 정형 counterexample의 임의 IP 증인이지 실제 접속이 아니다. |

이 실험에서 provider가 기여한 PyPI endpoint 자체로 트래픽을 보내지는 않았다. 공개 예제 profile의 binary 목록이 BusyBox `/bin/wget`과 맞지 않으므로, 관측한 provider 효과는 정책 합성·적용까지다. `/blocked`/`/ok`의 PEP 효과는 별도 base의 `h2local` rule에 대한 것이다. 이를 한 provider의 완전한 endpoint 평가로 읽지 않는다.

## FORGE의 더 좁은 동시성 조건

[FORGE v4 §4.3 Algorithm 1, §4.4](https://arxiv.org/html/2602.16708v4)은 후보 action을 내보내기 전에 관련 event graph의 backward slice가 동기화되기를 기다린 뒤 Datalog를 평가한다. [§7.1의 저자 명시 한계](https://arxiv.org/html/2602.16708v4)는 instrumented method 안에서 concurrent task가 메시지를 내보내고, 그 emission에 낮은 수준 join point가 없으면 event가 등록되기 전에 다른 경로가 이를 소비할 수 있다고 한다. 그때 인가 질의가 *불완전한 graph*를 읽을 수 있다. 이는 “가능한 실패 조건”에 대한 원문 근거이지, 이 세션에서 비인가 effect를 관측한 증거가 아니다. 원본 FORGE 평가가 고정한 SASY `6dedd2b...`의 Docker/Nix 빌드는 [5분 상한에서 중단](runs/K08_minimal_20261124/manifest.md)되어 이 race의 원저자 PEP 실행은 `NOT_RUN`이다.

**가장 좁은 반증 가능한 질문:** 같은 외부 목적지·method·resource에 대해 정상 메시지와 비신뢰 메시지가 동시에 들어오고, 정책은 *그 메시지의 출처/인과관계*로만 두 경우를 구별한다. FORGE가 정책 결정 시 필요한 event를 누락해 비신뢰 경우만 effect를 허용하는가? 정상 경우는 계속 완료되는가? 강한 대조군은 (1) emission의 더 낮은 join point에서 선등록, (2) event graph commit/barrier 후 인가, (3) 같은 효과의 finality sink가 provenance와 최신 permit을 검사하는 구성이다. [CONTINUITY §5.5 C7/§6.8](https://arxiv.org/html/2609.05269)은 마지막 구성의 전제와 broker 의무를 이미 제시한다. OpenShell의 coarse network rule이 같은 목적지의 두 출처를 자동 분간한다고 주장하지 않으며, 그 경우에는 신뢰된 provenance를 effect PEP까지 전달해야 한다.

**`GAP_SUPPORTED`로 올릴 최소 증거:** 고정 commit·정책·정상/비신뢰 입력·seed/스케줄에서 event 생성 시각, graph 등록·snapshot 시각, 정책 결정, 실제 upstream effect를 순서대로 기록한다. 동일 업무에서 barrier/낮은 join point 및 적절한 finality sink까지 적용했는데도 비신뢰 효과가 남고 정상 업무도 유지된다면 기존 대응의 잔여 조건을 인정한다. 반대로 barrier나 sink가 막으면 “동시성 메커니즘 부재” 가설은 기각한다. 단순히 tool-dispatch를 우회한 raw socket 한 건, 미설정 `audit`, 또는 정상 task까지 통째로 차단한 결과는 충분하지 않다. 현재 이 자료는 없다.

## H7의 자동 gate 질문은 남지만, 신규 Need의 증거는 아님

v0.1.9의 [provider attach 검증 함수](https://github.com/ai-openshell/openshell/blob/ce58cf8e9b953281352d98a637e41616295b1318/crates/openshell-server/src/grpc/policy.rs#L2473)는 후보 effective의 endpoint 충돌과 credential 결속 등을 검사한다. 조사한 경로에서 조직의 임의 승인 상한과의 prover 비교는 자동 호출되지 않는다. [공식 prover 문서](https://docs.nvidia.com/openshell/v0.1.9/how-it-works/policies/prover)는 그 명령이 로컬 파일을 검사할 뿐 정책을 적용하거나 승인하지 않는다고 분명히 한다. 즉 “전체 상한 검사”와 “attach 전 실패 폐쇄 배포”는 운영자가 결합해야 한다. 그 결합이 어려운 배포인지, 실제로 어떤 효과가 남는지는 이 세션에서 검증하지 않았다. 기존의 full candidate 검사, policy hash/`--wait` 적용 확인, global policy, 별도 승인 gate가 직접적인 대안이다.

K14의 기본 *shorthand* OCSF는 audit의 `/blocked`도 `ALLOWED`로 보였다. [원본 PEP 코드](https://github.com/ai-openshell/openshell/blob/ce58cf8e9b953281352d98a637e41616295b1318/crates/openshell-supervisor-network/src/proxy.rs#L6380)에는 `audit` decision 문자열과 이유를 event message에 넣는 경로가 있지만 이번 원시 OCSF JSON은 수집하지 않았다. 따라서 “모든 telemetry가 위반을 놓친다”는 판정은 성립하지 않는다. 이 shorthand를 유일한 oracle로 쓰지 않는 것이 현재의 재현 지침이다.

## 최종 판정과 다음 비용 상한

- **H2:** 저자 인정 동시성 전제와 미계측 채널은 구체적 `WATCH` 조건이다. 원본 PEP의 동일 조건 실패와 강한 대조군 미충족이 없어 **`UNVERIFIED`**. 동적 provider attach 자체가 모두 미중재된다는 주장은 K14의 합성·적용 관측으로 **기각**.
- **H7:** 검토한 base와 활성 full이 달랐고 audit/enforce의 실제 효과도 달랐다. 이것은 중요하지만 v0.1.9의 문서화된 동작이다. 전체 정책에 대한 공식 prover는 확대를 검출했으므로 이 형상에서 **`RESOLVED_IN_SCOPE`**; “검사 방법이 없다”는 주장은 **`REJECTED_HYPOTHESIS`**. 자동 배포 gate의 일반성·업무 의도는 `UNVERIFIED`.
- **Research Need:** 현재 **확정 0건**. 다음 실험은 원본 FORGE/SASY engine이 저비용으로 준비되는 경우에만 위 동시성 일정과 강한 대조군을 사전 등록해 수행한다. 무거운 Docker/Nix 재빌드는 반복하지 않는다. H7은 지원하지 않는 GraphQL/MCP 정책이 포함된 전체 후보에서 prover `unsupported`를 실패 폐쇄로 처리하는지 같은 운영 gate를 검증하면 충분하며, `unsupported`를 보안 보장으로 과장하지 않는다.
