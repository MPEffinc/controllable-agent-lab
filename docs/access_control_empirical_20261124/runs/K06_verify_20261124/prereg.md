# K06 AutoCedar 제공 workspace의 오프라인 검증 사전등록

- 시각: 2026-11-24 11:09 UTC.
- 고정 원저자 소스: `third_party/K06-autocedar` commit `a0cf180977d799cf943514b67ffc260fc579b9a5`; 원본을 수정하지 않는다. 입력 `workspace/`를 이 run 하위의 `input/`에 복사한 뒤 사본만 사용한다.
- 검증 질문: 원저자 README의 `autocedar verify workspace`가 제공된 Cedar 후보와 검증 계획을 독립 모델 API 없이 읽어 Cedar 구문·타입 및 floor/ceiling/liveness 조건을 검사하고, 결과 또는 반례를 반환하는가?
- 원래 주장: [AutoCedar v2](https://arxiv.org/html/2607.03656v2)는 사람 검토 target에 대해 Cedar/SymCC의 형식 검증을 수행한다고 설명한다. 이 시험은 **제공 sample의 verifier 실행 가능성**만 확인한다. 논문 221개 과제나 의미 일치율의 재현은 아니다.
- 예상 관찰: 고정 sample의 `candidate.cedar`는 주석에 Verified라고 되어 있어 구문·형식 검사 통과 및 plan check 성공(`loss: 0`)을 예상한다. 이 주석은 정답 근거가 아니다. 비용이 낮으면 사본에서 의도적으로 과권한 permit 하나를 추가하여 ceiling 위반이 포착되는지 대조한다.
- 반증 관찰: 필요한 verifier가 정상 설치되어도 sample 검사 실패, 추가 permit 후에도 검증 통과, 또는 API 호출 없이는 verifier가 작동하지 않는 경우. 단, 오래된/다른 버전 CLI와의 호환 실패는 저자 메커니즘 반증으로 해석하지 않는다.
- 최소 비용: 공식 Cedar CLI·CVC5의 기존 설치 또는 공식 사전 빌드 바이너리를 검사·다운로드할 수 있을 때만 로컬 임시 경로에 확보한다. 설치/빌드가 큰 자원이나 호스트 변경을 요구하면 실행을 멈추고 선행 조건과 정확한 실패 명령을 기록한다. 유료 모델/API 호출 0, 기존 소스 패치 0.
- 완료 조건: (a) 정상 후보 결과와 과권한 대조 결과의 raw stdout/stderr/exit code/도구 버전/입력 해시를 기록하거나, (b) 합리적인 저비용 의존성 확보 경로가 없음을 근거로 `NOT_RUN_PREREQUISITE`로 닫는다.
- 안전 확인: 원저자 `workspace/verification_plan.py`를 읽었다. 이 sample은 `os.path.join`으로 reference 파일을 가리키는 `get_checks()`만 정의한다. 일반적으로 AutoCedar가 이 파일을 Python `exec_module`로 실행하므로, 다른 workspace에는 무조건 적용하지 않는다.
