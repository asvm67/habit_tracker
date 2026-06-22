"""
Фикстуры pytest: создают тестовый экземпляр приложения
с отдельной временной базой данных, чтобы тесты не затрагивали
рабочую базу данных приложения.
"""
import os
import tempfile

import pytest

from app import create_app
from app.db import reset_db


@pytest.fixture
def app():
    """Создаёт тестовое приложение с временной базой данных SQLite."""
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        "TESTING": True,
        "DATABASE": db_path,
    })

    with app.app_context():
        reset_db()

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Тестовый клиент Flask для выполнения запросов."""
    return app.test_client()
