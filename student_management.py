import gspread

# Подключение к Google Sheets
def connect_to_sheets():
    """Устанавливает подключение к таблице Google Sheets."""
    gc = gspread.service_account(filename="client_secret.json")
    spreadsheet = gc.open("Ученики")  # Название таблицы
    worksheet = spreadsheet.sheet1
    return worksheet

worksheet = connect_to_sheets()

# Добавление студента
def add_student(fio, telegram, start_date, course_type, total_payment, paid_amount):
    """
    Добавляет студента в таблицу Google Sheets.

    Args:
        fio (str): ФИО студента.
        telegram (str): Telegram аккаунт студента.
        start_date (str): Дата начала обучения в формате ДД.ММ.ГГГГ.
        course_type (str): Тип обучения (например, Ручное тестирование).
        total_payment (int): Общая стоимость обучения.
        paid_amount (int): Сумма, уже оплаченная.
    """
    worksheet.append_row([fio, telegram, start_date, course_type, total_payment, paid_amount])

# Удаление студента
def delete_student(identifier):
    """
    Удаляет студента по ФИО или Telegram из таблицы.

    Args:
        identifier (str): ФИО или Telegram студента.

    Returns:
        bool: True, если студент удалён, иначе False.
    """
    students = worksheet.get_all_records()
    for i, student in enumerate(students):
        if student["ФИО"] == identifier or student["Telegram"] == identifier:
            worksheet.delete_rows(i + 2)  # Удаляем строку (i + 2, так как 1-я строка - заголовок)
            return True
    return False

# Редактирование студента
def update_student_data(identifier, field, new_value):
    students = worksheet.get_all_records()
    for i, student in enumerate(students):
        if student["ФИО"] == identifier:
            headers = list(student.keys())
            if field in headers:
                col_index = headers.index(field) + 1
                worksheet.update_cell(i + 2, col_index, new_value)
                return True
    return False


# Получение списка всех студентов
def get_all_students():
    """
    Возвращает всех студентов в виде списка словарей.

    Returns:
        list: Список студентов (каждый студент - словарь с ключами, соответствующими столбцам).
    """
    return worksheet.get_all_records()
