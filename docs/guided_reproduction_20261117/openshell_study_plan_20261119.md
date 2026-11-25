# OpenShell 학습·실습 준비 — 현재 가능한 범위와 실행 대기 범위

2026-11-19, Asia/Seoul. **준비 자료이며 실험 결과가 아니다.** 원본 코드·공식 문서·fixture·테스트를 읽고 환경 메타데이터만 확인했다. 설치, 빌드, Prover, sandbox, 네트워크 요청, Agent 및 유료 API는 실행하지 않았다.

## 기준과 현재 상태

- 원본: `third_party/guided-openshell-2e5589b/`, SHA `2e5589b2180dd432320adda124c4f7bcede119b5`. 작업 트리 clean 확인.
- 특정 논문의 artifact로 확인한 대상이 아니다. 공식 runtime의 문서·테스트·예제를 학습하며 논문 Section·ASR를 임의로 부여하지 않는다.
- 현재 커널: `5.15.0-203-generic`. 기존 조사 Landlock ABI=1; 이번에는 ABI를 재측정하지 않았다. 고정 원본은 ABI≥3 및 추가 seccomp·메모리 접근·socket 기능을 요구한다.
- `openshell`, `openshell-prover`, `cargo`, `rustc`, `rustup`, `cmake`는 PATH에 없다. `cc`, `pkg-config`, `uv`, Docker CLI는 있다. Docker CLI 존재는 daemon 가용성이나 sandbox 실행 가능성의 증거가 아니다.
- 준비 증거: `local/guided-reproduction-20261119/setup/openshell-study-preparation.json`. 원본 입력 hash와 공식 테스트의 예상값을 포함하며 모든 실행 상태는 NOT_RUN이다.
- Progent는 정책 생성·갱신·집행 및 정상 LLM 실행까지 학습했다. SMT·충돌 분석·공격 평가를 완료했다고 표현하지 않는다. 나머지 연구도 학습 목록에 유지한다.

## 가능 범위 구분

| 구분 | 지금 할 수 있는 것 | 필요한 준비 / 얻을 수 없는 증거 |
|---|---|---|
| A: 지금, 실행 없이 | architecture·YAML·호출 경로 읽기, 원본 fixture 비교, 테스트 assertion 해석, 설정의 예상 효과 설명 | runtime Allow/Deny, 실제 upstream effect, 성능을 관측한 것이 아님 |
| B: 현재 커널 유지, 도구 준비 후 | standalone Prover의 원본 contained/exceeds/unsupported/error 사례를 한 건씩 실행 | Rust/Z3 빌드 환경 또는 고정 버전과 출처를 검증한 바이너리 필요. 현재 실행 준비 완료 아님 |
| B의 선택 심화 | 고정 source의 Prover 공식 CLI 테스트 중 필요한 항목만 실행 | 동일 빌드 환경 필요. 자체 엔진/모조 Allow/Deny 테스트를 만들지 않음 |
| C: 적합한 환경 확보 후 | Landlock 파일 집행, 네트워크 L4/L7 집행, hot reload, advisor, credential 경계의 실제 검증 | Linux kernel 기능·실행 runtime·gateway·이미지 준비 필요. 현재는 설명과 원본 테스트 읽기만 |
| C의 후속 | 여러 sandbox를 쓰는 MAS 원본 예제 | 추가 이미지·모델·GitHub credential 및 실제 저장소 쓰기 포함. 현재 실행 대상에서 제외하고 정적 분석만 |

일반적인 Linux Docker 컨테이너는 호스트 커널을 공유한다. 이미지·Python 패키지만 바꾸어 ABI 문제를 해결했다고 가정하지 않는다. 커널 업그레이드가 유일한 선택은 아니며 별도 VM/서버도 후보지만, 실제 기능 qualification 전에는 지원된다고 확정하지 않는다.

## 학습에서 계속 구분할 네 가지

1. **Policy intent:** 허용한 경계가 사용자 작업과 맞는가?
2. **Policy model:** Prover가 실제로 모델링한 범위에서 candidate가 boundary를 넘는가?
3. **Runtime enforcement:** 선택한 정책 revision이 실행환경에 적용되고 요청을 차단하는가?
4. **Task/effect:** 정상 업무가 완료됐는가, 파일·upstream 상태가 실제로 변했는가?

