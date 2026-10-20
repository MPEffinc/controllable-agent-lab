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
