# C3 원본 AutoCedar 완료·승인 경계 결과

2026-11-25 UTC. [사전등록](prereg.md), [실행 코드](run.py), [원시 명령·출력·SHA·상태](raw.json), `service_state.sqlite`. 공식 AutoCedar source SHA `a0cf180977d799cf943514b67ffc260fc579b9a5`. 공개 `fig2_cyberchair/haiku-4-5-2026-10-27`은 **수동 AITL target의 디버그 trace**다. 논문 19개 gold 불일치 후보와는 관계를 확인하지 못했다. 모델/API 비용 $0, 외부 서비스 0.

- 저자 archive의 `stage3/final_candidate.cedar`와 `harness_runs/scenario/candidate.cedar` SHA 일치. 원본 `autocedar.cli verify` 재실행은 **42 PASS, 0 FAIL, loss 0, exit 0**.
- 저자 `stage2_5/final_user_decision.json`은 `approved=false`: 자동 또는 plumbing-only atom 승인에는 사람의 의미 승인 근거가 없다는 이유다. 이는 의미 오류를 발견한 reviewer 거부가 아니다.
- 원본 `cli._authoring_completed`는 후보 파일 존재만 확인해 `True`를 반환했다. `_cmd_author`는 `approved: False`를 별도 출력하지만 완료되면 exit 0을 반환한다. [코드](../../../../third_party/K06-autocedar/autocedar/cli.py)의 주석은 완료와 사람 승인 분리를 **의도적 설계**라고 밝힌다.
- 같은 저장 후보의 `submitStep1` 정상 요청은 Cedar CLI `ALLOW`. 독립 SQLite 소비자 `completion_only`는 이를 모의 서비스에 기록해 effect +1, `approval_gate`는 +0. 두 arm의 작업 정상성 차이는 human approval 없을 때의 합리적 보류 비용이다.

**판정:** `CLI exit=0` 또는 후보 파일만을 배포 승인으로 해석하는 소비자에는 **조건부 승인 경계 Gap이 실증**됐다. 원저자 시스템이 실제로 무승인 정책을 배포하거나 그 후보가 승인 의도와 틀렸다는 증거는 아니다. 이미 존재하는 `final_user_approved` 확인을 release gate에 결속하면 이 고정 문제는 해결되므로 새로운 메커니즘 Need는 기각된다. 여러 생성기/PEP에 걸친 서명된 승인 artifact와 활성 정책의 결속·정상성/비용이 실제로 미충족인지 별도 검증해야 한다.
