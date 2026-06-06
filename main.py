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
    raise RuntimeError("BOT_TOKEN is missing. Add it to .env or Render Variables")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

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

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Добро пожаловать в Центр поддержки Cordial Care.\n\n"
        "Выберите необходимый раздел:",
        reply_markup=MAIN_MENU
    )

@dp.message(F.text == "⬅️ Назад")
async def back(message: Message):
    await message.answer("Вы вернулись в главное меню:", reply_markup=MAIN_MENU)

@dp.message(F.text == "📦 Заказы")
async def orders(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Проверить заказ")],
            [KeyboardButton(text="❌ Отмена заказа")],
            [KeyboardButton(text="🔄 Изменить заказ")],
            [KeyboardButton(text="📋 История заказов")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Раздел: 📦 Заказы", reply_markup=kb)

@dp.message(F.text == "💰 Бонусы")
async def bonuses(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💵 Не начислились бонусы")],
            [KeyboardButton(text="📈 Как считается бонус")],
            [KeyboardButton(text="🎁 Реферальный бонус")],
            [KeyboardButton(text="🔷 Бинарный бонус")],
            [KeyboardButton(text="👥 Матчинг бонус")],
            [KeyboardButton(text="🏆 Структурный бонус")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Раздел: 💰 Бонусы", reply_markup=kb)

@dp.message(F.text == "👥 Регистрация")
async def registration(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🆔 Проблема с регистрацией")],
            [KeyboardButton(text="🔑 Не могу войти")],
            [KeyboardButton(text="📱 Смена телефона")],
            [KeyboardButton(text="📧 Смена почты")],
            [KeyboardButton(text="👤 Изменение данных")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Раздел: 👥 Регистрация", reply_markup=kb)

@dp.message(F.text == "🏪 ПВЗ")
async def pvz(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 Остатки товара")],
            [KeyboardButton(text="🚚 Поставка товара")],
            [KeyboardButton(text="🔄 Возврат товара")],
            [KeyboardButton(text="📄 Документы ПВЗ")],
            [KeyboardButton(text="🏪 Открытие ПВЗ")],
            [KeyboardButton(text="☎️ Связь с менеджером")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Раздел: 🏪 ПВЗ", reply_markup=kb)

@dp.message(F.text == "🚚 Доставка")
async def delivery(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Где мой заказ")],
            [KeyboardButton(text="🚚 Статус доставки")],
            [KeyboardButton(text="📦 Трек номер")],
            [KeyboardButton(text="❌ Проблема доставки")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Раздел: 🚚 Доставка", reply_markup=kb)

@dp.message(F.text == "💄 Продукция")
async def products(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✨ ESROOM")],
            [KeyboardButton(text="🌿 WELLSEED")],
            [KeyboardButton(text="💙 Collagen Health & Beauty")],
            [KeyboardButton(text="🦴 Calcium Madi D3")],
            [KeyboardButton(text="📖 Инструкция применения")],
            [KeyboardButton(text="📄 Сертификаты")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Раздел: 💄 Продукция", reply_markup=kb)

@dp.message(F.text == "🎓 Обучение")
async def education(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 Старт новичка")],
            [KeyboardButton(text="🎯 Маркетинг план")],
            [KeyboardButton(text="👥 Рекрутинг")],
            [KeyboardButton(text="📈 Построение команды")],
            [KeyboardButton(text="🎓 Академия Cordial Care")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Раздел: 🎓 Обучение", reply_markup=kb)

@dp.message(F.text == "📄 Документы")
async def documents(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Маркетинг план PDF")],
            [KeyboardButton(text="📄 Политика компании")],
            [KeyboardButton(text="🏪 Регламент ПВЗ")],
            [KeyboardButton(text="🎁 Условия акций")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Раздел: 📄 Документы", reply_markup=kb)

@dp.message(F.text == "☎️ Связаться с офисом")
async def office(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💰 Финансовый отдел")],
            [KeyboardButton(text="📦 Отдел заказов")],
            [KeyboardButton(text="🚚 Логистика")],
            [KeyboardButton(text="🏪 Отдел ПВЗ")],
            [KeyboardButton(text="🎓 Обучение")],
            [KeyboardButton(text="📞 Заказать звонок")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Выберите отдел офиса:", reply_markup=kb)

@dp.message()
async def fallback(message: Message):
    await message.answer(
        "Ваш запрос принят.\n\n"
        "На следующем этапе мы подключим создание заявок для офиса.\n"
        "Пока выберите нужный раздел из меню.",
        reply_markup=MAIN_MENU
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())