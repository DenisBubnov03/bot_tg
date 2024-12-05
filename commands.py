from datetime import datetime
from student_management import add_student, get_all_students, update_student_data
from notifications import check_calls, check_payments
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

# Состояния для ConversationHandler
TELEGRAM, FIO, FIO_OR_TELEGRAM, FIELD_TO_EDIT, START_DATE, COURSE_TYPE, TOTAL_PAYMENT, PAID_AMOUNT, WAIT_FOR_NEW_VALUE = range(9)



# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [
        ['Добавить студента', 'Просмотреть студентов'],
        ['Редактировать данные студента', 'Проверить уведомления'],
        ['Поиск ученика', 'Помощь']
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    await update.message.reply_text("Привет! Выберите действие:", reply_markup=markup)



# Просмотр списка студентов
async def view_students(update: Update, context: ContextTypes.DEFAULT_TYPE):
    students = get_all_students()
    response = "Список студентов:\n"
    for i, student in enumerate(students, start=1):
        response += f"{i}. {student['ФИО']} - {student['Telegram']} ({student['Тип обучения']})\n"
    await update.message.reply_text(response)


# Добавление студента: шаг 1 - ввод ФИО
async def add_student_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введите ФИО студента:",
    )
    return FIO


# Добавление студента: шаг 2 - ввод Telegram
async def add_student_fio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fio"] = update.message.text
    await update.message.reply_text(
        "Введите Telegram студента:",)
    return TELEGRAM


# Добавление студента: шаг 3 - ввод даты начала обучения
async def add_student_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_account = update.message.text
    if telegram_account.startswith("@") and len(telegram_account) > 1:
        context.user_data["telegram"] = telegram_account
        await update.message.reply_text(
            "Введите дату начала обучения (в формате ДД.ММ.ГГГГ):",)
        return START_DATE
    else:
        await update.message.reply_text(
            "Некорректный Telegram. Убедитесь, что он начинается с @. Попробуйте ещё раз.")
        return TELEGRAM


# Добавление студента: шаг 4 - выбор типа обучения
async def add_student_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        date_text = update.message.text
        datetime.strptime(date_text, "%d.%m.%Y")
        context.user_data["start_date"] = date_text
        await update.message.reply_text(
            "Выберите тип обучения:",
            reply_markup=ReplyKeyboardMarkup(
                [['Ручное тестирование', 'Автотестирование', 'Фуллстек',]],
                one_time_keyboard=True
            )
        )
        return COURSE_TYPE
    except ValueError:
        await update.message.reply_text(
            "Дата должна быть в формате ДД.ММ.ГГГГ. Попробуйте ещё раз.",)
        return START_DATE


# Добавление студента: шаг 5 - выбор стоимости обучения
async def add_student_course_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    valid_course_types = ["Ручное тестирование", "Автотестирование", "Фуллстек"]
    course_type = update.message.text

    if course_type in valid_course_types:
        context.user_data["course_type"] = course_type
        await update.message.reply_text(
            "Введите общую стоимость обучения:",)
        return TOTAL_PAYMENT
    else:
        await update.message.reply_text(
            f"Некорректный тип обучения. Выберите один из вариантов: {', '.join(valid_course_types)}.")
        return COURSE_TYPE


# Добавление студента: шаг 6 - ввод общей стоимости
async def add_student_total_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        total_payment = int(update.message.text)
        if total_payment > 0:
            context.user_data["total_payment"] = total_payment
            await update.message.reply_text(
                "Введите сумму уже внесённой оплаты:",)
            return PAID_AMOUNT
        else:
            await update.message.reply_text(
                "Сумма должна быть больше 0. Попробуйте ещё раз.",)
            return TOTAL_PAYMENT
    except ValueError:
        await update.message.reply_text(
            "Введите корректное число. Попробуйте ещё раз.")
        return TOTAL_PAYMENT


