import logging
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, BotCommand

from src.app.bot.keyboards.main_keyboards import get_model_keyboard

from src.app.services.bot_functions import (
    log_interaction,
    is_first_start,
)

from src.app.db.crud import create_user_interaction
from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger(__name__)

router = Router(name="Commands")


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запуск бота"),
        BotCommand(command="model", description="Выбрать модель GPT"),
        BotCommand(command="help", description="Справка по командам"),
    ]
    await bot.set_my_commands(commands)


@router.message(Command("start"))
async def cmd_start(message: Message, db: AsyncSession):
    response_text = "*Привет\! 👋*\nЯ – бот\-диетолог, готов помочь тебе улучшить питание и здоровье\!"
    await message.answer(response_text)

    start = await is_first_start(message.from_user.id)
    if start:
        await message.answer(
            "_Выбери модель для начала работы:_",
            reply_markup=get_model_keyboard(),
        )

    await log_interaction(
        message.from_user.id,
        message.from_user.username or "",
        "/start",
        "Приветствие отправлено.",
    )

    # Log interaction in the database
    await create_user_interaction(
        db,
        message.from_user.id,
        message.from_user.username or "",
        "/start",
        response_text,
    )


@router.message(Command("model"))
async def cmd_model(message: Message, db: AsyncSession):
    response_text = "*Выбор модели* 🤖\nПожалуйста, выбери одну из доступных моделей для получения рекомендаций:"
    await message.answer(response_text, reply_markup=get_model_keyboard())

    await log_interaction(
        message.from_user.id,
        message.from_user.username or "",
        "/model",
        "Изменена модель.",
    )

    # Log interaction in the database
    await create_user_interaction(
        db,
        message.from_user.id,
        message.from_user.username or "",
        "/model",
        response_text,
    )


@router.message(Command("help"))
async def cmd_help(message: Message, db: AsyncSession):
    help_text = (
        "*Справка* ℹ️\n\n"
        "*Доступные команды:*\n"
        "`/start` — запуск бота\n"
        "`/model` — выбор модели для ответа\n"
        "`/help` — справка по командам\n\n"
        "Для получения персональных рекомендаций просто отправь свой запрос\!\n"
    )
    await message.answer(help_text)

    await log_interaction(
        message.from_user.id,
        message.from_user.username or "",
        "/help",
        help_text,
    )

    # Log interaction in the database
    await create_user_interaction(
        db,
        message.from_user.id,
        message.from_user.username or "",
        "/help",
        help_text,
    )
