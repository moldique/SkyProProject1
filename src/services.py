import json
import logging
import re
from typing import Dict, List

from src.utils import file_reader_excel

logger = logging.getLogger("save_to_logs_services")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("../logs/save_to_logs_services.log", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def search_number(transactions: List[Dict]) -> str:
    """Функция возвращает, JSON строку, транзакции с мобильными номерами в описании"""
    logger.info("Функция поиска и фильтрации по телефонным номерам в описании - началась")
    pattern = re.compile(r"\D+ \+7 \d{3} \d{3}-\d{2}-\d{2}")
    result_list = [transaction for transaction in transactions if pattern.search(transaction["Описание"])]
    result = json.dumps(result_list, ensure_ascii=False)
    logger.info("Функция поиска и фильтрации по телефонным номерам в описании - выполнена")
    return result


if __name__ == "__main__":
    transactions = file_reader_excel("..//data/operations.xlsx")
    print(search_number(transactions))