# Завершение добавления студента
async def add_student_paid_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        paid_amount = int(update.message.text)
        if 0 <= paid_amount <= context.user_data["total_payment"]:
            context.user_data["paid_amount"] = paid_amount

            # Сохранение данных в Google Sheets
            add_student(
                context.user_data["fio"],
                context.user_data["telegram"],
                context.user_data["start_date"],
                context.user_data["course_type"],
                context.user_data["total_payment"],
                context.user_data["paid_amount"]
            )

            await update.message.reply_text(
                "Студент успешно добавлен!",
                reply_markup=ReplyKeyboardMarkup(
                    [['Добавить студента', 'Просмотреть студентов'],
                     ['Редактировать данные студента', 'Проверить уведомления']],
                    one_time_keyboard=True
                )
            )
            return ConversationHandler.END
        else:
            await update.message.reply_text(
                f"Сумма оплаты должна быть в пределах от 0 до {context.user_data['total_payment']}. Попробуйте ещё раз."
            )
            return PAID_AMOUNT
    except ValueError:
        await update.message.reply_text(
            "Введите корректное число. Попробуйте ещё раз."
        )
        return PAID_AMOUNT


# Поиск студента
async def find_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    search_query = update.message.text.lower()
    students = get_all_students()

    matching_students = [
        student for student in students
        if search_query in student["ФИО"].lower() or search_query in student["Telegram"].lower()
    ]

    if not matching_students:
        await update.message.reply_text("Студент не найден. Попробуйте ещё раз:")
        return FIO_OR_TELEGRAM

    if len(matching_students) > 1:
        response = "Найдено несколько студентов. Уточните:\n"
        for i, student in enumerate(matching_students, start=1):
            response += f"{i}. {student['ФИО']} - {student['Telegram']}\n"
        await update.message.reply_text(response)
        return FIO_OR_TELEGRAM

    context.user_data["student"] = matching_students[0]
    await update.message.reply_text(
        f"Вы выбрали студента: {matching_students[0]['ФИО']} ({matching_students[0]['Telegram']}).\n"
        "Что вы хотите отредактировать?",
        reply_markup=ReplyKeyboardMarkup(
            [['ФИО', 'Telegram', 'Дата последнего звонка', 'Сумма оплаты']],
            one_time_keyboard=True
        )
    )
    return FIELD_TO_EDIT

# Обработка команды редактирования
async def edit_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введите ФИО или Telegram студента, данные которого вы хотите отредактировать:")
    return FIO_OR_TELEGRAM

async def edit_student_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    field_to_edit = update.message.text
    valid_fields = ["ФИО", "Telegram", "Дата последнего звонка", "Сумма оплаты"]

    if field_to_edit in valid_fields:
        context.user_data["field_to_edit"] = field_to_edit
        await update.message.reply_text(
            f"Введите новое значение для '{field_to_edit}':",)
        return WAIT_FOR_NEW_VALUE  # Перевод в состояние ожидания нового значения
    else:
        await update.message.reply_text(
            "Некорректное поле. Выберите одно из предложенных.",
            reply_markup=ReplyKeyboardMarkup(
                [['ФИО', 'Telegram', 'Дата последнего звонка', 'Сумма оплаты']],
                one_time_keyboard=True
            )
        )
        return FIELD_TO_EDIT  # Повторно запрашиваем выбор поля


