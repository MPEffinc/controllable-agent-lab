# K01–K15 원문·공식 코드·실행 자원 레지스트리

2026-11-24 UTC 조회. 상세 URL·판본·실행 전제는 [K01–K08 출처 감사](agent_registry_a.md), [K09–K15 출처 감사](agent_registry_b.md)에 있다. `원격 HEAD`는 조회일 스냅샷이며 **논문 평가 commit으로 검증되지 않았다**. `LOCAL`은 코드 확보, `RUN`은 범위를 명시한 실행만 뜻한다. 소스 라이선스가 `UNKNOWN`이면 논문의 공개 라이선스로 대체하지 않는다.

| ID | 원문/공식 문서 | 원저자 코드 판정·데이터 | 고정 commit / 라이선스 | 로컬 상태·실행 조건 |
|---|---|---|---|---|
| K01 Conseca | [HotOS 2025, arXiv v3](https://arxiv.org/html/2501.17070v3) | 원문에 공개 artifact 링크 미확인; 합성 task 설명 | `UNKNOWN` / `UNKNOWN` | 코드 미확보; Gemini/합성 환경 요구. **코드 없음 단정 아님** |
| K02 DRIFT | [NeurIPS 2025, v3](https://arxiv.org/html/2506.12104v3) | [저자 프로젝트가 연결한 코드](https://github.com/SaFo-Lab/DRIFT), AgentDojo/ASB/AgentDyn | `6fd3df4763fad77398c3c273c2a4fe14dd50f7ea` / MIT | `third_party/drift` LOCAL, 모델 API 필요, 이번 세션 RUN 안 함 |
| K03 Progent | [arXiv v3 Appendix A](https://arxiv.org/html/2504.11703v3) | 논문 지정 [sunblaze-ucb/progent](https://github.com/sunblaze-ucb/progent), AgentDojo/ASB | 로컬 `b02783b896d4bf01a2adf24738015e258db8d35b` / MIT; 원격 HEAD `3e797539fbcd55b92459d627e29fdaef16b9089a` | `third_party/progent` LOCAL; 원본 wrapper [4조건 로컬 효과 RUN](reproduction_log.md), 논문 E2E 아님. 지시서의 `lindsey98/progent`는 논문 지정 artifact가 아님 |
| K04 PAuth | [arXiv v2](https://arxiv.org/html/2603.17170v2) | 원문 공식 구현/자체 데이터 링크 미확인 | `UNKNOWN` / `UNKNOWN` | 코드 미확보, 저자 server-side 서술 분석만 가능 |
| K05 Cedar | [OOPSLA 2024, v2](https://arxiv.org/html/2403.04651v2) | [원저자 Rust/CLI](https://github.com/cedar-policy/cedar), 별도 [Lean 명세](https://github.com/cedar-policy/cedar-spec) | `6eea3a4ad86aab30b59e67a3d2d16426f4ff212b` / Apache-2.0 | `third_party/K05-cedar` LOCAL, detached clean. Cargo 없음; 별도 공식 CLI v4.12.0으로 [조건부 결정·로컬 effect RUN](runs/K05_conditional_alternative_20261124/result.md), OOPSLA 당시 평가 판본은 아님. Lean repo 미확보 |
| K06 AutoCedar | [arXiv v2](https://arxiv.org/html/2607.03656v2) | [원저자 코드·gold 데이터](https://github.com/neselab/cedar-synthesis-engine), 별도 [동일 저자 조직 CedarBench repo](https://github.com/neselab/cedarbench), PyPI 패키지 | 본체 `a0cf180977d799cf943514b67ffc260fc579b9a5`, benchmark `26539202f02af19466002cecc3db42fbada40702` / 둘 다 Apache-2.0 | `third_party/K06-autocedar`, `third_party/K06-cedarbench` LOCAL, detached clean. [제공 workspace 형식 RUN](runs/K06_verify_20261124/manifest.md): 정상 plan 6 PASS/과권한 ceiling FAIL; 모델 합성·서비스 효과 아님 |
| K07 NGAC-IR | [arXiv v1](https://arxiv.org/html/2611.26941v1) | 원문은 artifact를 출판 시 공개 예정으로 기술; Text2NGAC artifact와 구분 | **NGAC-IR 저자 코드** `UNKNOWN` / `UNKNOWN`; **별도 공식 NIST PM 3.3.0** `7cc6b615354c871099d84bab8ec6667ef7c3e417` / `LICENSE.md` NIST Software Licensing Statement | NGAC-IR 코드 미확보·저자 생성 실험 재현 불가. NIST PM 공식 engine으로 [독립 조건 경계 6조건 RUN](runs/K07_condition_boundary/result.md) |
| K08 FORGE/SASY | [arXiv v4](https://arxiv.org/html/2602.16708v4) | 저자 [SASY 구현](https://github.com/sasy-labs/sasy)과 [FORGE 평가](https://github.com/sasy-labs/forge) 분리 | SASY `7dc9e524c5b1979b91d16b9d573219e358a6c332`; FORGE `ecc5ff9f7576f2669249609d9002c07674947913` / Apache-2.0 | `third_party/sasy`, `third_party/forge` LOCAL; Docker/Rust/Soufflé/모델 전제, 이번 세션 RUN 안 함 |
| K09 AuthGraph | [arXiv v1 §5](https://arxiv.org/html/2605.26497v1#S5) | 원문은 구현을 향후 공개 예정으로 기술 | `UNKNOWN` / `UNKNOWN` | 원저자 코드 미확보 |
| K10 CaMeL | [arXiv v2](https://arxiv.org/abs/2503.18813) | [google-research/camel-prompt-injection](https://github.com/google-research/camel-prompt-injection) 원저자 연구 artifact | `f083b6b396399d3b3c7f2ddaf613a5945eaf32d8` / Apache-2.0 | `third_party/camel` LOCAL; 모델 키 필요한 E2E 미실행 |
| K11 Multi-CaMeL | [arXiv v1](https://arxiv.org/html/2610.05640v1) | [저자 multiagentdojo](https://github.com/james-pete/multiagentdojo), Sequrity Control 백엔드는 별도 | `e71647382155dc6949d6ccf9a9d7ec7cf429b856` / MIT | `third_party/multiagentdojo` LOCAL; 공개 fake-client [25 test RUN](runs/K11_fake_client_20261124/manifest.md), 실제 Deny/논문 ASR 재현 아님 |
| K12 ControlValve | [arXiv v2](https://arxiv.org/html/2510.17276v2), ICLR 2026 표기 | 저자 출판 페이지의 code href가 비어 있고 원문 공식 repo 확인 못함 | `UNKNOWN` / `UNKNOWN` | 코드 미확보; 내부 agent tool/effect 실행 재현 불가 |
| K13 ActPlane | [arXiv v2](https://arxiv.org/abs/2606.25189) | [eunomia-bpf/ActPlane](https://github.com/eunomia-bpf/ActPlane) 원저자 구현 | `1cbb4d0f40e2bc6042d6883f045fe8e0e838b168` / MIT | `third_party/K13-actplane` LOCAL, detached clean; eBPF 실제 run은 권한 필요, 미실행 |
| K14 OpenShell | [공식 문서 v0.1.9](https://docs.nvidia.com/openshell/v0.1.9/), 논문 아님 | [공식 프로젝트](https://github.com/ai-openshell/openshell); 이전 `NVIDIA/OpenShell` URL redirect | 기존 실험 소스 `ce58cf8e9b953281352d98a637e41616295b1318` / Apache-2.0; 최신 원격 HEAD는 [상세 감사](agent_registry_b.md) | `local/openshell-20261124/source-v0.1.9` LOCAL; 이전 Docker 집행/Prover [원시 재감사](reproduction_log.md). `third_party/openshell`은 다른 커밋 |
| K15 CONTINUITY | [arXiv v1](https://arxiv.org/abs/2609.05269) | [zast-ai/continuity](https://github.com/zast-ai/continuity) 원저자 reference verifier/suite | `59cfe60930d247d1890b366ded686c718020a11e` / MIT | `third_party/continuity` LOCAL, 기존 R2/R3 합성 통합 결과 보존; 이번 세션 재실행 안 함 |

**확보 집계:** 10/15는 원저자/공식 공개 코드의 고정 commit 로컬 사본이 있다(K02, K03, K05, K06, K08, K10, K11, K13, K14, K15). K01/K04/K07/K09/K12는 조사한 원문에서 공식 공개 코드가 확인되지 않아 `NOT_FOUND_IN_CHECKED_SOURCES`이며 `NO_CODE_EXISTS`가 아니다. 새 clone K05/K06/K13은 원본 코드에 패치하지 않았다. 태그·release·논문 평가 commit의 대응은 개별 확인 전 `UNKNOWN`이다.

## 데이터·패키지·태그·유지 상태 보충

| ID | 벤치마크/데이터의 접근 상태 | 배포·태그/유지 상태 |
|---|---|---|
| K01 | 논문 합성 20 task 설명; 공개 데이터 링크 `UNKNOWN` | 공개 패키지/태그/유지 `UNKNOWN` |
| K02 | 저자 repo에 AgentDojo/ASB/AgentDyn 평가 코드 | 소스 설치; 논문 평가 tag `UNKNOWN`; 현재 원격 HEAD 확인, 유지 정책 `UNKNOWN` |
| K03 | 공식 repo에 AgentDojo/ASB·실행 스크립트 | `secagent` pip editable; 논문 평가 tag `UNKNOWN`, 원격 HEAD와 로컬 commit 다름; 유지 정책 `UNKNOWN` |
| K04 | 논문 자체 평가 task 서술, 공식 데이터 링크 `UNKNOWN` | 패키지/태그/유지 `UNKNOWN` |
| K05 | 원저자 Rust 테스트·예제와 별도 Lean spec | Cargo/CLI; 이번 확인 commit과 OOPSLA 2024 논문 평가 tag의 대응 `UNKNOWN`; 원격 HEAD 확인 |
| K06 | 원저자 본체 repo의 gold-reference dataset과 별도 CedarBench repo. **현재 benchmark README 226 scenario**, 논문 v2 평가 221로 판본 차이; gold 200 생성 trace는 별도 공개 경로에서 미확인 | PyPI `autocedar` 및 repo `pyproject.toml` 0.2.0; clone은 원격 HEAD, 논문 평가 tag 대응 `UNKNOWN` |
| K07 | 390 graph-decision replay와 714문장 의미 평가는 저자 보고; artifact 출판 시 공개 예정. [독립 PM 3.3.0 6조건](runs/K07_condition_boundary/result.md)은 별도 | NGAC-IR 패키지/태그/유지 `UNKNOWN`; NIST PM 3.3.0 tag와 pinned `protos` submodule만 별도 확보 |
| K08 | FORGE 평가 repo·결과, SASY는 별도 submodule | source/Docker 개발 경로; 평가 submodule commit `6dedd2b`와 현재 SASY HEAD가 다름; 논문 평가 tag `UNKNOWN` |
| K09 | AgentDojo/AgentDyn 평가 저자 보고; 공개 artifact `UNKNOWN` | 패키지/태그/유지 `UNKNOWN` |
| K10 | 연구 repo에 AgentDojo 실험 코드 | source/uv; README가 연구 artifact의 비유지·비지원 상태 명시 |
| K11 | 저자 repo에 MultiAgentDojo 평가, AssetOpsBench 별도 공개 범위 `UNKNOWN` | source/uv, Sequrity API 별도; 논문 평가 tag 대응 `UNKNOWN` |
| K12 | 논문 평가 서술, 공식 데이터/코드 링크 `UNKNOWN` | 패키지/태그/유지 `UNKNOWN` |
| K13 | 저자 repo 예제/설정, 논문 평가 dataset 대응 `UNKNOWN` | Cargo CLI; 실제 eBPF runtime은 Linux 권한 필요; 평가 tag/유지 정책 `UNKNOWN` |
| K14 | 공식 문서·policy 예제·release | 기존 실행은 공식 `v0.1.9` tag 소스; 현재 원격 HEAD는 별개. 프로젝트 이전/redirect 확인, 장기 유지 보장 `UNKNOWN` |
| K15 | 원저자 reference verifier와 deterministic fault suite | Python requirements/source 실행, 논문 평가 tag 대응 `UNKNOWN`; 현재 원격 HEAD와 로컬 일치 |

`UNKNOWN`은 자료가 없다고 확정한 것이 아니다. 의존성의 정확한 패키지 해시는 실제 실행한 K11과 소스/lock을 확보한 K03/K06에 한해 [환경 매니페스트](environment_manifest.md)에 기록했다. 다른 논문의 논문 평가 당시 의존성 재현성은 아직 검증하지 않았다.
