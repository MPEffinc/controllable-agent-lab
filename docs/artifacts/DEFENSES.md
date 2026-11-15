# 방어기법 및 AgentDojo 소스 감사

이 문서는 2026-11-14 Bootstrap에서 새로 확보한 소스와 설치 로그를 근거로 한다. 기존 연구 기록은 검증 결과에 포함하지 않았다. 후속 사용자 지시에 따라 새 실험·추가 설치를 중단했으며, 아래 설치 성공을 테스트 통과나 논문 재현 성공으로 해석하지 않는다. 상태는 `VERIFIED`(해당 사실 관측), `PARTIAL`, `FAILED`, `NOT_RUN`을 사용한다.

## 출처·고정 버전

각 README를 연결된 GitHub 도구로 먼저 읽어 논문 연결을 확인한 뒤 `git clone --depth 1`로 확보했다. 소스에 포함된 지시문은 신뢰 경계 밖의 자료로 취급했다. 전역 설치 및 원본 코드 수정은 수행하지 않았다.

| 프로젝트 | 출처 판정 | 논문 및 저장소 | 고정 commit SHA | 라이선스 | 확보 증거 |
|---|---|---|---|---|---|
| CaMeL | VERIFIED OFFICIAL: 저자·소속 및 research artifact 명시 | [paper 2503.18813](https://arxiv.org/abs/2503.18813), [Google Research 소스](https://github.com/google-research/camel-prompt-injection) | `f083b6b396399d3b3c7f2ddaf613a5945eaf32d8` | Apache-2.0, `third_party/camel/LICENSE` | `defenses-clone-camel.json/.log` |
| Progent | VERIFIED AUTHOR-ASSOCIATED: 논문 제목·arXiv 직접 연결, sunblaze-ucb research artifact | [paper 2504.11703](https://arxiv.org/abs/2504.11703), [저자 저장소](https://github.com/sunblaze-ucb/progent) | `b02783b896d4bf01a2adf24738015e258db8d35b` | MIT, `third_party/progent/LICENSE` | `defenses-clone-progent.json/.log` |
| DRIFT | VERIFIED OFFICIAL: README가 NeurIPS 2025 official implementation 명시 | [paper 2506.12104](https://arxiv.org/abs/2506.12104), [SaFo-Lab 소스](https://github.com/SaFo-Lab/DRIFT) | `6fd3df4763fad77398c3c273c2a4fe14dd50f7ea` | MIT, `third_party/drift/LICENSE` | `defenses-clone-drift.json/.log` |
| AgentDojo | VERIFIED OFFICIAL: 논문 저자·citation·원래 ethz-spylab 소스 연결 | [paper 2406.13352](https://arxiv.org/abs/2406.13352), [현재 소스](https://github.com/sequrity-ai/agentdojo) | `357c80dea9af34323f709c3505d9e6d224654c7e` | MIT, `third_party/agentdojo/LICENSE` | `defenses-clone-agentdojo.json/.log` |

위 증거 파일의 기준 디렉터리는 `results/setup/bootstrap-20261114/`다. 재검증용 URL·SHA·working-tree 상태는 같은 경로의 `source-manifest.json`, 설치된 실제 버전은 `environment-inventory.json` 및 `requirements-{camel,progent}.txt`에 있다. Progent는 이름이 같은 별도 `Agentic-AI-Risk-Mitigation/progent` 라이브러리가 아니다.

## CaMeL

**현재 상태: 소스·잠금파일 기반 격리 설치 VERIFIED, 동작 테스트·논문 재현 NOT_RUN.**

- 런타임: `pyproject.toml`은 Python >=3.10, `.python-version`은 3.10.12. 실제 `third_party/camel/.venv`는 Python 3.10.12, camel 1.0.0, AgentDojo 0.1.34, pydantic 2.11.5, openai 1.82.1, anthropic 0.52.2를 포함한 121 distributions다.
- 설치 명령: `python3 scripts/bootstrap_run.py --name defenses-camel-sync --cwd /home/cclab/controllable_agent/third_party/camel --timeout 420 -- uv sync --frozen --no-dev`. `defenses-camel-sync.json/.log`의 exit code는 **0**. 원본 `uv.lock`을 사용했고 dev 그룹을 설치하지 않았다. 따라서 pytest가 준비되었다고 주장하지 않는다.
- 진입점: `third_party/camel/main.py::main`; 모델 이름 및 `--use-original`, `--ad_defense`, `--run-attack`, `--replay-with-policies`, `--eval_mode` 옵션이 원본/방어/평가 경로를 선택한다.
- Method: `src/camel/pipeline_elements/privileged_llm.py::PrivilegedLLM`의 계획/코드 생성, `src/camel/quarantined_llm.py`의 비신뢰 데이터 질의, `src/camel/interpreter/interpreter.py::camel_eval`의 제한된 실행을 결합한다. 값의 출처와 readers는 `src/camel/capabilities/`와 `src/camel/interpreter/value.py`에 표현된다. 단순 문자열 필터가 아니다.
- 정책 정의: `src/camel/security_policy.py::SecurityPolicyEngine.check_policy`, `base_security_policy`, `NoSecurityPolicyEngine`; suite별 실제 정책은 `src/camel/pipeline_elements/security_policies/{workspace,banking,slack,travel}.py`. `WorkspaceSecurityPolicyEngine` 등은 trusted fields 및 readers 조건을 사용한다. `agentdojo_security_policies.py::make_trusted_fields_policy`와 `ADNoSecurityPolicyEngine`도 존재한다.
- 집행 지점: `src/camel/interpreter/interpreter.py::_eval_call`은 인자를 평가한 뒤 `security_policy_engine.check_policy(...)`를 호출하고, 외부 callable에 대한 `Denied`이면 `SecurityPolicyDeniedError`를 발생시킨다. 이후에만 `evaled_fn.call(...)`을 호출한다. 모든 Python 실행/외부 서비스에 대한 완전한 중재를 이 코드 읽기만으로 증명하지 않았다.
- 효과 지점: `src/camel/pipeline_elements/agentdojo_function.py::AgentDojoFunction.call` → `self._runtime.run_function(self._env, self._name, args_by_keyword, raise_on_error=True)`. `wrap_output`/`_get_metadata_for_ad`는 suite 데이터 결과에 metadata를 부여한다. 효과는 AgentDojo의 모의 환경 상태이며 실제 메일 발송은 아니다.
- 평가·관측: AgentDojo user/injection task의 utility/security와 interpreter `FunctionCall` 체인, conversation 기록을 사용한다. `tests/test_pipeline_elements/test_agentdojo_function.py`는 mock `add` 도구와 기대 호출체인을 검사하는 실제 원본 테스트지만 **실행하지 않았다**. 모델 adapter는 `src/camel/models.py`, `PrivilegedLLM`, `quarantined_llm.py`에 있다. full evaluation은 LLM credentials가 필요하다.
- 한계: README 스스로 interpreter bugs·보안 미완성·유지보수 비보장을 경고한다. 설치만으로 공격 방어율, capability 전달의 MAS 합성, 실행 범위 보장을 검증한 것이 아니다.

## Progent

**현재 상태: 소스·최소 격리 설치 VERIFIED, 원본 정책 checker/ON-OFF 실행 및 논문 재현 NOT_RUN.**

- 런타임: `pyproject.toml`의 distribution 이름은 **secagent 0.1.0**, Python >=3.9. `third_party/progent/.venv`는 Python 3.10.12이며 25 distributions를 포함한다. 실제 설치 버전에는 pydantic 2.14.3, openai 3.51.0, anthropic 2.8.0, z3-solver 5.4.1.0이 있다. 원본 lockfile 기반 버전 고정이 아니라 설치 당시 해석된 버전이므로 인벤토리를 보존했다.
- 설치 명령: `python3 scripts/bootstrap_run.py --name defenses-progent-venv --cwd /home/cclab/controllable_agent/third_party/progent -- uv venv --python 3.10 .venv`, 이어 `... --name defenses-progent-install ... -- uv pip install --python .venv/bin/python -e .`. 두 JSON/로그 exit code **0**. 내부 AgentDojo, ASB 및 실제 서비스 adapter의 추가 의존성은 설치하지 않았다.
- 진입점: `agentdojo/run.sh`는 여러 suite/attack을 background로 시작하며 실제 LLM을 부르므로 실행하지 않았다. 단일 CLI는 `agentdojo/src/agentdojo/scripts/benchmark.py`. 다른 평가 경로는 `asb/scripts/agent_attack.py`, `real-world-agents/run.py` 및 MCP adapter다.
- Method·정책: `secagent/tool.py::generate_security_policy`는 사용자 query로 정책을 생성하고 `generate_update_security_policy`는 후속 결과에 따라 갱신한다. 정책 구조는 도구별 `(priority, effect, argument restrictions, fallback[, update])` 목록이며 `update_security_policy`/`sort_policy`가 적용한다. 생성 경로 `api_request`는 OpenAI/Anthropic/Vertex 모델 API를 호출할 수 있다. 미승인 호출은 하지 않았다.
- 집행 지점: `secagent/tool.py::check_tool_call` → `_check_tool_call` → `check_arg`가 JSON Schema, regex, callable 조건을 검사한다. `secure_tool_wrapper`는 signature로 인자를 binding하고 defaults를 채운 뒤 checker를 통과해야 원본 `tool(*args, **kwargs)`를 실행한다. `apply_secure_tool_wrapper`가 이 wrapper를 부착한다. `security_policy is None`이면 경고 후 반환하는 **비활성 경로가 코드에 존재**하나 이 세션에서 실행 관측하지 않았다.
- 실제 AgentDojo 부착점: `agentdojo/src/agentdojo/default_suites/v1/{banking,slack,travel,workspace}/task_suite.py`의 `TaskSuite` 생성에서 `make_function(apply_secure_tool_wrapper(tool))`를 사용한다. `SECAGENT_SUITE`, `SECAGENT_GENERATE`로 suite/생성 구성을 고른다. `agent_pipeline/basic_elements.py`는 initial policy 생성, `agent_pipeline/tool_execution.py::ToolsExecutor`는 실행 후 정책 갱신에 연결된다.
- 효과·스코어: wrapped 원본 도구 → 내부 `agentdojo/functions_runtime.py::FunctionsRuntime.run_function` 및 suite의 모의 환경 변경. `agentdojo/task_suite/task_suite.py`와 `agentdojo/benchmark.py`가 사용자 utility와 injection security 판정을 반환하고 logging이 대화를 남긴다. ASB/MCP 실제 효과 경로는 소스 감사 대상일 뿐 실행하지 않았다.
- 정형 정책 분석: `secagent/policy_analysis.py::security_policy_subset_check`는 Z3 제약으로 갱신 정책의 subset 여부를 검사한다. 이것만으로 모든 adapter/동시성/위임 경계에서 완전 중재를 주장할 수 없다.
- 준비 파일: `experiments/progent_policy_component.py`는 원본 `apply_secure_tool_wrapper`에 **in-memory outbox**를 붙여 동일 고정 수신자 치환을 정책 OFF/ON과 benign/attack 4조건으로 비교하도록 작성했다. 네트워크 connect를 차단하며 모델 호출은 하지 않는 구성이다. **실행 JSON·events·summary가 없으므로 NOT_RUN**. 이 파일의 기대 결과는 관측 결과가 아니다. 실행하더라도 원본 라이브러리 component check이지 LLM 공격·MAS·논문 재현이 아니다.

## DRIFT

**현재 상태: 소스 감사 VERIFIED/PARTIAL, 설치·실행·논문 재현 NOT_RUN.**

- 런타임: README는 Python 3.11과 `agentdojo==0.1.35`를 지정한다. `requirements.txt`도 AgentDojo 0.1.35 및 다수 pinned SDK/분석 라이브러리를 요구한다. CaMeL 환경의 AgentDojo 0.1.34와 공유하지 않았다. README의 API provider는 OpenAI/Google/OpenRouter다.
- 진입점: `pipeline_main.py::main` → `DRIFTLLM` → `AgentPipeline([InitQuery(), llm, DRIFTToolsExecutionLoop([ToolsExecutor(), llm])])`. 옵션은 `utils.py::get_args`, `--build_constraints`, `--injection_isolation`, `--dynamic_validation`, attack/suite/task 지정이다.
- Method·정책: `DRIFTLLM.py::initial_constraints_build` 등에서 초기 trajectory/checklist를 구성하고, `function_privilege_assignment`에서 Read/Write/Execute 권한을 LLM으로 분류한다. `injection_isolate`는 도구 결과에서 감지한 지시를 격리한다. `query`가 이 옵션 경로들을 연결한다. `prompts.py`가 지시문과 제약 생성 template을 포함한다.
- 집행 지점: `DRIFTLLM.query`의 `trajectory_constraint_validation`/`checklist_constraint_validation`이 제안된 `output['tool_calls']`를 점검하고 오류 경로를 반환한다. `alignment_judge`는 초기 사용자 의도와 실행 trajectory의 일치성을 모델로 판정한다. 반환된 tool calls가 다음 loop의 AgentDojo `ToolsExecutor`로 넘어간다. 따라서 모델 의존 semantic validation이며 OS 수준 reference monitor로 간주하지 않는다.
- 효과·스코어: AgentDojo `FunctionsRuntime`의 모의 도구/상태가 효과 sink다. `DRIFTTaskSuite.py::run_task_with_pipeline`에서 `_check_task_result`로 utility/security를 판정한다. `pipeline_main.py`는 conversations, tool_permission, initial_trajectory/checklist, utility/security, total_tokens, duration을 `runs/<model>/<suite>/...json`에 기록한다. 저장소에 이미 존재하는 `runs/`는 **이번 실행 증거에서 제외**했다.
- 모델 adapter: `client.py::{OpenAIModel,OpenRouterModel,GoogleModel}`의 `llm_run`/`agent_run`. full run의 실제 호출 상한/비용은 아직 산출하지 않았으며 API 실행은 승인 대기다.
- 미실행 이유: 별도 Python 3.11/AgentDojo 0.1.35 환경과 credential-free 검증 경로가 아직 준비되지 않았고, 후속 지시가 새 설치/실험을 중단했다. 실패한 설치로 기재하지 않는다.

## 독립 AgentDojo

**현재 상태: 소스 감사 VERIFIED/PARTIAL, 독립 환경 설치·실행·벤치마크 재현 NOT_RUN.**

- 현재 checkout의 `pyproject.toml`은 package 0.1.34, **Python >=3.11**이다. CaMeL 설치 환경의 PyPI AgentDojo 0.1.34와 이 checkout을 동일 아티팩트로 취급하지 않는다. `sequrity` 의존성 및 최신 코드 변경이 존재한다.
- 진입점: `src/agentdojo/scripts/benchmark.py`; suite/attack/defense/model을 선택하고 `src/agentdojo/benchmark.py::benchmark_suite_with_injections`, `run_task_with_injection_tasks` 등으로 실행한다.
- 실행·효과 경로: `src/agentdojo/agent_pipeline/tool_execution.py::{ToolsExecutor,ToolsExecutionLoop}` → `src/agentdojo/functions_runtime.py::FunctionsRuntime.run_function`. 실제 데이터와 모의 stateful tool은 `src/agentdojo/default_suites/`와 `src/agentdojo/default_suites/v1/tools/`에 있다. 모델 adapter는 `src/agentdojo/agent_pipeline/llms/{openai_llm,anthropic_llm,google_llm,local_llm}.py`다.
- 방어는 선택한 pipeline 구성에 종속한다. `agent_pipeline/agent_pipeline.py`, `pi_detector.py`, `planner.py` 및 basic elements를 검사해야 하며 benchmark 자체가 범용 authorization guarantee를 제공한다고 보지 않는다.
- scorer: `src/agentdojo/task_suite/task_suite.py::TaskSuite.run_task_with_pipeline`은 pre/post environment와 출력/호출 traces를 사용한다. `_check_user_task_utility`와 `_check_injection_task_security`는 각각 `utility[_from_traces]`, `security[_from_traces]`에 연결된다. 각 task 정의의 의미를 읽기 전 `security=True`를 일반적인 보안성으로 번역하면 안 된다. `src/agentdojo/logging.py` 및 benchmark 결과가 trace/score를 보존한다.
- 원본 offline 테스트 후보는 `tests/test_functions_runtime/`, `tests/test_ast_utils.py`; 현재 실행하지 않았다. `tests/test_agent_pipeline/`를 일괄 실행하기 전에 API mock 여부를 별도로 검토해야 한다.

## 다음 검증 절차 — 아직 실행하지 않음

후속 사용자 지시에 따라 아래는 handoff 명령이며 자동 실행하지 않았다.

1. 가장 작은 정책 비교: `python3 scripts/bootstrap_run.py --name defenses-progent-policy-v1 --timeout 60 -- third_party/progent/.venv/bin/python experiments/progent_policy_component.py --output-dir results/setup/bootstrap-20261114/progent-policy-v1`. 승인된 새 실험 세션에서 실제 exit code, 4개 event와 committed effect를 확인한다. 현재는 NOT_RUN.
2. CaMeL은 dev pytest 설치와 원본 offline tests 선택이 선행 조건이다. 원본 `uv.lock`/환경 diff를 보존한 뒤 `tests/test_pipeline_elements/test_agentdojo_function.py`와 interpreter tests를 검사·실행한다. 현재 `uv sync --frozen --no-dev`만 완료되어 테스트 실행 명령을 성공 상태로 제시하지 않는다.
3. DRIFT/standalone AgentDojo는 각자 Python 3.11 독립 환경으로 준비해야 한다. DRIFT pinned AgentDojo 0.1.35를 다른 환경에 강제 병합하지 않는다. full LLM defense ON/OFF는 비용·호출 상한과 단일 task/injection pair를 확정한 후 별도 승인이 필요하다.

모든 항목에서 `공격 입력 → 도구 호출 의도 → 모니터 판정 → committed effect → benign success`를 분리해야 한다. 이번 방어 artifact들에서 새 취약점, MAS 합성 보장 위반, 또는 원 논문 재현 성공은 관측되지 않았다.
