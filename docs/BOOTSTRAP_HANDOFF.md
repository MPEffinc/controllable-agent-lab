# Bootstrap 결과 및 GitHub 인계

감사일 2026-11-15 (Asia/Seoul). 이번 작업은 **기존 실행 증거의 검증과 인계**다. 새 실험·대규모 설치는 시작하지 않았다. `.env`/API key·토큰·venv·외부 repo·wheel·전체 raw trial은 커밋하지 않는다. 과거 연구 코드·로그를 삭제하거나 현재 연구 결과로 재사용하지 않았다.

## 원격에서 먼저 읽을 순서

대상: https://github.com/MPEffinc/controllable-agent-lab

브랜치: `bootstrap/mas-security-keypapers` (기반 `baca6088f106d19a226feee84edc0f8cedec24be`). 이번 감사 시작 시 기존 브랜치는 `exp/service-observation-gates`, origin은 `git@github.com:MPEffinc/controllable-agent-lab.git`. 원격을 교체하지 않았다. 최종 commit SHA는 GitHub 브랜치와 최종 보고에서 확인한다.

1. [CONTEXT.md](../CONTEXT.md): 현재 목표·연구 범위·검증 상태.
2. [REPO_AUDIT](REPO_AUDIT.md): 10개 repo URL/SHA/license, 원본 entrypoint·정책·effect·scorer 연결.
3. [ENV_SETUP](ENV_SETUP.md): 실제 Python/패키지, 성공·실패 명령, 재생성 조건.
4. [command-index](../results/setup/bootstrap-20261114/command-index.json), [source-manifest](../results/setup/bootstrap-20261114/source-manifest.json), [environment-inventory](../results/setup/bootstrap-20261114/environment-inventory.json).
5. [A2A summary](../results/setup/bootstrap-20261114/a2a-asrf-original/summary.json), [stdout/stderr](../results/setup/bootstrap-20261114/a2a-asrf-original.log), [전체200건 sink 이벤트](../results/setup/bootstrap-20261114/a2a-asrf-observations.jsonl).

GitHub에서 main만 읽으면 과거 SREGym 연구가 보일 수 있다. 이 브랜치나 최종 보고의 commit permalink를 사용한다.

## 확인 결과

| 항목 | 상태 | 근거·해석 |
|---|---|---|
| 10개 외부 source의 URL/고정 SHA | VERIFIED / 일부 PARTIAL | agentcap·OpenShell source 확장 timeout, FORGE sparse. 전부 full source라고 주장하지 않음 |
| A2ASecBench install | VERIFIED | Python3.10.12, 43 distributions, install exit0 |
| A2A 원본 offline ASRF | VERIFIED | exit0, attack100/control100. attack ASR1.0/control pass1.0, 실제 localhost trap GET |
| A2A 전체 pytest/release validator | FAILED | 각 timeout124, 최종 pass summary 없음 |
| CaMeL install | VERIFIED | original frozen lock/no-dev,121 distributions; 테스트 NOT_RUN |
| Progent install | VERIFIED | secagent0.1.0 editable,25 distributions; wrapper 동작/ON-OFF NOT_RUN |
| ORBIT wheel download/checksum | VERIFIED | official v1.0.4, source revision `076104ae2479595b4c973df7758131401e684c7d` |
| ORBIT install / two-agent 실행 | FAILED / NOT_RUN | install timeout124; Python3.11.17 venv만 존재, packages0 |
| DRIFT·독립 AgentDojo·SASY/FORGE·IntentCap·OpenShell runtime | NOT_RUN | 소스 감사와 설치 성공을 구분 |
| 정책 OFF/ON·full model benchmark·원본 논문 전체 재현 | NOT_RUN | 실험 결과를 생성하거나 기대값으로 대체하지 않음 |

A2A ASRF는 정책이 없는 결정론적 coordinator의 fixture 실행이다. 공격100/100 성공은 LLM 취약성이나 기존 방어의 보장 위반을 의미하지 않는다. 전체 필드 `asr=0.5`는 control까지 분모에 포함한 수치다. 로그에 BrokenPipeError1건이 있어도 프로세스 exit는0이고200행이 생성됐다. 이는 전체 test suite 성공과 다르다.

## 원격 증거 검증

