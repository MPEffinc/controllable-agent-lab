# 재현 및 실행 로그

## 2026-11-24: Progent 원본 wrapper의 로컬 effect

- 질문·예측·반증·비용·종료 조건: [사전 등록](runs/progent_manual_boundary/prereg.md).
- 종류: `COMPONENT_REPRODUCTION`, 원저자 AgentDojo/논문 수치 재현 아님. 원본 `third_party/progent` commit `b02783b896d4bf01a2adf24738015e258db8d35b`; 원본 `secagent/tool.py` SHA-256 `59b2cd642a9c29f2459e919720fae935a5f6f99a2a5fa0c17f1ea95e9efbcd52`. 원본 소스 수정 없음.
- 환경: Python 3.10.12, 기존 격리 venv `third_party/progent/.venv`, 모델 호출 0, seed 해당 없음, API 비용 USD 0. `policy_model` 기본 이름은 모듈 import 로그에만 나타나며 실제 요청하지 않았다.
- 명령: 저장소 루트에서 `third_party/progent/.venv/bin/python docs/access_control_empirical_20261124/runs/progent_manual_boundary/run.py`.
- 입력·활성 정책·전후 서비스 상태·예외·경고 원시 기록: [results.json](runs/progent_manual_boundary/results.json). 서비스는 실서비스가 아닌 로컬 `ledger.json`이다. 모든 case에서 초기 상태 `[]`.

| 조건 | 활성 정책 | 결정과 effect | 후 상태 |
|---|---|---|---|
| 정상 | `recipient=approved`, `amount=10`만 허용 | 반환 `recorded`; 함수 실행 | 승인 항목 1건 |
| 비인가 | 같은 정확 정책, `recipient=unapproved` | `ValidationError`; 함수 실행 안 됨 | `[]` |
| 과권한 | 인자 제약 없는 허용 | 반환 `recorded`; 함수 실행 | 비인가 항목 1건 |
| 정책 미설정 | `None` | 경고 출력 후 반환 `recorded`; 함수 실행 | 비인가 항목 1건 |

PEP는 `secure_tool_wrapper`에서 실제 함수 호출 전에 `check_tool_call`을 부르는 지점(`secagent/tool.py` 718–759행)이다. 수동 정책 검사 자체는 `check_arg`, `_check_tool_call`, `check_tool_call`(같은 파일 508–590행)이다. 정책 미설정 때 `check_tool_call`이 경고 후 반환하는 분기는 575–577행. 여기서 직접 확인한 것은 **이 wrapper를 거친 호출**의 효과이며 다른 경로의 완전 중재는 검증하지 않았다. 과권한/미설정 조건은 생성기 실패의 측정이 아니고 설정 경계의 관찰이다.

## 2026-11-24: Progent 생성 규칙의 포함관계 검사

- 질문·예측: [사전 등록](runs/progent_subset/prereg.md). 종류 `COMPONENT_REPRODUCTION`, 원본 `secagent/policy_analysis.py:381`의 생성 규칙(priority 100) 검사만 호출.
- 명령: `third_party/progent/.venv/bin/python docs/access_control_empirical_20261124/runs/progent_subset/run.py`; 모델/API 호출 0, seed 해당 없음. 원시 입력·SMT stderr·결과는 [results.json](runs/progent_subset/results.json).
- 관측: 동일·좁힌 enum은 `True`; 확대 enum은 `False`와 반례 `"unapproved"`; 신규 tool은 `False`. 이 네 조건은 지정 JSON Schema의 포함관계 검사 경로를 확인한다. **실제 갱신 경로의 subset 검사는 `SECAGENT_ONLY_ALLOW_NARROW=True`일 때만 호출**되며 원본 코드 기본값은 `False`(`secagent/tool.py:465–482`). 이번에는 갱신 함수나 승인 UI를 호출하지 않았고, 초기 정책의 의미·수동 정책·모든 JSON Schema 구문을 검증하지 않았다.

## 2026-11-24: Multi-CaMeL 공개 fake-client 테스트

