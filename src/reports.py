import json
import logging
from datetime import datetime

import pandas as pd
from dateutil.relativedelta import relativedelta

from src.utils import file_reader_excel

logger = logging.getLogger("save_to_logs_reports")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("../logs/save_to_logs_reports.log", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def decorator_with_args(output_file: str):
    """Декоратор для сохранения результатов в JSON с логированием ключевых событий"""

    def my_big_decorator(func):
        def wrapper(*args, **kwargs):
            logger.info(f"Запуск функции {func.__name__} для категории: {kwargs.get('category', 'не указана')}")

            try:
                result = func(*args, **kwargs)

                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(result.to_dict("records"), f, ensure_ascii=False)
                logger.info(f"Данные сохранены в {output_file}")

                return result
            except Exception as e:
                logger.error(f"Ошибка в {func.__name__}: {str(e)}")
                raise

        return wrapper

    return my_big_decorator


@decorator_with_args("../logs/report.json")
def spending_by_category(transactions: pd.DataFrame, category: str, date: str = str(datetime.now())) -> pd.DataFrame:
    """Возвращает траты по категории за последние 3 месяца"""
    try:
        transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)
        end_date = pd.to_datetime(date, dayfirst=True)
        start_date = end_date - relativedelta(months=3)

        # Фильтрация данных
        mask = (
            (transactions["Дата операции"] >= start_date)
            & (transactions["Дата операции"] <= end_date)
            & (transactions["Категория"].str.upper() == category.upper())
        )
        transactions_filtered = transactions.loc[mask]

        logger.info(f"Найдено {len(transactions_filtered)} транзакций по категории '{category}'")

        # Агрегация результатов
        result_df = transactions_filtered[["Сумма операции"]].sum().to_frame().T
        result_df.columns = [category]

        return result_df
    except Exception as e:
        logger.error(f"Ошибка при обработке категории '{category}': {str(e)}")
        raise


if __name__ == "__main__":

    transactions = file_reader_excel("..//data/operations.xlsx")
    df = pd.DataFrame(transactions)
    result = spending_by_category(df, "Супермаркеты", "10.01.2019")
    print(result)
