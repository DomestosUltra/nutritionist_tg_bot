import logging
import asyncio
from logging.config import dictConfig
from contextlib import asynccontextmanager

from fastapi import status, FastAPI, Request, Depends
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from dependency_injector.wiring import inject, Provide

from src.app.core.config import create_app, settings
from src.app.core.containers import Container
from src.app.utils.log_config import LogConfig
from src.app.bot.handlers import command_handler, messages_handler

from src.app.bot.main import bot, dp
from src.app.bot.handlers.command_handler import set_bot_commands

logging.getLogger("uvicorn").handlers.clear()

log_config = LogConfig()
log_config_dict = log_config.model_dump()
log_config_dict["version"] = log_config.version

dictConfig(log_config_dict)

logger = logging.getLogger(__name__)


container = Container()
container.config.from_pydantic(settings)

container.wire(
    modules=[
        __name__,
        "src.app.integrations.rmq.consumer",
        "src.app.bot.handlers.messages_handler",
        "src.app.bot.handlers.command_handler",
        "src.app.services.bot_functions",
    ]
)


@asynccontextmanager
@inject
async def lifespan(
    app: FastAPI,
):
    dp.include_router(command_handler.router)
    dp.include_router(messages_handler.router)

    await set_bot_commands(bot)

    full_webhook_url = settings.bot.WEBHOOK_URL
    logger.info(f"Setting webhook to: {full_webhook_url}")

    await bot.set_webhook(
        url=full_webhook_url,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True,
    )

    yield

    await bot.delete_webhook()


app = create_app(settings, lifespan)
app.container = container


@app.get("/ping")
async def root():
    return {
        "status_code": status.HTTP_200_OK,
        "message": "pong",
    }


@app.post("/webhook/telegram/")
async def webhook_handler(
    request: Request,
):
    try:
        update = Update.model_validate(
            await request.json(), context={"bot": bot}
        )
        await dp.feed_update(bot, update)
        return {"ok": True}
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}, 500


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
