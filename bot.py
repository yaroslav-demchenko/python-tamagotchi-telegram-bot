import telebot
from telebot import types
from config import API_TOKEN, tick, buff_duration
from models.user import User
from models.pet import Pet
from services.storage import Storage
import threading
import time
import datetime

bot = telebot.TeleBot(API_TOKEN)

# Ініціалізація сервісу зберігання
storage = Storage()

# Використовуємо збережені дані
users_data = storage.users_data


# Функція для створення головного меню
def create_main_menu():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_shop = types.KeyboardButton('Магазин')
    btn_inventory = types.KeyboardButton('Інвентар')
    btn_pet_status = types.KeyboardButton('Стан тварини')
    keyboard.add(btn_shop, btn_inventory, btn_pet_status)
    return keyboard


# Функція для створення інлайн-клавіатури магазину
def create_shop_inline_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn_egg = types.InlineKeyboardButton('Купити яйце', callback_data='buy_egg')
    btn_food = types.InlineKeyboardButton('Купити їжу', callback_data='buy_food')
    btn_medicine = types.InlineKeyboardButton('Купити ліки', callback_data='buy_medicine')
    btn_buff_food = types.InlineKeyboardButton('Купити борщ', callback_data='buy_borsch')
    keyboard.add(btn_egg, btn_food, btn_buff_food, btn_medicine)
    return keyboard


# Функція для створення інлайн-клавіатури інвентаря
def create_inventory_inline_keyboard(user):
    keyboard = types.InlineKeyboardMarkup()
    for item, quantity in user.inventory.items():
        btn_item = types.InlineKeyboardButton(f"{item} ({quantity}): використати", callback_data=f'use_{item}')
        keyboard.add(btn_item)
    btn_back = types.InlineKeyboardButton('Повернутися в меню', callback_data='back_to_menu')
    keyboard.add(btn_back)
    return keyboard


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    if user_id not in users_data:
        new_user = User(user_id)
        users_data[user_id] = new_user
        storage.save_user(user_id, new_user)
        bot.send_message(user_id, "Привіт! Ти отримав 100 монет!", reply_markup=create_main_menu())
    else:
        bot.send_message(user_id, "Вітаю з поверненням!", reply_markup=create_main_menu())


@bot.message_handler(func=lambda message: message.text == 'Магазин')
def shop(message):
    user_id = message.chat.id
    user = users_data.get(user_id)
    if user:
        bot.send_message(user_id, f"Ласкаво просимо у магазин, у вас доступно {user.coins} монет",
                         reply_markup=create_shop_inline_keyboard())
    else:
        bot.send_message(user_id, "Спочатку запустіть бота за допомогою команди /start")


@bot.message_handler(func=lambda message: message.text == 'Інвентар')
def inventory(message):
    user_id = message.chat.id
    user = users_data.get(user_id)
    if user:
        user.ensure_attributes()  # Ensure the user has all necessary attributes
        if user.inventory:
            bot.send_message(user_id, "Ваш інвентар:", reply_markup=create_inventory_inline_keyboard(user))
        else:
            bot.send_message(user_id, "Ваш інвентар порожній", reply_markup=create_main_menu())
    else:
        bot.send_message(user_id, "Спочатку запустіть бота за допомогою команди /start")


@bot.message_handler(func=lambda message: message.text == 'Стан тварини')
def pet_status(message):
    user_id = message.chat.id
    user = users_data.get(user_id)
    if user and user.pet:
        status = user.pet.status()
        bot.send_message(user_id, f"Стан вашої тварини:\n{status}", reply_markup=create_main_menu())
    else:
        bot.send_message(user_id, "У вас ще немає тварини", reply_markup=create_main_menu())


@bot.callback_query_handler(func=lambda call: call.data.startswith('use_'))
def handle_use_item(call):
    user_id = call.message.chat.id
    user = users_data.get(user_id)
    if not user:
        bot.send_message(user_id, "Спочатку запустіть бота за допомогою команди /start")
        return

    item = call.data.split('_')[1]
    if item in user.inventory and user.inventory[item] > 0:
        if item == 'egg':
            if not user.pet:
                user.pet = Pet()
                bot.send_message(user_id, f"З яйця вилупилася нова тварина - {user.pet.type}!", reply_markup=create_main_menu())
            else:
                bot.send_message(user_id, "У вас вже є тварина!", reply_markup=create_main_menu())
        elif item == 'food' and user.pet:
            user.pet.feed()
            bot.send_message(user_id, "Ваша тварина нагодована!", reply_markup=create_main_menu())
        elif item == 'medicine' and user.pet:
            user.pet.heal()
            bot.send_message(user_id, "Ваша тварина здорова!", reply_markup=create_main_menu())
        elif item == 'borsch' and user.pet:
            user.pet.feed()
            now = datetime.datetime.now()
            user.pet.hunger_buff = [True, now]
            bot.send_message(user_id, "Ви нагодували улюбленця супер-їжею!", reply_markup=create_main_menu())

        user.inventory[item] -= 1
        if user.inventory[item] == 0:
            del user.inventory[item]
        storage.save_user(user_id, user)
    else:
        bot.send_message(user_id, "У вас немає цього предмета або недостатньо кількості",
                         reply_markup=create_main_menu())


@bot.callback_query_handler(func=lambda call: call.data in ['buy_egg', 'buy_food', 'buy_medicine', 'buy_borsch', 'back_to_menu'])
def handle_shop_purchase(call):
    user_id = call.message.chat.id
    user = users_data.get(user_id)
    if not user:
        bot.send_message(user_id, "Спочатку запустіть бота за допомогою команди /start")
        return

    if call.data == 'back_to_menu':
        bot.send_message(user_id, "Ви повернулися в меню", reply_markup=create_main_menu())
        bot.clear_step_handler_by_chat_id(chat_id=user_id)
        return

    if call.data == 'buy_egg':
        cost = 50
        item_name = 'egg'
    elif call.data == 'buy_food':
        cost = 10
        item_name = 'food'
    elif call.data == 'buy_medicine':
        cost = 20
        item_name = 'medicine'
    elif call.data == 'buy_borsch':
        cost = 30
        item_name = 'borsch'
    else:
        return

    if user.coins >= cost:
        user.spend_coins(cost)
        storage.add_item_to_inventory(user_id, item_name)
        bot.send_message(user_id, f"Ви купили {item_name}. Ваші залишкові монети: {user.coins}",
                         reply_markup=create_main_menu())
    else:
        bot.send_message(user_id, "Недостатньо монет для покупки цього товару", reply_markup=create_main_menu())

    storage.save_user(user_id, user)
    bot.answer_callback_query(call.id)


def degrade_pets():

    while True:
        for user_id, user in users_data.items():
            if user.pet:
                user.pet.degrade()
                storage.save_user(user_id, user)
                if user.pet.happiness > 70:
                    user.add_coins(0.2)
                if user.pet.hunger_buff[0]:
                    now = datetime.datetime.now()
                    buff_time = user.pet.hunger_buff[1]
                    time_difference = now - buff_time
                    difference_in_seconds = time_difference.total_seconds()
                    print(difference_in_seconds)
                    if difference_in_seconds > buff_duration:
                        print("різниця відчутна...")
                        user.pet.hunger_buff = [False, None]
                        storage.save_user(user_id, user)

        time.sleep(tick)


# Запуск потоку для деградації стану тварин
threading.Thread(target=degrade_pets, daemon=True).start()

# Основний цикл
if __name__ == '__main__':
    bot.polling(none_stop=True)
