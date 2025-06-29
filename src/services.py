import json
import pandas as pd
import re
from typing import Dict, List


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


def search_number(transactions: List[Dict]) -> str:
    """Функция возвращает, JSON строку, транзакции с мобильными номерами в описании"""
    pattern = re.compile(r"\D+ \+7 \d{3} \d{3}-\d{2}-\d{2}")
    result_list = [transaction for transaction in transactions if pattern.search(transaction["Описание"])]
    result = json.dumps(result_list, ensure_ascii=False)
    return result


if __name__ == "__main__":
    transactions = file_reader_excel('..//data/operations.xlsx')
    print(search_number(transactions))
