# Stage 0: credentials, privilege and baseline recovery

2026-11-22 UTC. Baseline root HEAD and remote branch were both `315d6d389b4f21ecfbc94e075ad0313a826afc9f`; source Progent checkout was clean at `b02783b896d4bf01a2adf24738015e258db8d35b`. Existing untracked guided-reproduction documents and `scripts/progent_demo*`, `progent_live*`, `progent_guided_effect.py` files were preserved.

## Approved API configuration search

Checked the current process for `OPENAI_API_KEY`, `LLM_API_KEY`, `OPENAI_BASE_URL`, and `LLM_BASE_URL`: all absent. Inspected filenames and *variable names only* in the project root and `local/` for `.env*`, `*.env`, `*.conf`, `*.toml`, `config`, `settings.py`, plus this user's `.bashrc`, `.profile`, `.bash_profile`. No populated project credential file or shell startup assignment was found. The only matches were `.env.example` templates in `legacy/lab-v0`, `third_party/camel`, and `third_party/orbit`; these are not credentials. Existing `scripts/progent_demo.py:84-96` already provides a safe `dotenv_values(..., interpolate=False)` parser for an explicitly selected file. No key value was printed or copied. Luna API validation is **BLOCKED** by missing approved credentials; no request was made at this stage.

## Privilege and runtime

`sudo -n -v` and `sudo -n -l` both exited 1 with `sudo: a password is required`; no cached sudo authentication. User `cclab` belongs to `sudo`, `kvm`, and `docker`, but sudoers details requiring authentication cannot be read without it. `/dev/kvm` is group accessible. Available disk: 89 GiB; available RAM: 21 GiB; CPUs: 8. No privileged change was made. User-space Kata installation and an independent runtime remain candidates; shared Docker/containerd services must remain unchanged.

This search supersedes the earlier narrower current-shell-only finding without altering the previous record. Minimum action to unblock Luna: supply a project-specific API key through `OPENAI_API_KEY` or an explicit project `.env` file.
