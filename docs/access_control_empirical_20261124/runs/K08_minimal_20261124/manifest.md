# K08 SASY: 원저자 message-flow 최소 Allow/Deny

## 실행 전 고정한 질문 (2026-11-24 UTC)

- **검증 질문:** FORGE 평가 submodule의 고정 SASY 원본(`6dedd2b`)이 Datalog `policy.dl`을 실제 엔진에서 평가해 정상 `send_summary`를 허용하고, 외부 note와 민감 report 모두에 의존한 `send_summary`를 실행 전 거부하여 인메모리 delivery 수를 0으로 만드는가?
- **원래 주장:** [원저자 예제 README](https://github.com/sasy-labs/sasy/tree/main/examples/message-flow)는 scripted run에 모델 API가 없지만 policy decision/dependency는 실제 SASY engine에서 나온다고 설명한다. [`demo.py`](/home/cclab/controllable_agent/third_party/guided-sasy-for-forge-6dedd2b/examples/message-flow/demo.py:40)는 `check_tool_call` 이후 authorized이면 `sent.append(...)`를 한다.
- **예상 결과:** `sensitive only`는 `ALLOW`, `sent=1`; `untrusted + sensitive`는 `DENY`, `sent=0`.
- **반증 관찰:** 엔진 시작/정책 컴파일 실패, 정상 거부/비인가 허용, 효과 수가 예측과 다름, 원본 checkout의 변경.
- **최소 비용:** 로컬 Docker/CPU, Python SDK; 모델/API 비용 USD 0. 원저자 코드에서 `--live`는 사용하지 않는다. Docker build는 5분 상한. 기존 컨테이너/포트는 건드리지 않는다.
- **완료 조건:** 고정 commit, engine image SHA, 정책 SHA, 명령/로그, Allow/Deny와 전후 효과 수 기록. source build 불가 시 그 원인을 남기고 동일 조건의 재개 명령 제시.

## 소스·안전 범위

- FORGE clone의 submodule 지시 commit: `6dedd2bc15da491d14ec07f87c0f1ef4d339efd6`. 동일 commit의 `/home/cclab/controllable_agent/third_party/guided-sasy-for-forge-6dedd2b` clean checkout을 사용. 최신 별도 `third_party/sasy`는 `7dc9e524c5b1979b91d16b9d573219e358a6c332` (2026-10-22)로 **다른 판본**이다.
- [AGENTS.md](/home/cclab/controllable_agent/third_party/guided-sasy-for-forge-6dedd2b/AGENTS.md:1)는 checkout에서 build한 engine으로 테스트하도록 지시한다. 호스트에 cargo/Soufflé/protoc 없음. 먼저 리뷰한 `Dockerfile`의 checkout 기반 Nix build를 고유 `sasy-k08-6dedd2b` image로 5분 제한 시도한다. release image `ghcr.io/sasy-labs/sasy:0.5.1`은 동일 version 이름이지만 이 checkout의 정확한 build라는 증거가 없어 source reproduction으로 간주하지 않는다.
- Docker 컨테이너/볼륨 이름 후보 `sasy-k08-6dedd2b`, `sasy-k08-6dedd2b-data`; loopback port 후보 `15189`; 실행 전 충돌 점검. 현재 다른 실험의 OpenShell과 SREGym 컨테이너는 보존.
- 정책은 [`examples/message-flow/policy.dl`](/home/cclab/controllable_agent/third_party/guided-sasy-for-forge-6dedd2b/examples/message-flow/policy.dl:1). `IsAuthorized(send_summary)`와 두 원천 의존시 `Unauthorized(send_summary)`를 함께 정의하므로 Deny 우선순위도 시험한다.
- 효과 관측은 **합성 문서·인메모리 `sent`**. 실메일/API 서비스 효과 아님. 메시지·의존 간선은 예제의 수동 instrumentation; 다른 framework/미계측 경로까지 보장하지 않는다.

## 실행 로그와 판정

[build.log](build.log)의 원본 checkout Dockerfile 빌드는 Nix가 pinned source/dependency를 내려받고 Rust crate를 컴파일하던 약 215초 지점에서 `Canceled: context canceled`로 종료됐다. `sasy-k08-6dedd2b` 이미지가 생성되지 않았고 SASY engine, `demo.py`, PEP Allow/Deny는 실행되지 않았다. **`NOT_RUN_BUILD_INTERRUPTED`**이며 정책 실패 또는 보안 반례가 아니다. 실행 환경의 작업 중단 때문에 빌드가 끊겼고 동일 빌드를 반복하면 상당량을 다시 컴파일해야 한다. 이 세션은 비용·시간 대비 이미 확보한 Progent/OpenShell/AutoCedar 경계 증거를 우선하여 반복하지 않는다.

재개 시 `third_party/guided-sasy-for-forge-6dedd2b`에서 checkout Dockerfile의 image 빌드를 충분한 시간 상한·고유 tag로 다시 실행한 뒤 README의 scripted `uv run examples/message-flow/demo.py --no-pause --quiet`를 별도 SDK 환경과 고유 loopback 포트에 연결한다. 빌드가 완료되기 전에는 source commit과 다른 release image 실행을 논문 commit 재현으로 표기하지 않는다. 다른 OpenShell/SREGym 컨테이너는 변경하지 않았다. 인증 값·생성 TLS 키·Docker 볼륨 내용은 기록하지 않는다.
