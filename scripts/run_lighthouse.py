#!/usr/bin/env python3
"""Run Lighthouse against local ArchiveVet web + worker."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = REPO_ROOT / "reports" / "lighthouse"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Lighthouse on ArchiveVet home page.")
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--port", type=int, default=3000)
    parser.add_argument("--worker-port", type=int, default=8000)
    parser.add_argument("--timeout-seconds", type=int, default=90)
    args = parser.parse_args()

    if not args.skip_build:
        completed = subprocess.run(
            [resolve_command("pnpm"), "build"],
            cwd=REPO_ROOT,
            check=False,
        )
        if completed.returncode != 0:
            return completed.returncode

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    report_base = REPORT_DIR / f"home-{timestamp}"
    worker_process = None
    web_process = None
    try:
        worker_process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "src.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(args.worker_port),
            ],
            cwd=REPO_ROOT / "apps" / "worker",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        wait_for_url(f"http://127.0.0.1:{args.worker_port}/health", args.timeout_seconds)

        web_env = os.environ.copy()
        web_env["ARCHIVEVET_WORKER_URL"] = f"http://127.0.0.1:{args.worker_port}"
        web_process = subprocess.Popen(
            [
                "node",
                str(REPO_ROOT / "node_modules" / "next" / "dist" / "bin" / "next"),
                "start",
                "--hostname",
                "127.0.0.1",
                "--port",
                str(args.port),
            ],
            cwd=REPO_ROOT / "apps" / "web",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=web_env,
        )
        wait_for_url(f"http://127.0.0.1:{args.port}", args.timeout_seconds)

        lighthouse_command = [
            resolve_command("pnpm"),
            "exec",
            "lighthouse",
            f"http://127.0.0.1:{args.port}",
            "--preset=desktop",
            "--only-categories=performance,accessibility,best-practices,seo",
            "--quiet",
            "--chrome-flags=--headless=new --no-sandbox",
            "--output=json",
            f"--output-path={report_base.as_posix()}",
        ]
        completed = subprocess.run(lighthouse_command, cwd=REPO_ROOT, check=False)
        json_path = report_base.with_suffix(".report.json")
        if not json_path.exists():
            return completed.returncode or 1
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        scores = {
            name: round(details["score"] * 100, 1)
            for name, details in payload["categories"].items()
        }
        verdict = "PASS" if all(score >= 95 for score in scores.values()) else "FAIL"
        print(json.dumps({"verdict": verdict, "scores": scores, "reportJson": str(json_path)}, indent=2))
        return 0 if verdict == "PASS" else 1
    finally:
        terminate_process(web_process)
        terminate_process(worker_process)


def wait_for_url(url: str, timeout_seconds: int) -> None:
    started = time.time()
    while time.time() - started < timeout_seconds:
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                if response.status < 500:
                    return
        except (urllib.error.URLError, TimeoutError):
            time.sleep(1)
    raise TimeoutError(f"Timed out waiting for {url}")


def terminate_process(process: subprocess.Popen[object] | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()


def resolve_command(command: str) -> str:
    if sys.platform == "win32":
        return shutil.which(f"{command}.cmd") or shutil.which(command) or command
    return shutil.which(command) or command


if __name__ == "__main__":
    raise SystemExit(main())
