import os
import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

ORDERS_GROUP_ID = -5034159641
FINANCE_GROUP_ID = -5012459213
LOGISTICS_GROUP_ID = -5175392722
PVZ_GROUP_ID = -5023952843
TRAINING_GROUP_ID = -5236071492

user_states = {}

MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📦 Заказы"), KeyboardButton(text="💰 Бонусы")],
        [KeyboardButton(text="👥 Регистрация"), KeyboardButton(text="🏪 ПВЗ")],
        [KeyboardButton(text="🚚 Доставка"), KeyboardButton(text="💄 Продукция")],
        [KeyboardButton(text="🎓 Обучение"), KeyboardButton(text="📄 Документы")],
        [KeyboardButton(text="☎️ Связаться с офисом")],
    ],
    resize_keyboard=True,
)

BACK_MENU = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="⬅️ Назад")]],
    resize_keyboard=True,
)

def submenu(buttons):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=b)] for b in buttons] + [[KeyboardButton(text="⬅️ Назад")]],
        resize_keyboard=True,
    )

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Добро пожаловать в Центр поддержки Cordial Care.\n\n"
        "Выберите необходимый раздел:",
        reply_markup=MAIN_MENU
    )

@dp.message(F.text == "⬅️ Назад")
async def back(message: Message):
    user_states.pop(message.from_user.id, None)
    await message.answer("Вы вернулись в главное меню:", reply_markup=MAIN_MENU)

@dp.message(F.text == "📦 Заказы")
async def orders(message: Message):
    await message.answer(
        "Раздел: 📦 Заказы",
        reply_markup=submenu([
            "🛒 Проверить заказ",
            "❌ Отмена заказа",
            "🔄 Изменить заказ",
            "📋 История заказов",
        ])
    )

@dp.message(F.text == "💰 Бонусы")
async def bonuses(message: Message):
    await message.answer(
        "Раздел: 💰 Бонусы",
        reply_markup=submenu([
            "💵 Не начислились бонусы",
            "📈 Как считается бонус",
            "🎁 Реферальный бонус",
            "🔷 Бинарный бонус",
            "👥 Матчинг бонус",
            "🏆 Структурный бонус",
        ])
    )

@dp.message(F.text == "👥 Регистрация")
async def registration(message: Message):
    await message.answer(
        "Раздел: 👥 Регистрация",
        reply_markup=submenu([
            "🆔 Проблема с регистрацией",
            "🔑 Не могу войти",
            "📱 Смена телефона",
            "📧 Смена почты",
            "👤 Изменение данных",
        ])
    )

@dp.message(F.text == "🏪 ПВЗ")
async def pvz(message: Message):
    await message.answer(
        "Раздел: 🏪 ПВЗ",
        reply_markup=submenu([
            "📦 Остатки товара",
            "🚚 Поставка товара",
            "🔄 Возврат товара",
            "📄 Документы ПВЗ",
            "🏪 Открытие ПВЗ",
            "☎️ Связь с менеджером",
        ])
    )

@dp.message(F.text == "🚚 Доставка")
async def delivery(message: Message):
    await message.answer(
        "Раздел: 🚚 Доставка",
        reply_markup=submenu([
            "📍 Где мой заказ",
            "🚚 Статус доставки",
            "📦 Трек номер",
            "❌ Проблема доставки",
        ])
    )

@dp.message(F.text == "💄 Продукция")
async def products(message: Message):
    await message.answer(
        "Раздел: 💄 Продукция",
        reply_markup=submenu([
            "✨ ESROOM",
            "🌿 WELLSEED",
            "💙 Collagen Health & Beauty",
            "🦴 Calcium Madi D3",
            "📖 Инструкция применения",
            "📄 Сертификаты",
        ])
    )

@dp.message(F.text == "🎓 Обучение")
async def education(message: Message):
    await message.answer(
        "Раздел: 🎓 Обучение",
        reply_markup=submenu([
            "🚀 Старт новичка",
            "🎯 Маркетинг план",
            "👥 Рекрутинг",
            "📈 Построение команды",
            "🎓 Академия Cordial Care",
        ])
    )

@dp.message(F.text == "📄 Документы")
async def documents(message: Message):
    await message.answer(
        "Раздел: 📄 Документы",
        reply_markup=submenu([
            "📋 Маркетинг план PDF",
            "📄 Политика компании",
            "🏪 Регламент ПВЗ",
            "🎁 Условия акций",
        ])
    )

@dp.message(F.text == "☎️ Связаться с офисом")
async def office(message: Message):
    await message.answer(
        "Выберите отдел офиса:",
        reply_markup=submenu([
            "💰 Финансовый отдел",
            "📦 Отдел заказов",
            "🚚 Логистика",
            "🏪 Отдел ПВЗ",
            "🎓 Отдел обучения",
        ])
    )