Python3 표준 라이브러리만 있으면 fresh clone에서 다음을 실행할 수 있다. benchmark/API/설치는 실행하지 않는다.

```bash
git clone --branch bootstrap/mas-security-keypapers https://github.com/MPEffinc/controllable-agent-lab.git
cd controllable-agent-lab
python3 scripts/audit_bootstrap.py --verify-saved
```

검증 범위:28개 기존 command의 log SHA256/exit/metadata,10개 source manifest의 URL/SHA 형식,200개 ASRF sink projection과 summary의 집계,4개 환경의 package snapshot 일치. 이는 **공유된 증거의 정합성**을 검사한다. 실제 외부 source의 독립 재설치나200건 재실행은 별도 절차다. 2건 full-event 표본도 제공한다. raw1.45MB는 로컬 보존하고 hash만 공유하며, projection은 원본에서 sink 이벤트와 score/count 필드를 추출한 파생 증거라고 표시한다.

이번 감사에서는 Git index에서 공유 대상만 별도 디렉터리로 추출해 위 명령을 실행했고 **exit0**이었다. 외부 checkout·venv·전체 raw 없이 실행한 확인 기록은 [handoff verification](../results/handoff-20261115/verification.json)이다. 새 benchmark 실행 결과가 아니다.

`python3 scripts/audit_bootstrap.py`(옵션 없음)는 원시 trial·third_party·venv가 있는 기존 로컬 환경에서 snapshot을 재생성하는 명령이다. fresh clone에서 그대로 실행하는 명령이 아니다. requirements는 관측 package inventory이며 upstream lock 또는 검증된 재설치 결과가 아니다. ORBIT의 빈 package snapshot은 실패의 증거다.

## 실패 원인과 다음 진입 조건

| 미완료 항목 | 입증된 원인/관측 | 다음 조건 |
|---|---|---|
| ORBIT dependency install | download 도중 TIMEOUT/124; 구체 네트워크 원인 미확정 | 같은 release wheel/Inspect0.3.263 설치 성공 후 공식 기본·negative-control smoke |
| A2A pytest/validator | 제한시간 초과, 상세 위치 로그 없음 | 원본 개별 offline test로 좁히고 verbose 진단. 원본을 patch해서 통과시키지 않음 |
| agentcap·OpenShell source 확장 | sparse-checkout timeout124 | 필요한 source만 별도 재확보; agentcap 라이선스 검증도 필요 |
| Progent 정책 비교 | 파일만 준비, 실행 기록 없음 | 아래 component check를 별도 실험 작업에서 실행해4조건과 실제 outbox effect 확인 |
| CaMeL/DRIFT/AgentDojo 원본 benchmark | 테스트·모델 실행 NOT_RUN | 각자 version pin·mock/API 경로 점검. paid run은 호출/토큰/비용 상한 승인 |
| FORGE/SASY | engine/toolchain 미설치 | 프로젝트 내부 설정 경로·소유한 로컬 엔진으로 준비; 기존 ~/.sasy/서비스 변경 금지 |
| MultiAgentDojo 등 | 공식 code URL 미확인 | 논문/저자/official artifact 역방향 연결 확인 후 clone |

다음 한 가지 후보는 설치된 Progent 원본 wrapper의 credential-free component check다. 현재는 **미실행**이며 새 method 개발이나 논문 재현으로 부르지 않는다.

```bash
python3 scripts/bootstrap_run.py --name progent-policy-first --timeout 120 -- third_party/progent/.venv/bin/python experiments/progent_policy_component.py --output-dir results/setup/progent-policy-first
```

다음 원본 재현으로 진입할 수 있는 환경은 **A2ASecBench offline(실행 확인), CaMeL·Progent(설치 확인)**이다. CaMeL은 no-dev 설치라 pytest 준비가 필요하고, Progent SDK 실행 호환성도 미검증이다. ORBIT은 설치 재개가 선행 조건이다. 세부 비교와 E1–E4 대조군은 [EXPERIMENT_PLAN](EXPERIMENT_PLAN.md).

Codex는 로컬 실행/로그/명령/manifest를 남기고, ChatGPT는 고정 commit에서 이를 읽어 관찰·가정·해석을 분리해 검토한다. 기존 방법의 원본 benchmark/defense ON/OFF부터 확인한 뒤 검증되지 않은 gap이나 새 방어의 필요성을 논한다.
