from flask import Flask
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from commands import *
from student_management import add_student, update_student_data, get_all_students
from notifications import check_calls, check_payments
import os
import threading

# Переменные окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Flask приложение
app = Flask(__name__)

@app.route("/")
def home():
    return "Telegram Bot is Running!"


# Состояния для ConversationHandler
TELEGRAM, FIO, FIO_OR_TELEGRAM, FIELD_TO_EDIT, START_DATE, COURSE_TYPE, TOTAL_PAYMENT, PAID_AMOUNT, WAIT_FOR_NEW_VALUE = range(9)


def start_bot():
    # Создание приложения Telegram
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Обработчик добавления студента
    add_student_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Добавить студента$"), add_student_start)],
        states={
            FIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_student_fio)],
            TELEGRAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_student_telegram)],
            START_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_student_date)],
            COURSE_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_student_course_type)],
            TOTAL_PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_student_total_payment)],
            PAID_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_student_paid_amount)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Обработчик редактирования студента
    edit_student_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Редактировать данные студента$"), edit_student)],
        states={
            FIO_OR_TELEGRAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, find_student)],
            FIELD_TO_EDIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_student_field)],
            WAIT_FOR_NEW_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_value)],  # Это важно
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Обработчик поиска студента
    search_student_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Поиск ученика$"), search_student)],
        states={
            FIO_OR_TELEGRAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, display_student_info)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("^Просмотреть студентов$"), view_students))
    application.add_handler(MessageHandler(filters.Regex("^Проверить уведомления$"), check_notifications))
    application.add_handler(add_student_handler)
    application.add_handler(edit_student_handler)
    application.add_handler(search_student_handler)

    # Запуск бота
    application.run_polling()


# Запуск Flask сервера и Telegram бота
if __name__ == "__main__":
    threading.Thread(target=start_bot).start()
    app.run(host="0.0.0.0", port=5000)