- 종류: `AUTHOR_ARTIFACT_FAKE_INTEGRATION`, 원저자 고정 commit `e71647382155dc6949d6ccf9a9d7ec7cf429b856`, 모델 API 0, 비용 USD 0. 사전 질문·원시 명령·lock hash·결과는 [실행 manifest](runs/K11_fake_client_20261124/manifest.md)와 [raw.log](runs/K11_fake_client_20261124/raw.log).
- 25개 테스트 통과. 코드에서 agent-as-tool 정책 생성·Sequrity 요청 전달, scripted 정상 경로의 인메모리 `inbox.sent` 변화를 확인. fake client가 실제 `hard deny`를 수행하지 않으므로 비인가 입력 차단이나 원저자 benchmark ASR의 재현은 `NOT_ESTABLISHED`.

## 2026-11-24: AutoCedar 제공 workspace 형식 검증

- 종류: `AUTHOR_ARTIFACT_FORMAL_CHECK`, 모델/API 0. 사전 질문·도구 해시·명령·원시 결과는 [K06 manifest](runs/K06_verify_20261124/manifest.md).
- 공식 Cedar CLI v4.12.0 experimental과 cvc5 v1.4.2로 원저자 `autocedar verify`를 실행. 제공 candidate는 6개 plan 검사 PASS, `loss: 0`; 사본에 넓은 View permit을 추가한 대조군은 ceiling 포함 실패, Cedar 요청 반례, `loss: 1`.
- 판정은 policy/target의 정형 관계만 다룬다. 사용자 의도와 독립 gold, 서비스 effect는 시험하지 않았다. Cedar CLI 버전은 AutoCedar README 예시 4.10.0과 달라 논문 당시 환경의 동일 재현으로 부르지 않는다.

## 2026-11-24: SASY/FORGE 고정 평가 commit 실행 시도

- 종류: `NOT_RUN_BUILD_INTERRUPTED`. [사전 질문과 build log](runs/K08_minimal_20261124/manifest.md)은 FORGE 평가 submodule SASY `6dedd2b`의 원본 Dockerfile/Nix source build를 기록. Rust 의존성 컴파일 중 context cancellation으로 image가 완성되지 않았다.
- 실제 policy/PEP Allow/Deny·인메모리 delivery effect는 **관측되지 않았다**. 이 결과를 원저자 구현 실패 또는 정책 위반으로 분류하지 않는다. 외부 모델/API 비용 USD 0.

## 2026-11-24: AutoCedar gold dataset 무결성

- [사전 질문/결과](runs/K06_gold_integrity_20261124/result.md): 원저자 `verify_gold.py`가 200개 저장 case의 spec/registry 재컴파일 결과와 gold policy/schema/AST의 일치를 보고(exit 0). 모델/API 0.
- 이것은 저장된 structured gold 산출물의 결정적 일치이며 자연어 승인 의도의 독립 검증이 아니다.

## 2026-11-24: 동일 승인 호출의 하위 파일 효과와 Docker 대조

- [사전 질문·원시 결과](runs/H5_dispatch_effect/result.md): Progent wrapper의 동일 `run_job(task_id='approved')`가 host와 Docker 두 조건에서 허용됐다. host에서는 정상 출력과 합성 비인가 출력이 함께 생겼다. script·정상 input만 mount한 Docker 조건에서는 정상 출력은 생기고 비인가 출력은 없었다. 모델/API 0.
- 이는 child 효과의 관측 계층을 구분하고 해당 합성 파일 경로에서 기존 자원 경계가 해결함을 확인한 결과다. OpenShell/Progent 원저자 평가 수치의 재현이 아니다.

## 2026-11-24: 위임 간선 철회·다중 witness·원자 effect fence 합성 대조

