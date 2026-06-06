import asyncio
import logging
import os
from datetime import datetime
from typing import Dict

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing. Add it to .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

CATEGORY_TO_CHAT: Dict[str, int] = {
    "orders": int(os.getenv("LOGISTICS_CHAT_ID", os.getenv("DEFAULT_MANAGER_CHAT_ID", "0"))),
    "bonuses": int(os.getenv("FINANCE_CHAT_ID", os.getenv("DEFAULT_MANAGER_CHAT_ID", "0"))),
    "registration": int(os.getenv("REGISTRATION_CHAT_ID", os.getenv("DEFAULT_MANAGER_CHAT_ID", "0"))),
    "delivery": int(os.getenv("LOGISTICS_CHAT_ID", os.getenv("DEFAULT_MANAGER_CHAT_ID", "0"))),
    "pvz": int(os.getenv("PVZ_CHAT_ID", os.getenv("DEFAULT_MANAGER_CHAT_ID", "0"))),
    "documents": int(os.getenv("DEFAULT_MANAGER_CHAT_ID", "0")),
    "products": int(os.getenv("PRODUCT_CHAT_ID", os.getenv("DEFAULT_MANAGER_CHAT_ID", "0"))),
    "training": int(os.getenv("TRAINING_CHAT_ID", os.getenv("DEFAULT_MANAGER_CHAT_ID", "0"))),
}

CATEGORY_LABELS = {
    "orders": "📦 Заказы",
    "bonuses": "💰 Бонусы / начисления",
    "registration": "👥 Регистрация / кабинет",
    "delivery": "🚚 Доставка",
    "pvz": "🏪 ПВЗ",
    "documents": "📄 Документы",
    "products": "💄 Продукция",
    "training": "🎓 Обучение",
}

FAQ = {
    "pvz": "🏪 ПВЗ: напишите город, адрес ПВЗ, ФИО оператора и суть вопроса. Например: прием товара, остатки, возврат, ошибка выдачи.",
    "bonuses": "💰 Бонусы: укажите ID партнера, период, сумму/баллы и что именно не совпадает.",
    "orders": "📦 Заказы: укажите номер заказа, дату, ФИО клиента и проблему.",
    "registration": "👥 Регистрация: укажите ID/телефон партнера и опишите ошибку.",
}

class TicketForm(StatesGroup):
    waiting_for_text = State()


def main_menu():
    kb = InlineKeyboardBuilder()
    for key, label in CATEGORY_LABELS.items():
        kb.button(text=label, callback_data=f"cat:{key}")
    kb.adjust(2)
    return kb.as_markup()


def back_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Главное меню", callback_data="menu")
    return kb.as_markup()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Ассалаумағалейкум! Это Cordial Support Bot.\n\n"
        "Выберите раздел, по которому нужна помощь:",
        reply_markup=main_menu(),
    )


@dp.message(Command("menu"))
async def menu_command(message: Message):
    await message.answer("Выберите нужный раздел:", reply_markup=main_menu())


@dp.callback_query(F.data == "menu")
async def menu_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Выберите нужный раздел:", reply_markup=main_menu())
    await callback.answer()


@dp.callback_query(F.data.startswith("cat:"))
async def choose_category(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split(":", 1)[1]
    await state.update_data(category=category)
    await state.set_state(TicketForm.waiting_for_text)

    faq_text = FAQ.get(category, "Опишите вопрос максимально конкретно: ID, ФИО, номер заказа, дата, сумма, скриншот при необходимости.")

    await callback.message.edit_text(
        f"Вы выбрали: {CATEGORY_LABELS.get(category, category)}\n\n"
        f"{faq_text}\n\n"
        "Теперь напишите ваш вопрос одним сообщением.",
        reply_markup=back_menu(),
    )
    await callback.answer()


@dp.message(TicketForm.waiting_for_text)
async def receive_ticket(message: Message, state: FSMContext):
    data = await state.get_data()
    category = data.get("category", "default")
    target_chat_id = CATEGORY_TO_CHAT.get(category, int(os.getenv("DEFAULT_MANAGER_CHAT_ID", "0")))

    user = message.from_user
    ticket_id = f"CC-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{user.id}"

    ticket_text = (
        f"🆕 Новая заявка: {ticket_id}\n\n"
        f"Категория: {CATEGORY_LABELS.get(category, category)}\n"
        f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        f"Отправитель:\n"
        f"ID Telegram: {user.id}\n"
        f"Имя: {user.full_name}\n"
        f"Username: @{user.username if user.username else 'нет'}\n\n"
        f"Текст заявки:\n{message.text}\n\n"
        f"Статус: новая"
    )

    if target_chat_id == 0:
        await message.answer(
            "Заявка принята, но не настроен чат отдела. Сообщите администратору: DEFAULT_MANAGER_CHAT_ID не указан.",
            reply_markup=main_menu(),
        )
        await state.clear()
        return

    try:
        await bot.send_message(chat_id=target_chat_id, text=ticket_text)
        await message.answer(
            f"✅ Ваша заявка принята.\n\nНомер заявки: {ticket_id}\nОтветственный отдел получил обращение.",
            reply_markup=main_menu(),
        )
    except Exception as e:
        logging.exception("Failed to send ticket")
        await message.answer(
            "Не удалось отправить заявку в отдел. Проверьте, что бот добавлен в группу и имеет права администратора.",
            reply_markup=main_menu(),
        )

    await state.clear()


@dp.message()
async def fallback(message: Message):
    await message.answer(
        "Я помогу оформить заявку. Выберите раздел:",
        reply_markup=main_menu(),
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
