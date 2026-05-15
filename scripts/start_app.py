import socket
import sys
import threading
import time
import webbrowser
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


def main() -> None:
    prepare_project_imports()
    host = "127.0.0.1"
    port = find_free_port()
    url = f"http://{host}:{port}/"
    print(f"AI Learning Platform: {url}")
    threading.Thread(target=open_browser_later, args=(url,), daemon=True).start()
    uvicorn.run("app.main:app", host=host, port=port)


if __name__ == "__main__":
    main()
