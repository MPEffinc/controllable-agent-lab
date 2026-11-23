"""Report API credential availability without printing credential contents or making requests."""

from __future__ import annotations

import argparse
import os
import stat
from pathlib import Path

from dotenv import dotenv_values


DEFAULT_FILES = (
    Path(".env"),
    Path(".env.local"),
    Path("local/.env"),
    Path("local/.env.local"),
    Path("local/progent-vm/.env"),
    Path("local/progent-vm/.env.local"),
)


def credential_status(files: tuple[Path, ...], environment: dict[str, str]) -> tuple[bool, str, str]:
    """Mirror the Live loader's key order; return only presence, source, and mode."""
    if environment.get("OPENAI_API_KEY"):
        return True, "process environment", "not applicable"
    llm_source = "process environment" if environment.get("LLM_API_KEY") else None
    llm_mode = "not applicable"
    for path in files:
        if not path.is_file():
            continue
        values = dotenv_values(path, interpolate=False)
        mode = f"{stat.S_IMODE(path.stat().st_mode):04o}"
        if values.get("OPENAI_API_KEY"):
            return True, str(path), mode
        if values.get("LLM_API_KEY") and not llm_source:
            llm_source, llm_mode = str(path), mode
    if llm_source:
        return True, llm_source, llm_mode
    return False, "none", "not applicable"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, help="check this dotenv file only")
    args = parser.parse_args()
    files = (args.env_file,) if args.env_file else DEFAULT_FILES
    present, source, mode = credential_status(files, os.environ)
    print(f"[API KEY] {'PRESENT' if present else 'ABSENT'}")
    print(f"[SOURCE] {source}")
    print(f"[FILE MODE] {mode}")
    print("[API AUTH / MODEL ACCESS] NOT CHECKED; no network request was made")
    if not present:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