- [사전 등록·원시 로그·결과](runs/H3_edge_fence/result.md): 저자 VERA artifact의 원본 `target_set_l2` 함수를 직접 호출했다. A 단독 경로에서 C가 철회 대상, X 독립 경로가 있으면 C는 대상 아님. **그 밖의** OR/AND witness, 원자 수락/fence, receipt 및 effect ledger는 이 조사에서 작성한 독립 in-memory fixture이다. 원저자 VERA/Authorization Revocation/원격 provider 재현이 아니다.
- 세 일정: 철회 전 수락 receipt의 늦은 effect 1을 `pre-fence`로 별도 분류; 철회 후 A 단독·A∧X 신규 수락과 effect 0; X 독립 OR의 정상 effect 1. 의도적으로 edge/fence 검사를 생략한 stale 대조군은 post-fence 비인가 effect 1. 모든 assertion 통과, [raw.json](runs/H3_edge_fence/raw.json)에 정책 witness·generation·receipt·전후 effect가 있다.
- 첫 실행은 원본 package `__init__`의 무관한 `cryptography` 의존성에서 멈췄다. 원본 두 모듈만 읽는 namespace shim을 fixture에 넣은 두 번째 실행이 exit 0; 원저자 파일 수정 없음. Python 3.12.15, 모델/API 0, 외부 비용 USD 0. 추상 원자 sink에서 조합이 **가능함**을 보이는 반례일 뿐 실제 provider의 원자성이나 비동기 경로 완전성을 입증하지 않는다.

## 2026-11-24: OpenShell v0.1.9 기존 실행 기록 재감사

- 종류: `PRIOR_RUN_VERIFIED`, 이 세션의 새 실행 아님. 원래 보고서 [results.md](../experiments/20261124_openshell/results.md), 실행 안내 [README.md](../experiments/20261124_openshell/README.md). 공식 태그 소스 `ce58cf8e9b953281352d98a637e41616295b1318`; 과거 `third_party/openshell` clone과 다른 버전.
- 원시 파일 직접 대조: `local/openshell-20261124/runs/sandbox-20261124T072945Z/terminal.log`은 기본 정책 `/tmp` 쓰기 성공, 제한 정책 `/tmp` 쓰기 `Permission denied`, `LANDLOCK ... Applying ... [abi:V3 compat:HardRequirement ...]`, Supervisor `NET:OPEN ... DENIED ... example.com:80`를 기록한다. 같은 기존 보고서의 Docker `readonly_rootfs=false`, UID 1000, `/tmp` 쓰기 POSIX 권한과 함께 해석한다.
- `local/openshell-20261124/runs/prover-20261124T072730Z/{contained,exceeds}.json`은 별도 정형 검사 `within_boundary`와 `/tmp` write 반례의 `exceeds_boundary`를 기록한다. 이것은 runtime 집행이 아니다.
- 범위: 특정 파일/네트워크 정책, Docker workload, 원본 v0.1.9. Agent 정책 생성, 모든 syscall/서비스 효과, VM/Kata의 OpenShell 격리, 오프라인 Prover와 실제 집행의 등치는 검증하지 않았다.

## 2026-11-24: OpenShell v0.1.9 새 provider effective policy와 L7 효과

- 종류: `AUTHOR_PRODUCT_VERSION_RUN`, 공식 v0.1.9 소스 commit `ce58cf8e...`에 대응하는 릴리스 binary. [사전 등록](runs/K14_effective_20261124/manifest.md), [원시 정책·전후 상태·효과·정리](runs/K14_effective_20261124/result.md), [소스 경로 대조](deep_h2_effective.md). 별도 Gateway/SQLite/mTLS, 고유 sandbox, synthetic upstream. 유료 모델/API 0.
- credentialless profile을 명시 import한 뒤 provider attach `--wait` receipt `ready`/`policy_active=true`; base network 규칙은 0, effective에는 `_provider_h2pypi` 추가. Supervisor `CONFIG:LOADED` hash로 적용 확인. PyPI 실제 호출은 시험하지 않았다.
- 같은 `GET /blocked`: L7 `audit`에서 HTTP 200과 upstream ledger +1, L7 `enforce`에서 HTTP 403과 ledger +0. 같은 `enforce`의 정상 `GET /ok`는 HTTP 200과 ledger +1. audit shorthand `ALLOWED`는 rule 위반 여부를 직접 드러내지 않았고 원본 OCSF JSON은 미수집.
- 담당 실험 세션이 사용량 한도로 중단된 뒤, 이 조사 소유 Gateway와 upstream 두 PID만 SIGTERM으로 정리하고 포트·컨테이너 상태를 확인했다. [실제 CLI argv·순서·초기 실패와 수정](runs/K14_effective_20261124/commands.md)을 원시 로그에서 복원했다. 기존 `oslab-*`/`sregym-*`는 보존.

