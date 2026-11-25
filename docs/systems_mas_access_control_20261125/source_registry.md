# 새 출처·코드 원장

기존 K01–K15 공식/후보 코드와 상태는 [기존 registry](../access_control_empirical_20261124/paper_registry.md)를 참조한다. 본 표의 새 checkout은 원본 변경 없이 보존한다.

| 연구 | 1차 출처 | 공개 코드 | 로컬 SHA·상태 | 한계 |
|---|---|---|---|---|
| ALPS | [INFOCOM 2026 원문](https://cclab.info/papers/2026_shin_infocom.pdf) | [연구실 공식](https://github.com/cclab-inu/ALPS), Apache-2.0 | `third_party/LAB_ALPS` `ace0fd2cabdc100bf5491bad3389e47bce6a37f9`, [공식 verifier 12 test 통과](runs/A3_alps_runtime_20261125/result.md) | 정적 함수 코드→IAM/SDK call; 동적 MAS origin scope 평가 미확인 |
| KubeAegis | [IEEE Access 2024 원문](https://cclab.info/papers/2024_kim_access_kubeaegis.pdf) | [연구실 공식](https://github.com/cclab-inu/KubeAegis), 최상위 LICENSE 미발견 | `third_party/LAB_KubeAegis` `79845cbcca83f12cab5cc7f6097a68dc2cb1fc5e`, clone clean·실행 전 | 논문 §VII의 이종 정책 의미 충돌 |
| KubeTeus | [INFOCOM 2025 원문](https://cclab.info/papers/2025_kim_infocom.pdf) | [연구실 공식](https://github.com/cclab-inu/KubeTeus), 최상위 LICENSE 미발견 | `third_party/LAB_KubeTeus` `d484afbfca924e68f5436a425ea0893c5346b7c0`, clone clean·실행 전 | 의도→네트워크 정책; MAS effect 범위 미확인 |
| Bambda | [IEEE Access 2025 원문](https://cclab.info/papers/2025_shin_access.pdf) | 공개 공식 코드 미확인 | 미확보 | 함수 호출 관계·caller 신원 결속을 원문에서 재확인 필요 |
| POLARIS | [연구실 출판 목록](https://www.cclab.info/publications), Journal of Cloud Computing 2026 to appear | 공개 공식 코드 미확인 | 미확보 | 파일 접근 정책, 정확 원문 링크 확인 필요 |
| ARES | [연구실 출판 목록](https://www.cclab.info/publications), 국내 학술대회 2026 | 공개 공식 코드 미확인 | 미확보 | 4쪽 PDF의 텍스트 추출 제한; 동명 외부 ARES와 혼동 금지 |

`code confirmed`는 `method reproduced`를 뜻하지 않는다. 신규 코드의 license 및 고정 버전 확인 전 설치·실행하지 않는다.
