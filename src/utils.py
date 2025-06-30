import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any

import pandas as pd
import requests

logger = logging.getLogger("save_to_logs_utils")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("../logs/save_to_logs_utils.log", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def file_reader_excel(excel_path: str) -> list[dict]:
    """Читает Excel файл и возвращает список словарей с данными."""
    try:
        logger.info(f"Начало чтения Excel файла: {excel_path}")
        df = pd.read_excel(excel_path)
        records = df.to_dict("records")
        logger.info(f"Успешно прочитано {len(records)} записей из файла")
        return records
    except FileNotFoundError:
        logger.error(f"Файл не найден по пути {excel_path}")
        print(f"Ошибка: файл не найден по пути {excel_path}")
        return []
    except Exception as e:
        logger.error(f"Ошибка при чтении файла: {str(e)}", exc_info=True)
        print(f"Произошла ошибка при чтении файла: {e}")
        return []


def get_greeting(input_datetime: str) -> str:
    """Возвращает приветствие в зависимости от времени суток"""
    hour = input_datetime.hour
    ""
    if 5 <= hour < 12:
        greeting = "Доброе утро"
    elif 12 <= hour < 18:
        greeting = "Добрый день"
    elif 18 <= hour < 23:
        greeting = "Добрый вечер"
    else:
        greeting = "Доброй ночи"

    logger.debug(f"Определено приветствие: {greeting} для часа {hour}")
    return greeting


def process_cards(transactions: List[Dict]) -> list[Any]:
    """Обрабатывает данные по картам"""
    logger.info("Начало обработки данных по картам")
    cards = {}
    processed_count = 0

    for t in transactions:
        card = t["Номер карты"]
        if not isinstance(card, str):
            continue

        last_digits = card[-4:]
        amount = abs(t["Сумма операции"]) if t["Сумма операции"] < 0 else 0

        if last_digits not in cards:
            cards[last_digits] = {"total_spent": 0, "cashback": 0}

        cards[last_digits]["total_spent"] += amount
        cards[last_digits]["cashback"] += amount * 0.01
        processed_count += 1

    result = []
    for last_digits, data in cards.items():
        result.append(
            {
                "last_digits": last_digits,
                "total_spent": round(data["total_spent"], 2),
                "cashback": round(data["cashback"], 2),
            }
        )

    logger.info(f"Обработано {processed_count} транзакций по {len(result)} картам")
    return result


def get_top_transactions(transactions: List[Dict], n=5) -> list[Any]:
    """Возвращает топ-N транзакций по сумме платежа"""
    logger.info(f"Начало формирования топ-{n} транзакций")
    expenses = [t for t in transactions if t["Сумма платежа"] < 0]
    logger.debug(f"Найдено {len(expenses)} расходных операций")

    sorted_trans = sorted(expenses, key=lambda x: abs(x["Сумма платежа"]), reverse=True)

    top = []
    for t in sorted_trans[:n]:
        top.append(
            {
                "date": t["Дата операции"].split()[0],
                "amount": abs(t["Сумма платежа"]),
                "category": t["Категория"],
                "description": t["Описание"],
            }
        )

    logger.info(f"Сформирован топ-{len(top)} транзакций")
    return top


def get_currency_rates():
    """Получает курсы валют"""
    logger.info("Запрос курсов валют")
    try:
        response = requests.get("https://api.exchangerate-api.com/v4/latest/RUB")
        data = response.json()
        rates = [
            {"currency": "USD", "rate": round(1 / data["rates"]["USD"], 2)},
            {"currency": "EUR", "rate": round(1 / data["rates"]["EUR"], 2)},
        ]
        logger.info("Успешно получены курсы валют")
        return rates
    except Exception as e:
        logger.error(f"Ошибка при получении курсов валют: {str(e)}", exc_info=True)
        print(f"Ошибка: {e}")
        # Возвращаем примерные значения, если API не доступно
        return [{"currency": "USD", "rate": 73.21}, {"currency": "EUR", "rate": 87.08}]


def get_stock_prices():
    """Получает цены акций с использованием Alpha Vantage API"""
    logger.info("Запрос цен акций через Alpha Vantage API")
    try:
        stocks = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
        prices = []
        api_key = os.getenv('API_KEY')
        for stock in stocks:

            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={api_key}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if "Global Quote" in data and "05. price" in data["Global Quote"]:
                price = round(float(data["Global Quote"]["05. price"]), 2)
                prices.append({"stock": stock, "price": price})
                logger.debug(f"Получена цена акции {stock}: {price}")
            else:
                logger.warning(f"Не удалось получить цену для {stock}: {data}")
                prices.append({"stock": stock, "price": 0.0})

        logger.info(f"Успешно получены цены {len(prices)} акций")
        return prices

    except Exception as e:
        logger.error(f"Ошибка при получении цен акций: {str(e)}", exc_info=True)
        print(f"Ошибка: {e}")
        return [
            {"stock": "AAPL", "price": 201.08},
            {"stock": "AMZN", "price": 223.3},
            {"stock": "GOOGL", "price": 178.53},
            {"stock": "MSFT", "price": 495.94},
            {"stock": "TSLA", "price": 323.63},
        ]


def generate_report(input_datetime_str: str, transactions: List[Dict]) -> str:
    """Генерирует полный отчет в формате JSON"""
    logger.info("Начало генерации отчета")
    try:
        input_datetime = datetime.strptime(input_datetime_str, "%Y-%m-%d %H:%M:%S")
        logger.debug(f"Время для отчета: {input_datetime}")
    except ValueError:
        input_datetime = datetime.now()
        logger.warning(f"Неверный формат даты '{input_datetime_str}', использовано текущее время")

    report = {
        "greeting": get_greeting(input_datetime),
        "cards": process_cards(transactions),
        "top_transactions": get_top_transactions(transactions),
        "currency_rates": get_currency_rates(),
        "stock_prices": get_stock_prices(),
    }

    logger.info("Отчет успешно сгенерирован")
    return json.dumps(report, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    print(file_reader_excel("..//data/operations.xlsx"))
    print(get_stock_prices())
