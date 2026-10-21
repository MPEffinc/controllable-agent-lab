# 진행 기록
단계마다 아래 항목을 채운다.

## S0 환경 세팅
- 날짜: 2026-10-20
- 한 일:
  - 저장소 뼈대 생성(CLAUDE.md, .gitignore, .claude/settings.json, .env.example, README.md, docs/·lab/·runs/·scripts/ 의 .gitkeep). 작성자는 저장소 로컬 설정만 사용했다(--global 미사용).
  - 도구 설치(모두 ~/.local 아래): uv 0.13.3(pip --user), Python 3.12.15(uv python install), helm v4.3.1(공식 tarball, sha256 검증 일치). kind v0.33.0 은 이전 단계에서 설치했고 kubectl v1.30.14 는 시스템 것을 쓴다.
  - ./.venv(Python 3.12.15)에 openai 3.35.1, python-dotenv 1.2.4 설치. lab/requirements.txt 에 15개 패키지 버전 고정.
  - ~/.config/controllable_agent/llm.env 생성(폴더 700, 파일 600). 키는 이전 실습의 키 파일에서 셸 안에서만 옮겼고 출력하지 않았다.
  - 모델 후보 2개(gpt-6-luna, gpt-6-astra)를 1회씩 호출해 둘 다 200. LLM_MODEL 은 gpt-6-luna 로 기록.
  - lab/s00_check_env.py 작성·실행: 파이썬 3.12 OK, openai 임포트 OK, llm.env 있음(권한 600), LLM 호출 성공(gpt-6-luna). 출력에 키 값 없음.
  - 안전장치(pre-commit)는 이번 단계에서 만들지 않았다(F 생략). 대신 커밋 전에 스테이징 내용에서 키 형식 문자열을 검색해 0건임을 확인했다.
- 관찰한 것(환경 스냅샷, 커밋 시점):
  - Docker: 컨테이너·이미지·볼륨 0개, 네트워크는 bridge/host/none 뿐, system df 전부 0B. kind 클러스터 없음.
  - kubectl: KUBECONFIG 미설정, ~/.kube/config 없음, 컨텍스트 목록 비어 있음.
  - 자원: 메모리 15Gi 중 4.0Gi 사용(가용 11Gi), 디스크 / 192G 중 69G 사용(남은 114G, 38%).
  - 리슨 포트(내 사용자): VS Code 서버 관련 프로세스(포트 5개)뿐이고 연구 잔여 리스너 없음.
  - 도구 위치: uv·kind·helm 은 ~/.local/bin, kubectl 은 /usr/bin/kubectl.
  - s00_check_env.py 는 python-dotenv 의 load_dotenv 로 llm.env 를 프로세스 환경 변수로 읽은 뒤 os.environ 으로만 값을 쓴다. CLAUDE.md 의 "환경 변수로만 받는다" 규약과 어긋나지 않는지 S1 전에 확인하면 좋다.
  - 작업 중 CLAUDE.md 가 디스크에서 이 작업의 지시문과 다른 내용(푸시 매번 승인, 내부 IP 등 마스킹)으로 바뀌어 있었다. 지시문 기준으로 교체했고 이전 버전은 저장소 밖에 백업해 두었다. 어느 쪽이 맞는지는 사용자가 확정해야 한다.
  - 저장소는 공개 상태이며, 이 단계의 커밋은 모두 그대로 공개된다.
- 막힌 곳: 없음. 건너뛴 항목도 없음(F 는 지시에 따라 생략).
- 다음 할 일(S1 시작 조건):
  - 사용자가 S1 진행을 지시한다. S1 시작 전에 5줄 이내 설명(만들 것, 이유, 관련 개념 번호)을 먼저 한다.
  - 필요한 환경은 모두 갖춰졌다: source .venv/bin/activate, llm.env 로 모델 호출 가능, 클러스터는 불필요.
  - CLAUDE.md 내용(푸시 승인 규칙, 로그 마스킹 규칙)을 사용자가 확정한 뒤 시작하는 것이 안전하다.
- 커밋: f18299e [S0] 저장소 뼈대와 환경 점검 스크립트 (태그 s0-done). 이 기록은 바로 다음 커밋 [S0] 진행 기록 에 들어간다.

