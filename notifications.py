import asyncio
from datetime import datetime, timedelta
from student_management import get_all_students

# Напоминание о звонке
async def check_last_calls():
    students = get_all_students()
    today = datetime.today()
    for student in students:
        last_call = datetime.strptime(student["Дата звонка"], "%d.%m.%Y")
        if (today - last_call).days > 20:
            # Логика уведомления
            print(f"Напоминание: Пора звонить студенту {student['ФИО']}!")


# Проверка звонков
def check_calls():
    students = get_all_students()
    today = datetime.today()
    notifications = []

    for student in students:
        # Проверяем, существует ли поле "Дата последнего звонка" и корректный формат даты
        if "Дата последнего звонка" in student and student["Дата последнего звонка"]:
            try:
                last_call = datetime.strptime(student["Дата последнего звонка"], "%d.%m.%Y")
                days_since_call = (today - last_call).days
                if days_since_call > 20:
                    notifications.append(
                        f"Пора звонить студенту {student['ФИО']}! Последний звонок был {student['Дата последнего звонка']}."
                    )
            except ValueError:
                notifications.append(f"Ошибка в формате даты у студента {student['ФИО']}. Проверьте данные.")

    return notifications


# Проверка задолженностей
def check_payments():
    students = get_all_students()
    notifications = []

    for student in students:
        # Проверяем поле "Полностью оплачено"
        if "Полностью оплачено" in student and student["Полностью оплачено"] == "Нет":
            total_payment = student.get("Стоимость обучения", 0)
            paid_amount = student.get("Сумма оплачено", 0)

            try:
                total_payment = int(total_payment)
                paid_amount = int(paid_amount)
            except ValueError:
                notifications.append(f"Ошибка в данных оплаты у студента {student['ФИО']}. Проверьте таблицу.")
                continue

            debt = total_payment - paid_amount
            if debt > 0:
                notifications.append(
                    f"Студент {student['ФИО']} задолжал {debt} рублей."
                )

    return notifications
