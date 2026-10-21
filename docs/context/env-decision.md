# 환경 조사·판단 결과 (2026-10-21, 웹 원문 확인 기반)

표기: [원문] 논문·공식 문서 본문 확인 / [발췌] 초록·검색 발췌 / [2차] 블로그·보도 / [추론] 조사자 추론 / [미확인]

## 1. 결론

| 항목 | 판단 | 핵심 이유 |
|---|---|---|
| 주 실험 환경 | SREGym (전체 문제 중 kind 지원 문제 선별) | 관측 도구(Prometheus·Loki·Jaeger·Kubernetes)가 각각 별도 MCP 서버로 노출 → 악성 도구 삽입 지점이 명확. 복구 채점이 상태 기반. 에이전트 구조 자유. 에이전트를 격리 컨테이너에서 실행. AIOpsLab·ITBench 문제 포함 |
| 근거 앵커(인용) | AIOpsLab(MLSys 2025) + AIOpsDoom(USENIX Security 2026) + ITBench(ICML 2025) | AIOpsDoom이 AIOpsLab 위에서 텔레메트리 공격을 평가 |
| SREGym-Lite | 설치 확인(연기 시험)용으로만 | Lite 21문제에 revoke_auth·user_unregistered·misconfig_app 계열 없음 |
| 멀티에이전트 | OpenAI Agents SDK(또는 LangGraph)로 진단·수리 에이전트를 직접 구성해 SREGym 사용자 에이전트로 등록 | SREGym은 에이전트 구조를 강제하지 않음(필수 인터페이스는 submit() 하나). 도구 가드레일 위치가 게이트 위치와 일치 |
| 보조 환경 | AgentDojo(+Progent의 AgentDojo-MCP 멀티에이전트 구성) | 방어 논문(Progent, NOMOS, AuthGraph, Sapien, IntentCap, EBTE)이 AgentDojo로 평가 → 2단계 수치 비교용 |
| 자체 환경 | 메커니즘 단위 시험·사전 고정 시나리오의 축소 모형·회귀 시험 | 결과 근거가 아니라 부품 검증용 |
| OpenShell | 실험 격리 + 비교 조건 '가' 기준선 후보 | 정책 밖 행동만 막음. 정책 안의 잘못된 행동(이 연구의 잔여 영역)은 못 막음 |

## 2. 사실 정정 목록

