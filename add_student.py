import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import gspread

# Область доступа для Google Sheets API
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


# Авторизация и сохранение токена
def authenticate():
    creds = None
    # Проверяем, существует ли файл токена
    if os.path.exists("token.pickle"):
        print("Загружаю существующий токен...")
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # Если токена нет или он устарел, выполняем авторизацию
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Обновляю токен...")
            creds.refresh(Request())
        else:
            print("Прохожу авторизацию...")
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Сохраняем токен для последующего использования
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
            print("Токен сохранён.")
    return creds

# Проверка текущей рабочей директории
print("Текущая рабочая директория:", os.getcwd())

# Проверяем наличие файла client_secret.json
if not os.path.exists("client_secret.json"):
    print("Ошибка: файл client_secret.json не найден!")
    exit()
else:
    print("Файл client_secret.json найден, продолжаю...")

# Авторизация
creds = authenticate()
client = gspread.authorize(creds)

# Подключение к таблице
try:
    spreadsheet = client.open("Ученики")  # Замените "Ученики" на название вашей таблицы
    worksheet = spreadsheet.sheet1
    print("Таблица найдена!")
except gspread.exceptions.APIError as e:
    print(f"Ошибка API: {e.response.json()}")
    exit()

# Пример данных для добавления
student_data = [
    "Мария Смирнова",  # ФИО
    "@maria_sm",       # Telegram
    "2024-01-15",      # Дата начала обучения
    "Автоматизация",   # Тип обучения
    "70k",             # Стоимость обучения
    "35k",             # Сумма оплачено
    "2024-01-25",      # Дата последнего звонка
    None,              # Компания
    None,              # Дата трудоустройства
    None,              # Зарплата
    "Нет"              # Полностью оплачено
]

# Добавление данных в таблицу
try:
    worksheet.append_row(student_data)
    print("Данные добавлены!")
except gspread.exceptions.APIError as e:
    print(f"Ошибка при добавлении данных: {e.response.json()}")
