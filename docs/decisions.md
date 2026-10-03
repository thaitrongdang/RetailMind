# Decision log

## 2026-10-03 — Initial local environment

- **Decision:** Use the already installed CPython 3.11.15 in a project-local `.venv` for Session 1.
- **Reason:** Python 3.11 is available locally and the isolated environment can be created offline. The first example needs no third-party packages.
- **Alternatives considered:** The default `python` command points to Anaconda Python 3.14.6; a local Python 3.13.5 is also installed. Dependency compatibility has not been checked for the later pipeline, so no project package versions are pinned yet.
- **Evidence:** `uv python list --only-installed` and successful `uv venv .venv --python 3.11 --offline` on 2026-10-03.
