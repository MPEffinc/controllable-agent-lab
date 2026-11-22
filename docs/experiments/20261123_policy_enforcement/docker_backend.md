# Stage C 준비: 제한된 Docker Controller

`scripts/progent_docker_backend.py`는 고정된 공식 `busybox:1.36.1` 이미지 digest `sha256:73aaf090f3d85aa34ee199857f03fa3a95c8ede2ffd4cc2cdb5b94e566b11662`를 사용한다. 컨테이너는 `cclab-progent-exp-<run-id>-<번호>` 이름과 Run ID Label로 만들고, 생성 직후 Docker ID를 메모리 소유 목록에 저장한다. 이후 모든 status/start/stop/restart/cleanup 전에 **이름·ID·Label**을 Docker inspect로 다시 대조한다. Agent에게 Docker CLI나 socket은 제공하지 않는다.

생성 옵션: `--network none`, 메모리 128 MiB, CPU 0.5, PID 64, read-only root filesystem. 컨테이너 명령은 `sleep 3600`; 호스트 디렉터리 마운트·privileged·host network 없음. `start`는 created/exited에서만, `stop`과 `restart`는 running에서만 허용한다. `start`와 `restart`는 서로 다른 Docker 명령이다.

작은 실제 Runtime probe에서 전용 컨테이너 1개를 생성(created), 시작(running), 종료(exited), 다시 시작(running)하고 자신이 생성한 ID만 삭제했다. 최종 `owned={}`. 기존 SREGym 4개 컨테이너에는 작업하지 않았다. `tests/test_progent_docker_backend.py`는 기존 리소스 이름이 소유 목록에 없으면 Docker 명령을 보내기 전에 거부하는지 확인한다. 정책 집행과 독립 상태 비교의 본 실험은 다음 기록에 분리한다.
