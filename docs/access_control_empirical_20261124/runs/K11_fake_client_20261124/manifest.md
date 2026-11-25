# K11 Multi-CaMeL: 공개 fake-client 통합 테스트

## 실행 전 고정한 검증 질문

- **검증 질문:** 공개 저자 artifact의 `MultiCaMeLPipeline`이 mock Sequrity 응답을 받아 `task`/`variables` 경로와 가상 서비스 `send_email` 효과를 연결하고, orchestrator 요청에 정책을 실어 보내는가?
- **원래 주장:** [논문 §IV](https://arxiv.org/html/2610.05640v1#S4)는 부모의 신뢰된 자연어 instruction과 도구 유래 데이터 `variables`를 분리하고, instruction channel 무결성을 enforcement한다고 주장한다. [artifact README](https://github.com/james-pete/multiagentdojo#tests)는 API 키 없는 fake client end-to-end 테스트를 제공한다.
- **예상 결과:** 공개 테스트 통과; `test_multi_camel_pipeline_end_to_end`가 `email_agent → get_variable → send_email`, 가상 inbox `sent` 변화, orchestrator request의 `security_policy` 필드를 확인한다.
- **반증 관찰:** 테스트 실패, 정책 필드 누락, 변수 획득 실패, 가상 sent 상태 미변화, 원본 저장소 변형.
- **최소 비용:** 로컬 CPU + PyPI 의존성 설치. 모델 API 호출 0, 예상 사용료 USD 0. 키 4종은 명시적으로 환경에서 제거.
- **완료 조건:** 한 번의 공개 테스트 실행 결과와 원시 로그·의존성/버전·시작/종료 시간을 기록. 실패하면 원인 2–3회 이내 분리.

이 테스트의 fake client는 정책 문자열을 전달받아 기록할 뿐 **실제 Sequrity 서버의 allow/deny 판정은 구현하지 않는다**. 정상 효과는 AgentDojo의 인메모리 inbox에 한정된다. 따라서 통과해도 논문의 공격 방어율, 실제 PEP, 외부 서비스 효과는 검증되지 않는다.

## 실행 정보

- 코드: `/home/cclab/controllable_agent/third_party/multiagentdojo`, 공식 artifact의 고정 HEAD `e71647382155dc6949d6ccf9a9d7ec7cf429b856`; 실행 전 `git status --short` 빈 결과.
- 환경: host Python 3.12.15, `uv 0.13.3`; uv가 실행 시 CPython 3.12.2를 내려받아 사용. 가상환경은 원본 저장소 밖 `docs/access_control_empirical_20261124/env/K11/venv`(129 MiB).
- 의존성: 원본 `uv.lock` SHA256 `2066f44517e140c85540b952c47695f03f1ad3ab2fb42f359f919a0c3d95a955`를 `--locked`로 적용. PyPI/uv Python 배포 다운로드가 있었다. 설치 63 + overlay 4 package; 설치 로그는 `raw.log`.
- 명령: `env -u OPENAI_API_KEY -u OPENROUTER_API_KEY -u SEQURITY_API_KEY -u SEQURITY_LLM_API_KEY UV_PROJECT_ENVIRONMENT=/home/cclab/controllable_agent/docs/access_control_empirical_20261124/env/K11/venv UV_NO_PROGRESS=1 uv run --locked --no-dev --extra camel --with pytest python -m pytest tests/test_multi_agent.py tests/test_camel.py -q`
- 출력: `raw.log`; 가상 서비스 상태는 테스트 내부 assertion으로 확인되므로 전후 전체 상태 snapshot은 없음 (`ASSERTED_IN_MEMORY_EFFECT`).

## 실제 결과 (2026-11-24 11:02 UTC)

- 명령 exit 0; `25 passed in 4.01s` (명령 wall 16.53초). 모델 API key 4종을 환경에서 제거했고, 테스트는 코드상 `ScriptedLLM`/`FakeSequrityClient` 사용. 유료 모델 호출이나 사용료 계측 대상이 없었으므로 **LLM 비용 USD 0**. 의존성 다운로드 네트워크는 사용했다.
- [`multi_agent.py:583`](/home/cclab/controllable_agent/third_party/multiagentdojo/src/agentdojo/agent_pipeline/multi_agent.py:583)에서 `tool "<agent>" { hard deny when not (task.producers is empty); result { @producers |= ... } }` 정책을 생성한다. [`multi_agent.py:645`](/home/cclab/controllable_agent/third_party/multiagentdojo/src/agentdojo/agent_pipeline/multi_agent.py:645)는 이를 orchestrator의 `SequrityLLM`에 연결한다. [`sequrity_llm.py:385`](/home/cclab/controllable_agent/third_party/multiagentdojo/src/agentdojo/agent_pipeline/llms/sequrity_llm.py:385)는 `security_policy`를 Sequrity 요청에 싣는다. 실질적 `hard deny` 판정은 이 adapter가 아니라 외부 Sequrity Control의 책임이다.
- [`multi_agent.py:655`](/home/cclab/controllable_agent/third_party/multiagentdojo/src/agentdojo/agent_pipeline/multi_agent.py:655)는 `variables`와 `get_variable`을 가진 sub-agent 도구를 만든다. [`test_camel.py:264`](/home/cclab/controllable_agent/third_party/multiagentdojo/tests/test_camel.py:264)의 scripted 정상 경로는 `email_agent → get_variable → send_email` 후 가상 `env_out.inbox.sent` 변화를 검사한다. 이는 실제 외부 email 송신이 아니다.
- `git status --short`는 실행 전후 빈 결과; 원저자 코드 및 lockfile 무변경.
- **닫힌 질문:** 공개 artifact의 정책 생성·전달과 정상 mock 경로 연결은 확인. **열린 질문:** Sequrity 서버가 tainted `task`를 실제로 거부하는지, 거부가 최종 서비스 effect를 막는지. 본 fake client는 서버 판정을 흉내 내지 않아 이 질문에 답하지 않는다.