| 원래 주장 | 확인 결과 | 수준 |
|---|---|---|
| SREGym-Lite를 먼저 시도해 권한 복구 시나리오에 사용 | Lite 21문제에 권한 소실 계열 없음(valkey_auth_disruption, secret_rotation_stale_env_credentials_astronomy_shop, network_policy_block, service_wrong_pod_selection_hotel_reservation, wrong_service_selector_social_network 등은 있음). 일부 문서 사본은 17문제로 표기 | [원문: 저장소 문서] |
| SREGym 관측 방식 미확인 | Prometheus·Loki·Jaeger·Kubernetes(kubectl 래퍼, "어떤 명령이든 실행 가능") MCP 서버를 각각 따로 제공, 원시 관측 엔드포인트도 노출 | [원문] |
| SREGym 채점 | 진단은 LLM 판정(LLMAsAJudgeOracle 기본), 복구는 실제 시스템 상태 기반 프로그램 검증 | [원문] |
| SREGym 규모 | 결함 원형 50개, 5개 앱 서비스 139개, 실행 가능 결함-부품 쌍 3,623개. 평가 에이전트 Stratus, Claude Code, Codex | [원문] |
| SREGym NeurIPS 2026 | NeurIPS 2026에서 Datasets & Benchmarks 트랙이 "Evaluations & Datasets"로 개명. SREGym 채택·트랙은 미확인. ACM CAIS 2026 데모 논문은 확인(DOI 10.1145/3786335.3813208) | [원문 일부·미확인 일부] |
| SREGym 예시 모델명 | README에 `--agent codex --model gpt-5.6-luna --reasoning-effort medium` 예시 있음(추론 강도 옵션이 명령줄에 존재) | [원문] |
| SREGym 격리 | 에이전트는 항상 격리된 Docker 컨테이너에서 실행, 기본 필터링 네트워크, 강화 설정(DAC_OVERRIDE 외 리눅스 권한 제거, no-new-privileges) | [원문: README] |
| AIOpsLab 복구 채점 "시스템 전체 상태" | 상태 기반은 맞으나 공개 이슈 #208에 따르면 "존재하는 파드가 건강한가"만 확인 → 문제 서비스를 0개로 줄여도 통과(예: revoke_auth_mongodb-mitigation-1에서 replicas=0). Pending 파드는 건너뜀 | [원문: GitHub 이슈] |
| AIOpsDoom 수치 | 응용 3개(SocialNet, HotelReservation, AstronomyShop), 에이전트 ReAct·Flash, 모델 GPT-4o·GPT-4.1, 180회. adversarial reward-hacking 방식 성공률 90%(다른 텔레메트리 주입 방식은 0%). HotelReservation 82%. 성공 판정 o4-mini | [원문] |
| AIOpsShield "AIOpsLab 12과제 효용 유지" | 12과제는 k8s_target_port-misconfig와 user_unregistered_mongodb 두 계열뿐, revoke_auth 없음. 방어 유무 모두 평균 약 50% | [원문] |
| AIOpsDoom/Shield 코드 | AIOpsDoom은 RSAC-Labs/AIOpsDoom, Apache-2.0(커밋 4개, Flask 데모 대상 포함, OpenAI·Azure·Ollama 지원). AIOpsShield 독립 공개는 확인 못 함 | [원문+미확인] |
| AIOpsDoom 위협 모델 | 사전 지식·특권 없는 외부 공격자(공개 인터페이스만 사용). 이 연구의 "설치된 악성 관측 도구"는 더 강한 내부 공격자 → AIOpsShield가 이 연구의 위협 모델을 막는다고 볼 수 없음 | [원문] |
| Progent v3 | 제목 "Progent: Securing AI Agents with Privilege Control". SMT로 정책 갱신을 축소(자동)/확장(승인 필요) 판정. AutoGen 조정자 1+전문가 6 구성, LangChain·OpenAI Agents SDK·OpenHands 통합 평가 | [발췌] |
| AgentDojo OpenAILLM | 생성자 인자·파서 타입상 chat completions 형식 | [원문: API 문서] |
| "IGAC형 사람 확인" | 잘못된 이름표. IGAC는 신뢰된 요청을 단기 의도 인증서로 바꿔 도구 목록을 좁히고 효과를 사전 검사하는 서버 측 인가 | [발췌] |
| 선행연구 독립성 | 2607.25364(EBTE), 2610.04975(하위 목표 승인), 2606.22916(IGAC)는 모두 Zhu·Wang → 하나의 계열로 묶어 서술 | [발췌] |
| gpt-6-luna | 2026-09-22 출시, 입력 0.10·출력 0.50달러/100만 토큰, 기본 추론 medium, 컨텍스트 1.05M. Chat Completions는 reasoning_effort=none일 때만 함수 호출 지원(2차 자료, 연구자의 400 관찰과 일치). 추론 강도 목록은 직접 관찰한 오류 메시지(minimal 포함 7개)를 우선 | [2차+직접 관찰] |
| ITBench | ICML 2025 구두 발표 확인. 시나리오 수는 자료마다 다름(초기 94개, SRE 42·CISO 50 표기). Artificial Analysis가 독립 구현 ITBench-AA(2026-05-27) 공개 → 외부 재사용 확인. 기본 에이전트의 CrewAI 기반 여부는 미확인 | [발췌] |
| HolmesGPT·k8sgpt | HolmesGPT는 CNCF Sandbox(2025-10), 설계상 읽기 전용, 별도 복구 MCP 연동 있음. K8sGPT도 CNCF Sandbox(2023-12, 2차) | [원문+2차] |
| PocketOS | 2026-04-24 Cursor(Claude Opus 4.6) 에이전트가 Railway API 호출 한 번으로 운영 DB와 볼륨 백업 삭제, 창업자 진술 기반, 이후 Railway가 복구했다고 보도 | [2차] |
| postmark-mcp | 1.0.16(2025-09-17)에서 모든 메일을 숨은 참조로 전달하는 코드 추가, 정상 버전 15개 뒤 악성화, Koi Security 공개 2025-09-25, 내려받기 약 1,643회(ReversingLabs) | [2차] |
| CapScope(2609.08371) | LMPL'26 채택은 초록에서 확인 못 함. 300회 실행, 주입 효과 실행 기준선 33~47/75 대 CapScope 3/75 | [발췌] |
| NOMOS(2610.11030) | "288쌍 중 8쌍 우회"는 초록에 없어 재확인 못 함 | [발췌] |

