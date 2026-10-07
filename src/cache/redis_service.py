import redis

from src.config import REDIS_HOST, REDIS_PORT


class RedisService:
    def __init__(self):
        self.client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True,
        )

    def get(self, key: str):
        return self.client.get(key)

    def set(self, key: str, value: str, expire: int = 3600):
        self.client.set(
            key,
            value,
            ex=expire,
        )

    def delete(self, key: str):
        self.client.delete(key)

    def ping(self):
        return self.client.ping()