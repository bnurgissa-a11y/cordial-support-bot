import os
import asyncio
import logging
from datetime import datetime
import base64

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart, Command
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
tickets = {}
ticket_counter = 1000
ticket_messages = {}
user_languages = {}

MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🤖 AI-консультант"), KeyboardButton(text="📸 Анализ кожи")],
        [KeyboardButton(text="📚 Каталог продукции"), KeyboardButton(text="💎 Маркетинг-план")],
        [KeyboardButton(text="🧴 Подбор ухода"), KeyboardButton(text="🧲 Скрипты продаж")],
        [KeyboardButton(text="❓ Возражения клиентов")],
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
LANGUAGE_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🇰🇿 Қазақша")],
        [KeyboardButton(text="🇬🇧 English"), KeyboardButton(text="🇨🇳 中文")],
    ],
    resize_keyboard=True,
)

def submenu(buttons):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=b)] for b in buttons] + [[KeyboardButton(text="⬅️ Назад")]],
        resize_keyboard=True,
    )

async def ask_ai(user_id: int, question: str) -> str:
    lang = user_languages.get(user_id, "ru")

    language_instruction = {
        "ru": "Отвечай на русском языке.",
        "kk": "Қазақ тілінде жауап бер.",
        "en": "Answer in English.",
        "zh": "请用中文回答。",
    }.get(lang, "Отвечай на русском языке.")

    question = f"{language_instruction}\n\n{question}"
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
        "Выберите язык / Тілді таңдаңыз / Choose language / 请选择语言:",
        reply_markup=LANGUAGE_MENU
    )