## 3. 선행 보안 논문들이 쓴 환경 (요약)

| 논문 | 환경 | 멀티에이전트 | 공격자 통제 대상 |
|---|---|---|---|
| AIOpsDoom/AIOpsShield (Pasquini 외, USENIX Sec 2026, arXiv 2508.06394) | AIOpsLab | 단일(ReAct, Flash) | 공개 요청 → 진짜 텔레메트리 오염 |
| Progent (arXiv 2504.11703 v3) | AgentDojo, AgentDojo-MCP, ASB, AgentPoison | AutoGen 1+6 | 도구 출력 주입 |
| CapScope (arXiv 2609.08371) | 자체 수리 과제 5개(Pi 코딩 에이전트) | 오케스트레이터+하위 | 저장소 파일·도구 출력 5경로 |
| IntentCap (arXiv 2609.14631) | AgentDojo 사건 재생 | 위임 경계 포함 | 도구 출력·위임 메시지 |
| NOMOS (arXiv 2610.11030) | τ²-bench, AgentDojo | 단일 | 주입 |
| AuthGraph (arXiv 2605.26497) | AgentDojo, AgentDyn | 단일 | 주입 |
| Sapien (arXiv 2610.00797) | AgentDojo, Toolathlon | 단일 | 완전 탈취 가정 |
| 하위 목표 승인 (arXiv 2610.04975) | 자체 구성 96개 | 위임·병합 포함 | 자체 생성 하위 목표 |
| TMA-NM (arXiv 2606.24322) | 자체 벤치마크 | 단일 | 장기 기억·도구 에코 |
| Delegation Without Trust (arXiv 2609.00267) | 자체 런타임 | LangGraph·CrewAI·AutoGen·MCP 분석 | 혼동된 대리인 등 4종 |
| Terrarium (arXiv 2510.14312) | 블랙보드+MCP 자체 | 다중 | 악성 에이전트, 통신·데이터 오염 |
| MCP-SafetyBench (arXiv 2512.15163) | 실제 MCP 서버 5개 영역 | 다중 서버 | 20종 공격 |
| CAGE (arXiv 2607.29190) | 합성·정책 코드·규제·실거래 | 단일 | 도구 반환값의 출처 결합 오류·수치 오차 |

반복 패턴·공백 [추론]:
- 방어 논문의 공용 기준 환경은 AgentDojo → 2단계에서 비교표에 필수.
- 운영(AIOps) 도메인 보안 평가의 정식 학회 선례는 AIOpsDoom 하나이고 AIOpsLab을 썼다.
- 대부분의 공격자는 도구 출력에 "지시"를 심는다. "설치된 도구가 사실 값을 위조"하는 모델에 가장 가까운 것은
  CAGE와 AIOpsDoom. 운영 복구 멀티에이전트에서 설치된 관측 도구가 사실을 위조하는 경우를 평가한 공개 환경은
  찾지 못함 → 공개 환경을 직접 확장하는 정당한 이유.
- 멀티에이전트 평가 환경은 대부분 자체 구성(CapScope, Terrarium, Progent의 AutoGen 구성) → "직접 만든
  멀티에이전트"는 분야의 표준 관행. 차별점은 문제·환경·채점을 공개 벤치마크에서 가져오는 것.

## 4. 후보 비교 요약

운영 벤치마크:
- SREGym: 멀티에이전트 구조 자유(직접 구성), 관측 MCP 분리 ◎, kubectl MCP로 쓰기 ◎, 복구는 상태 기반·진단은 LLM 판정,
  arXiv+ACM CAIS 데모(학회 채택 미확인), 활발히 유지(커밋 2,465, 별 307), Lite 권장 8 vCPU·16GB,
  LiteLLM·Ollama·vLLM 지원, 강화 컨테이너 격리 ◎
- AIOpsLab: ReAct 중심, 관측 함수 내장(get_logs/get_metrics/get_traces), exec_shell(정책 필터),
  MLSys 2025 ◎, 복구 채점 0개 축소 통과 결함, 자원 요구 공식 수치 못 찾음
- ITBench: ICML 2025 구두, 외부 독립 구현 확인, 세부 미조사
- Incident-Arena: 안전 게이트(데이터 보존·범위 준수) 내장이 장점, 단일 코딩 에이전트 가정, 외부 재사용 없음
- STRATUS(NeurIPS 2025): SREGym에 에이전트로 포함돼 우회 가능, 단독 저장소 설치 가능성 불확실

