# 2026-11-23 미팅용 핵심 결과

- 원본 Progent 소스는 변경하지 않고 메모리 Mock VM Tool `vm_action(vm_id, action)`에 원본 `apply_secure_tool_wrapper`를 연결했다.
- 수동 정책은 원본 tuple 형식으로 `lab-vm-01`의 `shutdown`을 priority 1 Deny, `status`를 priority 2 Allow로 표현했다.
- Harness 직접 입력에서 `status`는 Backend 1회, `shutdown` 명시적 Deny와 범위 밖 `lab-vm-02` 조회는 Backend 0회였다. 명시적 Deny와 규칙 불일치 후 fallback 거부를 나누어 기록했다.
- 정책 `None`이면 원본은 경고 후 호출을 통과시켜 Mock VM이 `stopped`로 바뀌었다. 정상 실험은 항상 정책을 설치했다.
- 이 단계는 **수동 정책의 원본 집행 검증**이다. 자연어→LLM 정책 생성 및 실제 Agent 제안은 연구자가 직접 실행할 Live 모드로만 준비했으며 **NOT RUN**이다.
- OS·SSH·실제 VM 경계는 검증하지 않았다. Mock Tool Wrapper의 결과만으로 시스템 수준 집행이나 새로운 연구 공백을 주장하지 않는다.
