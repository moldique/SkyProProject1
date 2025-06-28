from datetime import datetime
from typing import Dict, List
import pandas as pd
import json
import requests


def file_reader_excel(excel_path: str) -> list[dict]:
    """ Читает Excel файл и возвращает список словарей с данными."""
    try:
        df = pd.read_excel(excel_path)
        return df.to_dict('records')
    except FileNotFoundError:
        print(f"Ошибка: файл не найден по пути {excel_path}")
        return []
    except Exception as e:
        print(f"Произошла ошибка при чтении файла: {e}")
        return []


def get_greeting(input_datetime: str) -> None:
    """Возвращает приветствие в зависимости от времени суток"""
    hour = input_datetime.hour
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def process_cards(transactions: List[Dict]) -> None:
    """Обрабатывает данные по картам"""
    cards = {}

    for t in transactions:
        card = t['Номер карты']
        if not isinstance(card, str):  # Пропускаем операции без карты
            continue

        last_digits = card[-4:]
        amount = abs(t['Сумма операции']) if t['Сумма операции'] < 0 else 0

        if last_digits not in cards:
            cards[last_digits] = {
                'total_spent': 0,
                'cashback': 0
            }

        cards[last_digits]['total_spent'] += amount
        cards[last_digits]['cashback'] += amount * 0.01  # 1% кэшбэка

    # Форматируем результат
    result = []
    for last_digits, data in cards.items():
        result.append({
            'last_digits': last_digits,
            'total_spent': round(data['total_spent'], 2),
            'cashback': round(data['cashback'], 2)
        })

    return result


def get_top_transactions(transactions : List[Dict], n=5) -> None:
    """Возвращает топ-N транзакций по сумме платежа"""
    # Фильтруем только расходы (отрицательные суммы)
    expenses = [t for t in transactions if t['Сумма платежа'] < 0]

    # Сортируем по абсолютной величине платежа
    sorted_trans = sorted(expenses, key=lambda x: abs(x['Сумма платежа']), reverse=True)

    # Берем топ-N и форматируем
    top = []
    for t in sorted_trans[:n]:
        top.append({
            'date': t['Дата операции'].split()[0],
            'amount': abs(t['Сумма платежа']),
            'category': t['Категория'],
            'description': t['Описание']
        })

    return top


def get_currency_rates():
    """Получает курсы валют"""
    try:
        response = requests.get('https://api.exchangerate-api.com/v4/latest/RUB')
        data = response.json()
        return [
            {'currency': 'USD', 'rate': round(1 / data['rates']['USD'], 2)},
            {'currency': 'EUR', 'rate': round(1 / data['rates']['EUR'], 2)}
        ]
    except:
        # Возвращаем примерные значения, если API не доступно
        return [
            {'currency': 'USD', 'rate': 73.21},
            {'currency': 'EUR', 'rate': 87.08}
        ]


def get_stock_prices():
    """Получает цены акций"""
    try:
        stocks = ['AAPL', 'AMZN', 'GOOGL', 'MSFT', 'TSLA']
        prices = []

        for stock in stocks:
            response = requests.get(f'https://api.iextrading.com/1.0/stock/{stock}/price')
            prices.append({
                'stock': stock,
                'price': round(float(response.text), 2)
            })

        return prices
    except:
        # Возвращаем примерные значения, если API не доступно
        return [
            {'stock': 'AAPL', 'price': 150.12},
            {'stock': 'AMZN', 'price': 3173.18},
            {'stock': 'GOOGL', 'price': 2742.39},
            {'stock': 'MSFT', 'price': 296.71},
            {'stock': 'TSLA', 'price': 1007.08}
        ]


def generate_report(input_datetime_str : str, transactions: List[Dict]) -> None:
    """Генерирует полный отчет в формате JSON"""
    try:
        input_datetime = datetime.strptime(input_datetime_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        input_datetime = datetime.now()

    report = {
        'greeting': get_greeting(input_datetime),
        'cards': process_cards(transactions),
        'top_transactions': get_top_transactions(transactions),
        'currency_rates': get_currency_rates(),
        'stock_prices': get_stock_prices()
    }

    return json.dumps(report, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    print(file_reader_excel('..//data/operations.xlsx'))
