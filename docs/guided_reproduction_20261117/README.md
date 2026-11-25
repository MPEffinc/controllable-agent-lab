# Agent Security Key Papers — 단계별 학습 출발점

**사용자 원본 실행 결과(2026-11-19):** [실제 로그 해석](progent_original_result_20261119.md). 원본 GPT-4o CLI에서 Banking·Workspace·Travel·Slack 정상 각 1건은 utility=true. Banking 공격 pair는 utility=false, native security=true이며 실제 목표 계좌행 모의 송금도 확인해 방어 실패로 해석한다. 정상 로그와 공격의 넓은 초기 정책을 비교하며, 공격의 사전 능력 검사와 victim을 구분한다.

**Progent 현재 진행 기준(2026-11-19 최종 정정):** [원본 실행·로그·기능별 실습](progent_original_walkthrough_20261119.md). 원본 `python -m agentdojo.scripts.benchmark`를 직접 실행한다. 정상 한 건으로 범위를 끝내지 않고, 정적 검사·집행·갱신 통제·원본 공격/방어 비교·네 도메인·모델 비교·ASB·MCP/다중 Agent를 한 실습씩 다룬다. CLI가 없거나 환경이 미준비인 항목은 구분한다. [과거 명령·로그 검토](progent_execution_log_review_20261119.md)와 [별도 실행기 안내](progent_live_terminal_20261119.md)는 보존 기록이다. 새 유료 실행·공격 평가는 수행하지 않았다.

2026-11-17, Asia/Seoul. 이번 요청의 목표는 원본 정책·실행 경계·평가를 하나씩 이해하는 것이다. 기존 README/CONTEXT의 자체 연구 계획이나 자동 실행 방식은 이번 학습 범위로 가져오지 않는다. 기존 기록과 원본 코드를 보존했고 Git commit/push는 하지 않았다.

## 조사 결과와 학습 순서

아래 순서는 학습 연결을 위한 제안이다. 한 연구의 정상/방어 사례를 해석한 뒤 다음 연구로 간다. 구현이 미확인인 연구도 목록에 유지하며, 원문 분석과 실행 대기를 구분한다.

