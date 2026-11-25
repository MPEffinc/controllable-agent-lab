# 새 출처·코드 원장

기존 K01–K15 공식/후보 코드와 상태는 [기존 registry](../access_control_empirical_20261124/paper_registry.md)를 참조한다. 본 표의 새 checkout은 원본 변경 없이 보존한다.

| 연구 | 1차 출처 | 공개 코드 | 로컬 SHA·상태 | 한계 |
|---|---|---|---|---|
| ALPS | [INFOCOM 2026 원문](https://cclab.info/papers/2026_shin_infocom.pdf) | [연구실 공식](https://github.com/cclab-inu/ALPS), Apache-2.0 | `third_party/LAB_ALPS` `ace0fd2cabdc100bf5491bad3389e47bce6a37f9`, [공식 verifier 12 test 통과](runs/A3_alps_runtime_20261125/result.md) | 정적 함수 코드→IAM/SDK call; 동적 MAS origin scope 평가 미확인 |
| KubeAegis | [IEEE Access 2024 원문](https://cclab.info/papers/2024_kim_access_kubeaegis.pdf) | [연구실 공식](https://github.com/cclab-inu/KubeAegis), 최상위 LICENSE 미발견 | `third_party/LAB_KubeAegis` `79845cbcca83f12cab5cc7f6097a68dc2cb1fc5e`, clone clean·실행 전 | 논문 §VII의 이종 정책 의미 충돌 |
| KubeTeus | [INFOCOM 2025 원문](https://cclab.info/papers/2025_kim_infocom.pdf) | [연구실 공식](https://github.com/cclab-inu/KubeTeus), 최상위 LICENSE 미발견 | `third_party/LAB_KubeTeus` `d484afbfca924e68f5436a425ea0893c5346b7c0`, clone clean·실행 전 | 의도→네트워크 정책; MAS effect 범위 미확인 |
| Bambda | [IEEE Access 2025 원문](https://cclab.info/papers/2025_shin_access.pdf) | 공개 공식 코드 미확인 | 미확보 | 함수 호출 관계·caller 신원 결속을 원문에서 재확인 필요 |
| POLARIS | [Journal of Cloud Computing 2026 정식 DOI/초록](https://link.springer.com/article/10.1186/s13677-026-01014-0), 2026-10-23 공개 | [연구실 출판 목록](https://www.cclab.info/publications)에 code link 없음; 연구실 공개 org 11 repo에서 해당 코드 미발견(2026-11-25) | 코드 미확보, 원문 초록 확인 | LLM program inference 415 program–distribution pair, LSM-BPF symbolic-link PEP. 100%는 평가한 대상의 수치; MAS task authority 아님. 전문 PDF 접근 미완료 |
| ARES | [국내 학술대회 2026 원문](https://cclab.info/papers/kor/2026_shin_cisc-s.pdf) §III–IV, [저자 slide](https://cclab.info/papers/kor_ppt/2026_shin_cisc-s_ares.pdf) | [연구실 출판 목록](https://www.cclab.info/publications)에 code link 없음; 연구실 공개 org 11 repo에서 해당 코드 미발견(2026-11-25) | 코드 미확보, 원문·slide 직접 확인 | 사용자 Invoke + User Deny + 함수/자원 Reachability ARP; Llama-3.1-8B/vLLM, 4개 cloud 우회 차단 예시. 정상 완료/분모·실제 DB 상태는 원문에서 `NOT_ESTABLISHED`. 동명 외부 ARES repo 채택 금지 |
| Agent libOS (강한 외부 대안) | [SOSP AgenticOS 2026 논문](https://os-for-agent.github.io/papers/AgenticOS_SOSP_2026_paper_8.pdf) | [저자 공개 코드](https://github.com/yingqi-z20/Agent-libOS), Apache-2.0 | `third_party/ALT_Agent_libOS` `85e8ff94c1e562bfb1f891714e3bf4bed9795690`, clone clean·실행 전 | 현행 v1.6.0 코드의 Host-authored TaskAuthorityManifest는 논문 평가 version과 동일성 미확인. 현행 기능을 이전 논문의 관측 성능으로 소급하지 않음 |

`code confirmed`는 `method reproduced`를 뜻하지 않는다. 신규 코드의 license 및 고정 버전 확인 전 설치·실행하지 않는다.