REQUEST_ROUTES = {
    "🛒 Проверить заказ": ("Заказы", ORDERS_GROUP_ID),
    "❌ Отмена заказа": ("Заказы", ORDERS_GROUP_ID),
    "🔄 Изменить заказ": ("Заказы", ORDERS_GROUP_ID),
    "📋 История заказов": ("Заказы", ORDERS_GROUP_ID),
    "📦 Отдел заказов": ("Заказы", ORDERS_GROUP_ID),

    "💵 Не начислились бонусы": ("Финансы", FINANCE_GROUP_ID),
    "💰 Финансовый отдел": ("Финансы", FINANCE_GROUP_ID),

    "🆔 Проблема с регистрацией": ("Регистрация", TRAINING_GROUP_ID),
    "🔑 Не могу войти": ("Регистрация", TRAINING_GROUP_ID),
    "📱 Смена телефона": ("Регистрация", TRAINING_GROUP_ID),
    "📧 Смена почты": ("Регистрация", TRAINING_GROUP_ID),
    "👤 Изменение данных": ("Регистрация", TRAINING_GROUP_ID),

    "📦 Остатки товара": ("ПВЗ", PVZ_GROUP_ID),
    "🚚 Поставка товара": ("ПВЗ", PVZ_GROUP_ID),
    "🔄 Возврат товара": ("ПВЗ", PVZ_GROUP_ID),
    "📄 Документы ПВЗ": ("ПВЗ", PVZ_GROUP_ID),
    "🏪 Открытие ПВЗ": ("ПВЗ", PVZ_GROUP_ID),
    "☎️ Связь с менеджером": ("ПВЗ", PVZ_GROUP_ID),
    "🏪 Отдел ПВЗ": ("ПВЗ", PVZ_GROUP_ID),

    "📍 Где мой заказ": ("Логистика", LOGISTICS_GROUP_ID),
    "🚚 Статус доставки": ("Логистика", LOGISTICS_GROUP_ID),
    "📦 Трек номер": ("Логистика", LOGISTICS_GROUP_ID),
    "❌ Проблема доставки": ("Логистика", LOGISTICS_GROUP_ID),
    "🚚 Логистика": ("Логистика", LOGISTICS_GROUP_ID),

    "🚀 Старт новичка": ("Обучение", TRAINING_GROUP_ID),
    "🎯 Маркетинг план": ("Обучение", TRAINING_GROUP_ID),
    "👥 Рекрутинг": ("Обучение", TRAINING_GROUP_ID),
    "📈 Построение команды": ("Обучение", TRAINING_GROUP_ID),
    "🎓 Академия Cordial Care": ("Обучение", TRAINING_GROUP_ID),
    "🎓 Отдел обучения": ("Обучение", TRAINING_GROUP_ID),

    "✨ ESROOM": ("Продукция", TRAINING_GROUP_ID),
    "🌿 WELLSEED": ("Продукция", TRAINING_GROUP_ID),
    "💙 Collagen Health & Beauty": ("Продукция", TRAINING_GROUP_ID),
    "🦴 Calcium Madi D3": ("Продукция", TRAINING_GROUP_ID),
    "📖 Инструкция применения": ("Продукция", TRAINING_GROUP_ID),
    "📄 Сертификаты": ("Продукция", TRAINING_GROUP_ID),
}

@dp.message(F.text.in_(REQUEST_ROUTES.keys()))
async def start_request(message: Message):
    department, group_id = REQUEST_ROUTES[message.text]

    user_states[message.from_user.id] = {
        "step": "waiting_partner_id",
        "department": department,
        "topic": message.text,
        "group_id": group_id,
    }

    await message.answer(
        f"Вы выбрали: {message.text}\n\n"
        "Введите ваш ID партнера:",
        reply_markup=BACK_MENU
    )

@dp.message()
async def handle_request_steps(message: Message):
    user_id = message.from_user.id
    state = user_states.get(user_id)

    if not state:
        await message.answer(
            "Пожалуйста, выберите раздел из меню.",
            reply_markup=MAIN_MENU
        )
        return

    if state["step"] == "waiting_partner_id":
        state["partner_id"] = message.text
        state["step"] = "waiting_problem"

        await message.answer(
            "Теперь подробно опишите ваш вопрос или проблему:"
        )
        return

    if state["step"] == "waiting_problem":
        problem = message.text
        department = state["department"]
        topic = state["topic"]
        group_id = state["group_id"]
        partner_id = state["partner_id"]

        username = message.from_user.username
        full_name = message.from_user.full_name
        date = datetime.now().strftime("%d.%m.%Y %H:%M")

        text = (
            "📨 Новая заявка\n\n"
            f"Отдел: {department}\n"
            f"Тема: {topic}\n"
            f"ID партнера: {partner_id}\n"
            f"Имя: {full_name}\n"
            f"Telegram: @{username if username else 'нет username'}\n"
            f"Дата: {date}\n\n"
            f"Вопрос:\n{problem}"
        )

        await bot.send_message(chat_id=group_id, text=text)

        await message.answer(
            "✅ Ваша заявка принята и отправлена в нужный отдел.\n\n"
            "Менеджер рассмотрит обращение и свяжется с вами.",
            reply_markup=MAIN_MENU
        )

        user_states.pop(user_id, None)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())