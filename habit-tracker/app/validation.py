"""
Функции валидации входных данных форм.
Выделены в отдельный модуль, чтобы их было легко
покрыть отдельными тестами (см. tests/test_validation.py).
"""


def validate_habit_name(name):
    """Проверяет название привычки.
    Возвращает (True, "") если всё хорошо, иначе (False, "текст ошибки")."""
    if name is None or not name.strip():
        return False, "Название привычки не может быть пустым."
    if len(name.strip()) > 100:
        return False, "Название привычки слишком длинное (максимум 100 символов)."
    return True, ""


def validate_target_count(value):
    """Проверяет целевое количество раз в день. Должно быть целым числом > 0."""
    try:
        target = int(value)
    except (TypeError, ValueError):
        return False, "Целевое количество должно быть числом.", None
    if target <= 0:
        return False, "Целевое количество должно быть больше нуля.", None
    return True, "", target
