# 진행 기록

| 단계 | 상태 | 이번 기록에서 한 일 / 하지 않은 일 |
| --- | --- | --- |
| Phase 0 환경 조사 | 완료 | 루트 Git·원본 pin·Python·LLM 설정 접근 방식·소스 호출 관계·기존 trace를 읽고 문서화. 새 API/Tool/VM 실행 없음 |
| Phase 1 새 Use Case 준비 | 완료 | 메모리 Mock VM Backend와 원본 Wrapper 연결, 단위 테스트 2건 통과 |
| Phase 2 수동 정책 Allow/Deny | 완료 | UC01~UC06 직접 입력 10건 실행, 모두 예상과 일치; 단위 테스트 총 5건 통과 |
| Phase 3 실제 LLM Agent | 준비만 완료 | 대화형 Live 실행기 작성·정적 검사. 유료 API는 사용자 미실행, 결과 NOT RUN |
| Phase 4 시스템 수준 경계 | 선택·대기 | SSH·VM 작업 없음 |
| Phase 5 선행연구 대조 | 대기 | 실험 결과 전에는 연구 공백 판정 없음 |

Phase 0은 읽기 전용 조사였다. Phase 1은 Mock Backend와 Wrapper 단위 테스트, Phase 2는 직접 입력 전체 실행과 대화형 수동 스모크 테스트를 수행했다. Live 실행기는 API 호출 없이 문법·컴파일을 확인했다. 각 Phase Commit/Push SHA는 종료 보고에 기록한다.