정적 검사 통과, CLI 성공, 설정 저장, runtime 적용, 실제 업무 성공을 같은 결과로 세지 않는다.

## 학습 순서 — 한 단원씩 진행

아래 각 단원은 요청한 여섯 단계로 준비했다. 모든 명령은 해당 단원 설명 뒤에만 제시한다. A의 '실행 방법'은 파일 읽기 경로를 뜻하며 실제 sandbox 실행으로 바꾸지 않는다.

### 01. Architecture와 Trust Boundary — A

1. 무엇: Agent/workload, sandbox runtime, supervisor, gateway, compute driver, kernel의 역할.
2. 왜: Progent wrapper와 OS/프로세스 경계 집행의 차이를 이해한다. 위협에 노출되는 workload와 신뢰하는 kernel/runtime/supervisor/control plane을 구분한다.
3. 구조: Agent → syscall/네트워크 시도 → kernel·sandbox 중재 → 보호 채널 → supervisor → 허용된 upstream. filesystem 검사는 Landlock 경로다.
4. 방법: `docs/about/architecture.mdx`, `docs/security/best-practices.mdx`의 공식 그림과 설명을 읽는다. 네트워크 직접 egress fence와 정책 판단을 나누어 표시한다.
5. 관찰: 누가 실제 외부 연결을 여는가, 누가 credential을 보유하는가, workload가 무엇을 관찰할 수 있는가.
6. 해석: Agent의 판단을 신뢰하지 않고 접근을 제한하는 구조다. kernel/신뢰 구성요소의 무결성과 실제 fence 설정을 전제로 하며 모든 침해를 막는다는 주장이 아니다.

### 02. 원본 정책 읽기 — A

1. 무엇: YAML의 filesystem/process/network/Landlock 설정과 실행 시점.
2. 왜: policy correctness와 over-privilege는 집행 전에 발생할 수 있다.
3. 구조: authored/base policy → provider 기여 규칙 등을 반영한 effective policy → 실행 revision. global policy가 활성화되면 별도 선택 규칙이 적용된다.
4. 방법: `examples/sandbox-policy-quickstart/policy.yaml`, `docs/how-it-works/policies/{overview,schema,network-rules}.mdx`를 함께 읽는다.
5. 관찰: `/usr/bin/curl`, `api.github.com:443`, `protocol: rest`, `enforcement: enforce`, `access: read-only`; 파일 read_only/read_write와 include_workdir.
6. 해석: `read-only`는 GET/HEAD/OPTIONS 메서드 preset이다. upstream GET의 무부작용이나 데이터 비유출까지 보장하지 않는다. 허용 host도 데이터 전송 경로가 될 수 있다.

### 03. Policy Boundary 정적 검사 — B, 최초 실행 후보

1. 무엇: candidate가 operator가 정한 boundary를 넘는지 검사한다.
2. 왜: '정책을 파싱했다'와 '허용 범위를 넘지 않음을 확인했다'를 구분한다.
3. 구조: 원본 YAML 두 개 → CLI parse → containment 모델/SMT → result·coverage·counterexample. gateway/Agent/API/실제 파일 접근은 없다.
4. 방법: 아래 공식 fixture 쌍을 한 번에 하나씩 실행한다. 우선 OS-P01만 진행하며 결과를 해석한 뒤 다음으로 간다.
5. 관찰: exit code, `schema_version`, `prover_version`, `result`, `coverage.domains`, `counterexample`, `reason_code`, stderr.
6. 해석: 허용 집합의 포함 관계만 검증한다. boundary 자체가 적절한지, 실제 kernel이 설치됐는지, 정상 업무가 가능한지는 별개다.

### 04. Misconfiguration·Conflict·모델 한계 — A → 선택 B

