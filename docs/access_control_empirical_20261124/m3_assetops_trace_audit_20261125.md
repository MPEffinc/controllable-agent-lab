# M3 / Multi-CaMeL AssetOpsBench 범위 대체 궤적 공개 여부 감사

**감사일:** 2026-11-25 UTC. **대상:** 논문 저자 저장소 [james-pete/multiagentdojo](https://github.com/james-pete/multiagentdojo)의 로컬 고정 checkout `third_party/multiagentdojo/`, commit `e71647382155dc6949d6ccf9a9d7ec7cf429b856`. `git status --short`는 빈 결과였다. 읽기 전용 검색만 수행했으며 원본 코드·기존 `runs/`를 수정하지 않았고 모델/API를 호출하지 않았다.

## 결론

**§V-C.2의 “근접하지만 다른 asset/time/scope를 child가 반환하고 parent가 진행”한 특정 실패 궤적은 이 고정 저장소에서 찾지 못했다.** 논문은 여러 AssetOpsBench 궤적에서 이 정상 업무 실패를 관찰했다고 쓰지만 [§V-C.2](https://arxiv.org/html/2610.05640v1)에 그 사례의 task ID, raw child input/output, parent 실행 로그, 최종 service effect는 제시하지 않는다. 따라서 특정 실패의 exact asset/time 차이와 downstream effect는 `NOT_ESTABLISHED`; 비인가 provider write는 `UNVERIFIED`다. 저자 보고를 부정하는 결과도 아니다.

이 저장소의 [README](https://github.com/james-pete/multiagentdojo/blob/e71647382155dc6949d6ccf9a9d7ec7cf429b856/README.md)는 공개 artifact를 **MultiAgentDojo**(AgentDojo 확장)와 individual/multi-CaMeL 구현이라고 설명한다. [논문 §V](https://arxiv.org/html/2610.05640v1)는 utility 평가에는 **별도 AssetOpsBench**, 보안/utility 평가에는 MultiAgentDojo를 사용했다고 구별한다. 로컬 `src/agentdojo/data/suites/`의 suite는 `banking`, `slack`, `travel`, `workspace` 네 가지뿐이다. `runs/`에는 git tracked 파일 36,679개(전체 디렉터리 525 MB)가 있으나, JSON 내용에 대한 filename-only 고정 문자열 검색에서 `AssetOpsBench`, `IoTAgent`, `FMSRAgent`, `Chiller 6`, `assetnum` 각각 일치 파일 **0개**였다. `README.md`, `src/`, `tests/`, `docs/`, `examples/`, `util_scripts/`에서도 `AssetOpsBench` 문자열 0건이었다. 이는 **해당 checkout에서의 검색 범위**이지 저자의 모든 비공개/외부 실험 자료의 부재 증명은 아니다. 저장된 `runs/`는 기존 AgentDojo 계열 평가 출력이며 AssetOpsBench 실험 궤적으로 취급하면 안 된다.

## 공개된 가장 가까운 자료: 논문 부록 A의 task 609

[논문 Appendix A](https://arxiv.org/html/2610.05640v1)는 AssetOpsBench **task 609**의 Multi-CaMeL 예시를 공개한다. 이는 §V-C.2에서 지목한 실패 사례라고 명시되지 않는다. 공개된 것은 생성된 agent 프로그램이며 raw tool response 값은 보이지 않는다.

| 구분 | 부록 A에서 직접 확인한 내용 | 해석 한계 |
|---|---|---|
| 원래 요청·child 입력 | 부모는 IoTAgent에 `Chiller 6`, site `MAIN`의 정확한 sensor 목록을 요청한다(부록 A 441–454행). | 시점 범위 요청은 이 예시에 없음. |
| IoT child 생성 코드 | `sites()` 결과에 `MAIN`이 없으면 첫 번째 site로 `site`를 바꾸는 분기가 있고, 그 `site`로 `sensors(site_name=site, assetnum="Chiller 6")`를 호출한다(589–623행). | **다른 site로 바꿀 수 있는 코드 경로**이지만 `sites_r`의 실제 값/분기 실행은 공개 부분에서 확인되지 않는다. 실제 범위 대체를 관찰했다고 쓰면 안 된다. |
| child 출력 | `sens_r`, `sensor_names`에서 자연어 `final_return_value`를 생성하는 프로그램(653–699행). | 실제 `sens_r`/sensor 목록/IoTAgent 최종 문자열 값은 미제시. exact-scope 비교 불가. |
| 부모 후속 | 부모는 `iot_resp`를 `available_sensors` 변수로 FMSRAgent에 넘기고, `iot_resp`/`fmsr_resp`를 사용해 답변을 합성한 뒤 `verify_hypothesis`를 호출한다(455–585행). | 출력이 다를 때 어떤 branch가 실제 실행됐는지, 최종 사용자 답변 값은 미제시. provider write/상태 변화는 이 예시에서 보고되지 않는다. |

task 609의 site fallback은 확인 가능한 **잠재적 경로**다. `MAIN`이 실제로 없었거나 다른 site의 sensor를 썼다는 관찰은 아니다. 부모의 후속 코드가 IoT 결과를 이용하도록 작성돼 있다는 사실은 확인되지만, provider effect가 발생했다는 근거는 없다. [Appendix B](https://arxiv.org/html/2610.05640v1)의 29개 `impossible` task 목록에 609는 없으나, 그 목록 제외는 이 특정 프로그램의 성공/실패 판정이 아니다.

## 원본 코드 경계 및 작은 검사의 가능성

저장소 고정 소스 [`src/agentdojo/agent_pipeline/multi_agent.py` 647–692행](https://github.com/james-pete/multiagentdojo/blob/e71647382155dc6949d6ccf9a9d7ec7cf429b856/src/agentdojo/agent_pipeline/multi_agent.py)에서 `MultiCaMeLPipeline._make_subagent_tool`은 child 최종 assistant content를 `get_text_content_as_str(...)`로 **문자열** 반환한다(680행). 이 함수 내부에는 부모가 요청한 asset/site/time tuple과 child의 실제 응답 scope를 구조화해 대조하는 코드가 없다. 그러나 이것만으로 전체 AssetOpsBench 배포에 다른 validator가 없었다고 단정할 수 없다. 이 checkout에는 AssetOpsBench adapter, task 609 데이터, §V-C.2 실패 raw trajectory가 없다.

**API 없는 최소 검사의 실행 가능성:** [`tests/test_camel.py`](https://github.com/james-pete/multiagentdojo/blob/e71647382155dc6949d6ccf9a9d7ec7cf429b856/tests/test_camel.py)는 fake Sequrity client를 사용해 local 호출을 검증한다. 이 fake client와 새 synthetic `asset/site/time` 반환값을 이용하면, 별도 격리 test에서 *문자열 child 결과를 그대로 parent에 전달하는 현재 경계*와 *trusted request tuple·typed result tuple을 비교해 불일치를 차단하는 외부 adapter*를 저비용으로 대조할 수 있다. 이는 **MultiAgentDojo 소스의 일반 handoff 경계에 대한 독립 합성 실험**이지 AssetOpsBench task 609나 §V-C.2 실패의 원저자 재현은 아니다. 실제 실패를 source-native exact-scope로 확인하려면 평가 당시 AssetOpsBench 코드/데이터 버전, 특정 task ID, 원 요청, raw tool/child 결과, 부모 후속 궤적이 먼저 필요하다. 현재 고정 checkout만으로는 이 실험의 정답 label을 독립 결정할 수 없다.

## 재검사 명령과 판정

```bash
cd /home/cclab/controllable_agent/third_party/multiagentdojo
git rev-parse HEAD
git status --short
git ls-files 'src/agentdojo/data/suites/**' | sed -E 's@^src/agentdojo/data/suites/([^/]+)/.*@\1@' | sort -u
git ls-files 'runs/**' | wc -l
for term in AssetOpsBench IoTAgent FMSRAgent 'Chiller 6' assetnum; do printf '%s: ' "$term"; rg -l -F -m1 "$term" runs --glob '*.json' | wc -l; done
rg -l -F -m1 'AssetOpsBench' . --glob '!runs/**' --glob '!*.ipynb' --glob '!.git/**'
```

보고서 판정: 원문의 **정상 task utility 실패 저자 관찰**은 확인되지만 이 checkout에서 특정 사례의 raw trace/effect를 독립 검증하지 못해 `UNVERIFIED`다. 새 보안 Research Need 판정도 `UNVERIFIED`. 강한 반증 조건은 신뢰된 정확한 scope metadata를 child 결과에 붙이고 parent/sink에서 원 요청과 비교했을 때, 정상적인 정확 범위 결과는 통과하고 근접 범위는 차단되는지를 같은 작업에서 관찰하는 것이다. 그 대조가 성립하면 이 국소 조건은 기존 typed check로 해결된다.
