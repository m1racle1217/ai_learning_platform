from pathlib import Path
import subprocess
import sys


def test_editable_install_build_metadata_succeeds(tmp_path):
    target = tmp_path / "install-target"
    target.mkdir()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-deps",
            "--target",
            str(target),
            "-e",
            ".",
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
