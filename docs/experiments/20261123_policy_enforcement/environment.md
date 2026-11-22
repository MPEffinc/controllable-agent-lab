# Phase 0 환경 인벤토리

확인일: 2026-11-22 (UTC). 아래는 현재 로컬 상태이며 이전 세션의 설정을 현재 실행 가능성으로 간주하지 않는다.

## 저장소와 보존 상태

| 항목 | 확인 결과 |
| --- | --- |
| 프로젝트 루트 | `/home/cclab/controllable_agent` 존재, `git rev-parse --show-toplevel`과 일치 |
| 시작 시 루트 HEAD | `b86812ced989ecd7be0dfea5f78058fd809ef101`, `exp/r3-delegation-lineage` |
| 원격 | `origin = git@github.com:MPEffinc/controllable-agent-lab.git` (fetch/push) |
| Phase 0 브랜치 | `exp/20261123-progent-enforcement-usecase` 신규 생성. 생성 전 로컬·원격에 같은 이름의 브랜치 없음 |
| 시작 시 Working Tree | 추적 파일 변경 없음. `docs/guided_reproduction_20261117/`의 21개 문서/manifest와 `scripts/progent_*` 9개가 미추적 |
| 별도 체크아웃·로그 | 루트 `.gitignore:15,18`이 각각 `third_party/`, `local/` 제외. 원본과 원시 로그는 이번 Commit 대상 아님 |

기존 미추적 파일을 이동·삭제·추적하거나 내용을 덮어쓰지 않았다. 현재 브랜치의 실제 HEAD와 Push 결과는 단계 종료 보고에서 별도 기록한다.

## 원본과 Python

| 항목 | 확인 결과 |
| --- | --- |
| 원본 | `third_party/progent/`는 별도 clean Git checkout. HEAD `b02783b896d4bf01a2adf24738015e258db8d35b`, remote `https://github.com/sunblaze-ucb/progent.git` |
| Python | `local/guided-reproduction-20261117/envs/progent-agentdojo/bin/python` 존재, 3.10.12 |
| 설치 메타데이터 | `secagent 0.1.0`, `agentdojo 0.1.29`, `openai 3.52.0`, `httpx 0.28.1`, `python-dotenv 1.2.4` |
| 설치 위치 | `secagent`, `agentdojo` import가 위 원본 checkout의 editable 소스를 사용 |
| 패키지 점검 방식 | 이 환경에는 `pip` 모듈이 없으므로 `importlib.metadata`로 버전 확인. 설치·업데이트는 수행하지 않음 |

이전 설치 기록의 `openai 3.51.0` 요구와 현재 설치된 `3.52.0`은 다르다. 이 차이가 과거 결과에 영향을 주었는지는 검증하지 않았다. 원본 의존성 선언은 `third_party/progent/pyproject.toml`과 `third_party/progent/agentdojo/pyproject.toml`에 있다.

## LLM 및 실행 경로

원본 정책 모델 기본값은 `secagent/tool.py:41`의 `gpt-4o-2024-08-06`; `SECAGENT_POLICY_MODEL`로 변경할 수 있다. 원본 정책 생성 `api_request`는 모델 유형에 따라 Anthropic, Vertex AI 또는 OpenAI 호환 Chat Completions client를 만든다(`secagent/tool.py:167-240`). 업무 Agent 모델은 AgentDojo 원본 CLI의 `--model`로 선택한다. **정책 LLM과 업무 Agent LLM은 역할이 다르다.**

현재 셸에는 `LLM_API_KEY`, `OPENAI_API_KEY`, `LLM_BASE_URL`, `OPENAI_BASE_URL`, `LLM_MODEL`, `SECAGENT_POLICY_MODEL`, `PROGENT_AGENT_MODEL`이 설정되어 있지 않다(값은 읽거나 기록하지 않고 존재 여부만 확인). 다른 터미널이나 비밀 파일의 상태는 확인하지 않았다. API 접속, 모델 가용성, 비용은 이번 단계에서 확인하지 않았다.

| 기존 로컬 실행기 | 확인한 성격 |
| --- | --- |
| `scripts/progent_live_visible.py` | Luna용 외부 client/프롬프트/관찰 어댑터; 원본 모델 선택 경로와 동일하지 않음 |
| `scripts/progent_demo.py`, `progent_demo.sh`, `progent_demo_session.py` | 명시적 프로필·모델·endpoint를 쓰는 별도 대화형 실행기. 실행 전 `RUN` 입력 경로가 있음 |
| `scripts/progent_demo_terminal.py` | 저장된 로그의 `replay` 조회 가능; 새 Agent 실행과 구분 |
| `scripts/progent_guided_effect.py` | ground-truth Tool Call 재생 경로; 자율 Agent 실행과 구분 |

로컬 실행기들은 루트 Git에서 미추적이다. 과거 어댑터의 프롬프트/client/출력 방식이 원본 Progent의 기본 동작이라고 설명하지 않는다.

## 실제 실행한 비파괴적 확인

`pwd`, `git rev-parse --show-toplevel`, `git status --porcelain=v1 -uall`, `git remote -v`, 원본 checkout의 `git rev-parse HEAD`와 `git status`, Python `-c`의 `importlib.metadata`와 환경변수 존재 여부 검사, 소스·기존 로그 읽기만 수행했다. 새 benchmark, 정책 LLM, 업무 Agent, Tool Backend는 실행하지 않았다.
