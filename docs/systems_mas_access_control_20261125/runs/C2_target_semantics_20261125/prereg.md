# C2 사전등록 — AutoCedar 검증 목표의 의미 대조

2026-11-25 UTC. 공식 AutoCedar source `a0cf180977d799cf943514b67ffc260fc579b9a5`, gold dataset `case-011`. C1–C1c 모델 생성이 후보 전 종료됐으므로 이 실험은 **독립적으로 만든 후보와 검증 계획**을 원저자 `autocedar.cli verify`에 입력한다. 저자 평가의 후보 재현이 아니다.

- **RQ:** 형식 verifier가 주어진 target을 정확히 검사하더라도, 승인 의도에서 `onVpn` 조건이 빠진 target 자체의 오류는 어떤 추가 oracle이 있어야 발견되는가?
- **고정 정책:** 원본 `gold.cedar`의 단일 permit에서 `&& (context.onVpn)`만 삭제한 후보. 더 넓은 target도 같은 삭제본으로 구성한 self-reference arm, 원본 gold를 reference로 쓰는 independent-target arm. 두 arm의 후보·schema·toolchain은 동일하다.
- **검증:** 각 arm에 candidate⇒target ceiling과 target⇒candidate floor의 두 check를 넣고 원저자 `verify`를 호출한다. 독립 Cedar CLI `authorize`로 (정상 maintainer+VPN+승인), (같지만 VPN off), (작성자 본인) 세 요청의 allow/deny 및 격리된 모의 PR 상태 `open→merged`를 측정한다.
- **예상/반증:** self-reference는 통과하나 독립 gold ceiling은 반례를 줄 것으로 예상. 두 arm 모두 pass하거나 gold와 잘못된 후보의 효과 차이가 없으면 예측이 반증된다. 어떤 결과라도 기존 gold oracle/Cedar verifier로 해결 가능하면 새 메커니즘 Need는 기각한다.
- **범위/비용:** plan은 연구자가 작성했고 gold가 정답이라는 신뢰 전제다. 외부 GitHub 서비스 효과가 아니라 로컬 상태 어댑터. 모델/API $0. 원시 명령·stdout/stderr·정책·SHA·전후 상태 보존. 완료 후 plan을 변경해 결과를 맞추지 않는다.
