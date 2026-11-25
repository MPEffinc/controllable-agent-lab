# H7 전체 effective policy에 대한 공식 prover 대조 결과

사전 등록은 [manifest.md](manifest.md). 공식 OpenShell v0.1.9 prover binary `local/openshell-20261124/releases/v0.1.9/openshell-prover`를 사용했다. 이전 K14 실행의 `base-after.json`과 `full-after.json`에서 `policy` 객체만 Python 표준 `json`으로 추출했다. `boundary.json`은 provider 부착 전 승인 상한이고 `base-candidate.json`은 같은 base, `full-candidate.json`은 provider 부착 후 전체 effective 정책이다. 입력에 credential은 없다. SHA-256: boundary/base `9d0f66ab209e19700f62e817ddbabf2ef4ea876fb2d080b3f7970dfb5f5d4ff7`, full `8bee0024ae7088f085d62f48e71222a44ce420e734dcb62e8f1e1f9da6c7ff35`.

```bash
openshell-prover check base-candidate.json --boundary boundary.json --output json
openshell-prover check full-candidate.json --boundary boundary.json --output json
```

| 후보 | 원시 결과 | 해석 |
|---|---|---|
| base | [base-result.json](base-result.json), exit 0 `within_boundary` | 자신과 같은 상한이므로 통과. provider 기여를 빠뜨린 입력이다. |
| full | [full-result.json](full-result.json), exit 1 `exceeds_boundary` | network L4 `pypi.org:443` 허용 확대의 반례. `destination_ip: 8.8.8.8`은 prover의 정형 증인이고 실제 DNS 질의/접속 결과가 아니다. |

검사 도메인은 `filesystem,network_l4,network_rest,process,landlock`이다. 이 대조는 **정책 포함 검사**로서 provider endpoint의 실제 효과, 정책 목표 적절성 또는 runtime attach 전 자동 gate 적용을 증명하지 않는다. 그래도 이 정책 형상에서 “base만 검토하면 provider 확대가 보이지 않는다”는 위험과 “전체 effective를 검사하면 기존 prover가 그 확대를 검출한다”는 직접 반박을 동일 입력으로 확인했다. Docker/LLM/API 실행 0, 외부 비용 0.
