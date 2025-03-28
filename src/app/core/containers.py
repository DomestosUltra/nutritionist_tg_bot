import httpx
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from redis.asyncio import Redis
from dependency_injector import containers, providers

from openai import AsyncOpenAI

from src.app.core.config import settings
from src.app.integrations.redis import RedisService
from src.app.integrations.llm.openai import OpenaiService
from src.app.integrations.llm.yandexgpt import YandexService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.tests",
            "src.app.integrations.rmq.consumer",
            "src.app.bot.handlers.messages_handler",
            "src.app.bot.handlers.command_handler",
            "src.app.services.bot_functions",
        ]
    )

    config = providers.Configuration()

    redis_client = providers.Factory(
        Redis,
        host=settings.redis.REDIS_HOST,
        port=settings.redis.REDIS_PORT,
    )

    redis_service = providers.Factory(
        RedisService,
        redis_client=redis_client,
    )

    http_client_factory = providers.Factory(
        httpx.AsyncClient,
        verify=False
    )

    openai_client = providers.Factory(
        AsyncOpenAI,
        api_key=settings.openai.OPENAI_API_KEY,
        base_url=settings.openai.OPENAI_BASE_URL,
        http_client=http_client_factory,
    )

    openai_service = providers.Factory(
        OpenaiService,
        llm_client=openai_client,
        model=settings.openai.OPENAI_DEFAULT_MODEL,
    )

    bot = providers.Factory(
        Bot,
        token=settings.bot.TOKEN,
        default = providers.Factory(
            DefaultBotProperties, parse_mode=ParseMode.HTML
        ),
    )

    yandex_service = providers.Factory(
        YandexService,
        api_key=settings.yandex.YANDEX_API_KEY,
        folder_id=settings.yandex.YANDEX_FOLDER_ID,
        model_name=settings.yandex.YANDEX_DEFAULT_MODEL,
    )

    dispatcher = providers.Factory(
        Dispatcher, storage=providers.Factory(MemoryStorage)
    )


class TestContainer(Container):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.tests",
            "src.app.integrations.rmq.consumer",
            "src.app.bot.handlers.messages_handler",
            "src.app.bot.handlers.command_handler",
            "src.app.services.bot_functions",
        ]
    )

    config = providers.Configuration()

    redis_client = providers.Factory(
        Redis,
        host=config.redis.host,
        port=config.redis.port,
    )

    redis_service = providers.Factory(
        RedisService,
        redis_client=redis_client,
    )
