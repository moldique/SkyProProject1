import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.utils import (file_reader_excel, generate_report, get_currency_rates, get_greeting, get_stock_prices,
                       get_top_transactions, process_cards)

SAMPLE_TRANSACTIONS = [
    {'Дата операции': '10.01.2018 12:42:44', 'Номер карты': '*5441', 'Сумма операции': -400.0, 'Сумма платежа': -400.0,
     'Категория': 'Перевод', 'Описание': 'Перевод с карты'},
    {'Дата операции': '10.01.2018 12:41:24', 'Номер карты': '*5441', 'Сумма операции': -800.0, 'Сумма платежа': -800.0,
     'Категория': 'Перевод', 'Описание': 'Перевод с карты'},
    {'Дата операции': '08.01.2018 21:29:43', 'Номер карты': '*7197', 'Сумма операции': -364.49,
     'Сумма платежа': -364.49, 'Категория': 'Супермаркеты', 'Описание': 'Дикси'},
    {'Дата операции': '08.01.2018 14:21:23', 'Номер карты': '*4556', 'Сумма операции': -250.0, 'Сумма платежа': -250.0,
     'Категория': 'Связь', 'Описание': 'МТС'},
    {'Дата операции': '01.01.2018 12:49:53', 'Номер карты': None, 'Сумма операции': -3000.0, 'Сумма платежа': -3000.0,
     'Категория': 'Переводы', 'Описание': 'Линзомат'},
]


@pytest.mark.parametrize("hour,expected", [
    (5, "Доброе утро"),
    (11, "Доброе утро"),
    (12, "Добрый день"),
    (17, "Добрый день"),
    (18, "Добрый вечер"),
    (22, "Добрый вечер"),
    (23, "Доброй ночи"),
    (4, "Доброй ночи"),
])
def test_get_greeting(hour, expected):
    """Тестируем правильное приветствие в зависимости от времени"""
    test_time = datetime(2023, 1, 1, hour, 0, 0)
    assert get_greeting(test_time) == expected


def test_process_cards():
    """Тестируем обработку данных по картам"""
    result = process_cards(SAMPLE_TRANSACTIONS)

    assert len(result) == 3  # *5441, *7197, *4556

    card5441 = next(item for item in result if item["last_digits"] == "5441")
    assert card5441["total_spent"] == 1200.0
    assert card5441["cashback"] == 12.0

    assert not any(item["last_digits"] == "None" for item in result)


def test_get_top_transactions():
    """Тестируем получение топ-N транзакций"""
    result = get_top_transactions(SAMPLE_TRANSACTIONS, n=2)

    assert len(result) == 2
    assert result[0]["amount"] == 3000.0
    assert result[0]["description"] == "Линзомат"
    assert result[1]["amount"] == 800.0


@patch('requests.get')
def test_get_currency_rates_success(mock_get):
    """Тестируем успешный запрос курсов валют"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "rates": {"USD": 0.013, "EUR": 0.011}
    }
    mock_get.return_value = mock_response

    result = get_currency_rates()
    assert len(result) == 2
    assert result[0]["currency"] == "USD"
    assert result[1]["currency"] == "EUR"
    assert result[0]["rate"] == round(1 / 0.013, 2)


@patch('requests.get')
def test_get_stock_prices_success(mock_get):
    """Тестируем успешный запрос цен акций"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "Global Quote": {
            "05. price": "150.50"
        }
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    with patch.dict('os.environ', {'API_KEY': 'test_key'}):
        result = get_stock_prices()

    assert len(result) == 5
    assert result[0]["price"] == 150.50


def test_generate_report():
    """Тестируем генерацию полного отчета"""
    report_json = generate_report("2023-01-01 12:00:00", SAMPLE_TRANSACTIONS)
    report = json.loads(report_json)

    assert "greeting" in report
    assert report["greeting"] == "Добрый день"
    assert len(report["cards"]) == 3
    assert len(report["top_transactions"]) == 5
    assert len(report["currency_rates"]) == 2
    assert len(report["stock_prices"]) == 5


@patch('pandas.read_excel')
def test_file_reader_excel_success(mock_read_excel):
    """Тестируем успешное чтение Excel файла"""
    mock_df = MagicMock()
    mock_df.to_dict.return_value = SAMPLE_TRANSACTIONS
    mock_read_excel.return_value = mock_df

    result = file_reader_excel("test.xlsx")
    assert len(result) == len(SAMPLE_TRANSACTIONS)
    assert "Номер карты" in result[0]
