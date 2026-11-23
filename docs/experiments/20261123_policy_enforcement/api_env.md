# Progent Live API 키 저장 및 값 비노출 확인

2026-11-23 UTC. Live 실행기는 프로젝트의 `local/progent-vm/.env`를 이미 읽도록 구현되어 있다. 이 경로는 저장소 `.gitignore`의 `local/` 규칙으로 Git에서 제외된다. **현재 파일이 존재하는지만 확인했으며 내용은 열거나 변경하지 않았다.**

본인 터미널에서 편집기로 파일을 열어 아래 형식으로 키를 입력한다. 키를 셸 명령 인자로 쓰거나 채팅에 붙여 넣지 않는다.

```bash
cd /home/cclab/controllable_agent
mkdir -p local/progent-vm
umask 077
nano local/progent-vm/.env
chmod 600 local/progent-vm/.env
```

파일 내용 예시이며 `YOUR_KEY_HERE`는 실제 키로 교체한다.

```dotenv
OPENAI_API_KEY=YOUR_KEY_HERE
# OPENAI_BASE_URL=https://api.openai.com/v1
```

저장 후 **값을 표시하지 않고** 설정 여부만 확인한다.

```bash
bash scripts/progent_vm.sh check-env
```

`[API KEY] PRESENT`는 비어 있지 않은 키가 프로세스 환경이나 지원되는 프로젝트 dotenv 파일에 있다는 뜻이다. `[SOURCE]`는 값이 아닌 출처 경로만, `[FILE MODE]`는 권한 숫자만 출력한다. `check-env`는 API 요청을 하지 않는다. 따라서 **키의 유효성, 요금 계정, `gpt-6-luna` 모델 접근 가능 여부는 확인하지 않는다.** 실제 Live 실행은 인증정보를 메모리에서 읽어 API 요청에 사용하며 비용이 발생할 수 있다. Codex가 원시 키 값을 보거나 출력할 필요는 없다. 다만 비어 있지 않은지 판단하려면 검사 프로그램이 파일을 내부적으로 읽는 과정은 필요하다.

Live 실행 예시는 사용자 요청을 확정한 뒤 `bash scripts/progent_vm.sh system-live --backend kata --case A` 또는 `bash scripts/progent_vm.sh agentdojo --backend kata --case A`다. 이 두 명령은 **실제 유료 API 요청**을 할 수 있으므로 `check-env`와 구분한다. 원시 요청·응답 로그는 무시되는 `local/progent-vm/live/` 또는 `local/progent-vm/agentdojo/`에 저장되며 검토 없이 Git에 넣지 않는다.