## 2026-11-24: OpenShell 전체 effective policy의 prover 대조

- 종류: `AUTHOR_PRODUCT_VERSION_FORMAL_CHECK`. [사전 등록·입력 hash·원시 JSON·결과](runs/H7_policy_gate_20261124/result.md). 공식 v0.1.9 prover에 K14 run의 base와 provider 포함 effective policy를 각각 동일한 승인 상한과 비교했다. 모델/API/Docker 실행 0.
- base candidate는 exit 0 `within_boundary`; provider 포함 full candidate는 exit 1 `exceeds_boundary`와 network L4 `pypi.org:443` 반례. 이 반례는 정형 증인이지 실제 네트워크 연결이 아니다.
- 전체 정책을 입력하면 이번 확대를 검출하는 **기존 수단**이 있으므로 H7의 ‘검사 방법 부재’ 가설을 이 형상에서 기각한다. 자동 배포 gate가 실제로 적용됐는지, 승인 목표가 올바른지, 다른 policy 종류도 증명되는지는 이 검사에서 나오지 않는다.

## 2026-11-24: K07 조건부 권한에 대한 Cedar 기존 대안

- 종류: `INDEPENDENT_CEDAR_CONDITIONAL_ALTERNATIVE`. [사전 등록·정책·CLI SHA-256·원시 결과](runs/K05_conditional_alternative_20261124/result.md). 공식 Cedar CLI v4.12.0 실험 binary, 별도 요청 context, 인메모리 ledger. 모델/API/실서비스 0.
- 동일한 `read(doc)`에서 `registration_open=false`는 `DENY`/ledger 0→0, `true`는 `ALLOW`/ledger 0→1. 안전 조건 1/1, 정상 완료 1/1. 이 로컬 효과는 CLI 결과를 따르는 독립 wrapper의 기록이다.
- Cedar의 `when`과 신뢰된 request context가 단순 조건을 직접 해결하는 기존 수단임을 보여 준다. 사용자 의도 원본, context 값의 진실성, 상태 변화와 실제 provider commit의 원자성, K07 저자 생성기는 시험하지 않았다.

## 2026-11-24: NIST Policy Machine 3.3.0의 조건부 graph export 경계

- 종류: `INDEPENDENT_OFFICIAL_ENGINE_BOUNDARY_TEST`. [사전 등록·공식 고정 tag/submodule·Maven SHA512·정확 명령·원시 6행·전후 ledger](runs/K07_condition_boundary/result.md). NGAC-IR 저자 생성기가 공개되지 않아 **저자 390건 평가의 재현이 아니다**. 원본 NIST source clean, 격리 worktree에 test만 추가. Java 21/Maven 3.9.8, API/모델/실서비스 0.
- broad graph는 false/true 둘 다 PM Allow/ledger 0→1, strict graph는 false/true 둘 다 PM Deny/ledger 0→0. broad association+독립 앱 사전 guard는 false에서 PM graph 조회 Allow지만 PDP 미호출/ledger 0→0, true에서는 PDP Allow/ledger 0→1. 마지막 구성은 **우리의 대안**이고 논문의 strict+앱 구현은 아니다.
- 첫 build의 proto submodule 미초기화는 공식 고정 submodule을 초기화해 두 번째 build에서 해결했다. 원본 PM 정책 실패가 아니다. 정적 graph-only 조건 표현 한계를 effect로 확인했지만 앱/Cedar 대안이 고정 조건을 해결하므로 신규 메커니즘 Need를 입증하지 않는다. [H8 판정](h8_conditional_gap_verdict.md).

## 2026-11-25: Cedar 조건부 prohibition 기존 대안

- 종류: `INDEPENDENT_CEDAR_CONDITIONAL_PROHIBITION`. [사전 등록·공식 CLI·정확 명령·원시 결정·로컬 effect](runs/K05_conditional_prohibition_20261125/result.md). 무조건 permit + `registration_open=false`일 때만 적용되는 forbid. 조건 false는 `policy1` forbid로 Deny/ledger 0→0, true는 `policy0` permit으로 Allow/ledger 0→1. 모델/API/실서비스 0.
- K07 저자가 말한 strict graph의 조건부 prohibition 항상 적용과 대조되는 **기존 조건 PDP**의 최소 사례다. K07 생성·export 또는 실제 provider를 재현하지 않으며 신뢰된 최신 context 공급과 commit 원자성은 미검증이다.

