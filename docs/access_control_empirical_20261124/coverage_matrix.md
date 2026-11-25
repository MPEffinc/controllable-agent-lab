# K01–K15 공통 분석 / Coverage 매트릭스

근거 등급: `P` 원문/공식 문서의 메커니즘·저자 평가, `C` 고정 코드에서 확인, `E` 이 조사에서 원시 실행 효과 확인, `R` 이전 실험의 원시 로그 재감사, `U` 아직 `UNKNOWN`/`NOT_ESTABLISHED`. 각 논문·공식 코드의 정확한 URL·버전은 [레지스트리](paper_registry.md)에 있다. `P`는 이 세션 재현이 아니다. Coverage의 퍼센트는 공통 분모가 없으므로 적지 않는다.

## 문제·신뢰·정책·집행 (공통 필드 1–4)

| ID | Problem statement | Threat model / 신뢰 전제 | 정책 생성·명세 | 정책 집행 PEP |
|---|---|---|---|---|
| K01 | P: 작업별 최소 권한 | P: untrusted task data를 정책 생성 입력에서 배제, trusted context 신뢰 | P: user query+trusted context→tool/인자 정책 | P: `is_allowed` tool 명령 검사; 실제 코드 U |
| K02 | P: 동적 경로 이탈과 악성 instruction | P: validator/isolator 신뢰, 외부 데이터 공격자 통제 | P: 초기 경로+Read 확장·Write/Execute LLM validator | P: tool 경로 validator/isolator; 로컬 효과 U |
| K03 | P/C: tool/인자 권한 | P: 사용자 요청/정책 생성과 wrapper 적용 신뢰 | P: LLM 초기 정책·갱신; C: SMT 포함 검사는 `SECAGENT_ONLY_ALLOW_NARROW=True` 옵션, 기본 False; E: 수동 정책만 사용 | C/E: `secure_tool_wrapper→check_tool_call`에서 함수 호출 전 검사 |
| K04 | P: signed task에 대한 서버측 인가 | P: signed task·서버 권위 값/번역 신뢰 | P: 서버별 task slice, signed operand provenance | P: 서버 operator/operand 검사; 코드 U |
| K05 | P: 정형 정책의 안전한 평가·분석 | P: schema·정책 작성자와 요청 facts 신뢰 | P/E: 사람이 Cedar 정책/schema 작성; 독립 조건 대조에서 `when { context.registration_open }` | P/E: Cedar CLI 조건 결정 false Deny/true Allow, 독립 wrapper 로컬 effect 0/1. 실제 서비스 연결 U |
| K06 | P/C: 자연어 요구→검토 target→Cedar | P: 검토된 atom/target 및 gold 기준 신뢰 | C: schema/condition atom을 승인 후 plan 구성 | U: 서비스 runtime PEP 연결 미확인. `cedar validate/symcc`는 **형식 검증기**, PEP가 아님 |
| K07 | P: 자연어→NGAC 표현·검토 | P: 원문 해석과 역번역 검토 신뢰 | P: IR→NGAC export, back-translation; E: **별도 NIST PM graph 사전**을 독립 구성, NGAC-IR 생성기 아님 | P: NGAC Policy Machine의 graph 결정 replay; **저자 strict+app 검사 미실행**. E: 공식 PM의 static graph과 독립 broad+app guard 6조건 로컬 effect |
| K08 | P: 실행 history/provenance에 따른 정책 | P: 계측 join point·관측 graph 완전성 신뢰 | P: 수동 Datalog 또는 NL→정책 번역 | P: SASY/FORGE reference monitor의 action join point; 로컬 RUN U |
| K09 | P: 승인 graph와 실행 graph의 불일치 | P: graph-builder가 관측/귀속을 정확히 함 | P: 사전 approval graph | P: graph 비교 후 action 판단; 코드 U |
| K10 | P: 단일 agent instruction/data 분리 | P: trusted interpreter/도구 schema 신뢰 | P: capability 및 데이터 흐름 규칙 | P: CaMeL interpreter가 tool/effect 통제; 로컬 RUN U |
| K11 | P/C: MAS agent-as-tool 신뢰 경계 | P: tree 구조·외부 Sequrity Control·trusted task channel | C: SUITE_PARTITIONS 기반 정책, `task.producers` taint 조건 | C: 정책을 Sequrity 요청에 전달; 실제 hard deny 서버 판정 U |
| K12 | P: MAS control-flow hijack | P: orchestrator가 agent 전환을 관측; 내부 black-box tool은 비관측 | P: CFG/agent-edge policy 생성 | P: orchestrator의 agent 간 edge 검사; 코드 U |
| K13 | P: tool 호출 밖 OS 자원 효과 | P: kernel/LSM hook·policy compile/runtime 권한 신뢰 | P: eBPF/LSM 정책 | P: kernel hook; 무권한 compile과 실제 block 구분, RUN U |
| K14 | P/R/E: sandbox 자원·network 격리, provider effective policy | P: Landlock/seccomp/Supervisor, profile·설정·경계 신뢰 | P/E: YAML 정책, Prover boundary; E: provider attach 후 base/effective 별도 조회 | R: Landlock `/tmp` write deny·network deny; E: L7 `audit` 전달 vs `enforce` 403 차단·정상 `/ok` 통과 |
| K15 | P: origin grant→delegation→effect | P: issuer/verifier/key, 모든 finality sink 중재 | P: 서명 grant·field/effect contract·permit | P/R/E: effect broker/current grant 검사; R2의 구성된 sink 효과 및 [원본 verifier·FinalitySink EUR 대조](runs/M1_continuity_amount_20261125/result.md) |