## S0 후속: 비용 규약과 README 현재 상태
- 날짜: 2026-10-21
- 한 일:
  - CLAUDE.md 에 '## 비용' 절 추가(모델은 LLM_MODEL 하나, call_llm() 단일 경로, 토큰 기록·상한, 새 실험은 1회 시험 후 추정).
  - CLAUDE.md '기록과 커밋' 절에 README '## 현재 상태' 갱신 규칙 1줄 추가.
  - README.md 에 '## 현재 상태' 절 추가(S0 완료, 커밋 f18299e·47a8418).
- 결정: 모델은 gpt-6-luna(LLM_MODEL) 하나만 쓴다. gpt-6-astra 시험 지시는 취소됐다.
- 도구 호출 지원 시험(gpt-6-luna, 임시 스크립트로 방식당 1회, 가짜 도구 get_account_status):
  - s00_check_env.py 의 방식: chat.completions.create(messages, max_completion_tokens=64), tools 없음.
  - b chat.completions + tools: HTTP 400 (BadRequestError). 이때는 응답 본문을 읽지 않아 원인을 몰랐다(S1 에서 재시험해 확인, 아래 S1 절). 토큰 사용량 없음.
  - c responses + tools: HTTP 200, 도구 호출 요청 get_account_status({"account_id":"acct-7"}) 수신. 입력 68 / 출력 22 토큰.
  - d 텍스트 규약: c 가 성공해서 시험하지 않았다.
  - 결론: S1 코드는 responses 형식 하나로 만든다. 시험 호출 토큰(90)은 call_llm() 이 없던 때라 runs/usage.jsonl 에 없다.
- 다음 할 일: S1 을 튜터 모드로 시작한다(lab/common.py 의 call_llm() 부터 한 조각씩).

## S1 에이전트 루프 (진행 중)
- 날짜: 2026-10-21
- 한 일:
  - lab/common.py 작성: call_llm(input_items, tools, tag) 하나만 모델을 부른다. responses 형식 호출 → {"text","tool_calls":[{call_id,name,arguments}],"output_items","usage"} 로 정규화. 도구 정의는 우리 형식({name,description,parameters})으로 받아 call_llm 안에서 responses 형식으로 바꾼다.
  - 비용 장치: 호출마다 runs/usage.jsonl 에 입력·출력 토큰 기록, LAB_MAX_OUTPUT_TOKENS(기본 800) 강제, 누적이 LAB_MAX_TOKENS(기본 300000) 이상이면 호출 전에 TokenBudgetExceeded. 자동 재시도 없음(SDK max_retries=0).
  - non-2xx 처리: record_http_error() 가 상태 코드와 본문만 runs/llm_errors.jsonl 에 기록하고 LLMHTTPError 를 낸다(헤더 미저장, 본문 속 키 값은 *** 로 치환).
  - 설계 결정: 대화 이력은 항목 목록으로 직접 관리하고 매 호출에 전체를 보낸다(previous_response_id 미사용). 시스템 프롬프트도 instructions 가 아니라 입력 항목으로 넣어 이력 JSON 에 "모델이 본 입력 전체"가 남게 한다. arguments 는 모델이 낸 JSON 문자열 그대로 돌려주고 파싱은 루프가 한다.
- 관찰한 것:
  - call_llm() 1회 확인(tag s1-probe): 도구 호출 1개 수신, 입력 68 / 출력 22 토큰, usage.jsonl 에 한 줄 기록. output_items 에는 id("fc_...")와 status 가 붙어 있다.
  - chat.completions+tools 재시험(tag s1-retest-b, 이전 400 과 동일 요청) 오류 본문: "Function tools with reasoning_effort are not supported for gpt-6-luna in /v1/chat/completions. To use function tools, use /v1/responses or set reasoning_effort to 'none'." (param: reasoning_effort, type: invalid_request_error). 즉 chat 형식 자체가 아니라 추론(reasoning) 설정이 켜진 상태의 chat+tools 조합이 거부된 것이다.
  - 추측(미확인): chat.completions 에서 reasoning_effort='none' 을 주면 tools 가 통과할 것이다. S5(AgentDojo 연결)에서 chat 형식이 필요하면 이 값으로 1회 시험한다. responses 쪽 기본 추론이 토큰을 얼마나 쓰는지는 아직 모른다(간단한 호출은 출력 22).
- 막힌 곳: 없음.
- 다음 할 일: 에이전트 루프 조각(입력 항목 도우미, 도구 1개, 루프), 이력 JSON 저장, 프롬프트 주입 관찰 실험 2개.
