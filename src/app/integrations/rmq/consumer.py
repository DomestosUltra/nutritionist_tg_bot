import asyncio
import json
import base64
import logging
import aio_pika

from typing import Dict, Union
from aiogram import Bot
from logging.config import dictConfig

from src.app.utils.log_config import LogConfig
from src.app.core.config import settings
from src.app.core.containers import Container
from src.app.integrations.redis import RedisService
from src.app.integrations.llm.openai import OpenaiService
from src.app.integrations.llm.yandexgpt import YandexService
from src.app.bot.main import bot


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
                f"task:{user_id}:status", "processing"
            )

            response_text = await llm_service.get_response(
                user_query, system_prompt="Ты - профессиональный помощник."
            )

            await self.bot.delete_message(
                chat_id=chat_id, message_id=waiting_message_id
            )
            await self.bot.send_message(text=response_text, chat_id=chat_id)

            await self.redis_service.set(f"task:{user_id}:status", "completed")
            await self.redis_service.set(
                f"task:{task_id}:response", response_text, ex=60
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
        ]
    )

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(consumer())
    except RuntimeError:
        asyncio.run(consumer())  # Безопасный запуск