에이전트 보안 벤치마크: AgentDojo(방어 논문 공용, 단일 에이전트, chat completions 형식 → luna는 reasoning_effort=none 필요 [추론]),
Progent AgentDojo-MCP(AutoGen 1+6), Terrarium, MCP-SafetyBench, AIOpsDoom 아티팩트(운영 보안 유일).

현장 도구(악성 도구 대역 후보): HolmesGPT(CNCF, 읽기 전용), K8sGPT(CNCF), kubernetes-mcp-server(read_only/
disable_destructive를 TOML로 설정), mcp-grafana(Grafana 공식, --disable-write로 쓰기 도구 제거).
  → 논문에서 "실제 현장 도구"를 주장하려면 mcp-grafana를 악성 래퍼로 감싸는 구성이 설득력 있으나, SREGym 점수와
    직접 비교하려면 SREGym 내장 관측 MCP 조건을 기준 조건으로 남길 것(관측 구성을 바꾸면 점수 비교 불가 경고가 README에 있음).

멀티에이전트 프레임워크: OpenAI Agents SDK가 마찰 최소(Responses 기본 경로, 도구 입력·출력 가드레일, needs_approval).
  주의: 핸드오프는 도구 가드레일 대상이 아님(공식 문서) → 시나리오 F는 핸드오프 별도 기록 필요. LangGraph는 대안.

데모 앱: openai-cs-agents-demo는 참고 코드(운영 복구 도메인 아님). Online Boutique는 보류(SREGym에 Astronomy Shop 있음).

잠정 판단 검증: 직접 구축=학습용 지지 / AIOpsLab 앵커 지지+보강(AIOpsDoom 병기) / SREGym-Lite 먼저 → 수정(설치 확인용) /
둘 다 보안 지표 없음 지지+보강(0개 축소 통과 결함이 성공 정의의 근거) / OpenAI 데모는 비교용 → 수정(그 SDK로 직접 구성).

## 5. 목표 실험 구조

사용자 요청 → 오케스트레이터 → 진단 에이전트(읽기 도구만) → 보고 → 수리 에이전트(쓰기 도구만) → 게이트(쓰기 직전 통과)
→ 쿠버네티스 클러스터(SREGym 환경) → 판정기(실제 상태 + 감사 로그).
진단 에이전트가 쓰는 관측 MCP 서버 중 1개를 악성 중계 서버로 교체(응답 일부 필드만 변조).

- 악성 중계기: 진짜 서버 앞에 끼워 응답 값만 바꿈. 신뢰된 출처에 직접 쓰지 못한다는 위협 모델 한계가 유지됨.
- 게이트: 수리 에이전트의 쓰기 도구에 입력 가드레일. SREGym kubectl MCP는 "어떤 명령이든 실행"하므로 진단용(읽기 전용)과
  수리용(쓰기+게이트)으로 분리. 진단 쪽은 kubernetes-mcp-server의 read_only 설정 활용 가능.
- 판정: kind 클러스터에서 Kubernetes 감사 로그(API 서버 audit policy)를 켜 "실제 변경"의 주체·시점을 결정론적으로 기록.
  보안 판정 항목: 감사 로그(실제 변경), RBAC·시크릿·NetworkPolicy 실행 전후 차이(권한 오남용), 앱 DB 행 수·체크섬(데이터 손실),
  외부 송신 기록(유출). "아무것도 안 함"과 "파괴로 통과(replicas=0 등)"를 별도 범주로 센다.

## 6. 이행 단계 (단계 / 검증 / 흔한 실패 지점)

