from pathlib import Path

from scripts import start_app


def test_windows_launcher_uses_quiet_pythonw_helper():
    launcher = Path("start_windows.bat").read_text(encoding="utf-8").lower()
    helper = Path("scripts/start_windows_hidden.vbs").read_text(encoding="utf-8").lower()

    assert "wscript" in launcher
    assert "pause" not in launcher
    assert "pythonw" in helper
    assert "pyw" in helper
    assert "shell.run command, 0, false" in helper


def test_start_app_sets_quiet_uvicorn_defaults():
    config = start_app.build_uvicorn_config("127.0.0.1", 8010)

    assert config["host"] == "127.0.0.1"
    assert config["port"] == 8010
    assert config["log_level"] == "warning"
    assert config["access_log"] is False


def test_mac_launcher_keeps_diagnostics_visible():
    launcher = Path("start_mac.command").read_text(encoding="utf-8")

    assert "set -u" in launcher
    assert "AI Learning Platform" in launcher
    assert "python.org/downloads/macos" in launcher
    assert "brew install python@3.11" in launcher
    assert "python3 -m pip install --upgrade pip" in launcher
    assert 'pip install -e ".[dev]"' in launcher.replace('\\"', '"')
    assert "import fastapi, uvicorn, sqlalchemy, openpyxl" in launcher
    assert "tail -n" in launcher
    assert "nohup" not in launcher
    assert "read -r" in launcher
