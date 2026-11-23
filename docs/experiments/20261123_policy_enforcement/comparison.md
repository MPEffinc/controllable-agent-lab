# 정책·Controller·Runtime 경계 비교

| 계층 | 직접 확인한 결과 | 확인하지 못한 것 |
| --- | --- | --- |
| Progent 정책 생성 | 과거 GPT-4o Live 로그 2건의 생성 정책과 도구 제안이 남아 있음; 이번 Luna 호환 Adapter는 원본 `generate_security_policy`를 호출하도록 구현 | 새 Luna 정책 출력은 인증정보 부재로 NOT RUN. 생성 정책의 의도 정확성 미검증 |
| Progent Tool Wrapper | Phase 2 Mock과 Stage C Docker에서 명시적 Deny는 Tool 본체/Backend mutation 0회. 허용 종료는 실제 Docker stop 1회 | Wrapper를 통하지 않는 Shell·SDK·하위 프로세스의 전체 중재 |
| 신뢰된 Docker Controller | 이름·ID·Run ID Label 소유 검증. 정책 통과 후 존재하지 않는 ID를 Controller가 별도 거부 | Progent 자체가 Docker 소유권을 이해하거나 Docker daemon authorization을 제공하는지 여부 |
| Docker runtime | `docker inspect`로 허용 종료 running→exited, 허용 시작 exited→running, Deny 후 running→running 확인 | OS/kernel 수준 강제 정책, VM 전원 제어 |
| Kata runtime (2026-11-22 rootless 시도) | `docker --runtime kata` 실패, rootless 준비 장애 기록 | 당시 Kata guest boot·guest kernel·VMM 경계의 실제 효과 |
| Kata runtime (2026-11-23 Docker 등록 후) | Guest `6.18.62`, Host `5.15.0-203-generic`, Shim/QEMU PID, 허용 stop/start와 Deny 후 상태 확인. [실행 기록](runs/kata/kata-20261123T004347Z-aa1064.json) | Kata 격리 강도, OS 전체 명령 중재, 실제 VM 전원 관리 |

기존 두 GPT-4o Live 실행의 `DENY_OR_INPUT_ERROR`는 Progent Deny와 Backend Unknown VM 오류를 섞은 표시였다. 새 Runner는 `POLICY_DENIED`, `INPUT_VALIDATION_FAILED`, `BACKEND_EXECUTION_FAILED`, `LLM_API_ERROR`, `TASK_INCOMPLETE`, `SUCCESS`를 분리한다. 분류 기능은 **새 Adapter**이며 원본 Progent가 제공하는 별도 결과 코드가 아니다.

Mock에서 확인한 정책 `None` fail-open과 Docker 실험에서 확인한 명시적 Deny는 서로 다른 설정이다. Docker 성공은 기존 Progent의 Tool-level 검사 범위 안에서 설명할 수 있다. Kata 미실행이나 Wrapper 바깥 경계는 실험되지 않았으므로 새로운 Research Gap으로 판정하지 않는다. ActPlane, OpenShell, Kata, PAuth, AuthGraph의 상세 선행연구 대조는 추가 결과 이후 수행한다.

2026-11-23 후속 실행에서 Kata Guest는 실제 기동했다. 위 마지막 문단의 **Kata 미실행**은 작성 당시의 2026-11-22 상태다. Kata 실험의 명시적 Deny에서는 Progent Wrapper가 Controller 진입 전에 차단해 `docker stop` 호출이 0회였고 Guest 컨테이너가 `running`으로 남았다. Kata는 해당 컨테이너의 VM 기반 격리 계층이며, 이 Deny 결정의 출처는 Progent다. LLM 정책 자동 생성과 Wrapper 밖의 실행 경로는 이번 후속 실행에도 미검증이다.

2026-11-23 **추가 Live 실행**에서 위 문단의 LLM 미검증 상태도 갱신됐다. [Luna × Kata Run](e2e_luna_kata.md)은 정책 LLM의 생성 Allow와 별도 관리자 Deny, 업무 LLM의 실제 `stop_resource`, Progent의 `POLICY_DENIED`, Controller/Docker stop 0회, 독립 Runtime running 유지까지 연결했다. AgentDojo Custom Suite Live B/C의 Utility와 Trace 오류도 확인했다. 이는 직접 구성한 작업에서 원본 Wrapper의 정상 동작을 관찰한 결과이며, 생성 정책의 일반적 의미 정확성, OS 전체 집행, 원본 Benchmark 평균이나 새로운 Research Gap의 근거는 아니다.
