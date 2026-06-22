"""Тест 4. Обработка ошибки — 404 при обращении к несуществующему ID."""


def test_nonexistent_habit_returns_404(client):
    response = client.get("/habit/9999")
    assert response.status_code == 404
