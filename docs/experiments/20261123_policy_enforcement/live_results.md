# Stage E/F: gpt-6-luna Live 준비와 실제 실행 상태

2026-11-22 UTC. 공식 [GPT-6 Luna 모델 문서](https://developers.openai.com/api/docs/models/gpt-6-luna)는 Chat Completions function calling에 `reasoning_effort=none`을 요구하며 입력/출력 기준 요금을 1M token당 USD 0.10/0.50으로 표시한다. 원본 `secagent/tool.py:201-239`는 정책 요청에 `temperature`·`seed`를 넣는다. 새 `scripts/progent_system_live.py`는 **원본 `generate_security_policy`와 원본 Wrapper/checker는 그대로 사용**하면서 정책 API transport만 Luna용 요청(`reasoning_effort=none`, temperature/seed 생략)으로 교체한다. 이 차이는 원본과 별도 Adapter 동작이다.

## 인증 상태와 시도 결과

현재 셸에서 `OPENAI_API_KEY`, `LLM_API_KEY`, `OPENAI_BASE_URL`, `LLM_BASE_URL` 존재 여부는 모두 false였다. `bash scripts/progent_vm.sh system-live --backend mock --case A`를 실제 호출해 **exit 2**, `OPENAI_API_KEY is absent; no API call or Docker resource created`를 받았다. API 요청 수 0, 새 gpt-6-luna 응답·정책·Agent Tool Call **NOT RUN**. 키 값 탐색이나 생성을 하지 않았다. 모델의 이 계정 접근 가능 여부도 미검증이다.

이전 사용자의 `gpt-4o-2024-08-06` Live 기록 두 건은 `local/progent-vm/live/live-20261122T134601Z-325677.json`, `live-20261122T134630Z-93a5f1.json`으로 보존했다. 첫 실행은 잘못된 ID `1`, `2`가 정책 통과 뒤 Backend를 호출해 실패했다. 두 번째는 일부 정책 거부와 `1`·`vm1`의 Backend 실패가 섞였다. 당시 `DENY_OR_INPUT_ERROR` 출력만으로 이 둘을 구별하지 못했다. 새 결과로 재분류하거나 덮어쓰지 않았다.

## 새 CLI와 관찰 항목

```bash
cd /home/cclab/controllable_agent
read -rsp 'OPENAI_API_KEY: ' OPENAI_API_KEY; echo
export OPENAI_API_KEY
bash scripts/progent_vm.sh system-live --backend mock --case A
bash scripts/progent_vm.sh system-live --backend docker --case C
```

위 두 명령은 **실행 예시이며 아직 이 환경에서 API 실행 성공을 확인하지 않았다**. 실제 CLI 호출이 승인이다. `--case A|B|C|D|E`, `--backend mock|docker`, `--task '직접 작성한 요청'`, `--verbose`를 지원한다. 기본 한도는 정책 API 2회, Agent 턴 5회, Tool Call 5회. 전역 `local/progent-vm/luna_budget.json`에 예약 비용·요청 수를 누적하며 최대 30요청 또는 추정 USD 2에 도달하면 신규 요청을 막는다. SDK 자동 재시도는 0으로 설정했다. 실제 청구 금액은 확인하지 못하며 로그 비용은 추정치다.

일반 화면은 작업, 적용 정책의 규칙, 실제 Agent 제안, `SUCCESS`/`POLICY_DENIED`/`INPUT_VALIDATION_FAILED`/`BACKEND_EXECUTION_FAILED`/`LLM_API_ERROR`/`TASK_INCOMPLETE`, Backend 명령 수, 상태 전후만 표시한다. 원본 정책 프롬프트와 요청·응답은 Git에서 제외된 `local/progent-vm/live/<run-id>.json`에 저장하고 `--verbose`에서 정책 입력을 볼 수 있다. Resource ID는 `list_resources` Tool과 Runtime 생성 기록으로 제공한다. 프롬프트에 고정 ID를 적는 것만으로 Discovery를 주장하지 않는다. Docker 모드의 상태는 별도 `docker inspect` 호출로 확인하고 자신이 생성한 컨테이너만 정리한다.

Case C/D의 관리자 Deny와 자동 생성 Allow 결합은 관찰 대상이며 안전한 일반 결합의 증거가 아니다. 실제 Luna 실행이 없으므로 정상 작업 성공률, 공격 성공률, 모델이 금지 Tool을 제안하는지, 정책 생성 정확도는 모두 미검증이다.
