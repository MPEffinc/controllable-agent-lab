# H1 후속: AutoCedar의 19개 불일치 원본 trace 탐색

2026-11-24, 읽기 전용 조사. 대상은 [K06 AutoCedar v2 §V-D2 Table VI](https://arxiv.org/html/2607.03656v2)의 **자기 검증 계획을 통과하고 독립 gold와 불일치한 19/197건**이다. 논문의 집계는 floor가 gold-금지 요청을 허용한 16건, ceiling이 gold-허용 요청을 배제한 2건, 두 오류가 함께 있는 1건이다. 이는 저자 결과이며 아래에서 개별 19건을 재현했다는 뜻이 아니다.

## 사전 등록한 좁은 질문과 종료 조건

- **질문:** 공개 원저자 artifact에서 19건 중 적어도 1건의 `case ID + 생성 candidate.cedar + 생성 floor/ceiling plan 또는 trace + gold.cedar`를 동일 run으로 묶을 수 있는가?
- **예상/반증:** 네 종류가 있으면, 정책이 자기 계획을 통과하면서 gold와 다른 요청의 Cedar symbolic counterexample을 API 0으로 1건 확인한다. 없다면 개별 19건 재현 가능성은 `NOT_ESTABLISHED`로 기록하고 synthetic 사례를 저자 결과로 바꾸어 부르지 않는다.
- **최소 비용:** 원저자 repo 및 논문/공개 release 목록의 읽기, 이미 있는 Cedar/CVC5 도구의 단일 실행만 허용. 유료 모델 호출 0, 원저자 repo 수정 0.
- **완료 조건:** 같은 run의 원본 candidate/plan/gold 연결을 찾거나, 지정한 공식 경로에서 그 연결이 공개되었음을 확인하지 못한 사실과 검색 범위를 기록한다.

## 확인한 공개 경로와 실제 결과

1. **논문:** [v2 §V-A, §V-D2, §V-D3](https://arxiv.org/html/2607.03656v2)는 200 gold 사례 구성법과 Table VI 집계, GPT-6-Luna medium 조건을 설명한다. 개별 19건의 case ID, 생성 정책 파일, 생성 plan 경로는 본문에서 제시하지 않는다. §V-D3은 사람 검토 모드를 아직 평가하지 않았다고 명시한다.
2. **원저자 repo:** [neselab/cedar-synthesis-engine](https://github.com/neselab/cedar-synthesis-engine), 로컬 고정 commit `a0cf180977d799cf943514b67ffc260fc579b9a5` (`third_party/K06-autocedar`, clean). [gold dataset README](https://github.com/neselab/cedar-synthesis-engine/blob/a0cf180977d799cf943514b67ffc260fc579b9a5/dataset/gold-reference-dataset/GOLD_REFERENCE_DATASET_README.md)는 `dataset/gold-reference-dataset/cases/`에 **200개** case, case당 정확히 7파일을 명시한다. 로컬에서 200개 디렉터리 모두 7파일임을 확인했다. 7파일은 `requirement.md`, `controlled-source.txt`, `gold/spec.json`, `gold/registry.json`, `gold/gold.cedar`, `gold/schema.cedarschema`, `gold/predicate_ast.json`이다. **어느 case에도 생성 candidate/plan/trace/result label이 포함되지 않는다.** `verify_gold.py`는 이 gold 입력→compiler 출력 무결성 검사이지 저자 197/19 결과의 재실행이 아니다.
3. **원저자 실험 디렉터리:** `experiments/`의 공개 묶음은 `cedarbench_aitl_fast`, `fig2_cyberchair`, `rede_autocedar`, `terminal_bench_science`, `github`이다. `find experiments -iname '*gold*'`, `git ls-files experiments | rg 'gold-reference|gold_reference|goldref|gold-ref'`, repository-wide `rg -l 'gold-reference-dataset'`에서 200-case 생성 run/output 묶음을 찾지 못했다. CedarBench/그림 2의 candidate와 plan은 **다른 실험**이므로 19건에 연결하지 않았다.
4. **공식 Git refs/release:** `git ls-remote --heads --tags`로 `main`이 위 commit임을 확인했다. 공개 `feat/v5-harness`의 tree에도 dataset 원본 외 gold-result 경로를 찾지 못했다. [GitHub releases](https://github.com/neselab/cedar-synthesis-engine/releases)는 확인 시 `v0.2.0` 1건, 별도 release asset 0건이었다. 탐색은 이 시점의 공개 refs와 release에 한정한다.
5. **같은 저자 조직의 별도 CedarBench repo 재확인:** 검색으로 [neselab/cedarbench](https://github.com/neselab/cedarbench)를 추가 발견해 `third_party/K06-cedarbench`에 commit `26539202f02af19466002cecc3db42fbada40702`로 별도 고정했다(원본 clean, Apache-2.0). 현재 README는 **226개** fixed-target scenario(79 mutation+147 realworld)를 기술하며, `BENCHMARK_LEVELS.md`의 **논문 당시 221개** 결과와 판본이 다르다. 일부 ultra-hard 사례의 candidate가 있지만 `gold-reference-dataset` 200건의 **당시 생성 candidate/plan/case 결과**가 아니다. `rg --files | rg 'gold-reference|gold_reference|candidate|trace'`로 그 연결 경로가 없음을 확인했다. 따라서 19건 원본 trace 판정은 변하지 않는다.

## 판정 및 실행 여부

**개별 19건의 case ID·candidate·plan trace: `NOT_ESTABLISHED` (검사한 공개 artifact에 없음).** 공개된 gold 200은 독립 참조 정책의 재컴파일을 지원하지만, 논문에서 불일치한 **어떤 19 case인지**와 당시 생성 target/policy를 복원할 자료가 없다. 사례 하나를 임의로 생성하면 ‘저자의 19건’ 재현이 아니며, LLM 재호출은 비용·비결정성까지 달라진다. 따라서 이번 후속에서 19건의 단일 반증 실험을 **실행하지 않았다**. 기존 `runs/K06_verify_20261124/`의 부모 에이전트 offline baseline/overbroad verifier 및 gold-200 무결성 결과도 중복 실행하거나 수정하지 않았다.

**다음 검증 질문:** 저자가 Table VI의 per-case 결과(`case ID`, source commit, 최종 candidate, generated plan/trace, gold-fit 비교 로그)를 공개하면, 한 건을 고정해 `cedar validate`와 `cedar symcc`로 `L ⊆ P ⊆ U` 및 `P ≠ G`의 반례를 확인할 수 있다. 현재 H1의 좁은 Research Gap 판정은 계속 `UNVERIFIED`이며, 공개 trace 부재 자체를 기술적 갭이나 실패 사례로 판정하지 않는다.
