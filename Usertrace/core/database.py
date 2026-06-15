import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from core.constants import DATABASE_DIR, DATABASE_FILE, VALID_STATUSES

SCHEMA = """
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    email TEXT,
    domain TEXT,
    platform TEXT NOT NULL,
    status TEXT NOT NULL,
    url TEXT NOT NULL,
    timestamp TEXT NOT NULL
);
"""

INDEXES = (
    "CREATE INDEX IF NOT EXISTS idx_history_timestamp ON history(timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_history_username ON history(username);",
    "CREATE INDEX IF NOT EXISTS idx_history_email ON history(email);",
    "CREATE INDEX IF NOT EXISTS idx_history_domain ON history(domain);",
)


class HistoryDatabase:
    def __init__(self, db_path: Path = DATABASE_FILE) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(str(self.db_path))
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        DATABASE_DIR.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.execute(SCHEMA)
            for index_sql in INDEXES:
                connection.execute(index_sql)

    def insert_result(
        self,
        platform: str,
        status: str,
        url: str,
        username: Optional[str] = None,
        email: Optional[str] = None,
        domain: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> int:
        clean_status = status if status in VALID_STATUSES else "ERROR"
        created_at = timestamp or datetime.utcnow().isoformat(timespec="seconds") + "Z"

        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO history (username, email, domain, platform, status, url, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    username,
                    email,
                    domain,
                    str(platform),
                    clean_status,
                    str(url),
                    created_at,
                ),
            )
            return int(cursor.lastrowid)

    def insert_scan_result(
        self,
        target_type: str,
        target: str,
        result: Dict[str, Any],
        timestamp: Optional[str] = None,
    ) -> int:
        fields = {"username": None, "email": None, "domain": None}
        if target_type in fields:
            fields[target_type] = target

        return self.insert_result(
            username=fields["username"],
            email=fields["email"],
            domain=fields["domain"],
            platform=str(result.get("platform", "unknown")),
            status=str(result.get("status", "ERROR")),
            url=str(result.get("url", "")),
            timestamp=timestamp,
        )

    def insert_many(
        self,
        target_type: str,
        target: str,
        results: Iterable[Dict[str, Any]],
    ) -> List[int]:
        return [self.insert_scan_result(target_type, target, result) for result in results]

    def fetch_history(
        self,
        limit: int = 100,
        username: Optional[str] = None,
        email: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        safe_limit = max(1, min(int(limit), 1000))
        conditions = []
        params: List[Any] = []

        if username is not None:
            conditions.append("username = ?")
            params.append(username)
        if email is not None:
            conditions.append("email = ?")
            params.append(email)
        if domain is not None:
            conditions.append("domain = ?")
            params.append(domain)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        params.append(safe_limit)

        query = f"""
            SELECT id, username, email, domain, platform, status, url, timestamp
            FROM history
            {where_clause}
            ORDER BY timestamp DESC, id DESC
            LIMIT ?
        """

        with self.connect() as connection:
            rows = connection.execute(query, params).fetchall()
            return [dict(row) for row in rows]


def initialize_database(db_path: Path = DATABASE_FILE) -> HistoryDatabase:
    return HistoryDatabase(db_path)


def insert_result(
    platform: str,
    status: str,
    url: str,
    username: Optional[str] = None,
    email: Optional[str] = None,
    domain: Optional[str] = None,
) -> int:
    return HistoryDatabase().insert_result(
        platform=platform,
        status=status,
        url=url,
        username=username,
        email=email,
        domain=domain,
    )


def insert_scan_result(target_type: str, target: str, result: Dict[str, Any]) -> int:
    return HistoryDatabase().insert_scan_result(target_type, target, result)


def fetch_history(
    limit: int = 100,
    username: Optional[str] = None,
    email: Optional[str] = None,
    domain: Optional[str] = None,
) -> List[Dict[str, Any]]:
    return HistoryDatabase().fetch_history(
        limit=limit,
        username=username,
        email=email,
        domain=domain,
    )
