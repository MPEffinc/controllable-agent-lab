# OpenShell v0.1.9 입문 실습 (2026-11-24 UTC)

## 무엇을 확인하는가

이번 실습은 **OpenShell 원본 바이너리**로 정책 포함 관계와 실제 샌드박스 집행을 관찰한다. LLM, Progent, AgentDojo, Kata를 이 실행에 연결하지 않았다. 따라서 여기의 `wget`은 LLM Agent의 자율적 Tool Call이 아니라 연구자가 직접 입력한 명령이다.

| 구성요소 | 역할 | 이 실습에서 확인한 것 |
| --- | --- | --- |
| CLI → Gateway | 생성 요청, 정책 전달, 생명주기 관리 | mTLS 연결과 샌드박스 생성 |
| Docker driver | 전용 Supervisor와 workload 컨테이너 생성 | workload `network_mode=none`, UID 1000 |
| Workload 안 `openshell-sandbox` | 자식 프로세스 실행, Landlock·seccomp 적용, DNS/TCP 요청 전달 | Landlock 적용 로그와 파일 쓰기 거부 |
| 분리된 Supervisor | 네트워크 정책 판정, 허용된 연결의 실제 실행 | `example.com:80` Deny OCSF 이벤트 |
| Standalone prover | 후보 정책이 경계 정책 안에 있는지 검증 | `within_boundary`, `/tmp` 쓰기 반례 |

