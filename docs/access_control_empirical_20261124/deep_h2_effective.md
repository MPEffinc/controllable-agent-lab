# H2 후속: OpenShell v0.1.9 provider 정책 합성과 audit/enforce의 실제 효과

**기준:** 공식 소스 [v0.1.9 태그 `ce58cf8e9b953281352d98a637e41616295b1318`](https://github.com/ai-openshell/openshell/tree/ce58cf8e9b953281352d98a637e41616295b1318), 동일 버전 CLI/Gateway/Sandbox binary. 독립 실행은 [K14 사전 등록과 원시 자료](runs/K14_effective_20261124/manifest.md)에 있다. 기존 `oslab-*`와 `sregym-*` 컨테이너는 건드리지 않았다. 외부 API, LLM, credential 사용은 0이다.

## 코드에서 확인한 경로와 조건

1. [Policy 합성 함수 `compose_effective_policy`](https://github.com/ai-openshell/openshell/blob/ce58cf8e9b953281352d98a637e41616295b1318/crates/openshell-policy/src/compose.rs#L59)는 base policy를 복제하고 각 provider의 network rule을 `_provider_*` 키로 넣는다. 충돌 시 숫자 suffix를 붙이며 base를 수정하지 않는다. 이 규칙은 [공식 provider profile 문서](https://docs.nvidia.com/openshell/v0.1.9/how-it-works/providers/profiles)와 일치한다.
2. Gateway의 [attach handler](https://github.com/ai-openshell/openshell/blob/ce58cf8e9b953281352d98a637e41616295b1318/crates/openshell-server/src/grpc/sandbox.rs#L1452)는 provider 존재·profile·환경 키·후보 attachment/policy를 검사하고 sandbox spec의 provider 목록을 CAS로 갱신한다. 저장 후 config delivery를 publish한다. [effective policy 산출](https://github.com/ai-openshell/openshell/blob/ce58cf8e9b953281352d98a637e41616295b1318/crates/openshell-server/src/grpc/policy.rs#L2050)은 global policy가 있으면 그것을 쓰고 provider layer를 억제한다. global policy가 없으면 현재 base와 provider layer를 합친다. 따라서 *provider 생성만*으로 기존 sandbox의 권한이 바뀌는 것은 아니다. profile에 endpoint가 있고, provider를 sandbox에 attach하고, global policy가 없고, 새 구성이 실제 적용되어야 한다.
3. 저장 성공은 적용 완료가 아니다. [공식 문서의 `--wait` 의미](https://docs.nvidia.com/openshell/v0.1.9/how-it-works/providers/profiles)에 따라 attach가 sandbox에서 policy/환경을 적용할 때까지 기다렸다. [attach receipt](runs/K14_effective_20261124/attach.json)의 `state=ready`, `wait_outcome=complete`, `observed.policy_active=true`를 확인했다. [Supervisor 로그](runs/K14_effective_20261124/supervisor.log)의 `CONFIG:DETECTED`와 `CONFIG:LOADED`에서 변경 hash를 별도로 확인했다.
4. [공식 network rule 문서](https://docs.nvidia.com/openshell/v0.1.9/how-it-works/policies/network-rules)는 inspected endpoint의 `audit`가 L7 rule 위반을 전달하고, `enforce`가 차단한다고 명시한다. [원본 `proxy.rs`의 효과 결정](https://github.com/ai-openshell/openshell/blob/ce58cf8e9b953281352d98a637e41616295b1318/crates/openshell-supervisor-network/src/proxy.rs#L6380)은 `force_deny` 또는 `!allowed && enforcement==Enforce`일 때만 요청을 차단한다. [relay 경로](https://github.com/ai-openshell/openshell/blob/ce58cf8e9b953281352d98a637e41616295b1318/crates/openshell-supervisor-network/src/l7/relay.rs#L1826)도 audit에서 조건부 전달하며, `force_deny`와 middleware 거부는 audit여도 별개로 막는다.

## 이 세션의 격리 실행: base와 effective

별도 Gateway `127.0.0.1:18081`, 별도 SQLite·mTLS·CLI config, 고유 sandbox `h2eff-01` 한 개를 사용했다. v0.1.9 Gateway의 초기 profile catalog는 빈 배열이었다. `provider create --type pypi`가 `profile 'pypi' not found`로 거부되어, 동일 고정 소스의 [credentialless 예제 `providers/pypi.yaml`](https://github.com/ai-openshell/openshell/blob/ce58cf8e9b953281352d98a637e41616295b1318/providers/pypi.yaml)을 lint/import한 뒤 `h2pypi`를 만들었다. 이는 profile을 명시적으로 가져와야 한다는 [공식 문서](https://docs.nvidia.com/openshell/v0.1.9/how-it-works/providers/profiles)의 조건과 맞는다.

| 시점 | [base 원시 결과](runs/K14_effective_20261124/base-before.json) / [이후](runs/K14_effective_20261124/base-after.json) | [full 원시 결과](runs/K14_effective_20261124/full-before.json) / [이후](runs/K14_effective_20261124/full-after.json) | 해석 |
|---|---|---|---|
| attach 전 | network rule 없음 | network rule 없음 | baseline |
| `h2pypi` attach + `--wait` 후 | network rule 없음, active version 1 | `_provider_h2pypi` rule 추가, active version 1 | base는 유지되고 **실제 적용 policy hash가 변경**됨. |

이 provider profile의 `binaries` 목록은 현재 BusyBox `/bin/wget`을 포함하지 않는다. 따라서 여기서 확인한 것은 **동적 policy 합성과 적용**이며, `h2pypi`가 실제 PyPI 요청을 허용했다는 결과가 아니다. provider endpoint와 정상 업무 의미를 자동 검증했다는 주장도 하지 않는다.

## 이 세션의 격리 실행: 같은 요청의 audit/enforce

동일 sandbox의 base에만 독립적인 `h2local` REST rule을 적용했다. [audit 정책](runs/K14_effective_20261124/audit.yaml)과 [enforce 정책](runs/K14_effective_20261124/enforce.yaml)은 `/bin/wget`에서 `172.17.0.1:18083`의 `GET /ok`만 허용하고 mode만 다르다. Host의 Docker bridge 주소에 바인딩한 [synthetic upstream](runs/K14_effective_20261124/local_provider.py)은 도달한 request path만 ledger에 기록한다. 두 정책 모두 CLI `policy set --wait`로 active version 2/3 로드를 확인했다. 최종 [effective policy](runs/K14_effective_20261124/full-final.json)에는 provider rule과 `h2local` rule이 함께 있다.

| 조건과 입력 | CLI/PEP 결과 | upstream ledger의 실제 효과 |
|---|---|---|
| audit, `GET /blocked` | [원시 요청](runs/K14_effective_20261124/audit-request.log): HTTP 200, exit 0. [Supervisor](runs/K14_effective_20261124/openshell-logs.txt): L4 `ALLOWED`, L7 `ALLOWED`. | `/blocked` 1건 기록. 정책의 `/ok` allow rule 밖이어도 upstream까지 전달됨. |
| enforce, 동일 `GET /blocked` | [원시 요청](runs/K14_effective_20261124/enforce-blocked.log): HTTP 403, exit 1. Supervisor: `HTTP:GET ... DENIED`, `GET /blocked not permitted by policy`. | 기록 수 1건 그대로, **새 효과 0**. |
| enforce, 정상 `GET /ok` | [원시 요청](runs/K14_effective_20261124/enforce-allowed.log): HTTP 200, exit 0. Supervisor: L7 `ALLOWED`. | `/ok` 추가, 총 2건. 정상 업무 허용. |

주의할 관측 차이: audit의 *shorthand* OCSF 줄은 `ALLOWED`로만 보였고, 이 줄만 보면 `/blocked`가 rule 위반이었는지 알 수 없다. [v0.1.9 `proxy.rs`](https://github.com/ai-openshell/openshell/blob/ce58cf8e9b953281352d98a637e41616295b1318/crates/openshell-supervisor-network/src/proxy.rs#L6350)는 내부 decision string으로 `audit`를 만들고 OCSF message에 넣지만, 이번 기본 shorthand 출력에는 그 문자열이 드러나지 않았다. 원본 OCSF JSON은 이 실행에서 활성화하지 않았으므로 **JSON에서 위반 이유가 보이지 않는다고 주장할 수 없다**. 이는 audit 로그를 판정 근거로 쓸 때의 관측 형식 제한이며, 별도 Research Gap의 증거는 아니다. 또한 middleware나 malformed-request 강제 차단은 이번 실험 대상이 아니다.

## H2 판정

**`RESOLVED_IN_SCOPE`:** v0.1.9는 profile에 기술된 provider network rule을 attach된 sandbox의 effective policy에 동적으로 합성·적용하며, 본 실험에서 `--wait` receipt와 Supervisor reload로 확인했다. 정확히 설정된 L7 `enforce`는 동일 로컬 요청의 실제 upstream 효과를 막고 허용 요청은 유지했다. **`UNVERIFIED`:** 새 provider가 기존 허용 의도에 적합한지, profile이 모든 service effect를 표현하는지, 모든 다른 egress/API 경로가 계측되는지는 이 실험이 검증하지 않았다. `audit`는 차단 수단이 아니며, 기본 shorthand 로그만으로 rule 위반 여부를 충분히 판독하지 못했다. 따라서 H2의 범용 미해결 또는 신규 Need 판정은 여전히 `UNVERIFIED`다.