1. 무엇: 여러 규칙의 결합, 미지원 의미, binary identity와 ancestor 권한.
2. 왜: 각 줄을 좁게 작성해도 합쳐진 권한이 넓어질 수 있다.
3. 구조: network rule의 binaries×endpoints 조합, 여러 allow의 결합, matching deny 우선, provider 규칙, canonicalization/validation, Prover 지원 범위.
4. 방법: network-rules의 Binary Matching/Overlapping Rules, `openshell-policy/src/merge.rs`, `openshell-policy/src/lib.rs`, Prover CLI 테스트를 읽는다. B의 unsupported 사례로 모델 한계를 관측할 수 있다.
5. 관찰: rule 순서는 방화벽식 first-match가 아니다. 실행파일 realpath·ancestor와 TOFU hash를 확인한다. `audit` 기본값, protocol 생략, 넓은 glob, base/effective 차이를 체크한다.
6. 해석: deny 우선은 네트워크 request 의미에 적용되는 규칙이며 파일·모든 다른 정책 체계로 일반화하지 않는다. path 문자열의 부모/자식 관계만 보고 filesystem containment를 단정하지 않는다.

### 05. 정책 생성·제안·갱신 — A, 실제 적용 C

1. 무엇: operator 작성 정책, Agent의 network proposal, 자동 생성된 blocked-connection draft, 승인, revision 반영을 구분한다.
2. 왜: 정책 제안이 신뢰된 권한 부여가 되는 순간을 찾는다.
3. 구조: deny → Agent proposal/draft → validate·risk check → pending → manual/auto approval → policy revision → supervisor 적용 → retry.
4. 방법: `docs/how-it-works/policies/{advisor,manage-policies,prover}.mdx`, `openshell-policy/src/merge.rs`, `openshell-server/src/grpc/policy.rs`를 읽는다. advisor는 기본 off, 승인은 기본 manual이다.
5. 관찰: network만 추가 제안 가능; filesystem/process/Landlock은 이 API로 변경하지 못함. 승인 전 요청은 계속 차단. 자동 승인 범위·위험 finding·변경된 입력 재검사를 읽는다.
6. 해석: boundary check와 proposal risk check는 질문이 다르고 서로의 통과를 함의하지 않는다. 후자의 통과가 '권한 확대 없음'이나 '사용자 의도와 일치'를 뜻하지 않는다.

### 06. Credential과 동적 적용 — A, 실제 검증 C

1. 무엇: provider placeholder, 실제 secret의 위치, endpoint binding, 적용 실패·연결 수명.
2. 왜: 네트워크 접근 권한과 credential 전달 권한은 별개다. saved revision과 loaded revision도 다를 수 있다.
3. 구조: provider 설정 + effective policy → supervisor 요청 검사 → 허용된 endpoint에 credential 대입. 정책 변경은 gateway 및 runtime에서 각각 검증한다.
4. 방법: architecture, provider profiles, manage-policies, `tests/suites/conformance/src/credential_gating.rs`를 읽는다. 실제 credential 입력이나 로그 덤프는 하지 않는다.
5. 관찰: network hot reload 시 이전 연결 종료; 파일 권한은 재생성 필요; default fail_closed와 retain_last_valid의 차이; revision 오류와 client 응답을 구분한다.
6. 해석: placeholder 보호는 사용자가 일반 파일/env에 별도로 넣은 secret까지 자동 보호한다는 뜻이 아니다. provider가 추가하는 규칙까지 포함한 effective policy를 검증해야 한다.

### 07. 실제 집행과 Effect — 현재 설명 A, 실행 C

1. 무엇: Landlock read/write, 네트워크 연결 허용, HTTP 요청 허용을 별도 실습으로 본다.
2. 왜: Prover 통과를 실제 집행 증거로 대체하지 않는다.
3. 구조: 공식 quickstart의 L4 접속 검사 → L7 REST 검사 → upstream; 파일은 kernel Landlock 검사 → 실제 파일 상태.
4. 방법: 먼저 `examples/sandbox-policy-quickstart/README.md`의 로그를 **문서 예시**로 읽는다. 적합한 환경 확보 후 원본 conformance의 filesystem/process/credential 테스트를 하나씩 선택한다. 전체 demo.sh는 자동 실행하지 않는다.
5. 관찰: client 오류/HTTP 403, OpenShell policy_denied, OCSF의 binary·host·method·path·revision, 파일 전후 hash, 테스트가 소유한 upstream의 수신/변경 여부.
6. 해석: 일반 403·도구 실패만으로 정책 차단이라 판단하지 않는다. upstream이 안 받았다는 증거와 정상 요청 성공도 함께 필요하다. 공개 GitHub의 write 요청은 지금 실행 계획에 포함하지 않는다. 후속 effect 검증은 원본 테스트 소유 fixture를 우선한다.