OpenShell의 YAML은 파일, 프로세스 신원, 네트워크 대상과 요청을 정의한다. 파일 규칙은 시작 시 Landlock으로 적용되며, 네트워크 규칙은 실행 중 Supervisor에서 평가된다. 기본 네트워크 정책은 허용 규칙이 없는 연결을 거부한다. [공식 정책 설명](https://docs.nvidia.com/openshell/v0.1.9/how-it-works/policies/overview), [공식 아키텍처](https://docs.nvidia.com/openshell/v0.1.9/about/architecture).

## 코드 흐름

```text
openshell sandbox create --policy readonly_tmp.yaml
  → CLI: CreateSandboxRequest
  → Gateway gRPC / compute service
  → Docker driver: Supervisor 컨테이너 + network=none workload 컨테이너
  → workload의 openshell-sandbox가 자식 프로세스를 준비
  → Landlock ruleset 준비 → 자식에서 restrict_self() + seccomp 적용
  → 파일 접근: 커널 Landlock 판정

workload의 wget → seccomp user notification → sandbox network broker
  → Supervisor → 정책 엔진의 authorize_egress()
  → Deny면 연결하지 않고 OCSF NET:OPEN DENIED 기록

openshell-prover check candidate --boundary boundary
  → 별도 정적 포함 관계 검사; 샌드박스에 정책을 적용하지 않음
```

v0.1.9 공식 태그 `ce58cf8e9b953281352d98a637e41616295b1318` 기준 주요 위치:

- CLI 요청 구성과 전송: [`openshell-cli/src/run.rs:678`](https://github.com/ai-openshell/openshell/blob/ce58cf8e9b953281352d98a637e41616295b1318/crates/openshell-cli/src/run.rs#L678), [`:718`](https://github.com/ai-openshell/openshell/blob/ce58cf8e9b953281352d98a637e41616295b1318/crates/openshell-cli/src/run.rs#L718)
- Docker outer fence 검증: [`openshell-driver-docker/src/lib.rs:3119`](https://github.com/ai-openshell/openshell/blob/ce58cf8e9b953281352d98a637e41616295b1318/crates/openshell-driver-docker/src/lib.rs#L3119)
- 자식 정책 준비/적용: [`openshell-sandbox/src/process.rs:78`](https://github.com/ai-openshell/openshell/blob/ce58cf8e9b953281352d98a637e41616295b1318/crates/openshell-sandbox/src/process.rs#L78), [`:647`](https://github.com/ai-openshell/openshell/blob/ce58cf8e9b953281352d98a637e41616295b1318/crates/openshell-sandbox/src/process.rs#L647)
- Landlock 후 seccomp 적용: [`openshell-sandbox/src/sandbox/linux/mod.rs:58`](https://github.com/ai-openshell/openshell/blob/ce58cf8e9b953281352d98a637e41616295b1318/crates/openshell-sandbox/src/sandbox/linux/mod.rs#L58), [`:89`](https://github.com/ai-openshell/openshell/blob/ce58cf8e9b953281352d98a637e41616295b1318/crates/openshell-sandbox/src/sandbox/linux/mod.rs#L89)
- 네트워크 syscall 중재와 정책 평가: [`seccomp_notify.rs:333`](https://github.com/ai-openshell/openshell/blob/ce58cf8e9b953281352d98a637e41616295b1318/crates/openshell-sandbox/src/linux/seccomp_notify.rs#L333), [`opa.rs:606`](https://github.com/ai-openshell/openshell/blob/ce58cf8e9b953281352d98a637e41616295b1318/crates/openshell-supervisor-network/src/opa.rs#L606)
- YAML 파싱과 기본 정책: [`openshell-policy/src/lib.rs:857`](https://github.com/ai-openshell/openshell/blob/ce58cf8e9b953281352d98a637e41616295b1318/crates/openshell-policy/src/lib.rs#L857), [`:972`](https://github.com/ai-openshell/openshell/blob/ce58cf8e9b953281352d98a637e41616295b1318/crates/openshell-policy/src/lib.rs#L972)

기존 `third_party/guided-openshell-2e5589b/`는 **다른 커밋** `2e5589b2180dd432320adda124c4f7bcede119b5`이다. 이번 실행과 맞춰 읽으려면 로컬에 따로 받은 `local/openshell-20261124/source-v0.1.9/` 또는 위 공식 태그 링크를 사용한다. 원본 checkout은 수정하지 않았다.

## 현재 서버에서 직접 실행

루트: `/home/cclab/controllable_agent`. `local/openshell-20261124/releases/v0.1.9/`의 CLI, Gateway, prover와 `local/openshell-20261124/bin/openshell-sandbox`는 공식 v0.1.9 릴리스 아카이브에서 받아 SHA-256을 확인한 상태다. `local/`은 Git에 들어가지 않는다. 처음부터 새 서버에서 실행할 경우 [공식 릴리스](https://github.com/ai-openshell/openshell/releases/tag/v0.1.9)와 [지원 조건](https://docs.nvidia.com/openshell/v0.1.9/about/support-matrix)을 먼저 확인해야 한다.

첫 번째 터미널에서 Gateway를 **전경 실행**한다. 이 Gateway만 포트 `127.0.0.1:18080`, 전용 SQLite와 mTLS 인증서를 사용한다. 기존 Docker 서비스 설정을 바꾸지 않는다.

```bash
cd /home/cclab/controllable_agent
bash scripts/openshell_lab.sh serve
```

두 번째 터미널에서 정책 검증, 상태 확인, 실제 샌드박스 시연을 순서대로 실행한다.

```bash
cd /home/cclab/controllable_agent
bash scripts/openshell_lab.sh prover
bash scripts/openshell_lab.sh status
bash scripts/openshell_lab.sh demo
```

시연 후 두 번째 터미널에서 **실습이 생성한 두 샌드박스만** 삭제하고, 첫 번째 터미널은 `Ctrl-C`로 Gateway를 종료한다.

```bash
bash scripts/openshell_lab.sh stop
```

원본 Gateway/CLI 실행 결과는 `local/openshell-20261124/runs/sandbox-*/terminal.log`에, prover JSON은 `local/openshell-20261124/runs/prover-*/`에 저장된다. `demo`가 출력하는 Docker 컨테이너 이름으로 `docker logs <이름>`을 실행하면 Supervisor와 workload의 OCSF 로그를 볼 수 있다. 현재 서버의 mTLS 개인 키는 `local/openshell-20261124/`에만 있으며 Git에 추가하면 안 된다. 이 실습은 API 키나 LLM 호출을 사용하지 않는다.

## 실제 관찰 및 해석

실행 증거와 정확한 결과는 [results.md](results.md)에 기록했다. 파일 쓰기 실패는 `/tmp`의 POSIX 권한 실패만으로 설명되지 않는다. 같은 UID·이미지의 기본 정책 샌드박스는 `/tmp`에 썼고, 제한 정책 샌드박스는 `/sandbox`에 썼지만 `/tmp`에서 거부됐다. Docker workload의 `readonly_rootfs=false`였고, 원본 로그에서 Landlock ruleset 적용을 확인했다. 네트워크 실패 역시 단순한 `wget` 오류만으로 판단하지 않고 Supervisor의 `OCSF NET:OPEN DENIED`를 확인했다.

**검증 범위:** 특정 파일 및 네트워크 정책에 대한 OpenShell v0.1.9 Docker 샌드박스 결과와 독립적인 prover 포함 관계 결과. LLM 정책 생성, Progent와의 연동, provider 자격증명 주입, 실제 VM/Kata 기반 OpenShell 런타임, 모든 syscall 우회 가능성, 일반적인 보안성 보장은 이번에 검증하지 않았다. Prover의 `within_boundary`는 모델이 다루는 정책 차원의 결과이며, 실행 시 집행 성공을 자동으로 증명하지 않는다.
