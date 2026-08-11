import json

from redis import Redis

from app.core.config import settings


class MemoryService:

    client = Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True
    )

    @classmethod
    def add_message(
        cls,
        user_id: int,
        role: str,
        content: str
    ):

        key = f"chat:{user_id}"

        cls.client.rpush(

            key,

            json.dumps({

                "role": role,

                "content": content

            })

        )

        cls.client.expire(
            key,
            86400
        )
    @classmethod
    def get_history(cls,user_id: int,limit: int = 10):
        key = f"chat:{user_id}"

        messages = cls.client.lrange(key,-limit,-1)

        return [json.loads(message) for message in messages]