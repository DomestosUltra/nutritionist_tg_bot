import json
import logging
import asyncio
import aio_pika

from src.app.core.config import settings

import json
from uuid import UUID
from datetime import datetime
from typing import Any


logger = logging.getLogger(__name__)


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, bytes):
            return obj.decode("utf-8")
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


async def publish_to_queue(message: dict):
    try:
        connection = await aio_pika.connect_robust(
            f"amqp://{settings.rabbit.RABBITMQ_USER}:{settings.rabbit.RABBITMQ_PASS}@rabbitmq/"
        )
        async with connection:
            channel = await connection.channel()
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message, cls=EnhancedJSONEncoder).encode(
                        "utf-8"
                    ),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key="task_queue",
            )
    except Exception as e:
        logger.error(f"Failed to publish message: {e}")
        raise