async def handle_new_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    student = context.user_data.get("student")
    field_to_edit = context.user_data.get("field_to_edit")
    new_value = update.message.text  # Новое значение от пользователя

    if not student or not field_to_edit:
        await update.message.reply_text("Ошибка: данные для редактирования отсутствуют. Начните сначала.")
        return ConversationHandler.END

    if field_to_edit == "Сумма оплаты":
        try:
            additional_payment = int(new_value)
            current_payment = int(student.get("Сумма оплаты", 0))  # Убедитесь, что ключ совпадает с таблицей
            total_payment = int(student.get("Стоимость обучения", 0))

            if current_payment + additional_payment > total_payment:
                await update.message.reply_text(
                    f"Ошибка: итоговая сумма оплаты ({current_payment + additional_payment}) "
                    f"превышает стоимость обучения ({total_payment}). Введите корректное значение."
                )
                return FIELD_TO_EDIT

            updated_payment = current_payment + additional_payment
            result = update_student_data(student["ФИО"], "Сумма оплаты", updated_payment)

            if result:
                await update.message.reply_text(
                    f"Сумма оплаты успешно обновлена! Теперь оплачено: {updated_payment} из {total_payment}.",
                    reply_markup=ReplyKeyboardMarkup(
                        [['Добавить студента', 'Просмотреть студентов'],
                         ['Редактировать данные студента', 'Проверить уведомления'],
                         ['Помощь']],
                        one_time_keyboard=True
                    )
                )
                return ConversationHandler.END
            else:
                await update.message.reply_text("Ошибка обновления данных. Попробуйте снова.")
                return FIELD_TO_EDIT
        except ValueError:
            await update.message.reply_text("Введите корректное число. Попробуйте снова.")
            return FIELD_TO_EDIT

    else:
        result = update_student_data(student["ФИО"], field_to_edit, new_value)
        if result:
            await update.message.reply_text(
                f"Поле '{field_to_edit}' успешно обновлено на '{new_value}'!",
                reply_markup=ReplyKeyboardMarkup(
                    [['Добавить студента', 'Просмотреть студентов'],
                     ['Редактировать данные студента', 'Проверить уведомления'],
                     ['Помощь']],
                    one_time_keyboard=True
                )
            )
            return ConversationHandler.END
        else:
            await update.message.reply_text("Ошибка обновления данных. Попробуйте снова.")
            return FIELD_TO_EDIT


# Проверка уведомлений
async def check_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    calls = check_calls()
    payments = check_payments()

    messages = []

    if calls:
        messages.append("❗ Уведомления по звонкам:")
        messages.extend(calls)

    if payments:
        messages.append("❗ Уведомления по оплатам:")
        messages.extend(payments)

    if not messages:
        await update.message.reply_text("✅ Все в порядке, уведомлений нет!")
    else:
        await update.message.reply_text("\n".join(messages))

# Поиск и вывод информации об ученике
async def search_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введите ФИО или Telegram ученика, информацию о котором хотите посмотреть:")
    return FIO_OR_TELEGRAM  # Состояние для поиска

async def display_student_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    search_query = update.message.text.lower()
    students = get_all_students()

    # Фильтрация студентов по совпадению с ФИО или Telegram
    matching_students = [
        student for student in students
        if search_query in student["ФИО"].lower() or search_query in student["Telegram"].lower()
    ]

    if not matching_students:
        await update.message.reply_text("Ученик не найден. Попробуйте ещё раз'.")
        return FIO_OR_TELEGRAM

    # Если найдено несколько студентов
    if len(matching_students) > 1:
        response = "Найдено несколько учеников. Уточните запрос:\n"
        for student in matching_students:
            response += f"{student['ФИО']} - {student['Telegram']}\n"
        await update.message.reply_text(response)
        return FIO_OR_TELEGRAM

    # Если найден один ученик
    student = matching_students[0]
    context.user_data["student"] = student  # Сохраняем ученика в контекст

    # Вывод всей информации об ученике
    info = "\n".join([f"{key}: {value}" for key, value in student.items()])
    await update.message.reply_text(
        f"Информация об ученике:\n\n{info}",
        reply_markup=ReplyKeyboardMarkup(
            [['Добавить студента', 'Просмотреть студентов'],
             ['Редактировать данные студента', 'Проверить уведомления'], ['Поиск ученика']],
            one_time_keyboard=True
        )
    )
    return ConversationHandler.END

# async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     print(f"Cancel invoked! Полученный текст: {update.message.text}")  # Лог
#     await update.message.reply_text(
#         "Действие отменено. Возвращаюсь в главное меню.",
#         reply_markup=ReplyKeyboardMarkup(
#             [['Добавить студента', 'Просмотреть студентов'],
#              ['Редактировать данные студента', 'Проверить уведомления'],
#              ['Помощь']],
#             one_time_keyboard=True
#         )
#     )
#     return ConversationHandler.END

