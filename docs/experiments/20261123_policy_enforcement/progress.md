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