@dp.message(F.text.in_(["🇷🇺 Русский", "🇰🇿 Қазақша", "🇬🇧 English", "🇨🇳 中文"]))
async def set_language(message: Message):
    lang_map = {
        "🇷🇺 Русский": "ru",
        "🇰🇿 Қазақша": "kk",
        "🇬🇧 English": "en",
        "🇨🇳 中文": "zh",
    }

    user_languages[message.from_user.id] = lang_map[message.text]

    texts = {
        "ru": "Добро пожаловать в Центр поддержки Cordial Care.",
        "kk": "Cordial Care қолдау орталығына қош келдіңіз.",
        "en": "Welcome to Cordial Care Support Center.",
        "zh": "欢迎来到 Cordial Care 支持中心。",
    }

    await message.answer(
        texts[user_languages[message.from_user.id]],
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

@dp.message(F.text == "📸 Анализ кожи")
async def skin_analysis_start(message: Message):
    user_states[message.from_user.id] = {
        "step": "waiting_skin_photo"
    }

    await message.answer(
        "📸 Загрузите фото лица.\n\n"
        "Требования:\n"
        "• хорошее освещение\n"
        "• лицо полностью видно\n"
        "• без фильтров\n"
        "• без очков"
    )
@dp.message(F.text == "📚 Каталог продукции")
async def catalog_ai(message: Message):
    await message.answer(
        "📚 Каталог продукции Cordial Care\n\n"
        "Напишите название продукта или вопрос.\n\n"
        "Примеры:\n"
        "• Цена коллагена\n"
        "• Состав Calcium Madi D3\n"
        "• Что такое Wellseed Banaba?\n"
        "• Расскажи про ESROOM Essence\n"
        "• Какие продукты подходят для кожи?"
    )

@dp.message(F.text == "💎 Маркетинг-план")
async def marketing_ai(message: Message):
    await message.answer(
        "💎 Маркетинг-план Cordial Care\n\n"
        "Напишите вопрос по маркетинг-плану.\n\n"
        "Примеры:\n"
        "• Как считается бинарный бонус?\n"
        "• Что такое реферальный бонус?\n"
        "• Как получить матчинг бонус?\n"
        "• Какие есть статусы?\n"
        "• Сделай расчет на примере"
    )

@dp.message(F.text == "🧴 Подбор ухода")
async def skincare_ai(message: Message):
    await message.answer(
        "🧴 Подбор ухода\n\n"
        "Опишите вашу ситуацию:\n"
        "• возраст\n"
        "• тип кожи\n"
        "• основная проблема\n"
        "• что уже используете\n\n"
        "Пример:\n"
        "Мне 35 лет, кожа сухая, есть пигментация и морщины. Что посоветуете?\n\n"
        "Для точного анализа нажмите 📸 Анализ кожи и загрузите фото."
    )

@dp.message(F.text == "🧲 Скрипты продаж")
async def scripts_ai(message: Message):
    await message.answer(
        "🧲 Скрипты продаж\n\n"
        "Напишите, какой скрипт нужен.\n\n"
        "Примеры:\n"
        "• Скрипт приглашения в бизнес\n"
        "• Скрипт для клиента на коллаген\n"
        "• Скрипт для косметолога\n"
        "• Сообщение для WhatsApp\n"
        "• Сторис для Instagram"
    )

@dp.message(F.text == "❓ Возражения клиентов")
async def objections_ai(message: Message):
    await message.answer(
        "❓ Работа с возражениями\n\n"
        "Напишите возражение клиента или партнера.\n\n"
        "Примеры:\n"
        "• Дорого\n"
        "• Я подумаю\n"
        "• Это пирамида?\n"
        "• У меня нет времени\n"
        "• Я не умею продавать"
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
    "📚 Каталог продукции",
    "💎 Маркетинг-план",
    "🧴 Подбор ухода",
    "🧲 Скрипты продаж",
    "❓ Возражения клиентов",
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
@dp.message(F.photo)
async def handle_skin_photo(message: Message):
    state = user_states.get(message.from_user.id)

    if not state or state.get("step") != "waiting_skin_photo":
        await message.answer(
            "Фото получено. Для анализа кожи сначала нажмите кнопку 📸 Анализ кожи."
        )
        return

    await message.answer("🔍 Фото получено. Анализирую кожу...")

    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_bytes = await bot.download_file(file.file_path)

    image_base64 = base64.b64encode(file_bytes.read()).decode("utf-8")

    prompt = """
Ты — skin-коуч Cordial Care. Сделай анализ кожи по фото.

Ответ строго по структуре:

1. Тип кожи:
2. Основные признаки:
3. Возможные проблемы:
4. Морщины:
5. Пигментация:
6. Поры:
7. Уровень увлажненности:
8. Что будет, если не ухаживать:
9. Утренний уход:
10. Вечерний уход:
11. Рекомендации Cordial Care:
12. Витамины и питание:

Важно:
- Не ставь медицинский диагноз.
- Не обещай лечение.
- Пиши на языке пользователя.
- Рекомендуй CellCure, ESROOM Essence, Eye Cream, SPF, Cushion.
- При необходимости рекомендуй Collagen Health & Beauty, Calcium Madi D3, Wellseed Omega 3, Wellseed Banaba.
"""

    try:
        response = await client.responses.create(
            model="gpt-4.1",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{image_base64}",
                        },
                    ],
                }
            ],
        )

        answer = response.output_text[:3900]

        await message.answer(answer, reply_markup=MAIN_MENU)

    except Exception as e:
        logging.exception(e)
        await message.answer(
            "Сейчас анализ фото временно недоступен. Попробуйте позже.",
            reply_markup=MAIN_MENU
        )

    user_states.pop(message.from_user.id, None)
    if message.chat.type == "private":
        await message.answer("Эта команда работает только в группе отдела.")
        return

    try:
        parts = message.text.split(maxsplit=2)

        if len(parts) < 3:
            await message.answer(
                "Неверный формат.\n\n"
                "Правильно:\n"
                "/answer 1001 Ваш ответ партнеру"
            )
            return

        ticket_id = int(parts[1])
        answer_text = parts[2]

        if ticket_id not in tickets:
            await message.answer("Заявка не найдена. Проверьте номер заявки.")
            return

        partner_user_id = tickets[ticket_id]["user_id"]

        await bot.send_message(
            partner_user_id,
            f"📩 Ответ службы поддержки Cordial Care\n\n"
            f"Заявка №{ticket_id}\n\n"
            f"{answer_text}"
        )

        await message.answer("✅ Ответ отправлен партнеру.")

    except Exception as e:
        await message.answer(f"Ошибка при отправке ответа: {e}")
