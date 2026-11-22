# Phase 1: 격리된 VM Use Case

`scripts/progent_vm_usecase.py`는 `lab-vm-01`, `lab-vm-02`의 상태를 프로세스 메모리에만 보관한다. `status`, `shutdown`, `restart`는 메모리 상태를 읽거나 변경하며 SSH, Shell, Proxmox, OS 명령, 네트워크를 호출하지 않는다. Backend는 Run ID, Event ID, 전달 인자, 호출 수, 상태 전후, 변경 이력을 보관하고 `reset()`으로 초기화한다.

`make_wrapped_tool()`은 실제 `secagent.apply_secure_tool_wrapper()`를 사용한다. 수동 정책은 `secagent.update_security_policy()`로 설정한다. Mock Backend와 Tool 본체의 호출 기록은 Wrapper가 실제로 통과시킨 뒤에만 증가한다. 이 모듈은 별도 Allow/Deny 판정기를 구현하지 않는다.

실행 환경: `local/guided-reproduction-20261117/envs/progent-agentdojo/bin/python`. 단위 테스트 명령: `PYTHONPATH=. local/guided-reproduction-20261117/envs/progent-agentdojo/bin/python -m unittest tests.test_progent_vm_usecase -v`.

Phase 1은 Tool 구조와 Wrapper 연결만 확인한다. UC01~UC06의 독립 실험과 결과는 Phase 2에 기록한다.