## 2026-11-25: NIST PM의 복수 허용 route·조건부 금지 독립 대조

- 종류: `INDEPENDENT_OFFICIAL_ENGINE_ROUTE_COMPOSITION`. [사전 등록·고정 PM source·정확 Maven 명령·원시 7행·결과](runs/K07_route_composition_20261125/result.md). 공식 NIST PM 3.3.0의 PAP/PDP와 인메모리 ledger, 기존 격리 worktree/캐시. `mvn -o` 1회 성공, 유료 API/모델 0. NGAC-IR 저자 생성기/strict+앱 adapter 재현 아님.
- `registration_open=false`에 별도 무조건 허용 route가 있으면 전역 앱 gate는 PM이 허용할 요청을 거부/effect 0, 경로별 gate는 효과 1. 조건부 금지가 실제 inactive인데 정적 PM에 상시 export되면 PM Deny, 경로별 gate도 effect 0; 활성 금지에서는 Deny/effect 0이 의도와 일치. 7행은 설계된 반례 조건이며 발생률이 아니다.
- [같은 의미의 Cedar 규칙별 조건 6입력](runs/K05_route_composition_20261125/result.md)은 기대 결정/effect 6/6. 따라서 정적 graph+단순 앱 합성의 구체 과거부가 관측됐고 직접 기존 대안도 관측됐다. K07 원저자 경로와 동적 graph 갱신의 성질은 별도.

## 2026-11-25: Donno 공유키 확대 사례에 대한 CONTINUITY 원본 함수 독립 대조

