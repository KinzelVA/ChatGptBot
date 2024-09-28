import telebot
import requests

# Вставьте свои ключи
TELEGRAM_API_TOKEN = '7793135694:AAF9FeKZxuVnxBOjhUHQzWqY6EytPjyyXQk'
CHAD_API_KEY = 'chad-592ed89a0fb54181ac616739a2bf748bsenyrg7j'

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
        response = requests.post(url, json=request_json)

        if response.status_code != 200:
            return f'Ошибка! Код http-ответа: {response.status_code}'

        resp_json = response.json()

        if resp_json['is_success']:
            return resp_json['response']
        else:
            return f'Ошибка от API: {resp_json["error_message"]}'

    except Exception as e:
        return f'Ошибка при общении с Chad API: {str(e)}'


# Обработка команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот, интегрированный с Chad API. Задай мне любой вопрос!")


# Обработка текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_message = message.text
    bot.reply_to(message, "Думаю над ответом...")

    # Получаем ответ от Chad API
    chad_response = ask_chad_api(user_message)

    # Отправляем ответ пользователю
    bot.reply_to(message, chad_response)


# Запуск бота
bot.polling(none_stop=True)
