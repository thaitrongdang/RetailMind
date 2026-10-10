# Real-bundle acceptance on another Docker host

## Current boundary, 2026-10-11

The owner reports Windows Update offers no upgrade from Windows 11 22H2 build 22621. The same build is still observed locally and Docker is unavailable. Real-bundle Compose acceptance and `v1.0.0` remain **blocked**. Use an existing supported Docker host for the pending check. No host has been selected or accessed, and no transfer or container run is claimed.

Prefer an existing **Ubuntu 24.04 LTS x86_64** host with Docker Engine and the Compose plugin. Docker lists Ubuntu 24.04 as supported in its [official installation guide](https://docs.docker.com/engine/install/ubuntu/). Another currently supported Windows machine with Docker Desktop's Linux engine is also suitable; see [Docker's Windows requirements](https://docs.docker.com/desktop/setup/install/windows-install/). This is verification, not a public deployment; a paid server is unnecessary if an existing machine is available.

Run both the script and Docker CLI **on the daemon host**, with the source checkout and bundles on that host. [Docker bind mounts are resolved on the daemon host](https://docs.docker.com/engine/storage/bind-mounts/); a remote Docker context alone cannot mount files from this Windows client. The verifier also makes loopback HTTP requests, so using a remote context from this client would target the wrong HTTP host.

## What the owner needs to provide

- Which host to use, its OS/version and architecture; outputs of `docker version`, `docker info --format '{{.OSType}}'`, and `docker compose version`.
- Whether the owner will run commands, or an existing SSH alias/configuration that this workspace can use. Authenticate locally with SSH keys or the supported login flow; do not send passwords, private keys or tokens in chat.
- A writable checkout path on the host, permission to copy the existing bundles there, and permission to build/start the verification project. Port 8000 must be free on that host. Internet access is needed for GitHub, base images and locked package downloads.
- If no existing machine is available, state that first. Host provisioning, paid services and their costs need a separate choice before work can continue.

For planning, allow 8 GB RAM and 10 GB free disk for image build/cache and verification; these are conservative project allowances, not measured minimums. Exact bundle/archive sizes are printed by the transfer exporter. Git and Python **3.11–3.13** are needed on the host for the standard-library verification scripts; Python 3.11 or 3.12 is preferred. No host-side ML environment or retraining is needed. Node.js is needed for the UI controller check. Browser verification can run locally through an SSH tunnel.

## 1. Choose a clean candidate and prepare the transfer

Merge the handoff tooling through a passing PR, then export from the resulting clean candidate commit. The original machine's `docs/docker_setup.md` has a pre-existing uncommitted edit: preserve it separately and use a fresh checkout at the candidate commit if it remains unresolved. Do not discard it to make this tree clean. Copy the existing ignored bundles into that fresh checkout if needed.

On Windows, from the candidate checkout:

```powershell
git status --short
git rev-parse HEAD
& .\.uv-cache\venv\Scripts\python.exe scripts/transfer_bundles.py export --require-clean --output-dir .uv-cache/host-transfer
```

Use a new output directory on each export; existing archives/manifests are never overwritten. If using a new checkout, call the original workspace's working CPython 3.12 interpreter by its absolute path, or installed Python 3.11–3.13. The newly observed global Python 3.14 is outside this project's supported range; retain the existing locked environment for ML/API checks.

The exporter reads both frozen snapshot manifests and model metadata, checks cutoffs, hashes all required files and writes:

- `retailmind-bundles.tar.gz`: snapshot service tables/manifests, separate replay outcomes and six model bundles with metadata.
- `transfer_manifest.json`: candidate commit, source cleanliness, SHA-256 per file, archive SHA-256 and sizes. `compose_verified` remains false.

Raw workbook, unrelated processed files, environments, request logs and credentials are excluded. Keep the two transfer files together. No model is trained and no frozen evaluation report is changed. Do not upload the archive to public GitHub or commit it; it contains customer-level transaction data. Transfer privately to the selected host (SSH/SCP, private file transfer or removable storage).

## 2. Prepare the destination checkout and extract

Example for a Linux host; replace `CANDIDATE_SHA` with the full `candidate_commit` from the transfer manifest. Choose a new checkout directory instead of reusing a directory with unfinished work:

```bash
git clone https://github.com/thaitrongdang/RetailMind.git retailmind-v1-check
cd retailmind-v1-check
git checkout --detach CANDIDATE_SHA
mkdir -p .uv-cache/host-transfer
```

Copy the two transfer files into `.uv-cache/host-transfer/` there. With a user-supplied SSH alias and destination directory, SCP can copy those two files from Windows. Check archive SHA-256 against the source exporter output before extraction:

```bash
sha256sum .uv-cache/host-transfer/retailmind-bundles.tar.gz
tar -tzf .uv-cache/host-transfer/retailmind-bundles.tar.gz
```

Only extract into the fresh candidate checkout, whose `data/processed/` and `artifacts/` do not contain existing work:

```bash
tar -xzf .uv-cache/host-transfer/retailmind-bundles.tar.gz
python3 scripts/transfer_bundles.py check --require-clean --manifest .uv-cache/host-transfer/transfer_manifest.json
git status --short
```

Require transfer `status=passed` and exit 0 before container verification. This compares the archive and every extracted file with source hashes and rejects a different commit or dirty source/destination. **Transfer success is not Compose success.** Git status stays clean because full bundles are ignored. Matching tracked reports/configuration come from the exact Git commit, not an independent copy.

On supported Windows, use `tar -xf` and a Python 3.11–3.13 executable for the same steps; keep the same repository-relative paths. Do not copy the broken old Windows `.venv` onto the host.

## 3. Execute container acceptance on the host

Ensure Docker CLI and daemon work for the same user running Python. Install Engine/Compose with the host's [official Docker instructions](https://docs.docker.com/engine/install/ubuntu/) if needed; host administrators choose how to grant Docker access. Confirm these commands before proceeding:

```bash
docker version
docker info --format '{{.OSType}}'
docker compose version
python3 --version
python3 scripts/verify_compose.py --require-clean --output .uv-cache/compose_verification.json
```

Require Linux containers, `status=passed`, exit 0, and a JSON `commit` equal to the candidate. The verifier builds the image, waits for both snapshots, confirms read-only mounts, compares host/container bundle hashes and image serving-file hashes, and runs real HTTP checks for `/health`, `/ui/`, both snapshots and ranking/replay/error paths. It also confirms serving did not change the bundles. Missing CLI/engine is `blocked`; a failed check is `failed`. Record the full result rather than changing either state manually.

Then on the host:

```bash
RETAILMIND_API_URL=http://127.0.0.1:8000 node scripts/smoke_ui_logic.cjs
docker compose --project-name retailmind-v1-verification ps
docker compose --project-name retailmind-v1-verification logs --no-color --tail 50 api
```

## 4. Browser verification and evidence return

For a remote Linux host, open an SSH tunnel **from this Windows client** using the supplied SSH alias. The host's API remains bound to its loopback interface:

```powershell
ssh -N -L 8800:127.0.0.1:8000 HOST_ALIAS
```

Open `http://127.0.0.1:8800/ui/` locally. With Playwright available and the existing Chrome executable, run the portable browser check from a local checkout of the same commit:

```powershell
$env:RETAILMIND_API_URL = 'http://127.0.0.1:8800'
$env:RETAILMIND_BROWSER_EXECUTABLE = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
$env:RETAILMIND_BROWSER_OUTPUT = '.uv-cache/container-browser-verification'
node scripts/smoke_browser.cjs
```

Playwright is a browser-check dependency, separate from the app. This machine already has it in the bundled Node runtime; Codex can use that runtime's `NODE_PATH`. On another machine, install Playwright in an ignored tools directory or run the manual desktop/mobile flow in [demo_script.md](demo_script.md), preserving screenshots and results. The automated check uses installed Chrome when `RETAILMIND_BROWSER_EXECUTABLE` is provided; otherwise it needs Playwright's installed Chromium. It checks six pages at 1440×900 and 390×844, CSV, explicit new customer, expected 404/recovery, reveal gating, snapshot switching and mobile keyboard/overflow states. It writes PNGs and `browser_verification.json`; it is not a cross-browser audit.

Return the full `.uv-cache/compose_verification.json`, transfer manifest, UI controller stdout, and browser JSON/screenshots (or documented manual results). Include host OS/architecture and the exact candidate SHA. Preserve failed output/logs too if any check fails. Once these artifacts are reviewed, update aggregate release evidence with commit/image IDs and confirm CI on that same commit. If any tracked file changes afterward, run final acceptance again on the new clean candidate before tagging.

To stop only this verification project:

```bash
docker compose --project-name retailmind-v1-verification down
```

Bundles are retained. No `v1.0.0` release may be created until the real-bundle Compose and container UI gates have passed on the final release commit.
