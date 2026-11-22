# Phase 0 확인 사항과 해석 경계

## 확인된 사실

1. 원본 Progent pin과 Python 환경이 로컬에 존재한다. 새 Python Tool에 원본 `apply_secure_tool_wrapper`와 `update_security_policy`를 연결할 코드 경로가 있다. **새 Use Case에서 동작한다는 결과는 아직 없다.**
2. 원본 Wrapper는 checker를 통과한 뒤에만 Tool 본체를 호출한다. 정책이 `None`일 때는 경고 후 통과하므로, 적용 정책 존재와 Backend 효과를 반드시 분리해 검사해야 한다.
3. 기존 Banking 공격 두 실행은 서로 반대의 Tool 효과를 보인다. `6heKyOjj`의 넓은 초기 정책에서는 모의 악성 송금이 성공했고, `kgeF5az4`에서는 Agent가 송금을 제안했지만 Wrapper가 거부했다. 이는 **정책 상태가 다른 별도 실행**이지 동일한 실행에서 상충된 판정이 아니다.
4. Auto-Deny는 생성 정책의 확대 후보를 폐기하고 정상 송금 Tool을 거부했다. 이 실행의 utility 저하는 기록되어 있으나, 사용자 의도를 의미적으로 판정한 결과는 아니다. 해당 후보는 새 Tool 추가라서 subset 검사에서 Z3 단계 이전에 거부된다.

## 연구적 분류

넓은 초기 정책에서 허용된 악성 Tool Call은 정책 생성 범위 문제의 사례이며, 현재 증거만으로 checker 구현 오류 또는 기존 연구의 일반적 실패라고 결론 내릴 수 없다. 반대로 제한된 정책에서 거부된 호출은 원본 Wrapper 집행 사례다. 원본 CLI의 모의 Backend 반환과 채점은 실제 은행 시스템 효과가 아니다. 기존 결과는 AgentDojo의 특정 task·모델·설정이며 Benchmark 전체 평균으로 일반화하지 않는다.

## 미검증

- 새 Mock VM Tool에서 정책 생성, 수동 Deny, Wrapper 집행, 최종 상태 불변성
- 관리자 Deny와 생성 Allow를 함께 쓸 때의 모든 충돌·우선순위·의도 적합성
- 실제 LLM이 새 Use Case에서 금지 Tool Call을 제안할지 여부
- SSH/VM/하위 프로세스/OS 경계의 집행과 우회 가능성
- `kgeF5az4`의 정확한 전체 환경변수와 과거 원본 실행의 전체 종료 상태 snapshot

## 대조 연구 메모

[ActPlane: Programmable OS-Level Policy Enforcement for Agent Harnesses](https://arxiv.org/abs/2606.25189)는 arXiv 기록상 **2026년 6월 제출·수정된 프리프린트**다. arXiv 페이지에서 학회 게재 상태는 확인되지 않았다. 저자 [코드 저장소](https://github.com/eunomia-bpf/ActPlane)는 eBPF 기반 커널 집행, 프로세스 계보, 파일·네트워크 이벤트, 정보 흐름·순서 규칙을 설명한다. 이는 Progent의 Python Tool Wrapper와 다른 실행 경계를 다루므로, 이후 시스템 수준 비교에서 이미 제시한 범위를 빼고 해석해야 한다. **ActPlane을 이 프로젝트에서 실행하거나 주장된 보장을 독립 검증하지 않았다.**

관련 [Google Sheets의 `Overview`·`Related_works`](https://docs.google.com/spreadsheets/d/1abFjTBcpDAYTZFAVOTUtYH28jKw3xhKg6JCjCGX5Tjg/edit)는 읽기 전용으로 확인했다. `Related_works`에는 Progent가 여러 행에 있고, 두 주요 탭에서 ActPlane 문자열은 확인되지 않았다. 이번 Phase 0의 ActPlane 추가는 이 로컬 대조 메모에 한정한다. PAuth, AuthGraph, FORGE/SASY, Multi-CaMeL, OpenShell, AgentBound, CONTINUITY의 상세 비교·재현은 이번 단계 범위 밖이다.
