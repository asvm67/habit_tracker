"""Тест 5. Корректность данных — проверка, что функция валидации
отклоняет пустое поле."""
from app.validation import validate_habit_name, validate_target_count


def test_validate_habit_name_rejects_empty():
    ok, error = validate_habit_name("")
    assert ok is False
    assert error != ""


def test_validate_habit_name_rejects_whitespace_only():
    ok, error = validate_habit_name("    ")
    assert ok is False


def test_validate_habit_name_accepts_valid_name():
    ok, error = validate_habit_name("Чтение")
    assert ok is True
    assert error == ""


def test_validate_target_count_rejects_zero_and_negative():
    ok, error, target = validate_target_count("0")
    assert ok is False
    ok, error, target = validate_target_count("-3")
    assert ok is False


def test_validate_target_count_rejects_non_numeric():
    ok, error, target = validate_target_count("abc")
    assert ok is False
