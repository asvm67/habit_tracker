"""Тест 1. Главная страница должна возвращать код ответа 200."""


def test_index_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Трекер привычек".encode("utf-8") in response.data
