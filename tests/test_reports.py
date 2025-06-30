import pandas as pd
import pytest

from src.reports import spending_by_category

TEST_DATA = [
    {'Дата операции': '10.01.2018 12:42:44', 'Категория': 'Супермаркеты', 'Сумма операции': -100},
    {'Дата операции': '15.01.2018 10:00:00', 'Категория': 'Супермаркеты', 'Сумма операции': -200},
    {'Дата операции': '20.02.2018 15:30:00', 'Категория': 'Транспорт', 'Сумма операции': -50},
    {'Дата операции': '05.03.2018 09:15:00', 'Категория': 'Супермаркеты', 'Сумма операции': -150},
    {'Дата операции': '10.04.2018 18:45:00', 'Категория': 'Супермаркеты', 'Сумма операции': -75},
]


@pytest.fixture
def test_transactions():
    return pd.DataFrame(TEST_DATA)


def test_spending_by_category_basic(test_transactions):
    """Тест базовой функциональности - выборка по категории"""
    test_date = "15.04.2018"
    result = spending_by_category(test_transactions, category="Супермаркеты", date=test_date)

    assert result.iloc[0, 0] == -425  # -100 + -200 + -150 + -75 = -425


def test_spending_by_category_date_filtering(test_transactions):
    """Тест фильтрации по дате (только последние 3 месяца)"""
    test_date = "05.03.2018"
    result = spending_by_category(test_transactions, category="Супермаркеты", date=test_date)

    assert result.iloc[0, 0] == -300


def test_spending_by_category_empty_result(test_transactions):
    """Тест случая, когда нет подходящих транзакций"""
    test_date = "15.04.2018"
    result = spending_by_category(test_transactions, category="Рестораны", date=test_date)

    assert result.iloc[0, 0] == 0


def test_spending_by_category_case_insensitive(test_transactions):
    """Тест регистронезависимости поиска категории"""
    test_date = "15.04.2018"
    result = spending_by_category(test_transactions, category="супермаркеты", date=test_date)

    assert result.iloc[0, 0] == -425


def test_spending_by_category_future_date(test_transactions):
    """Тест с датой в будущем относительно транзакций"""
    future_date = "15.04.2025"
    result = spending_by_category(test_transactions, category="Супермаркеты", date=future_date)

    assert result.iloc[0, 0] == 0