| 순서·연구 | 읽을 원본과 확보한 구현 | 첫 학습 대상 | 현재 준비 / 원본 Evaluation 진입점 |
|---|---|---|---|
| 1. Progent | [paper v3](https://arxiv.org/html/2504.11703v3), [author artifact](https://github.com/sunblaze-ucb/progent) `b02783b…` | tool 이름·인자에 대한 JSON Schema 정책 → 허용/거부 → 실제 effect | 전용 Progent+vendored AgentDojo 환경 설치·import·CLI 도움말 확인. `agentdojo.scripts.benchmark::main`, `asb/scripts/agent_attack.py`, `real-world-agents/run.py`. [첫 가이드](progent.md) |
| 2. FORGE / SASY | [paper v4](https://arxiv.org/html/2602.16708v4), [SASY](https://github.com/sasy-labs/sasy), [FORGE eval](https://github.com/sasy-labs/forge) `ecc5ff9…` | Datalog로 과거 데이터 의존성까지 검사하는 reference monitor | full tracked source 확보. 평가용 SASY는 별도 `6dedd2b…`; standalone SDK는 `7dc9e52…`. engine/toolchain 미설치. `examples/message-flow/demo.py`, `scripts/evaluation/run_benchmark.py`, `experiments/agentdojo/run.py`. [가이드](forge_openshell.md) |
| 3. NVIDIA OpenShell | [NVIDIA official source](https://github.com/NVIDIA/OpenShell/tree/2e5589b2180dd432320adda124c4f7bcede119b5) `2e5589b…` | 정책을 OS·파일·syscall·network 경계에서 집행하는 차이 | 전체 source 확보. 현재 Landlock ABI1로 원본 필수 ABI≥3 미충족. Rust/prover 미설치. `crates/openshell-prover-cli/tests/cli.rs`, `examples/sandbox-policy-quickstart/demo.sh`. 특정 논문 artifact로 확인하지 못했으므로 공식 문서·테스트를 기준으로 한다. [가이드](forge_openshell.md) |
| 4. ControlValve | [paper v2](https://arxiv.org/html/2510.17276v2), [author page](https://rishijha.com/pubs/breaking_and_fixing.html) | CFG와 간선 규칙으로 orchestrator 호출 순서를 제한 | 공식 runnable repository 미확인. §4·부록 L의 원본 정책을 먼저 읽는다. AutoGen Magentic-One/CFH-Hard/수정 AgentDojo 평가 entry·lock·함수는 미확인. [조사](controlvalve_multicamel_pauth.md) |
| 5. Multi-CaMeL | [paper v1](https://arxiv.org/html/2610.05640v1), [author-associated artifact](https://github.com/james-pete/multiagentdojo) `e716473…` | tool-derived data가 child instruction으로 승격되는 문제와 provenance | 원본 source·uv.lock 확보. Python≥3.11/Sequrity Control API 필요. 독립 설치는 이 학습 단계에서 수행. `agentdojo.scripts.benchmark --multi-camel`, `tests/test_camel.py`. AssetOpsBench entry 미확인. [조사](controlvalve_multicamel_pauth.md) |
| 6. PAuth | [paper v2, Beyond OAuth](https://arxiv.org/html/2603.17170v2), [author page](https://homes.cs.washington.edu/~reshabh/) | 자연어 작업을 operand/guard slice로 변환해 tool 호출을 인가 | 공식 runnable repository·lock·CLI 미확인. §III–IV·§V-F 원문 slice부터 읽는다. 평가의 Deny는 permission dialog 의미다. [조사](controlvalve_multicamel_pauth.md) |
| 7. CONTINUITY | [paper v1](https://arxiv.org/html/2609.05269v1), [official artifact](https://github.com/zast-ai/continuity) `59cfe60…` | grant·검증 증거·permit과 최종 sink 시점의 재검증 | 기존 Python3.11.17 전용 환경/pins 확인, 재설치 없음. 원본은 LLM 없이 deterministic suite. `tests/test_experiment.py`, `scripts/run_experiments.py`. [가이드](continuity.md) |

Multi-CaMeL 전에 필요하면 [CaMeL 원논문](https://arxiv.org/abs/2503.18813)과 기존 `third_party/camel`의 privileged/quarantined LLM·capability 구조만 짧게 연결한다. 이는 Multi-CaMeL을 다른 연구로 대체하는 단계가 아니다. 새로운 MAS나 새로운 방어기법은 만들지 않는다.

## 시스템과 독립 환경

현재 관측: Ubuntu22.04 x86_64, Linux5.15.0-203, host Python3.10.12, RAM31GiB, uv0.13.3, Docker client/server version API28.3.2. Docker container나 sandbox는 실행하지 않았다. Rust/cargo/Soufflé/Nix/Node는 PATH에 없다. 관리자 명령·OS 변경·GPU 작업은 하지 않았다.

| 연구 | 독립 환경 / 필요한 준비 | 모델·서비스·OS 조건 |
|---|---|---|
| Progent | **신규 준비 완료:** `local/guided-reproduction-20261117/envs/progent-agentdojo/`; 핵심 엔진은 기존 `third_party/progent/.venv`도 유지 | core demo는 API/GPU/Docker 불필요. LLM AgentDojo는 별도 agent/policy model 호출. ASB/MCP·실제 agent framework는 각각 별도 환경 준비 필요 |
| FORGE/SASY | source 준비 완료, 설치 대기. standalone Python≥3.11; FORGE root3.11; FORGE AgentDojo 별도3.12 | SASY engine Docker 또는 Rust/Soufflé/Nix/native build. 모델별 API, MALADE는 Qdrant/OpenFDA, 번역 평가 추가 CLI 필요 |
| OpenShell | source 준비 완료, prover build 대기, sandbox는 호스트 조건 불충족 | Landlock ABI≥3 필수. kernel/VM 변경은 확인 후 진행. 공식 prover와 runtime 집행을 구분 |
| ControlValve | 구현·요구 dependency 미확인으로 원본 실행환경 구성 불가 | 원문은 Magentic-One 모델 사용. 코드·버전 확보 전 동명 package 설치하지 않음 |
| Multi-CaMeL | 전용 환경은 아직 미설치. 이 단계에서 새 `envs/multicamel/`을 `UV_PROJECT_ENVIRONMENT`로 지정해 frozen lock 설치 예정 | Python≥3.11, Sequrity0.4.2 lock, Sequrity key와 upstream provider key. fake-client tests는 외부 엔진 집행 검증 아님 |
| PAuth | 구현·dependency 미확인으로 원본 실행환경 구성 불가 | 논문 MCP middleware와 모델 설정만 확인. runnable 배포를 임의로 만들지 않음 |
| CONTINUITY | 기존 `third_party/continuity/.venv` 재사용, direct pins5개 일치 | Python≥3.11; API/GPU/Docker 불필요. in-memory 최종 효과 모델 |

이번 기본 환경 준비는 **현재 학습을 시작할 Progent**에 집중했다. 다른 논문의 대규모 의존성과 엔진은 해당 실습에 진입할 때 설치한다. `runs/<paper>/` 디렉터리를 만들어 둔 사실을 해당 엔진 설치 완료로 표현하지 않는다.

## 보존한 버전·증거·출력 경로

- [source_manifest.json](source_manifest.json): paper version, 전체 Git SHA, source 경로·상태, 환경 상태. 움직이는 main/latest를 재현 버전으로 쓰지 않는다.
- `local/guided-reproduction-20261117/setup/inventory-before.json`: 기존 checkout/환경 조사.
- 같은 setup 폴더: Progent 의존성 해석·설치·초기 import 실패·호환성 수정·최종 import/CLI 도움말/dependency 검증의 개별 명령, exit code와 로그.
- `setup/progent-agentdojo-resolved-v2.txt`: 이번 로컬 해석의 hash 포함 dependency pins. 저자 lockfile과 구분한다.
- `setup/20261117T074851Z-forge-openshell-acquisition.json`: FORGE/OpenShell/평가용 SASY 전체 source 확보 명령과 로그 hash.
- `papers/sources.json`, `missing-artifacts/sources.json`: 버전 고정 원문 HTML 다운로드와 SHA256. OpenShell은 Git SHA에 포함된 공식 문서를 읽는다.
- 새 실험 출력은 **`local/guided-reproduction-20261117/runs/<paper>/<새-run-id>/`**. 기존 이름은 재사용하지 않는다. 원본 checkout에 포함된 saved results와 과거 프로젝트 결과는 새 실행 증거가 아니다.

`scripts/progent_guided_effect.py`는 원본 policy/ground-truth request/runtime/tool을 연결하는 **조교 어댑터**이며, 자체 정책 엔진이나 MAS를 만들지 않았다. 원본 full evaluation 또는 실제 LLM 공격 실험이라고 부르지 않는다. 구문·default policy 표시만 확인했고 `--case`의 도구 실행은 하지 않았다.

## 진행 원칙과 현재 다음 단계

각 연구는 **개념 → 원본 코드 경로 → 작은 정상/방어 조건 → 사용자 실행 또는 실행 요청 → 로그 해석 → 관련 심화 → 논문 Evaluation 대조** 순서다. Deny/ASK/승인 요청/도구 에러와 최종 tool effect를 따로 기록한다. 정상 task 실패도 함께 봐야 과잉 차단을 알 수 있다.

유료 API·관리자 권한·운영 변경·대규모 실행은 사전 확인한다. 평범한 source 확보·전용 환경 설치·비파괴 import/help 확인은 수행했다. 논문의 보장을 코드 경로가 자동으로 충족한다고 가정하지 않고 설정과 실제 결과를 확인한다.

**현재 다음 단계는 [Progent 가이드의 A: 원본 정책 검사 예제](progent.md)의 실행과 경고 해석이다.** 아직 개별 논문 실험 성공이나 ASR/utility 재현을 주장할 실행 결과는 없다.

## 2026-11-18 논문 중심 학습 추가

[Progent Guided Study 01](progent_study_01_20261118.md)에 §2/Figure 1, §3 Threat Model, §4–5/Algorithm 2–3, §6의 보장과 실제 코드의 입력·출력·설정 차이를 누적했다. 첫 실습은 여전히 미실행이며, 원본 해설과 실행 구조를 먼저 학습한다. 전날 설명의 저자 의도 추정과 Figure 1/평가 scenario의 구분도 이 추가 기록에서 명확히 했다.

이후 사용자가 원본 정적 checker 출력을 전달했다. [Study 01 결과](progent_study_01_result_20261118.md)에 경고 한 건과 실행 출처를 기록했다. 다음은 [Study 02: 정상 요청 허용과 모의 도구 효과](progent_study_02_enforcement_20261118.md)이며, 아직 실행하지 않았다.

후속으로 Study02의 사용자 실행은 어댑터의 import 순서 때문에 실패했다. [Study02 코드 흐름과 실패 해설](progent_study_02_code_walkthrough_20261118.md)에 실제 중단 지점과 정책 집행 경로를 누적했다. 어댑터 import를 수정해 등록까지만 확인했으며, 정상/공격 도구 실행은 추가로 수행하지 않았다. 현재는 새 명령보다 원본 정책·요청·runtime·wrapper·effect의 연결을 먼저 학습한다.

사용자 요청에 따라 [Progent 전체 프레임워크 코드 지도](progent_framework_flow_20261118.md)를 먼저 읽는 순서로 전환했다. 핵심 library/평가 harness/통합 adapter를 구분하고, 요청 하나의 초기 정책 생성→업무 LLM→집행→feedback→갱신→평가를 따라간다. 개별 테스트 실행을 학습 진척으로 대신하지 않는다.

사용자가 실제 실행 계획을 요청해 [원본 LLM 실행 계획](progent_live_run_plan_20261118.md)을 추가했다. 첫 실행 대상은 원본 Banking UserTask0, 자동 정책 생성·갱신 ON 한 건이다. 원본 모델 상태·비용·필요한 계측 준비를 구분했고 유료 호출은 아직 하지 않았다.

## 2026-11-18 실제 LLM 실행 후 현재 상태

후속 승인으로 기존 키와 gpt-6-luna를 사용해 연결 확인1회 및 원본 정상 Banking task0 한 건을 실행했다. [Live01 결과와 코드 해설](progent_live_01_result_20261118.md)이 현재 읽을 기록이다. 정책 모델이 첫 응답에 잘못된 키를 사용하고 재시도에서 빈 배열을 반환해 read_file이 Deny됐다. 원본 utility=false, 환경 전후 동일, 거래 추가0이다. 모델 대체 실험이며 논문 수치 재현이나 공격 방어 성공으로 표현하지 않는다. 추가 유료 호출·공격 실험 없이 정책 생성의 출력 계약과 집행 경계를 먼저 학습한다. 앞의 미실행 표기는 당시 단계의 기록이다.

## 2026-11-18 중간 가시성을 갖춘 재시도

사용자의 재시도 요청에 따라 [Live02: 요청·응답·정책·실제 효과](progent_live_02_visible_20261118.md)를 진행했다. 원본 소스와 지난 결과를 보존하고 외부 어댑터에서 name/args 출력 형식 안내를 추가했다.14개 중간 확인 지점에서 내용을 대화에 표시한 뒤 계속했다. 초기 파일 읽기 정책 생성→read_file Allow→청구 정보로 send_money 규칙 추가→send_money Allow→거래5건에서6건→원본 utility=true를 확인했다. 총7API 요청이다. 날짜는 정책·utility에서 검증하지 않았으며 공격·Deny·SMT subset 검증도 이번 범위에 포함하지 않는다. 현재 학습 기록은 Live02를 기준으로 읽고, Live01은 실패 조건의 보존 기록으로 함께 대조한다.

## 2026-11-19 OpenShell 학습·실습 준비

[OpenShell 학습·실습 계획](openshell_study_plan_20261119.md)에 즉시 가능한 정적 학습, 도구 준비 후 가능한 원본 Prover 검사, 별도 실행환경이 필요한 runtime 실습을 구분했다. 8개 단원의 목적·구조·관찰·해석과 공식 fixture 기반 단일 실행 카드를 준비했다. 설치·빌드·정책 검사·sandbox·Agent는 미실행이다. 기존 환경 및 Progent 결과를 보존했다. Progent의 보안성 평가·충돌 분석 등은 후속 심화로 남겨둔다.
