# 진행 기록

| 단계 | 상태 | 이번 기록에서 한 일 / 하지 않은 일 |
| --- | --- | --- |
| Phase 0 환경 조사 | 완료 | 루트 Git·원본 pin·Python·LLM 설정 접근 방식·소스 호출 관계·기존 trace를 읽고 문서화. 새 API/Tool/VM 실행 없음 |
| Phase 1 새 Use Case 준비 | 완료 | 메모리 Mock VM Backend와 원본 Wrapper 연결, 단위 테스트 2건 통과 |
| Phase 2 수동 정책 Allow/Deny | 완료 | UC01~UC06 직접 입력 10건 실행, 모두 예상과 일치; 단위 테스트 총 5건 통과 |
| Phase 3 실제 LLM Agent | 준비만 완료 | 대화형 Live 실행기 작성·정적 검사. 유료 API는 사용자 미실행, 결과 NOT RUN |
| Phase 4 시스템 수준 경계 | 선택·대기 | SSH·VM 작업 없음 |
| Phase 5 선행연구 대조 | 대기 | 실험 결과 전에는 연구 공백 판정 없음 |

## 2026-11-22 추가 진행

| Stage | 상태 | 근거 |
| --- | --- | --- |
| A Runtime 조사 | 완료 | Docker 사용 가능, 기존 4개 워크로드 보존, Kata 조건·권한 기록 |
| B AgentDojo Suite | 부분 완료 | 실제 TaskSuite·UserTask 등록 및 단위 테스트 2건 통과; 원본 Benchmark LLM 평가는 미실행 |
| C Docker | 완료 | 전용 컨테이너 실제 생성·시작·종료·재시작, Progent Deny 0 mutation, 독립 inspect 6건 일치 |
| D Kata | 실행 시도 실패 | 기존 daemon unknown runtime, rootless uidmap 부재; guest 미기동 |
| E Luna | 준비 완료, API 미실행 | 공식 파라미터 확인·호환 Adapter 작성; 인증 환경변수 없음, launcher exit 2 |
| F 가시성 | 코드·오프라인 테스트 완료 | 오류 분류·요약 출력·verbose·전역 요청/비용 상한. 실제 Luna 출력은 미관찰 |

Phase 0은 읽기 전용 조사였다. Phase 1은 Mock Backend와 Wrapper 단위 테스트, Phase 2는 직접 입력 전체 실행과 대화형 수동 스모크 테스트를 수행했다. Live 실행기는 API 호출 없이 문법·컴파일을 확인했다. 각 Phase Commit/Push SHA는 종료 보고에 기록한다.

## 2026-11-22 End-to-End 후속 판정 (이전 표보다 최신)

| 항목 | 상태 | 근거 |
| --- | --- | --- |
| 1. Luna API 실제 호출 | BLOCKED | 승인된 프로젝트 범위에 키 없음, 요청 0회 |
| 2. Luna Agent Tool Call | BLOCKED | 모델 호출 전제 없음 |
| 3. Luna 정책 자동 생성 | BLOCKED | 모델 호출 전제 없음; 원본 함수/호환 어댑터만 준비 |
| 4. Luna + Docker 실제 실행 | BLOCKED | 모델 호출 전제 없음; 직접 Harness Docker 성공과 별개 |
| 5. Luna 호출에 대한 관리자 Deny 집행 | BLOCKED | Docker 직접 요청 Deny 후 stop 명령 0, running 유지한 별도 증거는 DONE |
| 6. 독립 Docker 상태 검증 | DONE (직접 입력) | Run ID `docker-20261122T150621Z-152d45`, 6/6 일치 |
| 7. AgentDojo 실제 LLM 평가 | BLOCKED | 연결된 Suite/Controller 오프라인 A/B는 성공, 모델 요청 0회 |
| 8. Kata 설치 | DONE | 공식 4.4.0 SHA-256 검증, Shim 4.4.0 실행 |
| 9. Kata Guest 기동 | FAILED | 독립 containerd/Kata Shim 후 cgroup.procs 권한 거부; 재실행에는 위임 필요 |
| 10. Luna + Kata | BLOCKED | Guest와 API 두 전제조건 부재 |
| 11. 회귀 테스트 | DONE | 기존 10건 및 신규 테스트 통과, 실제 Docker 직접 실험 6/6 재실행 |
| 12. 최종 Commit/Push | DONE | Stage 0 `30dc1d3`, 평가기 `d2423c3`, Kata `9f0ad09`, AgentDojo `9225a1e`, 회귀·요약 `9c4866e`를 push하고 원격 SHA를 확인. 이 최종 상태 갱신도 별도 push 확인 예정 |

이 표의 DONE은 해당 괄호에 적힌 실험 종류에 한정된다. API 키나 권한을 임의 생성하거나 우회하지 않았다.

## 2026-11-23 Kata 관리자 설치 단계

| Stage | 상태 | 근거 |
| --- | --- | --- |
| A. Root 설치 절차 준비 | DONE | `setup_kata_root.sh`, strict JSON 병합 Helper·테스트, `kata_root_setup.md`; read-only 검사·후보 Docker config validation 통과 |
| B. 사용자 Root 적용 | NOT RUN | 사용자 터미널의 `sudo bash scripts/setup_kata_root.sh --apply` 필요. Codex는 sudo 인증 없이 시스템 변경하지 않음 |
| C. Guest/Progent 실험 | NOT RUN | B 로그와 Runtime 등록을 확인한 후 실제 워크로드·Allow/Deny·독립 상태 관측 진행 |
