from redis.asyncio import Redis


class RedisService:
    def __init__(self, redis_client: Redis):
        self._redis_client = redis_client

    async def set(self, key: str, value: str, ex: int = None):
        return await self._redis_client.set(key, value, ex=ex)

    async def get(self, key: str):
        value = await self._redis_client.get(key)
        if value is None:
            return None
        return (
            value.decode("utf-8") if isinstance(value, bytes) else str(value)
        )
