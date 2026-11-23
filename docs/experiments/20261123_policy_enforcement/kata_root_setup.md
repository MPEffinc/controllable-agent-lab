# Kata 4.4.0 관리자 설치 절차 — Stage A 준비 결과

> 이 문서의 앞부분은 적용 전 검토 기록이다. 사용자의 실제 설치 성공은 끝의 **Stage B 적용 완료** 절에 기록했다.

2026-11-23 UTC. 이 문서는 **사용자가 실행하기 전 검토할 관리자 작업**을 설명한다. Codex는 Root 설치를 실행하지 않았다. 현재 `/opt/kata`와 `/etc/docker/daemon.json`은 없고, Docker 28.3.2에는 `kata` runtime이 등록되지 않았다. Docker 컨테이너 4개가 실행 중이며 모두 restart policy `on-failure`, `live-restore=false`다. `/dev/kvm` 접근은 가능하다. 원본 Progent와 기존 컨테이너는 변경하지 않았다.

## 검토와 실행

프로젝트 루트에서 아래 순서로 실행한다. `--check`가 기본값이다. `--check`, `--dry-run`, `--verify`는 시스템 설정을 변경하지 않는다.

```bash
cd /home/cclab/controllable_agent
bash scripts/setup_kata_root.sh --check
bash scripts/setup_kata_root.sh --dry-run
sudo bash scripts/setup_kata_root.sh --apply
bash scripts/setup_kata_root.sh --verify
```

`--apply`는 관리자 비밀번호를 인자·환경변수·파일에 저장하지 않는다. `sudo`가 사용자 터미널에서 평소처럼 인증한다. 설치 결과 로그는 `/var/log/cclab-progent-kata-setup/setup-<UTC>-<suffix>.log`에 남는다. 디렉터리는 `root:sudo` 0750, 로그는 `root:sudo` 0640이므로 `cclab` 계정이 읽을 수 있다. 로그에는 Docker 설정 **값**을 출력하지 않고 기존 키 이름·Runtime 이름·컨테이너 수·restart policy만 기록한다. 실패 시 실행 명령과 종료 코드, stderr는 이 로그에서 확인한다.

`--verify`는 설치 파일, Shim 버전, Docker config 유효성(읽기 권한이 있을 때), Docker가 보고한 `kata` Runtime을 확인한다. 현재 사전 상태에서 실행하면 Shim 부재로 **exit 1이 정상**이다. `--verify`의 성공도 Guest 기동 증거는 아니다.

## `--apply`가 변경하는 경로와 순서

1. 기존 `local/progent-vm/kata-4.4.0/kata-static-4.4.0-amd64.tar.zst`의 SHA-256을 공식 릴리스 값 `ccbc0cbc591089d0c57012b78da64b23ef43e0bac0f869dc7bfebe8588c33986`과 다시 대조한다. 다른 아키텍처·누락·심볼릭 링크·불일치는 거부한다. 외부 스크립트를 다운로드해 Root로 실행하지 않는다.
2. `/etc/docker/daemon.json`을 strict JSON으로 읽는다. 기존 값은 화면에 표시하지 않는다. 중복 키, 심볼릭 링크, 이미 존재하지만 다른 `kata` 설정은 자동 병합하지 않고 중단한다. `scripts/kata_daemon_config.py`가 기존 키와 기존 Runtime을 보존하고 `runtimes.kata`만 추가한다.
3. `/opt/.kata-stage.*`에 공식 아카이브를 압축 해제하고 Shim·QEMU 설정·Guest Kernel/Image·VERSION을 검증한 뒤, `/opt/kata`가 없을 때만 원자적으로 이동한다. 기존 `/opt/kata`가 4.4.0과 일치하면 재사용하고, 다른 설치이면 덮어쓰지 않는다.
4. 새 Docker 설정 후보를 `dockerd --validate --config-file <candidate>`로 검사한다. 기존 `daemon.json`이 있으면 `/var/lib/cclab-progent-kata-setup/daemon.json.before-<UTC>-<pid>`에 Root 전용 백업을 만든다. 그다음 `/etc/docker/daemon.json`을 원자적으로 갱신한다. 현재 파일이 없으므로 이 서버의 첫 적용에서는 새 파일이 생성된다.
5. `systemctl reload docker`를 실행하고 `docker info`로 Runtime 등록을 확인한다. **기본 `--apply`는 Docker를 재시작하지 않는다.** Docker 문서는 `runtimes`를 재로드 가능한 설정으로 명시한다. 재로드가 실패하면 스크립트가 이전 설정 복원을 시도한다. 설정은 유효하지만 Runtime이 활성화되지 않으면 exit 3과 `PENDING`을 기록하고 설정을 남겨 후속 검토가 가능하게 한다.