### 08. MAS와 보안 보장의 범위 — A, 실행은 별도 C

1. 무엇: Agent별 sandbox와 같은 sandbox의 여러 Agent가 갖는 경계 차이.
2. 왜: MAS 실행 지원과 instruction/data provenance 보호를 혼동하지 않는다.
3. 구조: 공식 multi-agent-notepad의 여러 worker sandbox → GitHub 공유 산출물 → synthesis sandbox. 호스트 script가 orchestration을 담당한다.
4. 방법: `examples/multi-agent-notepad/{README.md,demo.sh,policy.template.yaml}`과 worker/synthesis prompt를 읽는다. source 분석만 한다.
5. 관찰: 실제 isolation은 sandbox 단위이고 network에는 binary/ancestor 범위도 있다. 예제는 worker들이 공통 run 경로를 쓰는 정책이며 '각자 자기 파일만 쓴다'는 프롬프트를 ACL로 오해하지 않는다.
6. 해석: OpenShell은 허용된 공유 산출물의 내용을 다른 Agent가 지시로 해석하는 문제까지 자동 해결하지 않는다. Multi-CaMeL과 비교하되 결합 구현을 새로 만들거나 그 보장을 검증했다고 주장하지 않는다.

## 최초 실행 후보 — 원본 fixture와 assertion

공통 입력 경로: `third_party/guided-openshell-2e5589b/crates/openshell-prover-cli/tests/fixtures/`.
근거: 같은 crate의 `tests/cli.rs`. 아래 결과는 **원본 테스트 assertion에 따른 예상**이다.

| 순서 | candidate | boundary | 예상 | 배우는 내용 |
|---|---|---|---|---|
| OS-P01 | candidate-contained.yaml | boundary.yaml | within_boundary, exit 0 | boundary: /usr·/etc 읽기+/tmp 쓰기, candidate: /usr 읽기+/tmp 쓰기 |
| OS-P02 | candidate-exceeds.yaml | boundary-no-write.yaml | exceeds_boundary, exit 1, filesystem 반례 | write 권한 없는 경계에 /workspace write 추가 |
| OS-P03 | unsupported.yaml | boundary.yaml | unsupported, exit 3 | 검증 불가를 안전 판정과 구분; 원본 fixture는 process identity 비교 |
| OS-P04 | invalid.yaml | boundary.yaml | error, exit 2 | 입력 오류를 불허 판정/반례와 구분 |
| 선택 OS-P05 | candidate-process-root.yaml | boundary-execution.yaml | exceeds_boundary, process 반례 | non-root→root 권한 변화 |
| 선택 OS-P06 | candidate-landlock-best-effort.yaml | boundary-execution.yaml | exceeds_boundary, landlock 반례 | hard_requirement→best_effort 설정 변화; 실제 ABI 집행 검사는 아님 |

기존 `forge_openshell.md`의 범위 초과 예제는 candidate-exceeds와 boundary.yaml을 함께 제시했다. **이번 실행에서는 공식 테스트와 같은 boundary-no-write.yaml을 사용한다.** 다른 경로 비교는 unsupported가 될 수 있어 원본 fixture 이름만 보고 결과를 추정하지 않는다. 옛 조사 기록은 실행 증거가 아니며 보존한다.

## Prover 도구 준비 계획 — 아직 수행하지 않음

원본 고정 SHA에서 빌드하는 경로를 우선 검토한다. 최신 바이너리를 이 SHA의 빌드와 동일시하지 않는다.

