import telebot
import requests

# Вставьте свои ключи
TELEGRAM_API_TOKEN = '7793135694:AAF9FeKZxuVnxBOjhUHQzWqY6EytPjyyXQk'
CHAD_API_KEY = ''

# Инициализация бота
bot = telebot.TeleBot(TELEGRAM_API_TOKEN)


# Функция для общения с Chad API
def ask_chad_api(question):
    url = 'https://ask.chadgpt.ru/api/public/gpt-4o-mini'  # Используем нужную модель
    request_json = {
        "message": question,
        "api_key": CHAD_API_KEY
    }

    try:
        # Отправка запроса
        response = requests.post(url, json=request_json, timeout=10)  # Устанавливаем таймаут для запроса

        # Проверка статуса запроса
        if response.status_code != 200:
            return f'Ошибка! Код http-ответа: {response.status_code}. Проверьте API-ключ или модель.'

        # Обработка JSON-ответа
        resp_json = response.json()

        if resp_json.get('is_success'):
            return resp_json['response']
        else:
            return f'Ошибка от API: {resp_json.get("error_message", "Неизвестная ошибка")}'

    except requests.exceptions.Timeout:
        return 'Ошибка: Превышено время ожидания ответа от Chad API.'
    except requests.exceptions.ConnectionError:
        return 'Ошибка: Не удалось подключиться к Chad API. Проверьте соединение с интернетом.'
    except requests.exceptions.RequestException as e:
        return f'Ошибка запроса: {str(e)}'
    except Exception as e:
        return f'Непредвиденная ошибка: {str(e)}'


# Обработка команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        bot.reply_to(message, "Привет! Я бот, интегрированный с Chad API. Задай мне любой вопрос!")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {str(e)}")


# Обработка текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        user_message = message.text
        bot.reply_to(message, "Думаю над ответом...")

        # Получаем ответ от Chad API
        chad_response = ask_chad_api(user_message)

        # Отправляем ответ пользователю
        bot.reply_to(message, chad_response)
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при обработке сообщения: {str(e)}")


# Запуск бота
try:
    bot.polling(none_stop=True)
except Exception as e:
    print(f"Ошибка при запуске бота: {str(e)}")
