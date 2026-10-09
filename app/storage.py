from contextlib import contextmanager
from pathlib import Path
import sqlite3


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
VOICES = DATA / "voices"
PROJECTS = DATA / "projects"
EXPORTS = DATA / "exports"
TMP = DATA / "tmp"
MODELS = DATA / "models"
DB = DATA / "voz_local.sqlite3"


def initialize() -> None:
    for directory in (DATA, VOICES, PROJECTS, EXPORTS, TMP, MODELS):
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        directory.chmod(0o700)
    with connection() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS voices (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                transcript TEXT NOT NULL,
                sample_path TEXT NOT NULL,
                duration REAL NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                voice_id TEXT NOT NULL REFERENCES voices(id),
                script TEXT NOT NULL,
                mode TEXT NOT NULL DEFAULT 'fragments',
                settings TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                position INTEGER NOT NULL,
                text TEXT NOT NULL,
                audio_path TEXT,
                model_size TEXT,
                UNIQUE(project_id, position)
            );
            CREATE INDEX IF NOT EXISTS chunks_project_position ON chunks(project_id, position);
            """
        )
        columns = {row["name"] for row in db.execute("PRAGMA table_info(projects)")}
        if "settings" not in columns:
            db.execute("ALTER TABLE projects ADD COLUMN settings TEXT NOT NULL DEFAULT '{}'")
        if "mode" not in columns:
            db.execute("ALTER TABLE projects ADD COLUMN mode TEXT NOT NULL DEFAULT 'fragments'")
    DB.chmod(0o600)


@contextmanager
def connection():
    db = sqlite3.connect(DB, timeout=30)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    try:
        yield db
        db.commit()
    except BaseException:
        db.rollback()
        raise
    finally:
        db.close()


def one(query: str, parameters: tuple = ()) -> dict | None:
    with connection() as db:
        row = db.execute(query, parameters).fetchone()
    return dict(row) if row else None


def all_rows(query: str, parameters: tuple = ()) -> list[dict]:
    with connection() as db:
        rows = db.execute(query, parameters).fetchall()
    return [dict(row) for row in rows]
