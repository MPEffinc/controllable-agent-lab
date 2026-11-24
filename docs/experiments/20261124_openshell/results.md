# OpenShell v0.1.9 실제 실행 결과

실행일: 2026-11-24 UTC. 루트 HEAD 시작 시 `f457113313e24fbe7d892444a22db5ccc7c3b198`. 공식 v0.1.9 태그 소스 `ce58cf8e9b953281352d98a637e41616295b1318`. 사용자 영역 바이너리만 사용했다. 호스트 커널 `6.8.0-149-generic`, Landlock probe ABI 4, Docker 28.3.2. 기존 SREGym 컨테이너 4개는 건드리지 않았다.

워크로드 이미지: `busybox:1.36.1`, Docker image ID `sha256:b116e155074440ffd9e449559433feb4cd2341eb3554b1da1c638c976e56451d`, RepoDigest `busybox@sha256:73aaf090f3d85aa34ee199857f03fa3a95c8ede2ffd4cc2cdb5b94e566b11662`.

## Standalone prover — 실제 실행

`bash scripts/openshell_lab.sh prover`를 실행했다. 원본 v0.1.9 prover가 [boundary.yaml](boundary.yaml)에 대해 [candidate-contained.yaml](candidate-contained.yaml)을 `within_boundary`/exit 0으로, [candidate-exceeds.yaml](candidate-exceeds.yaml)을 `exceeds_boundary`/exit 1로 판정했다. 후자의 반례는 `filesystem write /tmp`. 검사 범위 출력: `filesystem, network_l4, network_rest, process, landlock`.

원본 JSON: `local/openshell-20261124/runs/prover-20261124T072730Z/`. 이 검사는 Gateway나 샌드박스를 사용하지 않았고, 어떤 정책도 집행하지 않았다. v0.1.9 [공식 prover 문서](https://docs.nvidia.com/openshell/v0.1.9/how-it-works/policies/prover)의 경계 검사에 해당한다.

## Docker 샌드박스 — 실제 실행

실행 명령: `bash scripts/openshell_lab.sh demo`. 최종 재실행 로그: `local/openshell-20261124/runs/sandbox-20261124T072945Z/terminal.log`. Gateway `openshell status`는 v0.1.9, `Connected`, `Authenticated (mTLS transport)`를 반환했다. 각 샌드박스는 별도 Supervisor와 workload 컨테이너로 기동됐다.

| 조건 | 입력과 실제 결과 | 추가 근거 |
| --- | --- | --- |
| 기본 정책 | UID 1000의 `printf allowed > /tmp/openshell-demo.txt` 성공, `allowed` 출력 | 기본 정책의 `/tmp`는 `read_write` |
| [readonly_tmp.yaml](readonly_tmp.yaml) | UID 1000의 `/sandbox` 쓰기 성공, 같은 UID의 `/tmp` 쓰기 실패, exit 1, `Permission denied` | `sandbox get --policy-only`가 `/tmp`를 `read_only`, `landlock.compatibility: hard_requirement`로 출력. Workload OCSF에 `Applying Landlock filesystem sandbox [abi:V3 compat:HardRequirement ...]` |
| 기본 정책의 네트워크 | `wget -T 4 -O - http://example.com/` 실패, exit 1 | Supervisor OCSF: `NET:OPEN [MED] DENIED /bin/wget(0) -> example.com:80 [reason:transparent_tcp_policy_denied]` |

독립 Docker 관측: 제한 정책 workload는 `readonly_rootfs=false`, `network_mode=none`, `user=1000:1000`. `/tmp` 권한은 `drwxrwxrwt`. 따라서 이번 `/tmp` 거부를 Docker의 읽기 전용 루트나 일반 POSIX 쓰기 권한 부족으로 해석하지 않는다. 원본 workload 로그에서 Landlock 적용을 확인했다. 네트워크는 Docker outer fence와 Supervisor 중재가 함께 구성된다. 여기서는 원본 Supervisor의 Deny 이벤트까지 확인했지만, 모든 네트워크 경로의 중재를 검증한 것은 아니다.

첫 샌드박스 생성 시 `cclab-openshell-lab-01`이라는 이름은 최대 19자를 초과해 CLI가 exit 1로 거부했다. 이름을 `oslab-1124-01`로 줄여 재시도해 성공했다. 이 초기 실패는 보안 정책 Deny가 아닌 입력 유효성 검사다.

실험 종료 시 OpenShell이 생성한 샌드박스·Supervisor 4개를 삭제했고, Gateway 프로세스를 종료했다. 이후 `docker ps`에는 기존 SREGym 컨테이너 4개만 남았다. API 호출, LLM Agent 실행, Progent 연결은 하지 않았다.
