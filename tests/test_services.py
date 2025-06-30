import pytest

from src.services import search_number

TEST_TRANSACTIONS = [
    {"Описание": "Пополнение +7 123 456-78-90", "Сумма": 100},
    {"Описание": "Оплата услуг +7 987 654-32-10", "Сумма": -500},
    {"Описание": "Перевод на карту", "Сумма": -1000},
    {"Описание": "Возврат +7 111 222-33-44", "Сумма": 200},
    {"Описание": "МТС +7 999 888-77-66 оплата связи", "Сумма": -300},
    {"Описание": "Без номера в описании", "Сумма": -50},
    {"Описание": "Неверный формат +71234567890", "Сумма": -100},
    {"Описание": "Другой формат +7(123)456-78-90", "Сумма": -200},
]


@pytest.fixture
def test_data():
    return TEST_TRANSACTIONS


def test_search_number_finds_correct_transactions(test_data):
    """Тест нахождения транзакций с корректными номерами"""
    result = search_number(test_data)
    result_data = eval(result)

    assert len(result_data) == 4
    descriptions = [t["Описание"] for t in result_data]
    assert "Пополнение +7 123 456-78-90" in descriptions
    assert "Оплата услуг +7 987 654-32-10" in descriptions
    assert "Возврат +7 111 222-33-44" in descriptions
    assert "МТС +7 999 888-77-66 оплата связи" in descriptions


def test_search_number_ignores_transactions_without_numbers(test_data):
    """Тест игнорирования транзакций без номеров"""
    result = search_number(test_data)
    result_data = eval(result)

    descriptions = [t["Описание"] for t in result_data]
    assert "Перевод на карту" not in descriptions
    assert "Без номера в описании" not in descriptions


def test_search_number_ignores_incorrect_formats(test_data):
    """Тест игнорирования некорректных форматов номеров"""
    result = search_number(test_data)
    result_data = eval(result)

    descriptions = [t["Описание"] for t in result_data]
    assert "Неверный формат +71234567890" not in descriptions
    assert "Другой формат +7(123)456-78-90" not in descriptions


def test_search_number_empty_input():
    """Тест обработки пустого списка транзакций"""
    result = search_number([])
    assert result == "[]"


def test_search_number_returns_valid_json(test_data):
    """Тест возвращения валидного JSON"""
    result = search_number(test_data)
    import json
    json_data = json.loads(result)
    assert isinstance(json_data, list)
