from src.utils import *


def main():
    """Функция для страницы «Главная» «Веб-страницы»"""
    transactions = file_reader_excel('..//data/operations.xlsx')
    input_datetime = "2023-05-15 14:30:00"
    return generate_report(input_datetime, transactions)


if __name__ == "__main__":
    print(main())