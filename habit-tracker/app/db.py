"""
Модуль работы с базой данных SQLite.
Содержит функции подключения, закрытия соединения
и инициализации схемы базы данных.
"""
import sqlite3

import click
from flask import current_app, g


def get_db():
    """Возвращает соединение с базой данных для текущего запроса.
    Если соединение уже было открыто в рамках этого запроса —
    возвращает существующее (хранится в объекте g)."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row  # доступ к колонкам по имени
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    """Закрывает соединение с базой данных, если оно было открыто."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


SCHEMA = """
DROP TABLE IF EXISTS habits;
DROP TABLE IF EXISTS logs;

CREATE TABLE habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    target_count INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    log_date TEXT NOT NULL,
    FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE
);
"""


def init_db(app=None):
    """Создаёт таблицы в базе данных, если их ещё нет.
    Не удаляет данные при повторном запуске обычного приложения —
    удаление (DROP TABLE) выполняется только при явном вызове init-db."""
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='habits'"
    )
    exists = cur.fetchone()
    if not exists:
        db.executescript(SCHEMA)
        db.commit()


def reset_db():
    """Полностью пересоздаёт таблицы (используется командой flask init-db)."""
    db = get_db()
    db.executescript(SCHEMA)
    db.commit()


@click.command("init-db")
def init_db_command():
    """CLI-команда: flask init-db — очищает и заново создаёт таблицы."""
    reset_db()
    click.echo("База данных инициализирована.")
