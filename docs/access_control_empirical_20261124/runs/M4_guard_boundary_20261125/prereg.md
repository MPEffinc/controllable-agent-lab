# M4 원저자 guard 함수의 write-back 경계 최소 확인 — 사전 등록

작성일 2026-11-25 UTC, 실행 전. 원저자 [VulcanLab/Memory-Rebirth-Attack](https://github.com/VulcanLab/Memory-Rebirth-Attack) 고정 commit `15dcd20b3c0de4f27d9a8dd10a830dea91641b81`의 `guard/stale_guard.py`를 **수정 없이** 직접 호출한다. 이는 Graphiti/모델/저자 Appendix C.1의 356개 run 재현이 아닌, 공개 guard 함수의 입력 경계에 대한 독립 합성 사례다.

## 질문

명시적으로 revoked 표시된 원본 `r1`과 현재 대체 `r2`가 있을 때, agent가 `r1`의 부적절한 결론을 **새 current journal `j`**로 쓴다면, 공개 `guard()`가 `r1`만 거르고 `j`를 남기는가? 외부에서 `j`에도 파생 무효 표지를 정확히 붙이면 같은 함수가 이를 거르는가? 실제 write-back ingestion은 이번 실험에 없다.

## 입력과 예측

- `r1`: `fact="Deployment may be approved by one reviewer."`, `expired_at=2026-01-01`, 과거 생성 시점.
- `r2`: `fact="Deployment requires two independent reviewers."`, current, `created_at=2026-02-01`.
- `j`: `fact="Deployment may be approved by one reviewer."`, current `created_at=2026-03-01`. `r1`에서 파생됐다는 metadata는 공개 guard 입력에 없다.
- Case A: `guard([r1,r2,j])`에서 `r1`은 withheld되고 `j`는 kept될 것으로 예상. `r2`는 현재 정책이므로 kept가 바람직하나 lexical conflict heuristic이 이를 다르게 처리할 수 있어 관찰로 기록한다. 핵심은 `j`가 남는가.
- Case B: 동일 입력에서 `j`에 `revoked_at=2026-03-02`를 추가한 반사실 대조. `j`도 withheld될 것으로 예상. 이 표지는 **실험이 외부에서 공급**하는 것이고 저자 시스템이 자동 유도했다는 뜻이 아니다.

반증 관찰: Case A에서 `j`가 withheld되면 공개 guard가 표지 없이도 이 예의 write-back을 식별한 것이다. Case B에서 `j`가 kept되면 명시 표지 필터 예측이 틀렸다. 두 case 모두 `r1`이 kept되면 기본 guard 단계가 예상대로 동작하지 않은 것이다.

## 비용/완료

`python3 -I`로 cwd `sitecustomize.py` 자동 실행과 환경 경로를 격리하고, `guard/stale_guard.py`만 import한다. stdlib만 사용, 네트워크·Docker·LLM/API 호출 0, 원저자 파일 수정 0. 입력 record, kept/withheld, source SHA-256과 정확한 명령을 raw JSONL 및 결과 파일에 기록하면 완료. 실행 1회, 오류 원인 확인 후 최대 1회 재시도.
