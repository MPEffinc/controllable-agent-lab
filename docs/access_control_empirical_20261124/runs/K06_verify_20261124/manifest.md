# K06 AutoCedar 제공 workspace 형식 검증 — 실행 결과

사전 질문·예상·반증·비용·완료 조건은 [prereg.md](prereg.md). **공식 원저자 코드** `third_party/K06-autocedar` `a0cf180977d799cf943514b67ffc260fc579b9a5`의 `autocedar.cli verify`를 호출했다. 원본 저장소는 수정하지 않고 `workspace/`의 검토한 사본만 `input/`에 복사했다. 사전 입력 해시는 [input.sha256](input.sha256). `verification_plan.py`는 `get_checks()`와 참조 파일 경로 정의만 포함하며, CLI가 Python `exec_module`로 로드하는 점을 실행 전에 확인했다.

## 독립 도구와 환경

- Python 3.11 격리 venv: `env/venv`; 원본 `uv.lock` SHA256 `b9c3d96c4a4c369bcf2aee9415728d88c2448bc3fc05db08b65082fac9746eb6` 기반. 모델/API 호출 0, 비용 USD 0, seed 해당 없음.
- [공식 Cedar CLI 실험 바이너리 릴리스 v4.12.0](https://github.com/cedar-policy/cedar/releases/tag/cedar-policy-cli-v4.12.0)의 Linux x86_64 archive SHA256 `bb991fe1fc25b24d1a1cd1b78266950e8d33015eb818acabe297365bc4905392`. 다운로드 archive와 [공식 릴리스 자산 checksum](https://github.com/cedar-policy/cedar/releases/expanded_assets/cedar-policy-cli-v4.12.0)이 일치했다. 이 버전은 AutoCedar README가 예시로 명시한 4.10.0보다 최신이므로 정확한 논문 도구 버전 재현은 아니다.
- [공식 cvc5 v1.4.2](https://github.com/cvc5/cvc5/releases/tag/cvc5-1.4.2)의 `cvc5-Linux-x86_64-static.zip` SHA256 `7eb18f8c814c36a46c5a7d003983e9cfbc4b0a9828d6dd596239291bd4cc61d8`. 다운로드 archive와 [공식 릴리스 자산 checksum](https://github.com/cvc5/cvc5/releases/expanded_assets/cvc5-1.4.2)이 일치했다.
- 바이너리·venv는 `env/`에 격리하고 `.gitignore`로 제외. 호스트 패키지나 원본 코드 설치·수정 없음. 실행 wrapper는 [run_verify.py](run_verify.py); 입력 경로/도구 버전/해시/원시 stdout·stderr/내부 exit code를 별도 저장한다.
- 제공 `verification_plan.py` 상단 설명은 "10 checks"라고 쓰지만 실제 `get_checks()`는 6개를 반환하며 CLI도 6개만 보고한다. 이 실험의 분모는 **실행된 6개**다. 주석 불일치를 추가 정책 실패로 세지 않는다.

## 명령과 관측

```bash
python3 docs/access_control_empirical_20261124/runs/K06_verify_20261124/run_verify.py docs/access_control_empirical_20261124/runs/K06_verify_20261124/input baseline
python3 docs/access_control_empirical_20261124/runs/K06_verify_20261124/run_verify.py docs/access_control_empirical_20261124/runs/K06_verify_20261124/input_overbroad overbroad
```

두 번째 입력은 첫 입력을 **새 run 디렉터리에서 복사**한 뒤 `candidate.cedar` 끝에 `permit(principal, action == Action::"View", resource);` 한 줄을 추가한 음성 대조군이다. 나머지 schema/plan/reference는 동일하다.

| 조건 | CLI exit | 형식 검사 / effect | 원시 증거 |
|---|---:|---|---|
| 제공 후보 | 0 | `view_safety`, `edit_safety`, auditor floor 2개, liveness 2개 모두 PASS; `loss: 0` | [stdout](baseline.stdout), [metadata](baseline.json) |
| 넓은 View 허용 추가 | 1 | `view_safety: FAIL (implies)`, `loss: 1`; `HighlyRestricted` 문서 등 허용 범위를 넘는 Cedar 요청 반례 출력. 다른 5개 검사 PASS | [stdout](overbroad.stdout), [metadata](overbroad.json) |

여기서 확인한 것은 제공 sample의 **정해진 schema·verification plan에 대한 Cedar/SymCC 판정**이다. 사용자/조직 의도와 target의 독립적 일치, LLM 정책 생성, 실제 서비스 PEP 및 effect는 `NOT_ESTABLISHED`. 원저자 논문의 200개 gold 정책 평가 재현도 아니다. 확대 규칙을 넣었을 때 왜 거부되는지 설명하는 **정형 반례**만 확인했다.
