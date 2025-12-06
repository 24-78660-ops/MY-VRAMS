import sqlite3
from pathlib import Path

DEFAULT_DB = "rams.db"

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS register (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    name TEXT,
    age INTEGER,
    address TEXT,
    contact_number TEXT,
    department TEXT,
    sr_code TEXT,
    work_type TEXT,
    sticker_code TEXT UNIQUE,
    qr_file TEXT
);

CREATE TABLE IF NOT EXISTS vehicle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    vtype TEXT,
    plate TEXT,
    license_no TEXT,
    sticker_no TEXT,
    sticker_file TEXT,
    vcolor TEXT,
    status TEXT,
    last_seen TEXT,
    FOREIGN KEY(user_id) REFERENCES register(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS entry_exit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    sticker_code TEXT,
    timestamp TEXT,
    direction TEXT,
    FOREIGN KEY(user_id) REFERENCES register(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS admin_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);
"""

class DBConnection:
    def __init__(self, db_file=DEFAULT_DB):
        db_path = Path(db_file)
        if not db_path.parent.exists():
            try:
                db_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass

        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        self.cursor.executescript(SCHEMA)
        self.conn.commit()

        self._migrate_old_admin_table()

    def _table_exists(self, name):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (name,))
        return self.cursor.fetchone() is not None

    def _migrate_old_admin_table(self):
        try:
            has_admin = self._table_exists("admin")
            has_admin_users = self._table_exists("admin_users")

            if has_admin and not has_admin_users:
                self.cursor.execute("ALTER TABLE admin RENAME TO admin_users;")
                self.conn.commit()
                print("Migrated table 'admin' -> 'admin_users'")

        except Exception as e:

            print("DB migration error:", e)

    def insert(self, sql, params=()):
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.lastrowid

    def update(self, sql, params=()):
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.rowcount

    def fetch(self, sql, params=()):
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def fetch_one(self, sql, params=()):
        self.cursor.execute(sql, params)
        return self.cursor.fetchone()

    def delete(self, sql, params=()):
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.rowcount

    def close(self):
        try:
            self.cursor.close()
        except Exception:
            pass
        try:
            self.conn.close()
        except Exception:
            pass
