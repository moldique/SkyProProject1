from src.utils import file_reader_excel, generate_report


def main(name: str, data: str) -> str:
    """Функция для страницы «Главная» «Веб-страницы»"""
    transactions = file_reader_excel(name)
    input_datetime = data
    return generate_report(input_datetime, transactions)


if __name__ == "__main__":
    print(main("..//data/operations.xlsx", "2023-05-15 14:30:00"))
