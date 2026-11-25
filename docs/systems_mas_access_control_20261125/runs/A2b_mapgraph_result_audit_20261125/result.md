# A2b: MAP-Graph 공개 Exp-5 결과의 재채점 가능성 감사

2026-11-25 UTC. 검증 질문: 공개된 41건의 `expected=BLOCK, actual=ALLOW`가 B2에서 확인한 모델 응답 파서 fallback 때문에 생겼는지 원시 자료로 확인할 수 있는가?

원저자 후보 공개 저장소 [MAP-Graph](https://github.com/xiaoqi-7/MAP-Graph/tree/d94b0bf3c73efdb60fcc08014989b44ce8eae99d), 고정 SHA `d94b0bf3c73efdb60fcc08014989b44ce8eae99d`. 원본 코드는 수정하지 않았다. 비용 USD 0, API 호출 0. 명령: `PYTHONDONTWRITEBYTECODE=1 python3 -B docs/systems_mas_access_control_20261125/runs/A2b_mapgraph_result_audit_20261125/audit.py` (exit 0). [감사 코드](audit.py)와 [기계 판독 결과](summary.json)를 보존한다.

`artifact/final_results/canonical/main/task_metrics.csv`에는 전체 21,600행, Exp-5는 8개 방법 각각 450행이다. `MAPGraph` 450행 중 41행은 `expected_decision=BLOCK`이면서 `actual_decision=ALLOW`였다. 이 수치는 집계 CSV에서 재확인된다. 그러나 이 CSV에는 모델 원문, 명시적 행동 파서 성공 여부, fallback 사용 여부, 외부 provider effect 필드가 없다. [원저자 README](https://github.com/xiaoqi-7/MAP-Graph/blob/d94b0bf3c73efdb60fcc08014989b44ce8eae99d/README.md)는 약 3.2GB의 원시 출력 root를 공개 아카이브에서 의도적으로 제외했다고 명시한다. 고정 clone에는 그 raw root가 없다.

**결론:** 41건의 결정 label은 재집계할 수 있다. 41건 중 fallback 발생 수, 모델의 실제 제안, 외부 서비스 효과 및 fallback이 결과를 바꾼 인과는 이 공개 자료로 **NOT_ESTABLISHED**. [B2](../B2_mapgraph_llm_20261125/result.md)는 별도 합성 2건에서 parser fallback 경계를 확인했지만, 이를 원저자 41건에 소급하지 않는다. H17의 구현 한정 Gap은 유지하고 논문 지표 오류/새 연구 Need는 `UNVERIFIED`로 둔다.
