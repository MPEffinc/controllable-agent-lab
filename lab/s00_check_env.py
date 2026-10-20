"""S0 환경 점검. 키 값은 어디에도 출력하지 않는다."""
import os
import stat
import sys
from pathlib import Path

LLM_ENV = Path.home() / ".config" / "controllable_agent" / "llm.env"
NEEDED = ("LLM_BASE_URL", "LLM_API_KEY", "LLM_MODEL")


def check_python() -> None:
    print(f"python: {sys.version.split()[0]} ({sys.executable})")
    print(f"python 3.12: {'OK' if sys.version_info[:2] == (3, 12) else 'NOT 3.12'}")


def check_openai() -> bool:
    try:
        import openai
    except ImportError as e:
        print(f"openai import: FAIL ({type(e).__name__})")
        return False
    print(f"openai import: OK (version {openai.__version__})")
    return True


def check_llm_env_file() -> bool:
    if not LLM_ENV.exists():
        print(f"llm.env: 없음 ({LLM_ENV})")
        return False
    mode = stat.S_IMODE(LLM_ENV.stat().st_mode)
    print(f"llm.env: 있음 (권한 {mode:o}, {LLM_ENV.stat().st_size} bytes)")
    return True


def load_env() -> None:
    from dotenv import load_dotenv

    load_dotenv(LLM_ENV, override=False)
    state = {name: "설정됨" if os.environ.get(name) else "없음" for name in NEEDED}
    print("환경 변수(이름만): " + ", ".join(f"{k}={v}" for k, v in state.items()))


def call_once() -> bool:
    import openai

    model = os.environ["LLM_MODEL"]
    client = openai.OpenAI(
        base_url=os.environ["LLM_BASE_URL"],
        api_key=os.environ["LLM_API_KEY"],
        max_retries=0,
        timeout=30,
    )
    try:
        client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Reply with the single word: ok"}],
            max_completion_tokens=64,
        )
    except openai.APIStatusError as e:
        print(f"LLM 호출: 실패 (HTTP {e.status_code}, 모델 {model})")
        return False
    except openai.APIConnectionError:
        print(f"LLM 호출: 실패 (연결 오류, 모델 {model})")
        return False
    print(f"LLM 호출: 성공 (모델 {model})")
    return True


def main() -> int:
    check_python()
    if not check_openai():
        return 1
    if not check_llm_env_file():
        print("LLM 호출: 건너뜀 (키 없음)")
        return 0
    load_env()
    if not all(os.environ.get(name) for name in NEEDED):
        print("LLM 호출: 건너뜀 (필요한 변수가 비어 있음)")
        return 0
    return 0 if call_once() else 1


if __name__ == "__main__":
    sys.exit(main())
