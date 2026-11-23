# 다음 세션 인계

## 고정한 사실

- 루트 `origin`: `git@github.com:MPEffinc/controllable-agent-lab.git`. Phase 0 전용 브랜치 `exp/20261123-progent-enforcement-usecase`를 만들었다. 시작 HEAD는 `b86812ced989ecd7be0dfea5f78058fd809ef101`.
- 원본은 별도 clean checkout `third_party/progent/`의 `b02783b896d4bf01a2adf24738015e258db8d35b`; 루트 Git에서는 무시된다. 기존 미추적 연구 문서·스크립트와 `local/` 로그를 보존한다.
- 원본 정책 생성 `generate_security_policy`, 갱신 `generate_update_security_policy`, 검사 `check_tool_call`, 집행 `secure_tool_wrapper`/`apply_secure_tool_wrapper`의 구현 위치와 관계는 [source_audit.md](source_audit.md)에 있다.
- 과거 Banking `6heKyOjj`의 모의 악성 송금 **성공**과 `kgeF5az4`의 송금 **거부**는 서로 다른 victim 실행이다. [prior_runs.md](prior_runs.md)의 실행 ID와 초기 정책을 먼저 대조한다.
- ActPlane은 2026년 arXiv 프리프린트로, OS 경계 대조 연구다. 이 프로젝트에서 실행하지 않았다.

## 다음에 결정할 사항

Phase 0 보고를 연구자가 검토한 뒤 Phase 1의 Mock Backend 상태 표현, VM ID·행동 이름, 수동 정책 예시와 기록 형식을 확정한다. 기본안은 외부 시스템에 연결되지 않는 `vm_action(vm_id, action)` 하나다. 수동 관리자 정책과 LLM 생성 정책을 별도 실험으로 남기고, 원본이 제공하지 않는 안전한 결합 기능을 원본 기능으로 소개하지 않는다.

Phase 1 이후에는 각 실행 ID마다 정책·Agent 제안/직접 Harness 입력·원본 판정·Backend 호출 수·상태 차이·평가 가능성을 기록한다. Phase 3 유료 API 실행은 모델, 제공자, 예상 호출 범위를 먼저 제시하고 사용자 승인을 받은 뒤 연구자가 직접 터미널에서 수행한다. Phase 4 SSH/실제 VM은 선택 단계이며 이 환경에서 허가·검증되지 않았다.

## 2026-11-22 자율 실험 후속 상태

이전 문단은 Phase 0 시점의 계획이다. 이후 사용자가 소규모 유료 호출을 승인했으나 **현재 프로세스에는 API 인증 환경변수가 없어** 새 Luna 호출은 0회다. Mock Phase 2 10건과 실제 Docker Stage C 6건의 결과는 각각 `phase2.md`, `docker_results.md`에 있다. Docker 실험 리소스는 모두 정리했고 기존 SREGym 컨테이너 4개는 그대로 실행 중이다. Kata는 `kata_results.md`의 실패 조건으로 미실행이다.

새 CLI는 `bash scripts/progent_vm.sh system-live --backend mock|docker --case A|B|C|D|E`다. 인증정보가 사용자 터미널에 설정되면 이 명령이 추가 확인 프롬프트 없이 API를 호출한다. `local/progent-vm/luna_budget.json`은 30요청·추정 USD 2 상한 기록으로, 이 파일과 `local/progent-vm/live/`의 원시 요청/응답을 Git에 넣지 않는다. 다음 세션은 새 Live 결과가 실제 존재하는지 먼저 확인하고, 모델 접근·정책 출력·Agent Tool Call·독립 상태를 Run ID별로 대조해야 한다. 기존 두 GPT-4o Live 기록은 보존하며 새 Luna 결과로 혼합하지 않는다.

## 2026-11-22 후속 End-to-End 시도 — 위 이전 계획을 대체하는 최신 상태

사용자는 프로젝트 범위 API 설정 탐색과 소규모 Luna 호출을 추가 승인했다. 현재 프로세스, 프로젝트 `.env*`/`local` 설정 파일, 사용자 셸 초기화 파일에서 **키 이름의 존재 여부만** 확인했으나 실키를 찾지 못했다. `sudo -n -v/-l`은 비밀번호 필요로 exit 1. 따라서 Luna API, 정책 자동 생성, Agent Tool Call, Luna→Docker/AgentDojo/Kata 실행은 모두 **BLOCKED**이며 0 API 요청이다. 이전 문단의 30회 상한은 구버전 정보다. 현재 `scripts/progent_system_live.py`는 파일 잠금이 있는 전역 **60요청/추정 USD 2** 상한이다.

독립 Kata 4.4.0 Runtime/Shim/Guest 바이너리를 공식 릴리스에서 다운로드해 SHA-256 검증 후 사용자 영역에 설치했다. 별도 containerd와 Kata Shim이 기동됐으나 Guest는 host cgroup 권한 오류로 부팅되지 않았다. RootlessKit은 `newuidmap` 부재로 실패했고 sudo 인증도 없다. `kata_installation.md`와 `kata_runtime_results.md`의 명령·오류를 참조한다. 이 설치를 VM 기동 성공이라고 소개하면 안 된다.

