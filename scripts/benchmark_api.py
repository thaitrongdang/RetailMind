"""Measure cold startup and sequential local HTTP recommendation latency."""

from __future__ import annotations

import json
import os
import platform
import socket
import statistics
import subprocess
import sys
import time
from datetime import datetime

import httpx
import pandas as pd

from retailmind.config import load_config


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def main() -> None:
    config = load_config()
    summary = json.loads((config.reports_dir / "snapshots.json").read_text(encoding="utf-8"))["test"]
    customers = pd.read_parquet(
        config.processed_dir / "snapshots" / summary["snapshot_id"] / "customers.parquet",
        columns=["customer_id"],
    ).customer_id.astype(str).tolist()
    sampled = [customers[int(i * (len(customers) - 1) / 19)] for i in range(20)]
    with socket.socket() as candidate:
        candidate.bind(("127.0.0.1", 0))
        port = candidate.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="4")
    started = time.perf_counter()
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "retailmind.api:app", "--host", "127.0.0.1", "--port", str(port), "--no-access-log"],
        cwd=config.root, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        with httpx.Client(timeout=15) as client:
            while True:
                if process.poll() is not None:
                    raise RuntimeError(f"API exited during startup: {process.returncode}")
                try:
                    health = client.get(base + "/health")
                    if health.status_code == 200:
                        break
                except httpx.TransportError:
                    pass
                if time.perf_counter() - started > 30:
                    raise TimeoutError("API did not become ready within 30 seconds")
                time.sleep(0.05)
            cold_start_ms = (time.perf_counter() - started) * 1000
            for i in range(20):
                response = client.get(base + "/recommendations", params={"snapshot": "test", "customer_id": sampled[i], "k": 10})
                response.raise_for_status()
            durations = []
            for i in range(200):
                tick = time.perf_counter()
                response = client.get(base + "/recommendations", params={"snapshot": "test", "customer_id": sampled[i % len(sampled)], "k": 10})
                response.raise_for_status()
                durations.append((time.perf_counter() - tick) * 1000)
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
    report = {
        "measured_at_local_time": datetime.now().isoformat(timespec="seconds"),
        "platform": platform.platform(), "python": platform.python_version(),
        "logical_cpu_count": os.cpu_count(), "snapshot_id": summary["snapshot_id"],
        "endpoint": "GET /recommendations?{snapshot=test,customer_id,k=10}",
        "method": "200 sequential loopback HTTP requests, 20 deterministic historical customers, 20 warmups, evidence enabled; one Uvicorn worker; no concurrency",
        "cold_start_to_ready_ms": round(cold_start_ms, 3),
        "request_p50_ms": round(statistics.median(durations), 3),
        "request_p95_ms": round(percentile(durations, 0.95), 3),
        "request_max_ms": round(max(durations), 3),
        "requests": len(durations),
    }
    output = config.reports_dir / "api_benchmark.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()