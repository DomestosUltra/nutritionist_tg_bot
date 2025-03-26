import uuid
import logging
from datetime import datetime
from fastapi import Depends
from aiogram import Router, F
from aiogram.types import Message
from dependency_injector.wiring import inject, Provide
from aiogram.types import (
    Message,
    CallbackQuery,
)

from src.app.integrations.redis import RedisService
from src.app.core.containers import Container
from src.app.integrations.rmq.publisher import publish_to_queue

from src.app.bot.keyboards.main_keyboards import get_model_keyboard
from src.app.services.bot_functions import (
    log_interaction,
    check_rate_limit,
    set_model,
    get_model,
    is_response_processing,
)

logger = logging.getLogger(__name__)


router = Router(name="Messages")


@router.callback_query(F.data.startswith("model_"))
async def model_selection(callback: CallbackQuery):
    model: str = callback.data.split("_")[1]

    if model == "chatgpt":
        str_model = "ChatGPT"
    elif model == "yandexgpt":
        str_model = "YandexGPT"
    else:
        return

    await set_model(callback.from_user.id, model)
    await callback.message.answer(
        f"Вы выбрали модель: {str_model}. Теперь введите ваш запрос."
    )

    await log_interaction(
        callback.from_user.id,
        callback.from_user.username or "",
        f"Выбор модели {model}",
        f"Модель {model} выбрана.",
    )


@router.message()
@inject
async def handle_message(
    message: Message,
    redis_service: RedisService = Depends(Provide[Container.redis_service]),
):
    if not await check_rate_limit(message.from_user.id):
        await message.answer(
            "Слишком много запросов. Пожалуйста, подождите немного."
        )
        return

    user_id: str = str(message.from_user.id)
    chat_id: str = str(message.chat.id)
    user_query: str = str(message.text)
    model: str = await get_model(user_id)

    if isinstance(model, bytes):
        model = model.decode("utf-8")
    elif model is None:
        await message.answer(
            "Выбери модель:",
            reply_markup=get_model_keyboard(),
        )
        return

    # if await is_response_processing(user_id):
    #     await message.answer("В процессе обработке. Отправьте запрос после ответа бота.")
    #     return

    waiting_message = await message.answer("Ожидайте ответ.")
    waiting_message_id = waiting_message.message_id

    task = {
        "type": "llm_task",
        "task_id": str(uuid.uuid4()),
        "user_id": user_id,
        "chat_id": chat_id,
        "user_query": str(message.text),
        "model": str(model) if model else None,
        "waiting_message_id": waiting_message_id,
        "timestamp": datetime.now().isoformat(),
    }

    logger.debug(f"Prepared task: {task}")
    await publish_to_queue(task)

    await log_interaction(
        message.from_user.id,
        message.from_user.username or "",
        user_query,
        response_text="",
    )