- 종류: `SOURCE_NATIVE_CONTINUITY_INDEPENDENT_FINANCE_ADAPTATION`. [사전등록·후속 추가 대조·정확 명령·원시 JSON·전후 effect](runs/M1_continuity_amount_20261125/result.md). 공식 CONTINUITY 고정 source `59cfe60930d247d1890b366ded686c718020a11e`의 `verify_bundle → issue_permit → EffectBroker/FinalitySink`를 직접 호출. Python 로컬 SimulatedWorld/NonceLedger, 모델/API/원격 provider 0.
- Signed root EUR120/액션 EUR120은 `EXECUTED`, 로컬 effect 0→1. **같은 EUR120 root로 EUR9000**은 `E_ROOT_FIELD_CONSTRAINT`, permit 없음/effect 1→1. 위임 wildcard 확대도 `E_ROOT_SCOPE_EXCEEDED`/effect 불변. 실제로 EUR9000 root를 서명한 정상 상한 대조는 `EXECUTED`, effect 1→2. 추가 위임 입력은 첫 3입력 확인 뒤 **별도 사전등록**했다.
- 이는 [Donno §V-B](https://arxiv.org/html/2611.07050)의 공유 HMAC·네 참여자·보험 지급 실험을 재현하지 않는다. 원점 private key가 Hospital에 없고 서명 root와 최종 sink가 정확히 매개된다는 다른 전제를 가진 기존 대안의 동작만 확인했다. 넓은 root의 성공은 정책 목표의 적절성이 집행 정확성과 분리됨을 다시 보여 준다.

## 2026-11-25: EAL-Bench v2 공개 아티팩트 오프라인 감사

- 종류: `AUTHOR_CODE_OFFLINE_AGGREGATE_AUDIT`. [사전등록·공식 repo/commit·명령·저장 집계·해시·제한](runs/EAL_offline_20261125/result.md). 저자 코드 `51648690bc52d7a9c7ac080a2c67a784fe9d56cb`, Python 3.12.15 표준 라이브러리. 유료 API/모델/실서비스 0; 원본 checkout clean.
- `analysis.paper_results`는 **논문 v1 5-writer** 저장 count와 3 domain 표를 출력했으나 raw artifact 0/715, route 0/45 재계산. 별도 `analysis.extension_results`는 v2 extension 보존 입력 **200개 해시 일치**, 원본 raw extension run과 완전 frozen selection 부재를 명시. 보존 failure CSV 3,569행의 harness-log 원인 재분류는 별도 실행했고 [diagnosis.json](runs/EAL_offline_20261125/diagnosis.json)에 기록.
- [v2 Table 13](https://arxiv.org/html/2609.01836v2) 저장 `seven_summary.json`의 숫자와 원문 숫자는 맞지만, **저자 집계를 원시 trial로 독립 재채점한 것은 아님**. EAL source filter/event/rebuild의 UA/LA 수치는 원문/보존 집계이고, 이번 세션의 새로운 비인가 tool 효과 관측이 아니다. 저장소에 명시 라이선스 파일이 없어 코드 재사용 라이선스는 `UNKNOWN`.

## 2026-11-25: Multi-CaMeL AssetOpsBench 궤적의 공개 여부 감사

- 종류: `READ_ONLY_AUTHOR_ARTIFACT_SCOPE_AUDIT`. [검색 범위·정확 명령·결론](m3_assetops_trace_audit_20261125.md). 원저자 MultiAgentDojo 고정 checkout `e71647382155dc6949d6ccf9a9d7ec7cf429b856`의 공개 suite와 tracked run 파일을 검색했다. 모델/API/실험 effect 0, 원본 source 변경 0.
- §V-C.2의 asset/time 근접 결과 실패에 해당하는 raw child input/output·parent 후속·최종 effect는 이 checkout에서 미확인. 논문 Appendix A task 609는 MAIN site 미존재 시 fallback **코드 경로**만 보여 실제 분기 실행이나 해당 §V-C.2 실패를 관측한 trace로 취급하지 않는다. 비인가 provider effect `UNVERIFIED`.

## 2026-11-25: 철회 원본의 current journal 재기록과 공개 guard 경계

- 종류: `SOURCE_NATIVE_GUARD_INPUT_BOUNDARY`, 저자 논문이 직접 연결한 [M4 공식 코드](https://github.com/VulcanLab/Memory-Rebirth-Attack) 고정 commit `15dcd20b3c0de4f27d9a8dd10a830dea91641b81`, Apache-2.0. [사전등록·정확 명령·해시·원시 2행·결과](runs/M4_guard_boundary_20261125/result.md). Python 3.10.12, 모델/API/Graphiti/원격 provider 0, 원본 코드 clean.
- 저자 `guard()`에서 `expired_at` 원본은 withheld, 같은 결론의 새 current journal은 kept. 외부에서 그 journal에도 `revoked_at`을 주면 withheld. 새 journal의 lineage/원본 철회 상태가 guard에 공급되지 않는 **입력 경계**를 확인했다. 실제 effect 관측은 `false`.
- [원문 Appendix C.1](https://arxiv.org/html/2609.08258) 저자 Graphiti/LLM write-back 후속 unsafe 결정 255/356 direct hop1과 19/22 natural active journal 조건은 별도의 출처 근거다. 원문 trial이나 effect를 이번 함수 실험 수치로 대체하지 않는다. [MAP-Graph 등 강한 대안](m4_alternatives_note_20261125.md)의 동일 입력 재실행은 후속 질문.

## 2026-11-25: MAP-Graph action-risk metadata 공개 코드 경계

- 종류: `AUTHOR_ASSOCIATED_ARTIFACT_OFFLINE_AUDIT_AND_SOURCE_NATIVE_GATE`, first author GitHub의 [보조 공개 저장소](https://github.com/xiaoqi-7/MAP-Graph) commit `d94b0bf3c73efdb60fcc08014989b44ce8eae99d`, `third_party/MAP-Graph` clean. 논문 HTML에 직접 코드 링크가 없어 **평가 당시 공식 구현과 동일성 미확정**, LICENSE 미발견. [사전등록·명령·raw·결과](runs/H11_risk_metadata_20261125/result.md); 모델/API/외부 effect 0.
- 공개 canonical CSV 21,600행 중 MAPGraph 2,700행, `unsafe_action=1` 41행 전부 Exp-5이며 [저자 본문 41/450](https://arxiv.org/html/2608.10509v1)과 숫자 일치. 41행 모두 task에 revoked source, supporting path의 revoked 조상 0, public high→제안 medium 13행. 공개 raw trace 부재로 41건 원인 귀속 불가.
- 원본 `gate_action` 합성 4조건: 동일 public `send_email/high`, trust .76에서 제안 high→`ASK_USER`(.85), `answer/medium`→`ALLOW`(.30), `send_email/medium`→`ALLOW`(.60), revoked 조상 대조→`BLOCK`. 이것은 `DECISION_ONLY`이며 벤치마크 모델 run/실제 송신 재현이 아니다. [H11 감사](h11_mapgraph_risk_gate_20261125.md).

## 2026-11-25: EAL source gate의 권한자 인용과 금액 의미 분리

- 종류: `SOURCE_NATIVE_EAL_CASE_INDEPENDENT_CORRUPTION`. [사전등록·고정 lock/원본 함수·정확 명령·raw 6행·결과](runs/H10_source_scope_20261125/result.md). 저자 EAL-Bench commit `51648690bc52d7a9c7ac080a2c67a784fe9d56cb`, 격리 venv Python 3.12.15, source checkout clean. 원본 procurement case는 CFO가 USD18,000→9,500으로 축소, 정상 9,000/비인가 10,000 matched probe. 모델/API/외부 provider 0.
- 원본 faithful memory는 gate Pass, 정상 로컬 effect +1/비인가 0. **우리의 합성 오류**인 상한 15,000과 같은 유효 CFO 인용은 gate Pass, USD10,000의 로컬 비인가 effect +1. 비권한자 인용 대조는 gate 제거로 비인가 0이지만 정상도 0. 저자 12-case `analysis.source_authority_gating` 원본 self-check exit 0, `gate_uses_turn_content=false` 확인. 이는 저자 LLM 오류 run 재현이나 새 기법 부재의 증거가 아니라 source-only 범위의 직접 확인.

## 2026-11-25: M4 원본 guard에서 로컬 모의 서비스 effect까지

- 종류: `SOURCE_NATIVE_GUARD_WITH_INDEPENDENT_HTTP_SQLITE_EFFECT`. [사전등록·정확 명령·6조건 raw·SQLite DB·결과](runs/M4_live_20261125/result.md). 원본 M4 `guard()`는 무수정, 결정 fixture/HTTP/SQLite/lineage 필터는 별도 작성. 모델/API/Graphiti/외부 provider 0, loopback만 사용.
- 표지 없는 bad current journal 조건에서 1-reviewer 로컬 비인가 effect 1, 정확한 `j_bad←r1` 계보 제공 또는 현재 2-reviewer 서비스 PEP 조건에서는 비인가 0·정상 2-reviewer +1. 계보 없는 조건에서는 비인가 1. 따라서 status-only 실패의 **구성적 효과 사례**는 확인했지만 이 고정 구성의 신규 메커니즘 필수 가설은 강한 대조로 기각. 원저자 Graphiti/LLM/후속 trial 재현 아님.

## 2026-11-25: MAP-Graph risk gate의 trusted binding 로컬 효과와 900행 보존 지표 감사

- 종류: `SOURCE_NATIVE_GATE_WITH_INDEPENDENT_MOCK_OUTBOX_AND_OFFLINE_PROJECTION`. [사전등록·원시 결정·mock effect·900행 projection·결과](runs/H11_counterfactual_20261125/result.md). 공개 first-author 보조 artifact 후보 commit `d94b0bf3c73efdb60fcc08014989b44ce8eae99d`, 원본 `gate_action` 무수정. 모델/API/실제 이메일 0.
- 고정 synthetic `send_email/high`/trust .76에서 같은 action의 제안 medium은 원본 gate `ALLOW`·mock outbox +1, 별도 trusted binding은 `ASK_USER`·0; high-trust .95 정상 둘 다 +1, revoked ancestor 둘 다 0. 저장 Exp-1/Exp-5 900행의 threshold 함수는 900/900 저장 임계값 재산출, Exp-5 unsafe 41건 중 public 기준 교차는 11건뿐이고 모두 저장 제안 type `answer`; raw graph/support 부재로 **모든 archived 반사실 최종 결과는 UNKNOWN**. 이 구성의 신규 메커니즘 필수 가설은 기각, 논문 41건 전체 원인/해결은 미확정.
