import logging
import pickle
from redis.asyncio import Redis
from src.core.config import configuration

logging.basicConfig(level=logging.INFO)


class RedisManager(Redis):
    def __init__(self):
        super().__init__(
            host=configuration.REDIS_DOMAIN,
            port=configuration.REDIS_PORT,
            password=configuration.REDIS_PWD,
            decode_responses=False,
            encoding="utf-8"
        )

    async def get_obj(self, key: str):
        data = await self.get(key)
        return pickle.loads(data) if data else None

    async def set_obj(self, key: str, value, ex: int = None):
        await self.set(key, pickle.dumps(value), ex=ex)


redis_manager = RedisManager()
