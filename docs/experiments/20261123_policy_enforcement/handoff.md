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
