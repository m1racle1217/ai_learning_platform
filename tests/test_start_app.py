import sys
from pathlib import Path

from scripts import start_app


def test_start_app_prepares_project_import_path(monkeypatch):
    project_root = Path(__file__).resolve().parents[1]
    scripts_dir = project_root / "scripts"
    monkeypatch.chdir(scripts_dir)
    monkeypatch.setattr(sys, "path", [str(scripts_dir)])

    start_app.prepare_project_imports()

    assert str(project_root) in sys.path
