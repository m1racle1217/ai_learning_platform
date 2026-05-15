import socket
import sys
import threading
import time
import webbrowser
from collections.abc import Callable
from pathlib import Path

import uvicorn


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def prepare_project_imports() -> None:
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    if Path.cwd() != PROJECT_ROOT:
        import os

        os.chdir(PROJECT_ROOT)


def find_free_port(start: int = 8001, attempts: int = 40) -> int:
    for port in range(start, start + attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError("No free local port found from 8001 to 8040.")


def open_browser_later(url: str) -> None:
    time.sleep(1.0)
    webbrowser.open(url)


def build_uvicorn_config(host: str, port: int) -> dict:
    return {
        "host": host,
        "port": port,
        "log_level": "warning",
        "access_log": False,
    }


def build_app_url(host: str = "127.0.0.1", start_port: int = 8001) -> tuple[str, int]:
    port = find_free_port(start_port)
    return f"http://{host}:{port}/", port


def start_shutdown_watcher(should_shutdown: Callable[[], bool], poll_seconds: float = 3.0) -> None:
    def watch() -> None:
        while True:
            time.sleep(poll_seconds)
            if should_shutdown():
                # Raising SystemExit from this daemon thread is not reliable; os._exit is
                # deliberate here because this helper owns the local-only learning server.
                import os

                os._exit(0)

    threading.Thread(target=watch, daemon=True).start()


def main() -> None:
    prepare_project_imports()
    from app.services.runtime_lifecycle import configure_auto_shutdown

    host = "127.0.0.1"
    url, port = build_app_url(host)
    if "--print-url" in sys.argv:
        print(url)
        return
    shutdown_state = configure_auto_shutdown()
    start_shutdown_watcher(shutdown_state.should_shutdown)
    if sys.stdout and sys.stdout.isatty():
        print(f"AI Learning Platform: {url}")
    threading.Thread(target=open_browser_later, args=(url,), daemon=True).start()
    uvicorn.run("app.main:app", **build_uvicorn_config(host, port))


if __name__ == "__main__":
    main()
