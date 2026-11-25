# ControlValve · Multi-CaMeL · PAuth 조사

확인일: 2026-11-17 (Asia/Seoul). 이번 작업은 원문·소스 조사다. 설치, LLM 호출, 정책 엔진 실행, benchmark 실행은 하지 않았다. 기존 연구 기록과 결과를 변경하지 않았다.

## 확보 상태와 고정 버전

| 연구 | 원문 고정 | 원본 코드 판정 | 실행환경 상태 |
|---|---|---|---|
| ControlValve | [arXiv:2510.17276v2](https://arxiv.org/html/2510.17276v2), 2026-03-05 | 공식 runnable repository **미확인** | 환경·의존성 lock·CLI 미확인, NOT_RUN |
| Multi-CaMeL | [arXiv:2610.05640v1](https://arxiv.org/html/2610.05640v1), 2026-10-05 | [james-pete/multiagentdojo](https://github.com/james-pete/multiagentdojo), SHA `e71647382155dc6949d6ccf9a9d7ec7cf429b856`, 원문 코드 수정 없음 | 확보 완료, 이번 담당 조사에서 설치·실행 안 함 |
| PAuth | [arXiv:2603.17170v2](https://arxiv.org/html/2603.17170v2), 2026-08-25 | 공식 runnable repository **미확인** | 환경·의존성 lock·CLI 미확인, NOT_RUN |

MultiAgentDojo 출처 근거는 README의 정확한 논문 artifact 선언과 commit author의 `jamespetersgill@gmail.com`이 논문 correspondence와 일치한다는 점이다. **저자 연관 artifact 확인**, 논문→저장소 역방향 URL은 미확인으로 구분한다. README·저자 metadata를 넘어 외부 Sequrity 서버의 배포 버전까지 검증한 것은 아니다.

ControlValve는 [저자 논문 페이지](https://rishijha.com/pubs/breaking_and_fixing.html)의 `[code]`가 실 URL로 연결되지 않았다. PAuth는 [제1저자 최신 홈페이지](https://homes.cs.washington.edu/~reshabh/)에 arXiv만 연결된다. GitHub 저장소 검색 `ControlValve`, `PAuth agent`, 정확한 논문 제목과 웹 검색을 확인했으나 인증 가능한 원본 다운로드를 확보하지 못했다. 공개 코드가 없다고 확정하지 않는다. 동명 프로젝트나 저자의 별도 연구 AC4A로 대체하지 않는다.

## ControlValve: 원문에서 먼저 배울 내용

| 연구 질문 | 원문 연결과 확인 내용 |
|---|---|
| Problem / Threat | [§2](https://arxiv.org/html/2510.17276v2#S2): 공격자가 외부 콘텐츠 한 조각을 제어하고, benign agent의 오류 보고를 통해 orchestrator 호출 순서를 오염시킨다. |
| Policy representation / generation | [§4](https://arxiv.org/html/2510.17276v2#S4): LLM 생성 context-free grammar와 간선별 자연어 규칙. 비신뢰 입력을 읽기 전에 생성한다. |
| Enforcement | §4: Lark parser의 trace 검사와 LLM의 간선 규칙 검사 후 permit/reject/re-plan. black-box agent 내부 tool call은 관찰하지 않는다. |
| Correctness | §4, [부록 C–F](https://arxiv.org/html/2510.17276v2#A3): parse retry, 최대 3회 re-plan; 과잉/과소 허용 그래프·잘못된 규칙은 남는 위험이다. |
| Evaluation | [§5–6](https://arxiv.org/html/2510.17276v2#S5): AutoGen Magentic-One, o4-mini orchestrator/GPT-4o subagents; CFH-Hard 및 수정한 AgentDojo Slack. |
| Limitations | §4: LLM 정책·judge 정확성, CFG 내부 공격, overhead; 내부 tool effect 전부를 직접 검사하는 보장이 아니다. |

원본 정책은 [부록 L](https://arxiv.org/html/2510.17276v2#A12)의 파일→차트 작업에서 확인한다. 아래는 원문 grammar의 짧은 발췌이며 구현 실행 결과가 아니다.

```lark
start: call*
call: "FileSurfer"
    | "Coder" ["Executor"]
```

재현 차단 요소: 실제 생성·집행 함수, 정책 파일, lock, evaluation command를 찾지 못했다. 현재는 위 절과 부록을 읽는 실습만 가능하다. Lark만 따로 실행하거나 Magentic-One을 새로 구성해도 **ControlValve 원본 재현이 되지 않는다**.

## Multi-CaMeL: 확보한 원본 코드의 실행 경로

| 연구 질문 | 원문 연결 |
|---|---|
| Problem / Threat | [§III-A](https://arxiv.org/html/2610.05640v1#S3.SS1): tool-derived 내용이 child의 사용자 명령으로 승격되는 boundary laundering. |
| Policy / generation | [§IV-A–B](https://arxiv.org/html/2610.05640v1#S4): trusted instruction과 opaque variables 분리, provenance/capability 유지. |
| Enforcement | §IV-B: instruction-channel integrity를 런타임에 강제. |
| Correctness / limits | [§IV-C·VI](https://arxiv.org/html/2610.05640v1#S6): unique-parent tree 가정, 기존 branch steering·일부 implicit dependency·retry leak은 별도 문제. |
| Evaluation | [§V](https://arxiv.org/html/2610.05640v1#S5): AssetOpsBench, MultiAgentDojo; 평가의 사용자 security policy는 trivial. |

코드에서 `message`에 대응하는 인자 이름은 `task`다. 아래 경로는 모두 고정 SHA의 `third_party/multiagentdojo/` 기준이다.

| 역할 | 실제 파일·함수 |
|---|---|
| 도구 분할 | `src/agentdojo/agent_pipeline/multi_agent.py::SUITE_PARTITIONS` |
| 정책 생성 | 같은 파일:583 `_multicamel_orchestrator_policy(specs)` — 정해진 template를 sub-agent별로 만든다. LLM이 이 SQRT 규칙을 발명하는 방식이 아니다. |
| 정책 부착 | 같은 파일:643 `MultiCaMeLPipeline._orchestrator_llm` → `SequrityLLM.with_security_policy` |
| 별도 data channel | 같은 파일:647 `_make_subagent_tool` → `run_subagent(task, variables, env)` → `get_variable` |
| 외부 집행 요청 | `src/agentdojo/agent_pipeline/llms/sequrity_llm.py:361 SequrityLLM.query` → `_sequrity_chat_request` → `client.control.chat.create`; `security_policy`를 Sequrity에 전송 |
| LLM 설정 | 같은 파일:54 `load_sequrity_headers`: single-step planning, `max_pllm_steps=1`, 실패 retry 제한, `force_to_cache` |
| 평가 entry | `src/agentdojo/scripts/benchmark.py::main` → `benchmark_suite` → benign/attack 평가 |
| effect / utility | `src/agentdojo/default_suites/v1/banking/user_tasks.py::UserTask0.utility`: 실제 모의 은행 transaction의 수취인·금액을 확인 |
| 원본 무API 테스트 | `tests/test_camel.py::test_multi_camel_pipeline_end_to_end`, `test_orchestrator_policy_mentions_every_agent`; `tests/test_multi_agent.py` |

생성 정책 예시(원본 함수의 template에서 `email_agent`로 치환한 결과):

```text
tool "email_agent" {
    hard deny when not (task.producers is empty);
    result { @producers |= {"email_agent"}; }
}
```

`task`가 앞선 tool output에 의존하면 child 호출 전에 거부하도록 요청한다. `variables`는 이 조건의 대상이 아니므로 데이터를 그쪽으로 넘긴다. 로컬 코드는 `Any` 값을 건네고 Sequrity API에 집행을 맡긴다. 공개 Python adapter를 읽은 사실만으로 외부 interpreter의 provenance/capability 보존을 검증할 수 없다. fake client 테스트는 정책 문자열 전송과 protocol 및 모의 effect를 확인하며, 실제 SQRT 엔진의 공격 차단을 시험하지 않는다.

필수 의존성: README는 Python≥3.11(기본 AgentDojo metadata는 ≥3.10), uv, `camel` extra의 `sequrity>=0.4.2`. 원본 `uv.lock` 존재. openai/pydantic/anthropic 등 기본 dependencies와 dev pytest를 사용한다. 실제 모델 실습에는 `SEQURITY_API_KEY`, upstream key(`SEQURITY_LLM_API_KEY` 또는 `OPENROUTER_API_KEY`), provider와 `PLLM,QLLM` 모델 쌍이 필요하다. Docker/GPU가 이 API 경로의 필수 조건으로 명시되지는 않는다. 서버 가용성·가격·SDK/서버 버전은 후속 확인이 필요하다.

아래는 **향후 명령이며 이번 조사에서 미실행**이다. 먼저 설치를 격리하고 원본 lock과 맞는지 확인한다. `uv sync --frozen --dev --extra camel`은 잠금파일을 수정하지 않는 준비 명령의 제안이다. README 자체의 명령에는 `--frozen`이 없다.

```bash
cd /home/cclab/controllable_agent/third_party/multiagentdojo
UV_PROJECT_ENVIRONMENT=/home/cclab/controllable_agent/local/guided-reproduction-20261117/envs/multicamel \
  uv sync --frozen --dev --extra camel
PYTHONDONTWRITEBYTECODE=1 /home/cclab/controllable_agent/local/guided-reproduction-20261117/envs/multicamel/bin/python -m pytest tests/test_camel.py::test_multi_camel_pipeline_end_to_end -q -p no:cacheprovider
```

관찰 지점은 `email_agent(task, variables)` → `get_variable` → `send_email` 순서 및 `env_out.inbox.sent`다. 새 로그는 `local/guided-reproduction-20261117/runs/multicamel/<새 실행ID>/`에 보관한다. 이 명령은 fake-client protocol 학습이다. 실제 Allow/Deny는 승인 후 한 작업으로 분리한다.

```bash
# 유료 API 사용 승인 및 새 출력 경로 준비 후에만 실행
/home/cclab/controllable_agent/local/guided-reproduction-20261117/envs/multicamel/bin/python -m agentdojo.scripts.benchmark \
  --multi-camel --camel-model openai/gpt-4.1,openai/gpt-4.1 \
  -s banking -ut user_task_0 \
  --logdir /home/cclab/controllable_agent/local/guided-reproduction-20261117/runs/multicamel/<새 실행ID>
```

banking `user_task_0`은 파일 도구와 송금 도구를 서로 다른 sub-agent에서 사용하므로 경계 데이터 전달을 볼 수 있다. 한 번의 benign 실행으로 paper ASR를 재현했다고 할 수 없다. 공격은 task/injection 한 쌍과 실제 `--attack` registry를 먼저 읽은 다음 선택한다. README 공격 예시는 `<attack_used_in_paper>` placeholder이므로 그대로 실행할 수 없다. 출력의 `Average security`는 injection 목표 성공률, 즉 ASR다. repo에 들어 있는 과거 `runs/`는 이번 실행 증거로 사용하지 않는다. **AssetOpsBench 원본 평가 entry는 이 저장소에서 미확인**이다.

## PAuth: 버전과 Deny 의미부터 구분

v1 제목은 “PAuth — Precise Task-Scoped Authorization For Agents”이고, 현재 고정한 v2 제목은 **“Beyond OAuth: Task-Scoped Authorization for AI Agents via Natural Language Slices”**다. v1 결과와 섞지 않는다.

| 연구 질문 | v2 원문 연결과 확인 내용 |
|---|---|
| Problem / Threat | [§III-A](https://arxiv.org/html/2603.17170v2#S3.SS1): agent는 악성일 수 있고 서버·사용자 task의 진위·통신 경계를 신뢰한다. |
| Policy | [§III-C–D](https://arxiv.org/html/2603.17170v2#S3.SS3): NL slice(operand symbolic expression+guard), 서명한 envelope provenance. |
| Generation | [§IV-B](https://arxiv.org/html/2603.17170v2#S4.SS2): NL→제한 Python→AST dependency slice→typed rules. 뒤 두 단계는 결정론적이다. |
| Enforcement | [§IV-C](https://arxiv.org/html/2603.17170v2#S4.SS3): MCP middleware가 tool 전에 서명·guard·operand를 검증한다. |
| Correctness | §IV-B, V-C: grammar 오류 retry 후 empty/default-deny, NonDet는 명시 동의 유발. 번역 의미의 정확성은 형식 검증되지 않았다. |
| Evaluation | [§V](https://arxiv.org/html/2603.17170v2#S5): AuthBench 100 tasks, off-task 634 calls, AgentDojo/OpenClaw, 기본 GPT-4.1. |
| Limitations | [§VI](https://arxiv.org/html/2603.17170v2#S6): task 해석, trusted UI/서버, 참여하지 않은 서버; 서버 고유 접근 통제를 대체하지 않는다. |

정책 예시는 [§V-F banking case](https://arxiv.org/html/2603.17170v2#S5.SS6)의 “이전 거래에서 확인한 sender에게 정확히 10을 환불” slice다. 수취인만 agent 임의 값으로 바꾸면 expected operand와 불일치한다. 이는 원문 예시이며 runnable policy 파일이 아니다.

**§V의 block/reject/deny는 사용자 permission dialog를 띄운다는 뜻이다.** 영구 hard-deny와 다르다. 원문 표 III의 original tasks 71/100 대 refined tasks 100/100은 개입 없는 인가이며 off-task 634건은 모두 dialog를 유발했다. 잘못된 LLM 규칙도 의도 밖 호출과 우연히 일치할 수 있음을 원문 V-C가 논의한다. default-deny가 의미적으로 잘못된 allow 규칙을 불가능하게 만드는 것은 아니다.

원본 함수·정책 파일·lock·evaluation CLI·MCP demo 배포법은 미확인이다. 알고리즘 1, 부록 BNF와 Python 같은 코드가 있어도 설치 가능한 원본 구현을 확보했다는 뜻은 아니다. 현재 학습은 원문 slice 분석까지이고, 원본 artifact를 찾기 전에는 재구현으로 논문 재현을 대체하지 않는다.

## 남은 확보 작업

1. ControlValve/PAuth의 공식 artifact URL과 해당 paper-version 대응 commit을 저자·공식 metadata에서 확인한다. 연락 발송은 하지 않았다.
2. MultiAgentDojo 독립 환경의 원본 lock 해석·설치 호환성 확인과 Sequrity 서비스 버전 기록이 필요하다.
3. Multi-CaMeL 원문의 capability 보존과 공개 artifact/API가 제공하는 구체적 metadata 경계를 실습에서 확인한다.
4. 세 논문을 학습 목록에 유지한다. 당장 실행이 가능한 연구와 artifact 확보 대기 연구를 구분하며 대체하지 않는다.

원문 HTML 다운로드 상태와 SHA256은 `local/guided-reproduction-20261117/missing-artifacts/sources.json`에 기록한다. 다운로드 실패 시 실패 상태가 남는다. 이는 출처 확보 기록이며 실행 결과가 아니다.
