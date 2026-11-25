# M4 원저자 guard 입력 경계: 결과

2026-11-25 UTC. [사전 등록](prereg.md) 후 [정확한 명령](commands.md)으로 저자의 변경하지 않은 `guard()`를 직접 호출했다. 입력과 원시 출력은 [decisions.jsonl](decisions.jsonl), 사용한 독립 합성 driver는 [guard_boundary.py](guard_boundary.py)다. 원저자 저장소는 [논문이 직접 연결한 코드](https://arxiv.org/html/2609.08258)이며, 고정 commit `15dcd20b3c0de4f27d9a8dd10a830dea91641b81`, Apache-2.0. `guard/stale_guard.py` SHA-256 `e85f804019fcfbd2e8cbc05a7ebd3997c2267259094be3ebddecf214232dcabf`; driver `d90d9746e8f838abb85f74638a9e0b12e48ae2a6ff9146ec2951672277083ce9`; 출력 `aa73c18a492e8e75b3f0cf4915d886e0e181c0dc521a116a0370a20d4e429c6d`. Python 3.10.12, 종료 0, 유료 API $0, 외부 서비스 효과 0.

| 합성 입력 | 공개 `guard()`의 `kept` | `withheld` | 판정 |
|---|---|---|---|
| 오래된 `r1`에 `expired_at`, 현재 대체 `r2`, agent가 오래된 결론을 새 현재 `j`로 재기록; `j`에 출처/파생 철회 정보 없음 | `r2`, **`j`** | `r1` (`backend marked expired_at`) | 현재 journal의 부적절한 결론을 guard가 그대로 반환 |
| 동일하되 외부에서 `j.revoked_at`을 정확히 제공 | `r2` | `r1`, `j` | 해당 표지가 있으면 두 기록 모두 제외 |

저자 함수의 1단계는 이미 표시된 `expired_at`/`revoked_at`을 필터링하고, 2단계는 남은 기록의 시간 순서와 텍스트 충돌 휴리스틱을 사용한다. 원본 `r1`을 제거한 뒤에는 새 `j`와 `r1` 사이의 출처 의존성이 입력에 없고, 이 합성 문장에서는 `j`를 제거하지 않았다. 이는 **source-native 함수 입력 경계 실험**이다. Graphiti ingestion, LLM의 실제 write-back, [Appendix C.1](https://arxiv.org/html/2609.08258)의 356/358 조건, 하위 결정 또는 provider effect는 재현하지 않았다. 실제 `j`가 어떻게 생성되는지와 양성 journal 오차율도 측정하지 않았다.

원문의 직접 측정은 별도다. [Appendix C.1/Table 14](https://arxiv.org/html/2609.08258)는 이미 hop-0에서 오염된 결정을 내린 조건에서 direct write-back의 필터 후 후속 unsafe 결정을 hop1 255/356, hop2 283/356, hop3 296/356으로 보고한다. natural ingestion은 active journal 22/358, 그 중 19/22가 hop1 필터 뒤 unsafe였고 전체 natural filtered hop1은 27/358이다. 두 분모/ingestion 모드를 합치지 않는다. 이는 Graphiti 및 저자 조건의 **결정 결과**이며 실제 외부 provider effect 보장이 아니다.

**판정:** 현재성 표지에만 의존하는 검색 guard가 철회된 출처에서 유래한 *표지 없는 새 journal*을 제거하지 못하는 조건은 원문·코드·독립 합성 입력이 일치하므로 이 **구체 조건에서 `GAP_SUPPORTED`**. 그래프가 trusted write-time lineage와 정확한 철회 event를 보유한다면 [MAP-Graph](https://arxiv.org/html/2608.10509v1)의 recursive ancestry/action gate, Audience-Bound Persistent Memory의 currentness cascade 등이 직접 반박이다([대안 감사](../../m4_alternatives_note_20261125.md)). 따라서 **새로운 독립 메커니즘 Need는 `UNVERIFIED`**. 다음 최소 반증은 동일 실제 write-back trace에 (1) current-only guard, (2) 정확한 code-owned lineage+revocation, (3) 빈약하거나 잘못 연결된 lineage를 붙여 정상 최신 journal 보존과 unsafe action/effect를 함께 비교하는 것이다.
