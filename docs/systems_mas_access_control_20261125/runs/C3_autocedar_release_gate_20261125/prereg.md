# C3 사전등록 — AutoCedar 완료·semantic approval 분리의 소비자 경계

2026-11-25 UTC. 공식 고정 source `a0cf180977d799cf943514b67ffc260fc579b9a5`의 공개 Fig.2 CyberChair trace는 **수동 AITL target을 만든 디버그 artifact**이다. case-011이나 논문 19개 gold 불일치 trace가 아니다. 저장된 `events.jsonl`에는 verifier passed와 final approval false가 함께 있으며 최종 후보 파일이 존재한다. 원본 `_cmd_author`/`_authoring_completed`는 candidate 존재를 CLI 성공으로 정의하고 approval은 별도 필드로 출력한다. 이는 원본 코드가 명시한 설계이므로 무조건 버그라고 하지 않는다.

- **RQ:** 최종 human semantic approval=false인 저장 저자 후보를 실행 성공만 보는 소비자와 명시 승인 확인 소비자가 각각 로컬 모의 서비스에 적용하면 어떤 effect 차이가 나는가? 원본 `verify`가 해당 후보를 통과시키는가?
- **대조:** 공식 archive `harness_runs/scenario`의 원본 `candidate.cedar`/schema/plan을 무수정으로 원본 `autocedar.cli verify`에 입력. 같은 후보에 `submitStep1` 정상 요청을 Cedar CLI로 평가. `completion_only` arm은 후보 파일 존재+verifier pass로 로컬 effect를 기록; `approval_gate` arm은 추가로 저장된 `final_user_decision.approved`를 요구한다.
- **예상/반증:** candidate pass, approval false면 completion-only는 effect 1, approval gate는 0. verifier가 실패하거나 effect가 달리 나면 그대로 기록. 이 비교는 소비자 인터페이스 misconfiguration 가능성을 보이며 원저자 제품이 승인 없이 배포했다고 증명하지 않는다.
- **범위/비용:** 모델/API $0, 외부 service 0. 원시 명령·파일 SHA·원본 decision·Cedar stdout/stderr·SQLite 상태 저장. 성공/실패 후 source·archive를 수정하지 않는다. human reviewer의 실제 정확성은 미평가다.
