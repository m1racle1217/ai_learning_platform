from pathlib import Path
import subprocess
import sys

from app.bootstrap import should_seed_database


def test_should_seed_database_when_db_missing(tmp_path):
    workbook_path = tmp_path / "source.xlsx"
    workbook_path.write_bytes(b"workbook")

    assert should_seed_database(tmp_path / "missing.db", workbook_path) is True


def test_should_not_seed_database_when_db_exists(tmp_path):
    db_path = tmp_path / "app.db"
    db_path.write_bytes(b"sqlite")

    assert should_seed_database(db_path, tmp_path / "source.xlsx") is False


def test_missing_database_is_seeded_with_days_resources_and_quiz(tmp_path):
    db_path = tmp_path / "fresh_clone.db"
    script = f"""
from sqlalchemy import create_engine, text

import app.main  # noqa: F401

engine = create_engine('sqlite:///{db_path.as_posix()}')
with engine.connect() as conn:
    days = conn.execute(text('select count(*) from learning_days')).scalar_one()
    resources = conn.execute(text('select count(*) from resources')).scalar_one()
    quiz = conn.execute(text('select count(*) from quiz_questions')).scalar_one()
print(days, resources, quiz)
"""

    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=Path(__file__).resolve().parents[1],
        env={**__import__("os").environ, "DATABASE_URL": f"sqlite:///{db_path.as_posix()}"},
        capture_output=True,
        text=True,
        check=True,
    )

    days, resources, quiz = [int(value) for value in result.stdout.strip().split()]
    assert days == 70
    assert resources >= 350
    assert quiz >= 4