1. repo `rust-toolchain.toml`은 Rust **1.95.0**을 선택한다. workspace의 최소 버전 1.94와 구분한다.
2. Rust/Cargo/Rustup 저장소와 target 출력은 `local/guided-reproduction-20261119/` 아래 전용 경로로 정한다. 기존 환경과 전역 default toolchain은 바꾸지 않는다.
3. Prover는 Z3를 링크한다. 기본 빌드는 system Z3 development library와 pkg-config를 요구한다. `vendored-z3`는 CMake와 C++ compiler가 필요하다. 현재 Rust·CMake가 없어 즉시 빌드할 수 없다. 설치 방식을 정하기 전 라이브러리 호환성·다운로드·용량을 확인한다.
4. OS/관리자 설치가 필요한 경로는 실행 전에 범위를 검토한다. 이 준비 단계에서는 설치하지 않는다.
5. 빌드할 때 Cargo.lock을 보존하기 위해 `--locked`, 별도 `--target-dir`를 사용한다. 이후 source clean, binary SHA256, toolchain·Z3 출처를 기록한다.
6. 빌드가 완료된 다음 원본 `--version`/`check --help`로 확인하고 OS-P01만 실행한다. 준비가 끝났다고 미리 표시하지 않는다.

다음은 **빌드 의존성 준비 후** repo root에서 사용할 명령 형태다. 아직 실행 지시가 아니다. 실행 시점에 확정한 Z3 방식과 전용 환경 경로를 먼저 설명한다.

```bash
cargo build --locked -p openshell-prover-cli --bin openshell-prover \
  --target-dir /home/cclab/controllable_agent/local/guided-reproduction-20261119/build/openshell
```

## 첫 실습 명령 카드 — 도구 준비 후, 한 건씩

cwd: `/home/cclab/controllable_agent`. 위 target-dir로 빌드한 경우의 절대 binary 경로다. 현재 파일이 존재하는 것으로 가정하지 않는다. `check`는 적용 명령이 아니고 로컬 YAML 비교 명령이다.

OS-P01만 먼저 실행할 명령:

```bash
local/guided-reproduction-20261119/build/openshell/debug/openshell-prover check \
  third_party/guided-openshell-2e5589b/crates/openshell-prover-cli/tests/fixtures/candidate-contained.yaml \
  --boundary third_party/guided-openshell-2e5589b/crates/openshell-prover-cli/tests/fixtures/boundary.yaml \
  --output json
```

`candidate`는 검사 대상, `--boundary`는 최대 허용 경계, `--output json`은 모델 coverage와 반례를 구조적으로 읽기 위한 옵션이다. 첫 결과를 해석한 뒤 OS-P02의 fixture 쌍으로 진행한다. 네 사례를 한꺼번에 실행하는 runner는 만들지 않는다.

## Prover 결과를 해석할 때의 필수 한계

- `within_boundary`만 포함 관계 검사 통과다. `unsupported`/`inconclusive`는 반례 발견도 안전 증명도 아니다. 정책 승인 근거로 사용하지 않는다.
- coverage: filesystem/network_l4/network_rest/process/landlock. domain 이름이 있다고 그 domain의 모든 기능을 모델링한 것은 아니다.
- filesystem의 서로 다른 경로는 symlink·이미지 정보를 모르므로 `/tmp/cache`⊆`/tmp`처럼 보여도 unsupported가 될 수 있다. include_workdir 의존성도 제한된다.
- REST 비교는 enforce mode의 지원되는 method/path 의미를 대상으로 한다. runtime의 query 검사와 Prover의 지원 범위는 다르다.
- GraphQL/MCP/WebSocket/JSON-RPC, REST query 조건, 일부 glob/identity 조합 등은 고정 모델에서 unsupported가 될 수 있다. runtime 지원과 Prover 지원을 구분한다.
- 일반 boundary CLI는 provider 규칙을 자동으로 합성하지 않는다. 배포 전 검증에서는 완성된 effective candidate를 입력해야 한다.
- prover의 Landlock compatibility 비교와 mandatory ABI≥3 검사는 별개다. best_effort가 mandatory baseline을 끄는 옵션은 아니다.

## 실제 runtime 실습을 열기 위한 후속 준비

