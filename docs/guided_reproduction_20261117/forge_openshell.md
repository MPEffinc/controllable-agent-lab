# FORGE / SASY 및 NVIDIA OpenShell — 원본 조사

조사일: 2026-11-17, Asia/Seoul. 아래는 **원본 코드·문서 조사, 고정 source 확보, 호스트 기능 조회**다. 엔진·에이전트·평가·정책 변경은 실행하지 않았다. 기존 기록을 새 실험 결과로 합산하지 않았다.

## 이번 source 준비에서 실제로 수행한 일

기존 sparse checkout을 보존하고 새 경로에 `git init` → `remote add` → `fetch --no-tags --depth=1 origin <SHA>` → `checkout --detach <SHA>`로 고정 revision의 **전체 tracked source**를 확보했다. 실행 명령·cwd·시각·exit code·로그 SHA256은 [source acquisition manifest](../../local/guided-reproduction-20261117/setup/20261117T074851Z-forge-openshell-acquisition.json)에 있다. 각 명령 exit 0, HEAD 일치, working tree clean, missing Git objects 0을 확인했으며 27개 로그의 SHA256도 재확인했다.

| 신규 checkout | SHA | tracked files | Git submodule 상태 |
|---|---|---:|---|
| `third_party/guided-forge-ecc5ff9` | `ecc5ff9f7576f2669249609d9002c07674947913` | 42,583 | `sasy` → `6dedd2bc15da491d14ec07f87c0f1ef4d339efd6`, **미초기화** |
| `third_party/guided-openshell-2e5589b` | `2e5589b2180dd432320adda124c4f7bcede119b5` | 2,049 | 없음 |
| `third_party/guided-sasy-for-forge-6dedd2b` | `6dedd2bc15da491d14ec07f87c0f1ef4d339efd6` | 486 | 없음 |

FORGE 전체 checkout에는 업스트림이 Git에 포함한 기존 평가 결과도 들어 있다(디스크 약 1.4 GiB). 이 파일들은 **저자 제공 결과**이며 이번 시스템에서 실행한 결과가 아니다. 별도 benchmark 다운로드·submodule 초기화·LFS payload 다운로드·설치·빌드·평가는 하지 않았다. FORGE가 기대하는 `sasy/` submodule은 비어 있고 동일 revision을 별도 checkout으로만 확보했으므로, setup 완료나 실행환경 준비 완료를 뜻하지 않는다.

## FORGE / SASY

### 출처와 버전

