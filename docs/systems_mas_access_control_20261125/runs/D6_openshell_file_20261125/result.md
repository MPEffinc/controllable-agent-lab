# D6 OpenShell 원본 파일 집행 대조

2026-11-25 UTC. [사전등록](prereg.md) 후 공식 OpenShell v0.1.9 CLI/Gateway/Sandbox binary를 별도 `18084` Gateway, `d6file01` 일회용 BusyBox sandbox에서 실행했다. [정확한 명령](run.sh), [정책](policy.yaml), [effective policy](full-policy.json), [요약](summary.txt), [원본 sandbox 로그](openshell-logs.txt), 각 CLI stdout/stderr를 보존했다. LLM/API 비용 $0, 누적 추정 $0.1211516/$5. 호스트 커널 설정과 기존 `oslab-*`/`sregym-*` 컨테이너는 변경하지 않았다.

| 입력 | CLI exit | 전후 효과 |
|---|---:|---|
| `/sandbox/d6-allowed` 정상 쓰기 | 0 | 내용 `normal` |
| `/tmp/d6-forbidden` 직접 쓰기 | 1 | `Permission denied`; 파일 부재 |
| 내부 자식 `sh -c`의 같은 `/tmp` 쓰기 | 1 | `Permission denied`; 파일 부재 |

원본 Gateway가 반환한 effective policy version 1/hash `5dcb76a41064372c9784aff6b82161b45d8df7a1419d365acb40713cc9f47377`은 `/tmp` read-only, `include_workdir=true`, `landlock.compatibility=hard_requirement`를 보인다. 원본 sandbox 로그에 `CONFIG:LOADED` 같은 version/hash가 있다. 내부 자식은 sandbox 안에서 직접 파일 쓰기를 수행하여 wrapper 밖 프로세스 상속 범위를 시험했다. D5 ActPlane은 개별 `/work/forbidden` BPF-LSM 파일 block, D6 OpenShell은 `/tmp` 디렉터리 read-only sandbox 정책이므로 **동일한 정상/금지 파일 효과 범주**의 비교이지 완전히 동일한 정책/경로/성능 조건은 아니다. 두 원본 모두 이 범주의 정상 쓰기와 금지 직접·자식 쓰기를 분리했다.

이번 run의 Docker 컨테이너 이름 필터가 실제 이름과 달라 workload `docker logs`와 outer Docker `readonly_rootfs` 설정을 별도로 수집하지 못했다. 따라서 D6만으로 `Permission denied`의 단일 원인을 Landlock이라고 확정하지 않는다. [이전 공식 OpenShell 직접 실행](../../../experiments/20261124_openshell/results.md)은 같은 read-only `/tmp` 정책에서 workload의 Landlock 적용 OCSF, Docker rootfs writable·UID 1000·`/tmp` POSIX writable, 정상/금지 효과를 함께 기록했다. D6는 새 Gateway의 정책 활성화와 내부 자식 효과를 추가한다.

요청당 CLI 경과 시간은 정상 79.0ms, 직접 거부 77.8ms, 자식 거부 81.3ms(각 1회)이다. 네트워크/컨테이너/SSH 제어 경로가 포함되므로 D5 BPF나 OpenShell의 순수 집행 overhead로 비교하지 않는다. 전용 sandbox 삭제 접수, 전용 Gateway 프로세스 종료, 포트 `18084` 및 `d6file` 컨테이너 부재를 확인했다. MAS 작업별 OS subject 결속, 실행 중 정책 변경·철회, 열린 FD와 최종 서비스 업무 효과는 이 실험 범위 밖이다. **고정 파일 경계의 새로운 집행 메커니즘 Need는 기각**하며, 넓은 MAS 동적 권한 문제는 미검증이다.