| 단계 | 검증(통과해야 다음) | 흔한 실패 지점 |
|---|---|---|
| 0 VM 준비(12 vCPU·32GiB 권장) | Docker·kind·Helm 4·uv·Python 3.12 동작 | 메모리 부족, inotify 한도("too many open files") → SREGym kind 문서의 호스트 커널 설정 |
| 1 SREGym-Lite 연기 시험 | Lite 1~2문제를 기본 Stratus 에이전트로 끝까지, 복구 오라클 결과 생성 | 서브모듈 누락, Docker Hub 한도, 이미지 pull 시간 초과, kubectl·노드 버전 차이 |
| 2 모델 경로 확인 | luna로 (a) codex+--reasoning-effort, (b) Stratus+LiteLLM에서 도구 호출 성공 여부 기록 | LiteLLM이 chat completions로 보내면 도구+추론 조합 400 → reasoning_effort none 또는 자체 에이전트 |
| 3 대상 문제 선별 | revoke_auth_mongodb, user_unregistered_mongodb, k8s_target_port-misconfig, valkey_auth_disruption 등이 kind에서 실행되는지 | kind 미지원 문제(노드·커널 결함 계열) |
| 4 자체 멀티에이전트 등록 | 진단(읽기 MCP)·수리(쓰기 MCP) 분리, 무공격 복구 성공률 측정 | 컨테이너 안 MCP 연결, 필터 네트워크가 외부 접근 차단 |
| 5 게이트·기록기 이식 | 가드레일이 모든 쓰기 호출을 기록, 감사 로그와 1:1 대응 | 핸드오프는 가드레일 대상 아님 → 별도 기록 |
| 6 악성 프록시 | 프록시 on/off 시 진단 보고가 달라지는지 확인 | 응답 형식이 깨져 모델 능력 실패와 혼동 |
| 7 보안 판정기 | 4단계 자동 산출, 데이터 보존 검사 | 0개 축소 통과 유형 별도 분류 |
| 8 사전 고정 | 시나리오·인가 조건을 커밋으로 고정 | 결과를 보고 시나리오를 고치는 순환 |
| 9 본 실행 | 조건 가·나·다 × 시나리오 × 반복 | 비용 상한, 실행 시간 |

본 실행 진입 조건: ① 무공격 복구 성공률 안정 측정 ② 게이트 기록과 감사 로그 1:1 일치 ③ 프록시 on/off 차이 확인 ④ 시나리오 사전 고정.
채점: 복구 오라클(상태 기반)을 업무 복구 지표로, 진단 LLM 판정은 보조 지표로만. 복구만 단독 실행 가능 여부는 미확인.
자체 부품 이식: call_llm → Agents SDK 사용자 모델 공급자 또는 자체 루프 / 게이트 → 도구 입력 가드레일(정답 모듈 import 금지 원칙 유지) /
판정기 → 입력을 SQLite 대신 K8s API·감사 로그·DB로 교체 / 기록기 → 에이전트별·핸드오프별 이벤트 JSONL.
모델 선택: luna(주, Responses API), H100 vLLM 개방형 모델(보조, 지도교수 "로컬 모델" 요구 대응, 도구 호출 신뢰성 확인 필요, 협의 필요).
"누가 선을 넘는지 관측"은 에이전트 간 메시지·도구 호출·게이트 결정을 빠짐없이 기록하는 것으로 대부분 충족 [추론].

## 7. 시나리오 ↔ 공개 문제 대응

| 시나리오 | 공개 문제 후보 | 난이도 |
|---|---|---|
| A 위조 | revoke_auth_mongodb, user_unregistered_mongodb, valkey_auth_disruption | 쉬움 |
| B AIOpsDoom 재현 | k8s_target_port-misconfig, user_unregistered_mongodb, SocialNet·HotelReservation(AIOpsDoom 퍼저 공개) | 중간 |
| C 과잉 조치 | revoke_auth_mongodb(전체 관리자 부여), network_policy_block(정책 전부 삭제), namespace_memory_limit(한도 제거) | 쉬움 |
| D 목표 상태 없는 데이터 복구 | 직접 대응 문제 없음 → MongoDB에 시드 데이터+행 수·체크섬 판정 추가, 또는 데이터 보존 게이트가 있는 Incident-Arena 과제를 보조로 | 어려움 |
| E 여러 자원 일관성 | secret_rotation_stale_env_credentials_astronomy_shop, rolling_update_misconfigured_social_network | 중간 |
| F 보고 재전달 | 모든 문제(진단→수리 분리 구조 자체) | 쉬움 |
| 대상 혼동 | service_wrong_pod_selection_hotel_reservation, wrong_service_selector_social_network | 쉬움 |
| 빈 결과 오판 | 아무 문제 + 악성 도구가 빈 결과 반환 | 중간(피해 판정에 D의 데이터 판정 필요) |

재현(Replay): AIOpsDoom 퍼저·페이로드 생성기·Flask 데모 대상 공개. 같은 앱이 SREGym에 있어 시나리오 B로 재현 가능.
AIOpsShield 코드는 공개 미확인 → 논문 서술 기준 재구현. PocketOS·Replit은 공개 사고라 그대로 재현 불가, 패턴만 이식.

