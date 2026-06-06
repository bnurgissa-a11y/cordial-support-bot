import os
import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing")
if not ASSISTANT_ID:
    raise RuntimeError("ASSISTANT_ID is missing")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

ORDERS_GROUP_ID = -5034159641
FINANCE_GROUP_ID = -5012459213
LOGISTICS_GROUP_ID = -5175392722
PVZ_GROUP_ID = -5023952843
TRAINING_GROUP_ID = -5236071492

user_states = {}
user_threads = {}

MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🤖 AI-консультант")],
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

async def ask_ai(user_id: int, question: str) -> str:
    if user_id not in user_threads:
        thread = await client.beta.threads.create()
        user_threads[user_id] = thread.id

    thread_id = user_threads[user_id]

    await client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=question
    )

    run = await client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=ASSISTANT_ID
    )

    while run.status in ["queued", "in_progress", "cancelling"]:
        await asyncio.sleep(1)
        run = await client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )

    if run.status != "completed":
        return "Сейчас AI-консультант временно недоступен. Попробуйте позже."

    messages = await client.beta.threads.messages.list(thread_id=thread_id)
    latest = messages.data[0]

    answer = ""
    for content in latest.content:
        if content.type == "text":
            answer += content.text.value

    return answer[:3900]

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Добро пожаловать в Центр поддержки Cordial Care.\n\n"
        "Выберите раздел или просто напишите вопрос AI-консультанту:",
        reply_markup=MAIN_MENU
    )

@dp.message(F.text == "⬅️ Назад")
async def back(message: Message):
    user_states.pop(message.from_user.id, None)
    await message.answer("Вы вернулись в главное меню:", reply_markup=MAIN_MENU)

@dp.message(F.text == "🤖 AI-консультант")
async def ai_intro(message: Message):
    await message.answer(
        "Напишите ваш вопрос.\n\n"
        "Например:\n"
        "• Как принимать Calcium Madi D3?\n"
        "• Как считается бинарный бонус?\n"
        "• Что лучше для сухой кожи?\n"
        "• Напиши скрипт для приглашения в бизнес."
    )

@dp.message(F.text == "📦 Заказы")
async def orders(message: Message):
    await message.answer("Раздел: 📦 Заказы", reply_markup=submenu([
        "🛒 Проверить заказ",
        "❌ Отмена заказа",
        "🔄 Изменить заказ",
        "📋 История заказов",
    ]))

@dp.message(F.text == "💰 Бонусы")
async def bonuses(message: Message):
    await message.answer("Раздел: 💰 Бонусы", reply_markup=submenu([
        "💵 Не начислились бонусы",
        "📈 Как считается бонус",
        "🎁 Реферальный бонус",
        "🔷 Бинарный бонус",
        "👥 Матчинг бонус",
        "🏆 Структурный бонус",
    ]))

@dp.message(F.text == "👥 Регистрация")
async def registration(message: Message):
    await message.answer("Раздел: 👥 Регистрация", reply_markup=submenu([
        "🆔 Проблема с регистрацией",
        "🔑 Не могу войти",
        "📱 Смена телефона",
        "📧 Смена почты",
        "👤 Изменение данных",
    ]))

@dp.message(F.text == "🏪 ПВЗ")
async def pvz(message: Message):
    await message.answer("Раздел: 🏪 ПВЗ", reply_markup=submenu([
        "📦 Остатки товара",
        "🚚 Поставка товара",
        "🔄 Возврат товара",
        "📄 Документы ПВЗ",
        "🏪 Открытие ПВЗ",
        "☎️ Связь с менеджером",
    ]))

@dp.message(F.text == "🚚 Доставка")
async def delivery(message: Message):
    await message.answer("Раздел: 🚚 Доставка", reply_markup=submenu([
        "📍 Где мой заказ",
        "🚚 Статус доставки",
        "📦 Трек номер",
        "❌ Проблема доставки",
    ]))

@dp.message(F.text == "💄 Продукция")
async def products(message: Message):
    await message.answer("Раздел: 💄 Продукция", reply_markup=submenu([
        "✨ ESROOM",
        "🌿 WELLSEED",
        "💙 Collagen Health & Beauty",
        "🦴 Calcium Madi D3",
        "📖 Инструкция применения",
        "📄 Сертификаты",
    ]))

@dp.message(F.text == "🎓 Обучение")
async def education(message: Message):
    await message.answer("Раздел: 🎓 Обучение", reply_markup=submenu([
        "🚀 Старт новичка",
        "🎯 Маркетинг план",
        "👥 Рекрутинг",
        "📈 Построение команды",
        "🎓 Академия Cordial Care",
    ]))

@dp.message(F.text == "📄 Документы")
async def documents(message: Message):
    await message.answer("Раздел: 📄 Документы", reply_markup=submenu([
        "📋 Маркетинг план PDF",
        "📄 Политика компании",
        "🏪 Регламент ПВЗ",
        "🎁 Условия акций",
    ]))

@dp.message(F.text == "☎️ Связаться с офисом")
async def office(message: Message):
    await message.answer("Выберите отдел офиса:", reply_markup=submenu([
        "💰 Финансовый отдел",
        "📦 Отдел заказов",
        "🚚 Логистика",
        "🏪 Отдел ПВЗ",
        "🎓 Отдел обучения",
    ]))

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

    "🎓 Отдел обучения": ("Обучение", TRAINING_GROUP_ID),
}

AI_TOPICS = {
    "📈 Как считается бонус",
    "🎁 Реферальный бонус",
    "🔷 Бинарный бонус",
    "👥 Матчинг бонус",
    "🏆 Структурный бонус",
    "✨ ESROOM",
    "🌿 WELLSEED",
    "💙 Collagen Health & Beauty",
    "🦴 Calcium Madi D3",
    "📖 Инструкция применения",
    "📄 Сертификаты",
    "🚀 Старт новичка",
    "🎯 Маркетинг план",
    "👥 Рекрутинг",
    "📈 Построение команды",
    "🎓 Академия Cordial Care",
    "📋 Маркетинг план PDF",
    "📄 Политика компании",
    "🏪 Регламент ПВЗ",
    "🎁 Условия акций",
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

@dp.message(F.text.in_(AI_TOPICS))
async def ai_topic_answer(message: Message):
    await message.answer("⏳ AI-консультант готовит ответ...")
    answer = await ask_ai(
        message.from_user.id,
        f"Ответь как Cordial AI Consultant по теме: {message.text}"
    )
    await message.answer(answer, reply_markup=MAIN_MENU)

@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    state = user_states.get(user_id)

    if state:
        if state["step"] == "waiting_partner_id":
            state["partner_id"] = message.text
            state["step"] = "waiting_problem"
            await message.answer("Теперь подробно опишите ваш вопрос или проблему:")
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
            return

    await message.answer("⏳ AI-консультант готовит ответ...")
    answer = await ask_ai(user_id, message.text)
    await message.answer(answer, reply_markup=MAIN_MENU)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())