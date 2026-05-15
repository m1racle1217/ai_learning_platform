from pathlib import Path

from app.bootstrap import should_seed_database


def test_should_seed_database_when_db_missing(tmp_path):
    workbook_path = tmp_path / "source.xlsx"
    workbook_path.write_bytes(b"workbook")

    assert should_seed_database(tmp_path / "missing.db", workbook_path) is True


def test_should_not_seed_database_when_db_exists(tmp_path):
    db_path = tmp_path / "app.db"
    db_path.write_bytes(b"sqlite")

    assert should_seed_database(db_path, tmp_path / "source.xlsx") is False