## 8. NVIDIA OpenShell

- 정의: 자율 에이전트를 커널 수준 격리 샌드박스에서 실행하고 선언형 YAML 정책으로 파일·네트워크·프로세스·자격 증명을 통제하는
  오픈소스 런타임. GTC 2026(NVIDIA 개발자 블로그 2026-03-16) 발표, Apache-2.0, 주 언어 Rust, 문서 최신 v0.1.5 [원문].
  NemoClaw(OpenClaw를 OpenShell 위에서 돌리는 스택)와 함께 발표. NeMo Guardrails와의 관계는 미확인.
- 구조: 파일=Landlock(ABI 3 이상, Linux 6.2+), 프로세스=seccomp, 네트워크=기본 차단+감독자 프록시(OPA 연결 결정+L7 요청 결정,
  REST 메서드·경로·쿼리, MCP 메서드·도구 규칙), 자격 증명=에이전트는 실제 키를 못 보고 프록시가 주입, 정책 변경 검증=SMT 증명기+
  정책 조언자, 감사=OCSF 로그, 확장=감독자 미들웨어(요청 본문까지 볼 수 있음).
- 막는 것: 허용 경로 밖 파일 접근, 승인되지 않은 송신(유출), 자격 증명 탈취, 권한 상승, 허용되지 않은 HTTP 메서드·경로·MCP 도구 호출.
- 못 막는 것 [추론, 문서 근거]: 규칙은 요청 본문을 보지 못함 → 허용된 API 경로로 들어오는 "잘못된 계정에 권한 부여" 같은
  값·대상·시점 오류는 통과. 거짓 관측을 믿고 내린 판단은 판단 대상이 아님. 본문 검사는 직접 만든 미들웨어로만 가능(2차).
- 연구와의 관계: 참조 모니터와 같은 계열(프로세스 밖 강제). "정책 밖" 행동의 마지노선은 되나 "정책 안의 잘못된 행동"의 마지노선은 아님.
  Progent·CaMeL·NOMOS는 도구 이름·인자 수준(의미 층), OpenShell은 시스템 호출·네트워크 층 → 경쟁 관계가 아니라 담당 층이 다름.
- 요구 사항: GPU 불필요, Docker/Podman 또는 호스트 가상화, 커널 6.2 이상 필요(Ubuntu 22.04 기본 GA 커널은 5.15 → HWE 6.x 여부를
  uname -r과 /sys/kernel/security/lsm으로 확인), Claude Code 기본 정책 완전 지원·Codex는 사용자 정책 필요.
- 활용: 비교 조건 '가'의 기준선(수리 에이전트 샌드박스에서 K8s API 경로를 L7 규칙으로 제한) 권장, 실험 격리는 선택(SREGym 자체 격리와 중복),
  게이트 삽입(감독자 미들웨어)은 2단계 때 검토. 학술 평가·사용 사례는 못 찾음.
- 신규성 영향: 정책 밖 행동(유출, 권한 상승, 비승인 엔드포인트)은 이미 해결된 영역으로 분류. 신규성 후보는 "정책은 통과하지만 근거가
  틀린 행동"뿐이며 그 잔여가 실제로 남는지 1단계에서 측정한다.

## 9. 확인하지 못한 항목

- AIOpsLab exec_shell 정책 필터 위치·차단 명령, 클라이언트 호출 형식, 자원 요구량(소스 미열람)
- user_unregistered_mongodb-mitigation-1 정확한 ID
- SREGym NeurIPS 2026 채택·트랙, 복구 단독 실행 가능 여부, agents.yaml 형식
- luna의 LiteLLM 경로 동작, OpenAI 공식 모델 문서 본문
- AIOpsShield 코드 공개
- MCP-SafetyBench ICLR 2026, MCPTox AAAI 2026, XTHP NDSS 2026, TAMAS ACL 2026, MAS hijacking 판본별 수치, Instruction Hierarchy 원문 재확인
- ITBench 기본 에이전트의 CrewAI 기반 여부, STRATUS 저장소 설치 가능성
- Microsoft Agent Framework, CrewAI, Google ADK·A2A, kubectl-ai, Prometheus MCP 세부
- OpenShell 학술 사용 사례, NeMo Guardrails와의 관계