## 정확성·평가·한계·대조 (공통 필드 5–10)

| ID | 생성 정확성: 의도 oracle | 정책 정확성: 정형 속성 | 집행 정확성: 실제 효과·완전성 | 평가 coverage | 한계 종류 / 근거 | 직접 대조·대안 |
|---|---|---|---|---|---|---|
| K01 | U: 독립 의도 oracle 미확인 | U | U: 원저자 코드 미확보 | P: 합성 filesystem/email task | P: 동적 외부 값 사전 예측 어려움 | K02 동적 확장, K04 서버 provenance |
| K02 | P: LLM validator가 의미 판단 | U: 검증 target 형식 증명 미확인 | U: 이 세션 효과 미시험 | P: AgentDojo/ASB/AgentDyn, 판본별 차이 | P: validator 의미 판정에 의존 | K03 포함 검사, K06 검토 target |
| K03 | P: 초기 LLM 정책·승인자의 정확성은 별도 | C/E: 옵션 함수의 생성 규칙 동일·축소 True, 확대·신규 tool False(반례 포함); 기본 갱신 경로 미검증 | E: wrapper 통과 경로 Deny effect 0; [H5 합성 대조](runs/H5_dispatch_effect/result.md)는 허용된 동일 호출의 child 파일 효과가 wrapper의 인자 검사를 넘어서는 범위를 보임 | P: AgentDojo/ASB; E: 4 effect + 4 subset case + 별도 H5 2조건 | E: `None` 경고 후 효과; 과권한 정책도 효과; H5는 Docker 자원 경계에서 정상 출력 유지·추가 효과 0 | K06 target review, K05 Cedar, K14 OS PEP |
| K04 | P: task self-contained·서버 번역 전제 | P: signed provenance/operand 검사 | U: 원저자 코드 미확보 | P: 원본 task 71/100, refined 100/100, off-task call 634/634 | P: task 모호성/권위 값 진실성 전제 | PACT/ROPE; K15 effect permit |
| K05 | U: 사용자 의도와의 일치는 별도 | P: schema/type, policy equivalence/inclusion; E: 고정 `when` 조건 판정 | E: [단일 조건](runs/K05_conditional_alternative_20261124/result.md) false 0/true 1, [복수 route·조건부 금지](runs/K05_route_composition_20261125/result.md) 6/6 기대 결정과 wrapper 로컬 ledger; 실제 서비스 PEP U | P: 논문 Cedar 언어/성능 평가; E: 별도 조건 2+2+6 요청, 원저자 평가 아님 | P: 정해진 명세·schema/신뢰된 context 상대적, 실제 provider 원자성 U | K06 정책 생성 검증, K07 정적 NGAC export의 기존 조건 PDP 대안 |
| K06 | P: human/model atom review; **사람 검토 방식 평가 미실시**(v2 §V-D3); 독립 gold 별도 | C/E: 제공 plan 6개 통과, 넓은 View 대조군 ceiling 실패·반례 | U: service effect 미평가 | P: gold 200; 완료 197, gold 동치 178; E: sample 2조건, gold 저장 산출물 200 무결성 | P: plan 통과 19건 gold 불일치, §VI; [개별 trace 공개 경로 미확인](deep_h1_trace.md) | K05 형식 언어; Reparo/NGAC-IR/Text2NGAC 의미 대안 |
| K07 | P: back-translation 원문 대조; 714문장 95.7% faithful(저자 평가) | P: grammar/compiler checks; E: 별도 PM static graph 질의 | P: 저자 PM 390 graph-decision replay는 **NL intent 검증 아님**; E: [독립 PM 6조건](runs/K07_condition_boundary/result.md): broad false effect 1, strict true 정상 effect 0, broad+앱 guard false 0/true 1. [독립 복수 route 7조건](runs/K07_route_composition_20261125/result.md)은 전역 gate/조건부 금지 상시 export 과거부 확인. 저자 strict+app 최종 효과 U | P: 714문장 의미 평가와 390 graph-decision replay는 별도 분모; E: PM 독립 6+7 설계 조건 | P: [§5.1/§6](https://arxiv.org/html/2611.26941v1) broad export의 조건부 허용 98/715 무조건화; strict export 23/390 요청을 PM에서 거부·app check 미시험; 조건부 금지 항상 적용; quantity/delegation/nested obligation 한계. [H8 판정](h8_conditional_gap_verdict.md) | Text2NGAC, K05 Cedar/ABAC app PEP, XACML 조건 PDP, NIST 동적 graph |
| K08 | P: trace judge/back-translation; 독립 oracle 아님 | P: Datalog 이력 정책 | U: instrumented 경로 밖 효과; 로컬 source build 제한 시간 초과로 실제 PEP `NOT_RUN` | P: 사례·AgentDojo; Appendix H held-out | P: Task 43 허용 취소 차단; §4.4 완전 중재·충실 관측, §7.1 raw socket/stdio 및 내부 동시성 전제 | K06 independent gold; K13/K14 lower-layer PEP, K15 finality sink |
| K09 | P: 승인 graph를 기준 | P: graph 제약, 정형 포괄성 U | U: builder/관측 완전성 | P: AgentDojo/AgentDyn 저자 평가 | P: §5 graph-builder 귀속·multi-agent 경계 | K08 event graph, K15 origin→effect |
| K10 | P: trusted instruction 기준 | P: capability/IFC 성질(정확한 정리 범위 재확인) | U: 실제 효과 미시험 | P: 단일 agent AgentDojo | P: implicit dependency 등 후속 K11 논의 | K11 MAS tree, FIDES/LLMbda |
| K11 | P: trusted task vs variable 분리 | C: 정책 문자열 생성·전달 확인 | E: fake-client 테스트의 **in-memory benign sent assertion**, 전후 snapshot 없음; hard deny U | P: 97 benign task/949 injection instances **per model/configuration**; E: fake tests 25 | P: §VI tree/CFI 범위, DAG·async·implicit-flow 제외 | K12 edge PEP, K15 effect grant, LLMbda |
| K12 | P: CFG가 task 의도라는 전제 | P: edge rule; 목표의 형식 oracle U | P: 내부 black-box tool 비관측; E U | P: 원문 agent 경로 평가 | P: 내부 tool/effect 범위 밖 | K08 join point, K13/K14 lower layer |
| K13 | P: 사람이 정책/관측 hook 정함 | P: policy compile; runtime correctness U | U: 커널 PEP 실행 미시험 | P: 원문 저자 평가, 이 세션 U | P: OS event에서 업무 의미 추론 제한 | K03 tool 인자, K14 sandbox |
| K14 | U: YAML 의도 정확성 별도 | R: Prover 포함/초과와 `/tmp` 반례; 전체 effective policy가 입력돼야 함 | E: [v0.1.9 새 실행](runs/K14_effective_20261124/result.md)에서 `audit` `/blocked` upstream +1, `enforce` 같은 요청 +0/403, `/ok` +1/200; R: 이전 `/tmp`/network deny | E: provider attach 1, L7 audit/enforce/정상 3 요청; R: 이전 Docker workload 2 정책+Prover | E: provider profile의 PyPI 실제 요청은 시험 안 함; shorthand audit 로그의 위반 식별 모호성, 원본 OCSF JSON 미수집; Agent의 업무 의미·다른 경로 미시험 | K13 kernel, K03 tool, provider sink |
| K15 | P: signed grant 의도/issuer 신뢰; E: 실제 넓은 signed root는 넓은 effect 허용 | P/E: 원본 root 금액 상한·위임 scope 검사 | R: R2 단일 sink·최신 상태에서 effect 0; E: 서명 EUR120 root의 EUR9000 effect 0, 정상 EUR120 effect 1, 실제 넓은 root EUR9000 effect 1 | R: R2 18 A2A 조건; P: 저자 quick suite; E: 별도 finance 적응 4 설계 입력 | P/R/E: 완전 sink 중재, Donno 공유 HMAC/A2A·실제 보험 provider/concurrency 제외 | Donno 공유 HMAC 사례, Lineage, Authorization Revocation, EffectBound |

## Coverage를 네 가지 분모로 분리

| 집합 | 이 매트릭스에서 기록하는 범위 | 아직 확립되지 않은 것 |
|---|---|---|
| 정책 표현 | K03 tool/인자, K05/K06 Cedar request, K08 Datalog history, K11 agent-as-tool taint, K14 FS/network, K15 effect permit 등 서로 다른 언어·사실 | 각 논문의 표현 범위를 통일한 공통 분모 `NOT_ESTABLISHED` |
| 실제 집행 경로 | 이 세션 E: K03 래핑 함수, H5의 같은 허용 호출 host/Docker 파일 효과, K14 v0.1.9 L7 synthetic upstream audit/enforce 및 provider effective policy, K07 별도 공식 PM PDP/인메모리 ledger 6+7조건, K05 CLI+독립 wrapper ledger 2+2+6조건, K15 원본 verifier/FinalitySink finance 적응 4입력, K11 fake 정상 경로(실제 Deny 없음); K06은 형식 결정만; 이전 R: K14 Docker FS/network, K15 합성 sink | 외부 서비스 전체 effect-equivalent 경로 `NOT_ESTABLISHED`; K05/K07/K15 새 실험의 ledger는 원격 provider effect가 아님 |
| 평가한 위협·정상 task | K04의 원본/refined task 분모, K06 gold 200, K11 저자 97/949와 로컬 fake 25 등 각각 별도 | 논문 간 ASR/utility 공통 조건 `NOT_ESTABLISHED` |
| 정형 증명 속성 | K03 지정 enum 포함 조건, K06 제공 plan floor/ceiling/liveness 및 overbroad 반례, K14 boundary 포함은 실행 확인. K05 Cedar 동치/포함·K15 contract는 원문/기존 기록 범위 | 사용자 의도와 자동 동치 또는 모든 runtime 효과 보장 `NOT_ESTABLISHED` |

**해석:** `U`는 0% 실패가 아니다. 이 표의 `P` 중 상세 평가 수치/정리 가정은 원문의 해당 절·표와 [출처 감사](agent_registry_a.md)/[출처 감사](agent_registry_b.md)를 따라가며 재검증해야 한다. Progent·OpenShell·Multi-CaMeL의 실행 근거는 [재현 로그](reproduction_log.md)와 [K11 실행](runs/K11_fake_client_20261124/manifest.md)에 연결했다.

## 보조 Gap 후보의 별도 coverage (K01–K15 분모에 합산하지 않음)

| 후보 | 정책/신뢰 입력 | 실제 검사·관측 범위 | 저자 평가/이번 실험 | 정형 보장·미확정 |
|---|---|---|---|---|
| H10 EAL-Bench | 권한자 출처·장기 NL grant/revoke/scope, writer memory | 저자 synthetic executor tool 행동; [이번 오프라인 감사](runs/EAL_offline_20261125/result.md)는 저장 집계·입력 hash, [원본 source gate/정책 함수 6입력](runs/H10_source_scope_20261125/result.md)은 별도 합성 local ledger effect | v2 저자 paired UA/LA, source filter 후 false authority; 새 실행은 공식 corpus의 **독립 조작 memory**에서 비인가 local effect 1, 정확 memory 정상 1/비인가 0. 로컬 raw v2 trial 0 | 독립 oracle-exact/3-block rebuild 및 WTB/current service PEP가 강한 대조; 실제 provider effect·자연 생성 오류의 같은 case 대응 `NOT_ESTABLISHED` |
| H12 M4 | 원본 validity 표지와 agent가 새 current journal로 재기록한 결론 | [저자 guard 원본 함수](runs/M4_guard_boundary_20261125/result.md)의 `kept/withheld`; [별도 HTTP/SQLite 6조건](runs/M4_live_20261125/result.md)은 원본 guard→결정 fixture→로컬 effect | [저자 Appendix C.1](https://arxiv.org/html/2609.08258) direct/natural write-back 조건부 후속 unsafe **결정**; 로컬 bad journal 비인가 +1/정확 lineage 또는 service PEP 비인가 0·정상 +1 | Graphiti/LLM 자연 write-back, trusted derivation/currentness 자동 capture 정확성 `NOT_ESTABLISHED`; 고정 effect는 기존 대안으로 해결 |
| H11 MAP-Graph | public task type/risk와 model-proposed type/risk, provenance/support | [원본 `gate_action` 4입력](runs/H11_risk_metadata_20261125/result.md) `DECISION_ONLY`; [별도 mock outbox](runs/H11_counterfactual_20261125/result.md)는 동일 action type 위험 하향 시 로컬 effect +1, trusted binding 0/정상 +1 | 논문 2,700 synthetic task 중 Exp-5 unsafe 41/450; 공개 보조 artifact 900행 threshold projection, **모든 저장행 최종 반사실 UNKNOWN**, 3.2GB raw trace 미제공 | 정확 supporting ancestry와 41건 인과·평가 commit 일치·provider 효과 `NOT_ESTABLISHED`; 고정 risk downgrade는 기존 binding으로 해결 |