AgentDojo Suite를 Mock 및 Docker Controller에 연결했다. 최초 두 오프라인 실행은 `make_function`의 필수 인자 스키마가 비어 `TypeError`가 났고, `:param resource_id:` 문서화로 수정했다. 이후 GroundTruth 직접 호출 Mock A/B, Docker A/B가 모두 Utility=True; Docker B는 독립 inspect에서 running→exited였다. 새 `bash scripts/progent_vm.sh agentdojo --backend docker --case A --offline-ground-truth`는 **LLM 없는 진단**이다. `--offline-ground-truth` 없이 실행하면 Luna 기반 원본 AgentDojo Pipeline을 사용하도록 준비했지만 인증 부재로 미실행이다. 원본 Benchmark 전체 평균으로 해석하지 않는다.

원본 Progent와 AgentDojo checkout은 clean pin 그대로다. 기존 `docs/guided_reproduction_20261117/`와 미추적 `scripts/progent_demo*`, `progent_live*`, `progent_guided_effect.py`는 보존한다. 자세한 현재 12개 완료 판정, 회귀 테스트, 미팅 설명은 `regression_results.md`와 `meeting_20261123_final.md`를 참조한다. 새 key 또는 cgroup 위임이 제공되면 각 Run ID별 생성 정책·실제 모델 Tool Call·원본 판정·Controller 진입·독립 Runtime 상태를 다시 확인해야 한다.

## 2026-11-23 Kata 관리자 설치 Stage A

사용자가 이 개인 연구 서버에서 Root 설치를 직접 실행하기로 승인했다. Codex에는 sudo 인증이 없어 **Stage A만** 진행하며 `scripts/setup_kata_root.sh`와 `kata_root_setup.md`를 준비했다. 현재 Docker 서비스는 active/CanReload=yes, `/etc/docker/daemon.json`과 `/opt/kata`는 없고, 기존 컨테이너 4개가 실행 중이며 `live-restore=false`다. 스크립트 기본값은 `--check`; `--apply`는 공식 4.4.0 SHA 확인, `/opt/kata` 설치, Docker JSON의 `runtimes.kata` 병합·검증·백업, 서비스 **reload**를 수행한다. 기본 경로에서 restart하지 않는다. `--check`·`--dry-run`·병합 단위 테스트만 Codex가 실행했다. Root `--apply`와 실제 Kata Guest는 아직 NOT RUN이다.

사용자가 프로젝트 루트에서 `sudo bash scripts/setup_kata_root.sh --apply`를 실행하면 결과 로그가 `/var/log/cclab-progent-kata-setup/`에 기록된다. 다음 세션은 로그 및 `bash scripts/setup_kata_root.sh --verify` 결과를 확인한 후 Stage C의 Kata Guest 기동과 Progent 실험을 이어간다. 설치 스크립트와 수동 복구 절차는 `kata_root_setup.md`에 있다. 기존 미추적 파일과 원본 checkout을 계속 보존한다.

## 2026-11-23 Stage B/C 실행 후 현재 상태

위 Stage A 계획은 완료됐다. 사용자가 Root `--apply`를 실행했고 `/var/log/cclab-progent-kata-setup/setup-20261123T003621Z-jYb5io.log`에서 SHA·설정 검증·Docker reload·Runtime 등록 성공을 확인했다. Docker 서비스 restart는 없었다. Codex가 전용 BusyBox Kata Guest를 실제 기동해 Guest `6.18.62`, Host `5.15.0-203-generic`, Shim/QEMU PID를 확인했다. Probe의 stop/start/restart를 확인한 후 Probe만 정리했다.

Controller Commit `fb8a3bb2f52601864ec71d25cb3b2290dc5bb3de`는 `DockerBackend(runtime="runc"|"kata")`를 지원한다. 최종 직접 Harness `bash scripts/progent_vm.sh kata`의 Run `kata-20261123T004347Z-aa1064`는 6/6 PASS이며 [전체 JSON](runs/kata/kata-20261123T004347Z-aa1064.json)에 정책·Controller/Docker 호출·독립 상태·Guest 증거가 있다. 명시적 stop Deny는 Controller 0, Docker 0, running 유지였다. runc 회귀 6/6와 AgentDojo Kata 오프라인 A/B Utility True도 별도 JSON에 있다. 모든 실험 Label 리소스는 정리했고 원래 SREGym 4개는 실행 중이다.

다음 세션은 **이 직접 Harness와 오프라인 GroundTruth를 LLM Live라고 소개하지 말 것**. 이번 Stage C에서 새 API 호출·정책 자동 생성·모델 제안 Tool Call은 0회다. Kata VM 격리와 Progent Tool Wrapper 판정도 별도 계층이다. 실제 SSH/Proxmox, OS 전역 정책 집행, Wrapper 밖 실행 경로는 미검증이다. 새 연구 공백은 확정하지 않았다. 현재 Git SHA와 후속 문서 Commit/Push 상태를 확인한 뒤 Live 테스트가 필요한지 연구자와 결정한다.

## API 환경 파일 준비

연구자 요청에 따라 `scripts/progent_vm.sh check-env`와 `api_env.md`를 추가했다. 기존 `local/progent-vm/.env`는 **존재 여부만** 확인했고 값은 읽거나 출력하지 않았다. 이 파일은 Git에서 제외된다. 연구자가 키를 직접 입력한 후 `check-env`는 내부적으로 비어 있지 않은지만 검사해 PRESENT/ABSENT를 출력한다. 이 명령은 API 요청 0회이며 인증 유효성·모델 접근은 검증하지 않는다. 이 단계에서 Codex는 Live 실행을 시작하지 않았다.