- 논문: [Formal Policy Enforcement for Agentic Systems, arXiv 2602.16708v4](https://arxiv.org/html/2602.16708v4). §1 첫 각주가 아래 구현과 평가 저장소를 직접 연결한다.
- 구현: [sasy-labs/sasy](https://github.com/sasy-labs/sasy), 로컬 `third_party/sasy`, SHA `7dc9e524c5b1979b91d16b9d573219e358a6c332`. Python SDK 0.5.1, Apache-2.0. source checkout 있음, 설치·실행 없음.
- 평가: [sasy-labs/forge](https://github.com/sasy-labs/forge), SHA `ecc5ff9f7576f2669249609d9002c07674947913`. 기존 `third_party/forge`는 sparse 상태로 보존했다. 이번 학습용 전체 source는 `third_party/guided-forge-ecc5ff9`이며 README·pyproject·.gitmodules·공개 기존 결과를 포함한다.
- **평가용 엔진 pin은 별개다.** [setup_evaluation.py:18](https://github.com/sasy-labs/forge/blob/ecc5ff9f7576f2669249609d9002c07674947913/scripts/setup_evaluation.py#L18)은 SASY `6dedd2bc15da491d14ec07f87c0f1ef4d339efd6`을 요구한다. 기존 standalone SASY `7dc9e5…`를 FORGE 평가에 끼워 넣지 않는다. root source와 평가용 엔진 pin의 별도 source는 확보했다. 실제 workspace 설치 전에는 `sasy/` submodule 연결도 완료해야 한다.

### 학습 질문과 원문·함수 연결

| 질문 | 원문 / 실제 코드에서 볼 곳 |
|---|---|
| 문제·공격자 | 논문 §2.3. 비신뢰 에이전트가 제안하는 행동을 실행 경계에서 중재한다. |
| 정책 표현 | §3.1–3.3. Datalog와 이벤트 의존 그래프. `examples/message-flow/policy.dl`의 `CurrentDepends`, `Unauthorized`. |
| 작성·생성 | §3.4, Appendix H. 수기 정책과 자연어 번역을 구분한다. 평가 `experiments/translation/run_variant_set.py`, `generated_policy_fidelity.py`; `scripts/policy_finalize.py::{step_validate,step_scenarios,step_convergence,step_round_trip}`. |
| 집행 | §4.1–4.3, Appendix A. SDK `sdk/python/sasy/reference_monitor/api.py::check_tool_call` → `crates/sasy-refmon/src/service.rs::check_tool_call` → policy checker `check_authorization`. |
| 정확성 | §3.4, §4.4, Appendix H. 정책 의도 정확성과 중재 구현의 보장을 구분. coverage/faithfulness 및 실행 기반 검증은 합성 정책의 형식적 의도 일치 보장이 아니다. |
| 평가 | §5.1 정보흐름, §5.2 tau2 고객서비스, §5.3 MALADE, §5.4 AgentDojo; Appendix G/H. 평가 entry는 아래 참조. |
| 한계 | §7.1. 계측하지 않은 raw socket/stdio 경로와 잘못 작성한 정책은 보장 밖. |

표의 설명은 원문 요지이며 아래 코드는 조사한 checkout의 실제 구현 경로다. **실행 보장 검증 결과는 아니다.**

### 첫 원본 정책·효과 관찰

`third_party/sasy/examples/message-flow/policy.dl`은 `send_summary`가 untrusted 문서와 sensitive 문서 **모두**에 의존할 때 `Unauthorized`를 도출한다. `IsAuthorized`도 동시에 만족할 수 있지만 deny가 우선한다. 수신자 blacklist나 공격 문자열 검사와 다르다.

원본 실행 경로:

1. `examples/message-flow/demo.py::run_scenario`가 새 policy session에서 문서를 읽고 요약을 만든다.
2. `dispatch`가 tool request와 입력 의존성을 기록한다.
3. `sasy.check_tool_call`이 실제 엔진 판정을 요청한다.
4. authorized일 때만 `sent.append(arguments.copy())`가 수행된다. 이 append는 **모의 발송 효과**다.

구현 SHA `7dc9e5…`의 공식 명령은 repo root에서 `uv run examples/message-flow/demo.py`다. 원본은 Enter를 기다리는 해설형 실행을 지원한다. `--trace`는 기록 이벤트, `--no-pause`는 자동 진행, `--sensitive-only`는 허용 baseline을 선택한다. 정상 입력에서는 Allow와 `sent` 1건, sensitive+untrusted에서는 Deny와 미발송을 **예상**한다. 아직 실행하지 않았다.

`--live`는 기본 모델 `gpt-4.1-mini`로 유료 호출하며 별도 승인이 필요하다. scripted 모드는 모델 없이 선택을 고정하지만 **SASY 엔진 판정은 실제**다. 두 모드 모두 문서 저장소와 발송 sink는 모의다. 이 예제를 논문의 전체 정보흐름/AgentDojo 재현으로 표현하지 않는다.

### 의존성과 실행환경 준비 조건

- standalone SASY: Python ≥3.11. SDK는 grpc/protobuf, pydantic, httpx, cryptography, networkx 등을 사용. 기존 Python 3.10 환경과 혼합하지 않는다.
- 원본 workspace는 `sasy[all]`와 LangChain/ADK/Langroid 등 선택 통합을 포함해 설치량이 크다. 첫 scripted 예제에서 필요한 SDK와 원본 import를 검토한 뒤 전용 환경을 구성한다.
- 엔진은 Docker 또는 Rust/Soufflé/C++ native toolchain이 필요. 원본 Dockerfile은 Nix 기반 build다. repo `AGENTS.md`는 해당 checkout에서 빌드한 엔진을 명시해 시험하도록 안내한다. 단순 SDK 버전 tag의 컨테이너를 고정 SHA build와 같다고 간주하지 않는다.
- Python CLI `sasy engine start`의 기본 설정 경로는 `~/.sasy`, 이미지 기본값은 `ghcr.io/sasy-labs/sasy:<SDK version>`. 학습 실행 시 전용 profile·name·volume·port와 로컬 config를 먼저 정해 기존 엔진/설정을 보존한다.
- FORGE root workspace의 `pyproject.toml`은 **Python ≥3.11,<3.12**를 요구한다. 별도 AgentDojo 환경은 `experiments/agentdojo/setup.sh`가 **Python 3.12**, `agentdojo==0.1.35`, 평가 pin의 `sasy/sdk/python[otel]`을 설치한다. 이 두 환경을 구분하고 standalone CaMeL/AgentDojo 환경을 재사용하지 않는다.
- 평가 credentials: Azure/OpenAI, tau2 사용자 시뮬레이터·judge, Vertex 등 선택 모델에 따라 다름. MALADE는 OpenFDA 및 Qdrant도 필요. 번역 harness는 Claude Code CLI, jq, make, Soufflé, C++ 추가 필요.
- 현재 호스트 PATH에서 rustc/cargo/souffle/nix를 찾지 못했다. 설치·Docker pull/build/start는 이번 조사에서 수행하지 않았다.

### 원본 Evaluation 진입점과 최소화

- 총괄: `scripts/evaluation/run_benchmark.py::main`; `--targets agentdojo|infoflow|tau2|malade`. `--targets paper`는 네 평가를 모두 선택하므로 첫 실습에 쓰지 않는다.
- AgentDojo: `experiments/agentdojo/run.py` → `sasy_agentdojo/runner.py::run` → `pipeline.py::build_pipeline` → `monitor.py::SasyToolsExecutor.query/check`.
- 정책: `experiments/agentdojo/policies/agentdojo_policy.dl`; `policy_metadata.py`, `presets.py`가 정책 switches와 tool taxonomy를 공급한다.
- `presets.py::TABLE_SETTINGS`: Azure gpt-4o deployment, pipeline label gpt-4o-2024-08-06, tool_knowledge 공격, benchmark v1.2.2, 5 sweeps. 모델 label은 실제 deployment 동일성을 보증하지 않는다.
- **주의:** README의 suite/task/repeat 최소화 명령도 preset을 생략하면 **8개 비교 arm**을 선택한다. 한 cell부터 `--agentdojo-preset provenance`로 제한하고 warmup 추가 호출도 따로 센다.

환경·비용 확인 후 검토할 단일 정상 task 명령(미실행, repo root):

```bash
experiments/agentdojo/.venv/bin/python experiments/agentdojo/run.py \
  --preset provenance --attack none \
  --suite workspace --user-task user_task_0 --repeats 1 --threads 1 \
  --logdir /home/cclab/controllable_agent/local/guided-reproduction-20261117/runs/forge/clean-01/runs \
  --decisions /home/cclab/controllable_agent/local/guided-reproduction-20261117/runs/forge/clean-01/decisions.jsonl
```

별도 `make serve`/인증·TLS 설정이 먼저 필요하다. 공격 실습은 `runner.py::build_jobs`에서 특정 task와 연결되는 injection task ID를 먼저 확인하고 `--injection-task ID`로 한 건을 좁힌다. `--attack none`만 제거하면 task별 공격이 여러 건 생길 수 있어 바로 실행하지 않는다.

관찰은 정책 decision, `runtime.run_function` 호출 여부, 최종 AgentDojo environment 효과, native scorer를 따로 본다. `SasyToolsExecutor.check`는 **ASK만 있는 판정을 `authorized=True, asked=True`로 돌려 실제 도구를 실행**한다. 이후 security/utility가 서로 다른 가정으로 집계할 수 있다. ASK를 Deny로 세거나 native ASR을 실제 tool effect와 동일시하면 안 된다. 효과 분석은 `scripts/evaluation/{agentdojo_effect.py,audit_agentdojo_effect_asr.py,summarize_agentdojo.py}`다.

## NVIDIA OpenShell

### 출처·범위·보유 소스

- 공식 [NVIDIA/OpenShell](https://github.com/NVIDIA/OpenShell), SHA `2e5589b2180dd432320adda124c4f7bcede119b5`, Apache-2.0. OpenShell 자체는 이번 조사에서 특정 논문 artifact로 확인되지 않았다. 논문 section을 임의로 부여하지 않고 공식 architecture/policy/support 문서와 테스트를 연결한다.
- 기존 `third_party/openshell`은 root 파일만 있는 sparse partial checkout으로 보존했다. 아래 runtime 함수들을 GitHub 연결 도구로 고정 SHA에서 읽은 뒤, 신규 `third_party/guided-openshell-2e5589b`에 전체 tracked source를 확보했다. source 확보와 실행환경 설치는 구분한다.
- 모든 아래 파일 링크의 기준: [고정 source tree](https://github.com/NVIDIA/OpenShell/tree/2e5589b2180dd432320adda124c4f7bcede119b5).

### 정책과 실제 집행·검증

| 질문 | 공식 문서 및 고정 코드 |
|---|---|
| 문제·경계 | `README.md::How It Works`, docs architecture. 파일·syscall·네트워크 및 provider credential 경계. |
| 표현 | YAML `filesystem_policy`, `landlock`, `process`, `network_policies`; `crates/openshell-policy-schema/src/yaml.rs`, `crates/openshell-policy/src/lib.rs`. |
| 생성·갱신 | `docs/how-it-works/policies/advisor.mdx`. agent가 network rule만 제안. 기본은 사람 검토; proposal 자체가 정책을 바꾸지 않는다. |
| filesystem | `crates/openshell-sandbox/src/sandbox/linux/landlock.rs::{probe_availability,require_abi,prepare_current_user,enforce}`. |
| syscall | `crates/openshell-sandbox/src/sandbox/linux/seccomp.rs::{apply,build_filter_rules}`. |
| network | `crates/openshell-supervisor-network/src/opa.rs::{evaluate_network,authorize_egress,reload_from_proto,enter_fail_closed}`, `proxy.rs::{start_with_bind_addr,preauthorize_transparent_open}`. |
| 정책 충돌·확대 | `crates/openshell-policy/src/merge.rs::{merge_policy,canonicalize_advisor_add_rule,policy_covers_rule}`, `validate_and_canonicalize_sandbox_policy`. invalid input·최종 정책을 검증하고 부분 mutation 노출을 막는다. |
| 정적 보장 | `docs/how-it-works/policies/prover.mdx`, `crates/openshell-prover-cli/README.md`. SMT 기반 candidate⊆boundary 검사. 검사 coverage는 filesystem/network_l4/network_rest/process/landlock. GraphQL/MCP 등은 unsupported일 수 있다. |

### 현재 호스트의 실제 제약

고정 [support-matrix.mdx](https://github.com/NVIDIA/OpenShell/blob/2e5589b2180dd432320adda124c4f7bcede119b5/docs/about/support-matrix.mdx)는 **Landlock ABI≥3**을 mandatory baseline으로 요구한다. upstream Linux 6.2 이상에서 도입되었으며 filesystem `best_effort`로 이 baseline을 끌 수 없다. `landlock.rs::require_abi`도 실제로 3 이상만 통과시킨다.

현재 host는 Linux 5.15.0-203-generic이다. 버전 추측에 그치지 않고 아래 **읽기 전용 kernel capability query**를 실행했다. `/usr/include/x86_64-linux-gnu/asm/unistd_64.h:359`에서 syscall 번호 444를 확인했다. 규칙 생성/적용/권한 변경은 없다.

```python
import ctypes
libc = ctypes.CDLL(None, use_errno=True)
libc.syscall(444, ctypes.c_void_p(0), ctypes.c_size_t(0), ctypes.c_uint(1))
# landlock_create_ruleset(NULL, 0, LANDLOCK_CREATE_RULESET_VERSION)
```

관측: `Landlock ABI=1`, `errno=0`. 따라서 **이 SHA의 OpenShell runtime은 현재 host의 mandatory baseline을 충족하지 못한다.** Docker가 host kernel을 공유하는 구성은 이 차이를 해결하지 못한다. host 변경·새 VM·관리자 작업은 사용자 확인 후 별도 결정한다. Docker client28.3.2와 server version API28.3.2 응답은 이번 전체 조사에서 확인했다. container 생성·권한·OpenShell sandbox 집행은 검증하지 않았다. `openshell`, `openshell-prover`, Rust toolchain은 PATH에서 찾지 못했다.

### 최소 원본 실습 순서와 명령(모두 미실행)

1. 전체 source는 확보했다. 다음은 **standalone prover** 의존성/바이너리 준비 후 학습한다. gateway/운영정책을 바꾸지 않는다. 고정 `crates/openshell-prover-cli/tests/fixtures/`의 `boundary.yaml`, `candidate-contained.yaml`, `candidate-exceeds.yaml`을 사용한다. 공식 CLI:

```bash
openshell-prover check candidate-contained.yaml --boundary boundary.yaml --output json
openshell-prover check candidate-exceeds.yaml --boundary boundary.yaml --output json
```

예상 exit 0=within boundary, 1=exceeds, 2=input/internal error, 3=unsupported/inconclusive. JSON `coverage.domains`를 확인한다. **정책 containment 통과는 실제 runtime 설치·집행 증명이 아니다.** pinned source build 명령은 `cargo build -p openshell-prover-cli --bin openshell-prover`; 지금은 toolchain이 없다. 임의 latest 바이너리를 이 SHA와 같다고 취급하지 않는다.

2. kernel 조건을 충족한 별도 실행환경을 승인받은 후 [원본 network policy tutorial](https://github.com/NVIDIA/OpenShell/blob/2e5589b2180dd432320adda124c4f7bcede119b5/docs/tutorials/first-network-policy.mdx)을 사용한다. entry는 `examples/sandbox-policy-quickstart/demo.sh`지만 처음에는 자동 script 전체를 실행하지 않고 각 단계로 읽는다. `openshell sandbox create`는 컨테이너/gateway를 만들므로 사전 검토 대상이다. tutorial의 `registry.example.com/team/agent-tools:1.0`은 placeholder이므로 그대로 실행 불가.

3. network policy에서 `/usr/bin/curl`만 `api.github.com:443`, protocol=rest, enforcement=enforce, access=read-only로 허용한다. 원본 명령은 `openshell policy update demo --rule-name github_api --binary /usr/bin/curl --add-endpoint api.github.com:443:read-only:rest:enforce --wait`. 전용 학습 sandbox에만 적용한다.

4. GET 허용과 POST 차단을 정책 decision·L7 403·upstream effect로 구분한다. tutorial POST는 GitHub issue endpoint이므로 **외부 변경 가능성이 있는 명령은 이번에 실행하지 않았다.** 실제 실습에서는 사용자가 이 조건을 검토한 뒤 실행 범위를 정한다. `enforcement:audit`는 로깅만 하고 차단하지 않으므로 `enforce`와 섞지 않는다.

원본 runtime unit/integration 테스트는 `crates/openshell-supervisor-network/src/opa.rs`, `crates/openshell-policy/src/merge.rs`, `crates/openshell-prover-cli/tests/cli.rs`; sandbox Landlock/seccomp behavioral tests와 e2e는 kernel·runtime 조건이 필요하다. 모델과 benchmark가 없는 원본 정책/런타임 검증을 특정 논문의 attack success rate 재현이라고 부르지 않는다.

## 권장 연결 순서

Progent의 tool argument 정책을 익힌 뒤 SASY message-flow에서 **과거 입력의 의존성**까지 정책에 들어가는 변화를 확인한다. 이어 FORGE의 단일 원본 AgentDojo cell로 native scorer와 tool effect를 비교한다. OpenShell은 독립적인 OS/network 경계 학습으로 이어가되, 현재 host에서는 prover·source 학습까지만 가능하다. 모든 새 로그는 `local/guided-reproduction-20261117/runs/{forge,openshell}/<새 run ID>/`에 저장하고 원본 source와 과거 결과는 수정하지 않는다.
