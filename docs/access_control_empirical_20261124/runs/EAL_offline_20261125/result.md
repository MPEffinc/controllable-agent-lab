# 결과 — EAL-Bench 지속 승인 메모리 공개 자료 오프라인 감사

2026-11-25 UTC. [사전등록](prereg.md)·[정확 명령](commands.md)·[v1 저장 집계 출력](tables/)·[v2 보존 실패 진단 재계산](diagnosis.json). 논문 [v2](https://arxiv.org/html/2609.01836v2) 2026-10-24, 논문이 연결한 [저자 공식 저장소](https://github.com/tommasocerruti/eal-bench) 고정 commit `51648690bc52d7a9c7ac080a2c67a784fe9d56cb`(2026-09-23). 로컬 원저자 소스 변경 0. 저장소 root에 `LICENSE`/`COPYING` 파일이 없고 `pyproject.toml`에 라이선스 선언이 없어 **코드 재사용 라이선스 `UNKNOWN`**으로 기록한다. 이 조사에서는 읽기·실행만 했으며 코드를 복제한 보고서에 포함하지 않는다.

## 우리가 실제 실행해 확인한 것

| 자료/명령 | 출력 | 증거 수준 |
|---|---|---|
| `python3 -m analysis.paper_results --domain all ...` | 3 domain의 고정 manifest/source hash를 읽고 표를 생성. 각 domain의 원시 artifact는 procurement 0/230, cybersecurity 0/230, finance 0/255 검증; 원시 trial route 0/15씩 재계산 | **저장 count 검증**, 논문 v1 기준. v2 저자 실행 재현 아님 |
| `python3 -m analysis.extension_results` | v2 extension의 보존 snapshot·진단 파일 **200개 SHA-256 일치**. 원본 raw extension run 및 완전한 frozen run selection 부재를 자체 보고 | 해시 연결된 저자 집계 존재 확인; **독립 trial 재채점 불가** |
| `--diagnosis --out ...` | 보존 `results/diagnosis/failures.csv` 3,569 failure row를 진단 규칙으로 재분류: harness-log `restatement_applied` 1,998, `own_action_as_approval` 285, `authoritative_change_misapplied` 119, `update_failed` 1,157, `other` 10; [출력 JSON](diagnosis.json) | 보존된 **파생 CSV의 재계산**. 원래 model/tool trace 전체 재검증 아님 |

저장 `seven_summary.json`의 v2 Table 13 숫자는 [원문 Appendix B Table 13](https://arxiv.org/html/2609.01836v2)과 맞는다. 예: typed incremental에서 Procurement 비인가 도구 행동 402/1512·정상 행동 1455/1512, Cybersecurity 282/2688·2376/2688, Finance 617/1344·1328/1344. 이 일치는 보존 snapshot을 읽은 결과이며 7 writer/3 seed raw trials에서 독립 재계산한 결과가 아니다. `analysis.paper_results`의 출력 분모가 1080/1920/960인 것은 manifest가 **v1 5 writer**를 고정하기 때문이다; v2 Table 13의 1512/2688/1344와 합쳐 하나의 실험으로 쓰지 않는다.

해시: `results/extensions/manifest.json` `bb6beb0228787dd809fdfaefcbce8fa337c74d28c3e37a4c0378d2bc1f70663a`; `seven_summary.json` `74d6067d853593b7c17ba7ff16912d2cbab0d0baec6e0283a9ae5880901e7d33`; `gate_added_table.json` `035c46414ac3706fc1f53339ce521610dad533e3aaf43f55c3f6009a77d1256e`; `parity_pool.json` `9b7b4a70d75385a2e7d563e3bd6c1807740daf92c76ee66ce3b9bfc0d665ead4`. 사용 Python 3.12.15, 외부 설치/모델/API/운영 서비스 0, 비용 USD 0. 원본 repo의 `git status --short` 빈 결과.

## 보안 질문에 대한 원문 판정

[v2 §4.2–4.6, Appendix C.1–C.4](https://arxiv.org/html/2609.01836v2)는 **권한 있는 출처를 확인하는 것과 그 출처의 승인 내용·철회 시점이 메모리에 정확히 남는 것을 분리**한다. 같은 typed incremental comparison에서 source-authority filter의 비인가 행동은 23.5%→7.3%지만 정상 행동은 93.1%→53.2%; event-based memory는 23.4%→9.3%, 정상 93.0%→68.6%다. 전자는 source가 권한 있는 사람이어도 잘못 기억한 범위/철회가 남고, 후자는 중요한 grant/revoke update를 놓친다. 이것들은 **저자 결과**, 본 오프라인 실행이 생성한 행동 관측이 아니다. 본 저장소의 v2 snapshot `gate_added_table.json`은 Appendix C.1의 **별도 진단**에서 출처 filter 후에도 45/1848 비인가 probe가 잘못 승인 상태로 표현된 것을 저장한다; 본문 paired comparison의 분모와 섞지 않는다.

가장 강한 **같은 논문 내부 반박**인 3-block마다 전체 history 재구축은 비인가 행동 23.5%→4.9%, 정상 행동 93.1%→95.2%로 개선했으나, writer input token 1.2–3.0배와 타이밍 의존성을 저자가 인정한다. 이 성능은 의미 보존의 원리적 불가능성을 증명하지 않는다. [oracle-exact memory](https://arxiv.org/html/2609.01836v2)는 선택된 오류 사례에서 390 trial 중 1건만 비인가 행동을 보였으므로 **정확한 승인 상태가 있으면 직접 해결**된다. 필요한 남은 질문은 자연어 승인 변경으로부터 이 정확한 상태를 어떤 비용·정상 업무 손실로 확보하는가다.

**현재 판정:** 이 벤치마크·완화책의 잔여 의미 오류와 안전/정상 tradeoff는 **저자 관측에 기반한 좁은 실증 Gap 후보**다. 본 실행은 저장 집계와 코드 경로만 검증했으며, 독립 trial 재채점·실제 provider effect·다른 기존 해법의 같은 입력 대조는 `NOT_ESTABLISHED`. 따라서 *범용 신규 메커니즘 Need는 `UNVERIFIED`*. 기존의 정확한 event ledger/권한자 검토/주기적 재구축이 같은 입력·비용에서 안전과 정상 행동을 충분히 유지한다면 가설을 기각한다.
