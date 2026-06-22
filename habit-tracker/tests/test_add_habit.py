"""Тест 2. Добавление объекта (привычки) — проверка, что объект появляется в БД."""
from app.db import get_db


def test_add_habit_appears_in_db(app, client):
    response = client.post(
        "/habit/new",
        data={"name": "Пить воду", "description": "2 литра в день", "target_count": "8"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        db = get_db()
        habit = db.execute("SELECT * FROM habits WHERE name = ?", ("Пить воду",)).fetchone()

    assert habit is not None
    assert habit["target_count"] == 8
