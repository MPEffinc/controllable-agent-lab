# D5 결과 — ActPlane 원본 eBPF 집행, 격리 VM

2026-11-25 UTC. [사전등록](prereg.md) 후 수행. 원본 ActPlane SHA `1cbb4d0f40e2bc6042d6883f045fe8e0e838b168`, CLI `0.1.8`. 유료 API $0, 누적 추정 **$0.0754388 / $5**. 호스트 LSM·커널 설정, 기존 서비스·컨테이너는 변경하지 않았다. QEMU KVM guest는 `-net none`, 별도 Ubuntu 24.04 컨테이너 rootfs와 `/work` 실험 파일만 썼다. 사전등록 remote SHA `1d29d9d163fdeb6aa31890b3145cb3cff7723a24`.

## 원본/adapter 경계와 환경

- **원본:** 고정 SHA의 `actplane` CLI, 원본 DSL compiler, 원본 `bpf/process.c` 정적 loader 및 `process.bpf.c` eBPF Hook. CLI는 읽기 전용 checkout에서 `cargo build --locked --release -p actplane`로 빌드했다. C loader는 동일 SHA를 별도 로컬 clone하고 고정 submodule을 받아 `make -C bpf process`로 빌드했다. 원본 코드는 수정하지 않았다. CLI SHA256 `4cd5a66a97907d1d02f724bdc9906cb824b8d246ab1362d6a1a829705328e21a`, 정적 loader SHA256 `a62372ff5e94f913ed6693e0b5d4bc7cb33863039f690d9e2949c3d6f4fb34db`.
- **연구자 adapter:** [guest init](guest_init.sh), [정적 실행 드라이버](static_case.sh), [반복 쓰기 드라이버](perf_case.sh), 일회용 QEMU guest 구성. 이들은 정책을 제안하거나 ActPlane 결정 로직을 바꾸지 않는다. `--seed-pid`/`--seed-label 1`로 실험 bash를 원본 loader에 명시적으로 결속했다. 실제 MAS 작업 신원 자동 결속은 시험하지 않았다.
- 호스트 6.8.0-149는 `CONFIG_BPF_LSM=y`이나 실행 LSM 목록에 `bpf`가 없고 sudo가 비대화형으로 불가했다. guest에서는 부팅 인자 `lsm=lockdown,capability,landlock,yama,apparmor,bpf`를 사용했다. 6.8 guest에서도 `bpf`가 활성화됐고, 6.15 guest에서는 `lockdown,capability,landlock,yama,apparmor,bpf,ima,evm`을 확인했다([원시 환경](guest_6_15_env.txt)). 6.15 guest kernel은 [Ubuntu mainline 6.15 이미지 패키지](https://kernel.ubuntu.com/mainline/v6.15/amd64/)에서 내려받았다. 패키지 SHA256 `9dd17f90c3bd56e839565979ddeeee5423b0f787c63d9bb04ae2c542b8848d20`.

## 실제 관측

| 경로 | 정상 대조 | 금지 대조·실제 파일 효과 | 관측/판정 |
|---|---|---|---|
| 6.8 원본 CLI `kill exec "**/true"` | 같은 Agent 자식 `/bin/echo` 정상 완료 | 자식 `/bin/true` exit 137, `KILLED` 위반 이유·AGENT provenance | [원시 출력](kill.stdout)·[stderr](kill.stderr). **원본 tracepoint eBPF 집행 확인.** 사후 `kill`이므로 pre-op 차단 증거는 아니다. 정책 없는 `/bin/true`는 exit 0이었다. |
| 6.8 원본 CLI `block write` | 정책 설치 전 종료 | 파일 변경 시도 없음 | [CLI 오류](cli_write_error.txt): singleton의 초기 예약 feature에 `write sink rules`가 없어 delta 설치 거부(`missing=0x8`). `ACTPLANE_HOOK_PROFILE=full` 재시도도 같은 오류. [원본 `PinnedEngine::open_or_install_singleton()`](../../../../third_party/K13-actplane/bpf/src/lib.rs)은 빈 config와 hook 예약으로 시작하며, file sink matcher class는 포함하지 않는다. **이 CLI 경로의 고정 정책 설치 제한**이지 ActPlane 커널 PEP의 보안 실패가 아니다. |
| 6.8 원본 정적 loader, 같은 [정책](policy.dsl) | loader `ready`에 도달하지 않음 | loader 미설치 상태에서 금지 파일 `child`로 변경 | [검증기 stderr](static_6_8.loader_stderr)에서 `trace_rename_exit`의 7-call stack 544 bytes를 거절. [stdout](static_6_8.stdout)의 정상/금지 결과는 **무집행 상태**이며 보안 차단 결과로 세지 않는다. |
| 6.15 원본 정적 loader, 같은 정책 | `/work/allowed` 쓰기 exit 0, 내용 `normal` | 직접·자식 `/work/forbidden` 쓰기 모두 exit 1/`Operation not permitted`; 내용 `baseline` 유지 | loader `ready_count=1`, [요약](static_6_15.stdout)·[stderr](static_6_15.stderr)·[자식 stderr](static_6_15.child_error). [원본 커널 이벤트 2건](static_6_15.loader_stdout)은 모두 `effect=block`, `blocked=true`, `op=2`, 동일 금지 경로를 기록하며 둘째 이벤트는 자식 bash provenance를 포함. **원본 BPF-LSM 사전 효과 차단 확인.** |
| 6.15 반복 대조 | 정책 전 `/work/allowed` 5,000회 쓰기 ×3 모두 성공 | 정책 적용 뒤 동일 쓰기 ×3 모두 성공, 직접·자식 금지 쓰기 exit 1/1, 내용 `baseline` | [원시 시간·효과](perf_case.stdout)·[위반 이벤트](perf_loader.stdout)·[오류](perf_case.stderr). 안전·정상 관측을 반복 확인. |

6.15 반복 쓰기의 경과 시간은 정책 전 `71.50, 64.13, 63.92 ms`, 정책 중 `152.96, 155.11, 176.88 ms`였다. 각 3회 중앙값은 `64.13` 대 `155.11 ms`(약 `2.42×`)이다. 단일 VM의 bash redirection 루프이며 실행 순서가 고정돼 있고 통계적 성능 평가나 논문 수치와 비교할 수 없다. 정책 중 정상 완료 비용이 무시할 수 없다는 **예비 관측**으로만 사용한다. 파일별 정책 범위·Hook 구성에 따른 비용을 추가 검증해야 한다.

초기 6.15 드라이버는 정책 대상 bash가 보호된 loader를 종료한 뒤 `wait`하도록 작성돼 완료 메시지에 도달하지 않았다. 해당 run의 금지/정상 효과와 커널 이벤트는 이미 기록돼 있다. 후속 반복 드라이버는 loader 종료를 작업에 요구하지 않고 정상 exit 0을 남겼다. guest는 호스트에서 종료했다. 이 관측만으로 loader 보호의 세부 원인을 확정하지 않는다.

## 강한 대안과 남은 반박

원본 ActPlane은 Tool Wrapper 밖의 직접·자식 파일 효과를 이 정책/커널 조건에서 중재했다. 별도 파일 접근 PEP의 존재 자체는 새 연구 Need가 아니다. [ActPlane 공식 support matrix](https://eunomia.dev/actplane/support-matrix/)도 `block`의 BPF-LSM 의존성과 tracepoint `kill`의 사후 시점을 구분한다. [ContractWarden 원문](https://arxiv.org/pdf/2609.38248)은 사람 승인 asset contract, pidfd와 실행 gate를 통한 task 결속, eBPF-LSM 파일·네트워크 차단, 지원 객체의 단조 정보흐름을 강한 직접 대안으로 제시하며 미선언 asset·미지원 IPC·영속 source-bit 재사용의 한계를 명시한다. 공개 원본 구현은 이번 검색에서 확인하지 못해 실행 대조는 하지 않았다. OpenShell 기존 [원본 실행](../../../access_control_empirical_20261124/runs/K14_effective_20261124/result.md)은 sandbox/L7 경계의 별도 증거이며 같은 정책·kernel Hook 비교로 취급하지 않는다.

**D1:** 파일 효과에 대한 원본 OS PEP는 확보. Tool Wrapper/OS/service의 동일 업무 요청 비교는 미완료. **D2:** 원본 loader의 명시적 seed는 확인. 공유 Worker의 작업별 신원·Agent A→B→C 위임 결속은 미시험. **D3:** 동적 정책 변경·철회, 이미 열린 FD·비동기 요청은 미시험. **D4:** 파일을 막은 사실은 DB 업무 action의 의미를 제한했다는 증거가 아니다. 실제 서비스 PEP와 결합 비교가 필요하다. 따라서 Track D의 **OS 집행 가능성은 확립**, 독립 신규 Research Need/Contribution은 `UNVERIFIED`로 유지한다.