@dp.message(Command("answer"))
async def answer_ticket(message: Message):
    if message.chat.type == "private":
        await message.answer("Эта команда работает только в группе отдела.")
        return

    parts = message.text.split(maxsplit=2)

    if len(parts) < 3:
        await message.answer(
            "Неверный формат.\n\n"
            "Правильно:\n"
            "/answer 1001 Ваш ответ партнеру"
        )
        return

    try:
        ticket_id = int(parts[1])
    except ValueError:
        await message.answer("Номер заявки должен быть числом.")
        return

    answer_text = parts[2]

    if ticket_id not in tickets:
        await message.answer(
            "Заявка не найдена.\n\n"
            "Важно: после перезапуска Render старые заявки забываются. "
            "Создайте новую заявку и ответьте на новый номер."
        )
        return

    partner_user_id = tickets[ticket_id]["user_id"]

    try:
        await bot.send_message(
            partner_user_id,
            f"📩 Ответ службы поддержки Cordial Care\n\n"
            f"Заявка №{ticket_id}\n\n"
            f"{answer_text}"
        )

        await message.answer("✅ Ответ отправлен партнеру.")

    except Exception as e:
        await message.answer(f"Не удалось отправить ответ партнеру: {e}")
@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    state = user_states.get(user_id)

    # Ответ менеджера на заявку через Reply в группе
    if message.chat.type != "private" and message.reply_to_message:
        replied_message_id = message.reply_to_message.message_id

        if replied_message_id in ticket_messages:
            ticket_id = ticket_messages[replied_message_id]

            if ticket_id not in tickets:
                await message.answer("Заявка не найдена. Возможно, бот перезапускался.")
                return

            partner_user_id = tickets[ticket_id]["user_id"]
            answer_text = message.text

            if not answer_text:
                await message.answer("Пока можно отправлять только текстовый ответ.")
                return

            await bot.send_message(
                partner_user_id,
                f"📩 Ответ службы поддержки Cordial Care\n\n"
                f"Заявка №{ticket_id}\n\n"
                f"{answer_text}"
            )

            await message.answer("✅ Ответ отправлен партнеру.")
            return

    # Ответ менеджера через команду /answer
    if message.text and message.text.startswith("/answer"):
        if message.chat.type == "private":
            await message.answer("Эта команда работает только в группе отдела.")
            return

        parts = message.text.split(maxsplit=2)

        if len(parts) < 3:
            await message.answer("Формат: /answer 1001 Ваш ответ партнеру")
            return

        try:
            ticket_id = int(parts[1])
        except ValueError:
            await message.answer("Номер заявки должен быть числом.")
            return

        answer_text = parts[2]

        if ticket_id not in tickets:
            await message.answer("Заявка не найдена. Создайте новую заявку после перезапуска.")
            return

        partner_user_id = tickets[ticket_id]["user_id"]

        await bot.send_message(
            partner_user_id,
            f"📩 Ответ службы поддержки Cordial Care\n\n"
            f"Заявка №{ticket_id}\n\n"
            f"{answer_text}"
        )

        await message.answer("✅ Ответ отправлен партнеру.")
        return

    # Создание заявки: шаг 1 — ID партнера
    if state:
        if state["step"] == "waiting_partner_id":
            state["partner_id"] = message.text
            state["step"] = "waiting_problem"
            await message.answer("Теперь подробно опишите ваш вопрос или проблему:")
            return

        # Создание заявки: шаг 2 — описание проблемы
        if state["step"] == "waiting_problem":
            problem = message.text
            department = state["department"]
            topic = state["topic"]
            group_id = state["group_id"]
            partner_id = state["partner_id"]

            global ticket_counter
            ticket_counter += 1
            ticket_id = ticket_counter

            tickets[ticket_id] = {
                "user_id": message.from_user.id,
                "partner_id": partner_id,
                "department": department,
                "topic": topic,
            }

            username = message.from_user.username
            full_name = message.from_user.full_name
            date = datetime.now().strftime("%d.%m.%Y %H:%M")

            text = (
                f"📨 Заявка #{ticket_id}\n\n"
                f"Отдел: {department}\n"
                f"Тема: {topic}\n"
                f"ID партнера: {partner_id}\n"
                f"Имя: {full_name}\n"
                f"Telegram: @{username if username else 'нет username'}\n"
                f"Дата: {date}\n\n"
                f"Вопрос:\n{problem}"
            )

            sent_message = await bot.send_message(chat_id=group_id, text=text)
            ticket_messages[sent_message.message_id] = ticket_id

            await message.answer(
                "✅ Ваша заявка принята и отправлена в нужный отдел.\n\n"
                "Менеджер рассмотрит обращение и свяжется с вами.",
                reply_markup=MAIN_MENU
            )

            user_states.pop(user_id, None)
            return

    # Все остальные сообщения идут в AI
    await message.answer("⏳ AI-консультант готовит ответ...")
    answer = await ask_ai(user_id, message.text)
    await message.answer(answer, reply_markup=MAIN_MENU)
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())