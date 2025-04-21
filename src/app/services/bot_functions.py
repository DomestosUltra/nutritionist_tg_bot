import logging
from fastapi import Depends
from dependency_injector.wiring import inject, Provide
from sqlalchemy.ext.asyncio import AsyncSession


from src.app.integrations.redis import RedisService
from src.app.core.containers import Container
from src.app.core.config import settings
from src.app.db.session import get_db
from src.app.db.crud import create_user_interaction


logger = logging.getLogger(__name__)


@inject
async def check_rate_limit(
    user_id: str,
    redis_service: RedisService = Depends(Provide[Container.redis_service]),
) -> bool:
    key = f"tg_user:{user_id}:msg_count"
    try:
        count = await redis_service.get(key)
        logger.info(f"Проверка лимита для user_id {user_id}: count = {count}")

        if count is None:
            await redis_service.set(key, "1", ex=60)
            logger.info(f"Установлен новый счётчик для user_id {user_id}: 1")
            return True
        else:
            count = int(count)
            if count >= settings.bot.MAX_MESSAGES_PER_MINUTE:
                logger.info(
                    f"Лимит превышен для user_id {user_id}: {count} >= {settings.bot.MAX_MESSAGES_PER_MINUTE}"
                )
                return False
            else:
                new_count = count + 1
                await redis_service.set(key, str(new_count), ex=60)
                logger.info(
                    f"Счётчик увеличен для user_id {user_id}: {new_count}"
                )
                return True
    except ValueError:
        logger.error(
            f"Некорректное значение счётчика для user_id {user_id}: {count}"
        )
        return False
    except Exception as e:
        logger.error(f"Ошибка Redis для user_id {user_id}: {e}")
        return True  # Разрешаем запрос, если Redis недоступен


@inject
async def is_first_start(
    user_id: str,
    redis_service: RedisService = Depends(Provide[Container.redis_service]),
) -> bool:
    key = f"tg_user:{user_id}"
    user = await redis_service.get(key)
    if user is None:
        await redis_service.set(key, value="False")
        return True

    return False


@inject
async def set_model(
    user_id: str,
    model_name: str,
    redis_service: RedisService = Depends(Provide[Container.redis_service]),
) -> None:
    key = f"tg_user:{user_id}:model"
    await redis_service.set(key, value=model_name)


@inject
async def get_model(
    user_id: str,
    redis_service: RedisService = Depends(Provide[Container.redis_service]),
) -> str | None:
    key = f"tg_user:{user_id}:model"
    model = await redis_service.get(key)
    return model if model else None


@inject
async def is_response_processing(
    user_id: str,
    redis_service: RedisService = Depends(Provide[Container.redis_service]),
) -> str:
    key = f"task:{user_id}:status"
    status = await redis_service.get(key)
    if not status or status == "completed":
        return False
    return True


@inject
async def log_interaction(
    user_id: int,
    username: str,
    message_text: str,
    response_text: str,
    db: AsyncSession = Depends(get_db),
):
    # Log to console
    logger.info(f"{user_id}||{username}||{message_text}||{response_text}")

    # Save to database
    try:
        await create_user_interaction(
            db=db,
            user_id=str(user_id),
            username=username,
            user_query=message_text,
            bot_response=response_text,
        )
        logger.info(f"User interaction saved to database: user_id={user_id}")
    except Exception as e:
        logger.error(f"Failed to save user interaction to database: {e}")
