# Codex bootstrap: using these files

1. Extract this archive **inside your existing `controllable_agent/` working directory**, keeping existing work. It contains only `CONTEXT.seed.md` and `CODEX_BOOTSTRAP_PROMPT.md`, so it does not overwrite an existing `CONTEXT.md`.
2. Open Codex with its working directory set to `controllable_agent/`.
3. Paste this message:

   > `CODEX_BOOTSTRAP_PROMPT.md`와 `CONTEXT.seed.md`를 읽고 지시된 Bootstrap 작업을 즉시 실행해. 이 디렉터리의 기존 파일을 삭제하거나 기존 실험 기록을 검증된 결과로 간주하지 말고, 공식 오픈소스 저장소를 확인해 클론·분석하고 격리 환경을 구성해. 가능한 오프라인 테스트를 실제 실행하고 로그를 남겨. 완료 후 프로젝트 루트에 `CONTEXT.md`를 실제 진행 상태로 작성/갱신하고, 무엇이 성공·실패했는지 실행 명령과 함께 한국어로 보고해. 유료 LLM API는 승인 없이 호출하지 마.

4. Check `results/setup/` and `docs/ENV_SETUP.md` after Codex finishes. These should contain real commands, commit hashes and observed results, not just a plan.

The prepared files themselves are **not** evidence that the source repositories were cloned or their tests run on your own computer.
