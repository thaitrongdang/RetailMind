# Docker setup and real-bundle acceptance

## Observed host state, 2026-10-07

- Windows 11 Pro 22H2, build 22621.2134, x64; Dell Latitude 7480, Intel Core i7-7600U.
- Approximately 15.9 GiB installed RAM. Firmware virtualization, SLAT and VM monitor extensions report enabled/supported; `HypervisorPresent` is false.
- No Docker, Podman or nerdctl executable, Docker installation directory or Docker registry entry was found. No Docker engine was available for a Compose run.
- `wsl --version` shows inbox help instead of a version; `wsl --status` exits 50 with no status. No Store WSL package was found. WSL is not verified usable.
- `Win32_OptionalFeature` reports `InstallState=2` (disabled) for both `VirtualMachinePlatform` and `Microsoft-Windows-Subsystem-Linux`. The DISM cmdlet required elevation; the read-only CIM query established these states without changing them. Microsoft defines [the InstallState values](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-optionalfeature).
- `LanmanServer` is running with Automatic startup, which meets that Docker prerequisite.

The current [Docker Windows requirements](https://docs.docker.com/desktop/setup/install/windows-install/) specify Windows 11 build 22631 or later, a Windows version still within Microsoft's servicing period, WSL 2.1.5 or later, at least 8 GB RAM, SLAT and firmware virtualization. This machine meets the observed RAM/virtualization prerequisites; its Windows release and WSL setup need attention. A Docker Desktop installer alone does not resolve the OS prerequisite.

## Actions on this Windows machine

1. Open **Settings > Windows Update** and update to a currently supported Windows 11 release offered for this device. Restart, then use `winver` to confirm the resulting release/build. If a supported update is unavailable for the device, use another supported Windows or Linux Docker host for the packaging acceptance below.
2. In **PowerShell as Administrator**, install modern WSL without a user Linux distribution:

   ```powershell
   wsl --install --no-distribution
   ```

   Restart when requested. Then run `wsl --update`, `wsl --version` and `wsl --status`. Confirm WSL is at least 2.1.5. Microsoft documents [the install options and update commands](https://learn.microsoft.com/en-us/windows/wsl/basic-commands). Docker's [WSL backend documentation](https://docs.docker.com/desktop/features/wsl/) confirms that a separately installed Ubuntu distribution is optional.
3. Download the x86_64 installer from the [official Docker Desktop Windows page](https://docs.docker.com/desktop/setup/install/windows-install/). Install with the WSL 2 backend, start Docker Desktop and complete its first-run prompts. Use Linux containers for RetailMind.
4. Open a new terminal and run:

   ```powershell
   docker version
   docker info --format '{{.OSType}}'
   docker compose version
   ```

   `docker version` must show both Client and Server, `OSType` must be `linux`, and the Compose command must succeed. A present CLI with an unreachable engine is not ready.

These OS/WSL installation commands have not been executed by the project. Updating Windows and rebooting require the user's interactive session.

## Acceptance with the existing real bundles

From the repository root, after Docker is ready and the checkout is clean:

```powershell
& .\.uv-cache\venv\Scripts\python.exe scripts/verify_compose.py --require-clean --output .uv-cache/compose_verification.json
```

On a normally installed project environment, use `.\.venv\Scripts\python.exe` instead. On another Docker host, clone the candidate commit and securely copy the existing ignored `data/processed/` and `artifacts/` directories to that checkout before running the script with Python 3.11 or later. Keep the matching tracked `reports/` and configuration. Bind mounts refer to files on the Docker daemon's host, so merely selecting a remote Docker context will not transfer local bundles.

The script runs `docker compose --project-name retailmind-v1-verification --file compose.yaml up --build --detach --wait --wait-timeout 180 api`. It verifies the Linux engine, normalized Compose configuration, container health, read-only snapshot/model mounts, bundle hashes inside the container, and the serving files copied into the image. It then checks `/health`, `/ui/` and assets, both snapshot IDs/counts, all three ranking models, CSV metadata, explicit new-customer mode, history/outcome time bounds, frozen evaluation reports, similarity, and expected 404/422 errors. Reading outcomes must leave the original ranking unchanged. Bundle hashes are compared again after serving.

`status=passed` and exit code 0 are required. `blocked` or `failed` with exit code 1 leaves acceptance pending. The JSON evidence records the commit, clean-checkout state, image ID, engine/Compose versions, container health and file hashes. It is ignored local evidence; no model training takes place. Docker-dependent stages of this script are still unexecuted on this machine.

The successful container remains running at `http://127.0.0.1:8000/ui/`. Verify browser interactions against that address as well:

```powershell
$env:RETAILMIND_API_URL = 'http://127.0.0.1:8000'
node scripts/smoke_ui_logic.cjs
```

Use the six-page desktop/mobile flow in `docs/demo_script.md` for visual verification and snapshot switching. To inspect or stop this verification project:

```powershell
docker compose --project-name retailmind-v1-verification ps
docker compose --project-name retailmind-v1-verification logs --tail 50 api
docker compose --project-name retailmind-v1-verification down
```

The source mount directories are retained. Run acceptance again on the exact clean commit selected for `v1.0.0`, confirm CI on that commit, and record the evidence before creating the release.
