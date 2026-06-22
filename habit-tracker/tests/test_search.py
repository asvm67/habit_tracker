"""Тест 3. Поиск/фильтрация — проверка, что возвращаются только нужные записи."""


def add_habit(client, name):
    client.post("/habit/new", data={"name": name, "description": "", "target_count": "1"})


def test_search_returns_only_matching_habits(client):
    add_habit(client, "Чтение книг")
    add_habit(client, "Бег по утрам")
    add_habit(client, "Чтение перед сном")

    response = client.get("/?q=Чтение")
    page = response.data.decode("utf-8")

    assert response.status_code == 200
    assert "Чтение книг" in page
    assert "Чтение перед сном" in page
    assert "Бег по утрам" not in page
