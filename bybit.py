import re
from telethon import TelegramClient, events
from pybit.unified_trading import HTTP

# Данные для основного аккаунта
api_id = '28705807'
api_hash = '5526eaa9080d6d0426783d1016e10a84'
phone_number = '+79059805177'  # Твой текущий номер телефона

# API ключи Bybit
api_key = 'H71fARksx55TUUesmP'
api_secret = 'LYOEcpstkYVoqTwCmOisit2e0sfKVo1OoLQh'

# Создаем Telegram-клиент
client = TelegramClient('my_session12', api_id, api_hash, system_version='4.16.30-vxCUSTOM')

# Авторизация
client.start(phone=phone_number)

# Подключение к Bybit API (используем демо-счет)
session = HTTP(
    demo=True,  # Включаем демо-счет
    api_key=api_key,
    api_secret=api_secret
)

# Функция для удаления эмодзи
def remove_emoji(string):
    return re.sub(r'[^\w\s#]', '', string)

# Обработчик новых сообщений
@client.on(events.NewMessage(chats=['https://t.me/signalyp', 'https://t.me/vypytm_i_pokurim']))
async def new_message_listener(event):
    message = event.message.message
    message = message.replace("\xa0", " ")  # Убираем неразрывные пробелы
    message_lines = message.split("\n")  # Разделим сообщение на строки для точного анализа
    print(f"Сырое сообщение: {repr(message)}")  # Выводим сырое сообщение для анализа
    print(f"Строки сообщения: {message_lines}")  # Выводим все строки сообщения по отдельности

    symbol = None
    side = None
    leverage = None
    entry = None
    take_profit = None
    stop_loss = None

    # Проверим строки на наличие ключевых данных
    for line in message_lines:
        if "#" in line:  # Символ и направление сделки
            parts = remove_emoji(line).split()  # Убираем эмодзи и разбиваем строку
            if len(parts) >= 2:
                symbol = parts[0].replace("#", "").strip()  # Убираем # и лишние пробелы
                symbol += "USDT"  # Добавляем "USDT" к символу
                side = parts[1].strip().upper()  # Направление сделки (LONG/SHORT) в верхний регистр
                print(f"Найден символ: {symbol}, сделка: {side}")
            else:
                print("Ошибка: не удалось извлечь символ или сделку")

        elif "Плечо" in line:  # Плечо
            leverage = re.search(r"(\d+x)", line)
            if leverage:
                leverage = leverage.group(1).strip()  # Убираем пробелы
            print(f"Найдено плечо: {leverage}")

        elif "Точка входа" in line or "Диапазон входа" in line:  # Точка входа или Диапазон входа
            entry_match = re.search(r"(по рынку|[\d\.]+)", line)
            if entry_match:
                entry = entry_match.group(1).strip()  # Убираем пробелы
            print(f"Найдена точка входа (или диапазон): {entry}")

        elif "Тейки" in line:  # Тейки
            take_profit_line = re.sub(r"[^\d\s\.]", "", line.replace("Тейки:", "").strip())
            take_profit = [float(x) for x in take_profit_line.split()]
            print(f"Найдены тейки: {take_profit}")

        elif "Стоп" in line:  # Стоп-лосс
            stop_match = re.search(r"([\d\.]+|пока не ставлю)", line)
            if stop_match:
                stop_loss = stop_match.group(1).strip()  # Убираем пробелы
                if stop_loss == "пока не ставлю":
                    stop_loss = None  # Если стоп-лосс не установлен, оставляем None
            print(f"Найден стоп-лосс: {stop_loss}")

    # Вывод всех найденных данных
    print(f"Символ: {symbol}, Сделка: {side}, Плечо: {leverage}, Точка входа: {entry}, Тейки: {take_profit}, Стоп: {stop_loss}")

    # Проверяем корректность данных
    if symbol and side and leverage and entry and take_profit:
        #symbol += "USDT"  # Добавляем USDT к символу
        order_side = "Buy" if side == "LONG" else "Sell"

        print(f"Отправляем запрос на создание ордера: символ={symbol}, сторона={order_side}, тейк-профит={take_profit[0]}, стоп-лосс={stop_loss}")

        # Создание рыночного ордера через метод place_order
        try:
            order_params = {
                "category": "linear",  # Категория ордеров (например, linear для USDT perpetual)
                "symbol": symbol,
                "side": order_side,
                "order_type": "Market",  # Рыночный ордер
                "qty": 5,  # Количество (например, 1 контракт)
                "time_in_force": "GoodTillCancel"
            }

            # Добавляем stop_loss и take_profit, только если они есть
            if stop_loss is not None:
                order_params["stop_loss"] = str(stop_loss)  # Преобразуем в строку
            if take_profit is not None:
                order_params["take_profit"] = str(take_profit[0])  # Преобразуем первый тейк-профит в строку

            response = session.place_order(**order_params)  # Передаем параметры в виде словаря
            print("Ответ от API Bybit:", response)  # Выводим ответ от API Bybit
        except Exception as e:
            print(f"Ошибка при создании ордера: {e}")
    else:
        print("Не удалось собрать все необходимые данные для ордера.")

# Запуск клиента
client.run_until_disconnected()
