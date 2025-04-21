import re
import json
import asyncio
import logging
import aio_pika

from typing import Dict
from aiogram import Bot
from logging.config import dictConfig
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.utils.log_config import LogConfig
from src.app.core.config import settings
from src.app.core.containers import Container
from src.app.integrations.redis import RedisService
from src.app.integrations.llm.openai import OpenaiService
from src.app.integrations.llm.yandexgpt import YandexService
from src.app.core.prompts import SYSTEM_PROMPT
from src.app.bot.main import bot
from src.app.utils.general import (
    convert_to_allowed_tags,
)
from src.app.db.session import async_session
from src.app.db.crud import get_user_interactions, update_interaction_response


log_config = LogConfig()
log_config_dict = log_config.model_dump()
dictConfig(log_config_dict)

logger = logging.getLogger(__name__)


class BaseTaskHandler:
    async def handle(self, task: dict):
        raise NotImplementedError


class LLMTaskHandler(BaseTaskHandler):
    def __init__(
        self,
        redis_service: RedisService,
        openai_service: OpenaiService,
        yandex_service: YandexService,
        bot: Bot,
    ) -> None:
        self.redis_service = redis_service
        self.openai_service = openai_service
        self.yandex_service = yandex_service
        self.bot = bot

    async def handle(self, task: Dict) -> None:
        task_id = task.get("task_id")
        user_id = task.get("user_id")
        chat_id = task.get("chat_id")
        user_query = task.get("user_query")
        model = task.get("model")
        waiting_message_id: int = int(task.get("waiting_message_id"))

        try:
            if model == "chatgpt":
                llm_service = self.openai_service
            elif model == "yandexgpt":
                llm_service = self.yandex_service
            else:
                raise ValueError(f"Unknown model: {model}")

            await self.redis_service.set(
                f"task:{user_id}:status", "processing", ex=60
            )

            response_text: str = await llm_service.get_response(
                user_query, system_prompt=SYSTEM_PROMPT
            )

            html_response_text = convert_to_allowed_tags(response_text)
            await self.bot.delete_message(
                chat_id=chat_id, message_id=waiting_message_id
            )
            await self.redis_service.set(f"task:{user_id}:status", "completed")
            await self.bot.send_message(
                text=html_response_text,
                chat_id=chat_id,
                parse_mode=ParseMode.HTML,
            )

            await self.redis_service.set(
                f"task:{task_id}:response", response_text, ex=60
            )

            # Save the bot response to the database
            try:
                async with async_session() as db:
                    # Get the latest interaction for this user
                    user_interactions = await get_user_interactions(
                        db=db, user_id=user_id, limit=1
                    )
                    if user_interactions:
                        # Update the most recent interaction with the bot's response
                        latest_interaction = user_interactions[0]
                        await update_interaction_response(
                            db=db,
                            interaction_id=latest_interaction.id,
                            bot_response=response_text,
                        )
                        logger.info(
                            f"Updated interaction record for user {user_id} with bot response"
                        )
                    else:
                        logger.warning(
                            f"No recent interaction found for user {user_id}"
                        )
            except Exception as db_error:
                logger.error(
                    f"Failed to save bot response to database: {db_error}"
                )

        except Exception as e:
            logger.error(f"Ошибка при обработке задачи {task_id}: {e}")
            await self.redis_service.set(f"task:{task_id}:status", "failed")


TASK_HANDLERS: Dict[str, BaseTaskHandler] = {
    "llm_task": LLMTaskHandler(
        redis_service=Container.redis_service(),
        openai_service=Container.openai_service(),
        yandex_service=Container.yandex_service(),
        bot=bot,
    ),
}


async def on_message(message: aio_pika.IncomingMessage):
    async with message.process():
        task = json.loads(message.body)

        task_type = task.get("type")
        handler = TASK_HANDLERS.get(task_type)

        if handler:
            asyncio.create_task(handler.handle(task))
            logger.info(f"Task scheduled: {task_type}")
        else:
            logger.info(f"Unknown task type: {task_type}")


async def consumer():
    connection = await aio_pika.connect_robust(
        f"amqp://{settings.rabbit.RABBITMQ_USER}:{settings.rabbit.RABBITMQ_PASS}@rabbitmq/"
    )
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)
    queue = await channel.declare_queue("task_queue", durable=True)
    await queue.consume(on_message)
    await asyncio.Future()


if __name__ == "__main__":
    from src.app.core.containers import Container
    from src.app.core.config import settings

    container = Container()
    container.config.from_pydantic(settings)
    container.wire(
        modules=[
            "src.app.integrations.rmq.consumer",
            "src.app.bot.handlers.messages_handler",
            "src.app.bot.handlers.command_handler",
            "src.app.services.bot_functions",
            "src.app.db.crud",
        ]
    )

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(consumer())
    except RuntimeError:
        asyncio.run(consumer())  # Безопасный запуск
