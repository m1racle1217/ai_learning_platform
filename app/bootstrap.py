from pathlib import Path

from app.config import DATABASE_URL, SOURCE_WORKBOOK, resolve_project_path


def database_path_from_url(database_url: str = DATABASE_URL) -> Path | None:
    if not database_url.startswith("sqlite:///"):
        return None
    return resolve_project_path(database_url.removeprefix("sqlite:///"))


def should_seed_database(db_path: Path, workbook_path: Path) -> bool:
    return not db_path.exists() and workbook_path.exists()


def ensure_database_seeded() -> None:
    db_path = database_path_from_url()
    if db_path is None:
        return
    workbook_path = resolve_project_path(SOURCE_WORKBOOK)
    if should_seed_database(db_path, workbook_path):
        from app.seed_from_excel import create_schema, seed_from_workbook

        db_path.parent.mkdir(parents=True, exist_ok=True)
        create_schema()
        seed_from_workbook(workbook_path)