- 기존 호스트 커널 업데이트, 별도 VM, 별도 서버 중 실행환경을 먼저 선택한다. 지금은 선택·생성하지 않는다.
- ABI뿐 아니라 공식 Support Matrix의 seccomp user notification/ADDFD, task-memory access, SO_BINDTODEVICE와 runtime profile을 확인한다. kernel 버전 숫자만으로 합격 처리하지 않는다.
- 전용 gateway/sandbox 이름·이미지 digest·포트·출력 경로를 정하고 모델 없는 단일 sandbox부터 시작한다.
- credential은 첫 네트워크 실습에 사용하지 않는다. 실제 secret 보호 검증은 그 후 별도 범위로 준비한다.
- 공식 quickstart는 공개 GitHub 대상 write 요청을 포함하므로 demo.sh를 그대로 실행하지 않는다. 실제 upstream effect는 원본 conformance가 사용하는 테스트 소유 service/fixture를 확인한 후 계획한다. 대체 mock을 만들면 별도 교육용 실습으로 표시한다.
- MAS demo는 모델 호출과 GitHub 쓰기가 있어 현재 실행 범위 밖이다. 정적 구조를 학습한 뒤 별도 실행 범위·비용·저장소를 정한다.

## 기록 및 검증 기준

새 결과는 `local/guided-reproduction-20261119/runs/openshell/<새-run-id>/`에 보존한다. 기존 이름을 덮어쓰지 않는다.

각 단원 결과는 분류(정적 코드 분석 / 원본 컴포넌트 실행 / 원본 runtime 테스트 / 별도 교육용), 명령·cwd·시각·입력 hash·source SHA·binary hash·예상·관측·해석·미검증 범위를 기록한다. runtime에는 정책 revision/loaded 상태/decision/client 결과/실제 effect를 추가한다. credential 값·인증 header는 수집하지 않는다.

현재 얻은 것은 원본 준비와 정적 해석이다. Prover pass/fail, runtime Allow/Deny, 원본 테스트 성공, Agent utility/ASR는 아직 측정하지 않았다. 다음 수업은 **01 Architecture**, 이어 **02 원본 정책 읽기**이며, 실제 도구 실행은 목적과 구조를 이해한 뒤 한 건씩 진행한다.

## 원본 코드 지도

경로 기준은 `third_party/guided-openshell-2e5589b/`다.

| 컴포넌트 | 파일·함수 | 입력 → 출력 / 의미 |
|---|---|---|
| ABI 전제 | `crates/openshell-sandbox/src/sandbox/linux/landlock.rs::require_abi` | kernel probe → 최소 ABI 검사 |
| 파일 집행 | 같은 파일 `prepare_current_user`, `enforce` | 정책·경로 → ruleset → child 실행 전 제한 |
| syscall 경계 | `crates/openshell-sandbox/src/sandbox/linux/seccomp.rs::apply` | 정책 → BPF/실행 제약 |
| 네트워크 판단 | `crates/openshell-supervisor-network/src/opa.rs::evaluate_network`, `authorize_egress` | binary·목적지 등 → 결정·사유·권한 |
| 네트워크 전달 | 같은 crate `src/proxy.rs::preauthorize_transparent_open` | 중재된 open 요청 → 승인 뒤 연결 경로 |
| 정책 적용 | 같은 crate `src/opa.rs::reload_from_proto`, `enter_fail_closed` | 새 revision/오류 → loaded state/차단 상태 |
| 정책 validation | `crates/openshell-policy/src/lib.rs::validate_and_canonicalize_sandbox_policy` | authored policy → 검증·정규화 |
| 제안·merge | 같은 crate `src/merge.rs::canonicalize_advisor_add_rule`, `merge_policy`, `policy_covers_rule` | 제안+기존 정책 → 제한된 변경·coverage 확인 |
| boundary CLI | `crates/openshell-prover-cli/src/main.rs` | 파일·옵션 → parse·check·JSON/exit |
| containment | `crates/openshell-prover/src/containment.rs::check_within_boundary` | candidate+boundary → 판정·반례/미지원 |
| 공식 단위 검증 | `crates/openshell-prover-cli/tests/cli.rs` | 원본 fixture → assertion, 실제 effect 없음 |
| runtime conformance | `tests/suites/conformance/src/{filesystem_policy,process,credential_gating,policy_advisor}.rs` | 실제 환경 fixture → 동작 검증; 현재 미실행 |

원문: [고정 source](https://github.com/NVIDIA/OpenShell/tree/2e5589b2180dd432320adda124c4f7bcede119b5). support matrix·architecture·policy/prover/advisor/network 문서는 같은 SHA의 `docs/`를 기준으로 읽는다. 현재 latest 문서의 기능을 고정 버전 결과에 섞지 않는다.