Kata [공식 설치 문서](https://github.com/kata-containers/kata-containers/blob/main/docs/installation.md)는 4.x `runtime-rs` Shim, QEMU `ConfigPath`, Docker `runtimeType` 값을 제시한다. Docker [daemon 설정 문서](https://docs.docker.com/reference/cli/dockerd/)는 `runtimes` 재로드를 지원한다고 명시한다. 이 스크립트는 기본 Runtime을 바꾸지 않고 `/sys/fs/cgroup` 권한·방화벽·기존 컨테이너를 수정하지 않는다.

## 서비스 영향과 선택적 재시작

현재 4개 컨테이너가 실행 중이고 `live-restore=false`이므로 Docker 서비스 **재시작은 기존 작업에 영향을 줄 수 있다**. 기본 경로의 `systemctl reload docker`는 daemon 재구성 요청이며 컨테이너 중지 명령을 보내지 않는다. 실제 적용 후 Runtime 등록을 `docker info`로 확인해야 한다.

재로드만으로 등록되지 않을 때만 별도 `--apply --restart-docker` 경로가 있다. 실행 중인 컨테이너가 있으면 `--accept-container-impact`도 명시해야 재시작을 진행한다. 두 옵션은 사용자가 영향 범위를 검토한 후 직접 선택하는 용도다. 스크립트는 먼저 재로드를 시도하며 이미 `kata`가 활성화되면 재시작하지 않는다. 이번 Stage A에서는 재시작을 실행하지 않았다.

## 복구 방법

스크립트가 설정을 갱신한 뒤 재로드 명령에서 실패하면, 해당 설정이 스크립트가 쓴 내용과 동일한지 SHA-256으로 확인한 후 자동 복원을 시도한다. 기존 파일이 있었다면 백업을 되돌리고, 없었다면 스크립트가 새로 만든 파일을 제거한다. 자동 복원도 실패하면 로그의 `[RESTORE FAILED]`를 확인한다.

성공 후 수동 복구가 필요하면 먼저 실험용 Kata 컨테이너가 없는지 확인하고, 변경 후 다른 관리자가 Docker 설정을 수정했는지 비교한다. 이전 설정 파일이 있었으면 로그의 `[BACKUP]` 경로를 `/etc/docker/daemon.json`으로 복사한 뒤 `dockerd --validate`와 `systemctl reload docker`를 수행한다. 현재 서버처럼 이전 파일이 없었다면, 스크립트가 생성한 파일임을 확인한 뒤 그 파일을 제거하고 재로드한다. **`/opt/kata` 바이너리는 실행 중인 Shim/Guest의 사용 가능성이 있으므로 자동 삭제하지 않는다.** 수동 복구 시에도 기존 컨테이너를 삭제하거나 중단하지 않는다.

## Stage A에서 실제로 확인한 것과 Stage C 전제조건

- `bash -n scripts/setup_kata_root.sh`: 통과.
- `python3 -m unittest discover -s tests -p test_kata_daemon_config.py -v`: 4/4 통과. 기존 설정·다른 Runtime 보존, idempotence, 충돌·중복 키·symlink 거부, 값 비노출을 검사했다.
- `bash scripts/setup_kata_root.sh --check`와 `--dry-run`: exit 0, 공식 아카이브 SHA-256 재확인. 실행 전후 `/opt/kata`와 `/etc/docker/daemon.json`은 모두 부재.
- 후보 JSON에 대한 `dockerd --validate --config-file <temporary candidate>`: exit 0, `configuration OK`. Docker 서비스는 active이고 `CanReload=yes`.
- `bash scripts/setup_kata_root.sh --verify`: 설치 전 예상대로 exit 1, `Kata shim, configuration, guest kernel or image missing`.

사용자의 `sudo ... --apply` 결과가 로그에 저장된 후 일반 사용자 권한으로 Docker `kata` 등록, 실제 Guest `uname -r`, Host/Guest 커널 차이, Shim/QEMU 프로세스, 종료·시작·재시작을 확인한다. 그다음 **이 실험에서 생성한 리소스만** 대상으로 Progent Controller의 `runc`/`kata` 선택과 Allow/Deny 및 독립적인 Docker 상태 검증을 수행한다. 그 전까지 Kata Guest 기동과 Progent×Kata 결과는 **NOT RUN**이다.

## 2026-11-23 후속 결과 — Stage B 적용 완료

위 내용은 **설치 전 Stage A 기록**이다. 사용자가 `sudo bash scripts/setup_kata_root.sh --apply`를 직접 실행했다. Root 로그는 `/var/log/cclab-progent-kata-setup/setup-20261123T003621Z-jYb5io.log`이며, 공식 SHA-256 대조, `/opt/kata` 설치, Docker 후보 설정 `dockerd --validate`, `/etc/docker/daemon.json` 작성, `systemctl reload docker`가 모두 exit 0이다. 마지막 줄은 `[PASS] kata runtime active after reload`다. 이전 `daemon.json`은 없었으므로 기존 파일 백업은 없고 복구 절차는 위 문단에 기록했다. Docker **restart는 실행되지 않았다**. 일반 사용자 `--verify`에서도 Shim 4.4.0과 활성 Runtime을 확인했으며, Root 전용 `daemon.json`의 재검증은 설치 로그의 `dockerd --validate` 결과를 사용한다.

실제 Guest 기동과 정책 실험 결과는 [Kata Runtime 후속 기록](kata_runtime_results.md)과 [Kata 정책 결과](kata_results.md)에 있다. 설치 성공과 Guest 실행 성공을 별도 단계로 기록했다.
