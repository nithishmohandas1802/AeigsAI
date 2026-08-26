import json

from app.cache.redis import redis_client


def get_cache(key: str):
    value = redis_client.get(key)

    if value is None:
        return None

    return json.loads(value)


def set_cache(
    key: str,
    value,
    ttl: int,
):
    redis_client.set(
        key,
        json.dumps(value),
        ex=ttl,
    )


def delete_cache(key: str):
    redis_client.delete(key)