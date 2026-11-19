"""Lifecycle management for the real Snargent frontend and backend."""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import signal
import shutil
import socket
import subprocess
import time
import uuid
from urllib.request import urlopen


@dataclass
class AppServices:
    root: Path
    output: Path
    backend_port: int
    frontend_port: int
    canaries: dict[str, str]
    backend: subprocess.Popen[str] | None = None
    frontend: subprocess.Popen[str] | None = None
    run_id: str = ''

    @property
    def backend_url(self) -> str:
        return f"http://127.0.0.1:{self.backend_port}"

    @property
    def frontend_url(self) -> str:
        return f"http://127.0.0.1:{self.frontend_port}"

    def start(self) -> None:
        self.output.mkdir(parents=True, exist_ok=True)
        backend_log = (self.output / "backend.log").open("w", encoding="utf-8")
        frontend_log = (self.output / "frontend.log").open("w", encoding="utf-8")
        environment = os.environ.copy()
        environment.update({
            "HOST": "127.0.0.1",
            "PORT": str(self.backend_port),
            "CORS_ORIGIN": self.frontend_url,
            "BENCH_EVIDENCE": "1",
            "BENCH_CANARIES": json.dumps(self.canaries),
            "BENCH_RUN_ID": self.run_id or uuid.uuid4().hex,
        })
        self.run_id = environment["BENCH_RUN_ID"]
        self.backend = subprocess.Popen(
            [shutil.which("npm.cmd" if os.name == "nt" else "npm") or "npm", "--prefix", "backend", "run", "dev"],
            cwd=self.root,
            env=environment,
            stdout=backend_log,
            stderr=subprocess.STDOUT,
            text=True,
            start_new_session=True,
        )
        frontend_environment = environment.copy()
        frontend_environment["VITE_BACKEND_URL"] = self.backend_url
        frontend_environment["VITE_BENCH_RUN_ID"] = self.run_id
        self.frontend = subprocess.Popen(
            [shutil.which("npm.cmd" if os.name == "nt" else "npm") or "npm", "--prefix", "frontend", "run", "dev", "--", "--host", "127.0.0.1", "--port", str(self.frontend_port)],
            cwd=self.root,
            env=frontend_environment,
            stdout=frontend_log,
            stderr=subprocess.STDOUT,
            text=True,
            start_new_session=True,
        )
        self._wait_for(f"{self.backend_url}/health")
        with urlopen(f"{self.backend_url}/health", timeout=2) as response:
            if json.load(response).get('benchmarkRunId') != self.run_id:
                raise RuntimeError('Health endpoint belongs to a different benchmark process')
        self._wait_for(self.frontend_url)
        if self.backend.poll() is not None or self.frontend.poll() is not None:
            raise RuntimeError('A benchmark service exited during startup')
        (self.output / "services.json").write_text(json.dumps({
            "backend_url": self.backend_url,
            "frontend_url": self.frontend_url,
            "backend_pid": self.backend.pid,
            "frontend_pid": self.frontend.pid,
            "run_id": self.run_id,
        }, indent=2), encoding="utf-8")

    def _wait_for(self, url: str, timeout: float = 30) -> None:
        deadline = time.monotonic() + timeout
        last_error = "not attempted"
        while time.monotonic() < deadline:
            try:
                with urlopen(url, timeout=2) as response:
                    if response.status < 500:
                        return
            except Exception as error:  # service startup is expected to race readiness
                last_error = f"{type(error).__name__}: {error}"
            time.sleep(0.2)
        raise RuntimeError(f"Service did not become ready at {url}: {last_error}")

    def close(self) -> None:
        for process in (self.frontend, self.backend):
            if process is None or process.poll() is not None:
                continue
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                               capture_output=True, check=False)
                process.wait(timeout=10)
                continue
            try:
                os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=5)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        self.frontend = None
        self.backend = None


def find_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def start_services(root: Path, output: Path, canaries: dict[str, str]) -> AppServices:
    backend_port = find_port()
    frontend_port = find_port()
    while frontend_port == backend_port:
        frontend_port = find_port()
    services = AppServices(root, output, backend_port, frontend_port, canaries)
    try:
        services.start()
    except Exception:
        services.close()
        raise
    return services
