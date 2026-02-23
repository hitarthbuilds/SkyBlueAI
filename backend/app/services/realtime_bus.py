import asyncio
import json
from typing import Any, AsyncIterator, Dict, Set

from redis.asyncio import Redis

from app.core.config import get_settings

settings = get_settings()

_redis_by_loop: Dict[int, Redis] = {}
_local_subscribers: Dict[str, Set[asyncio.Queue]] = {}


async def _get_redis() -> Redis | None:
    if not settings.redis_url:
        return None
    loop = asyncio.get_running_loop()
    key = id(loop)
    cached = _redis_by_loop.get(key)
    if cached is not None:
        return cached
    try:
        client = Redis.from_url(settings.redis_url)
        await client.ping()
        _redis_by_loop[key] = client
        return client
    except Exception:
        return None


def _serialize(message: Any) -> str:
    return json.dumps(message, default=str)


async def publish(channel: str, message: Any) -> None:
    payload = _serialize(message)
    redis = await _get_redis()
    if redis:
        try:
            await redis.publish(channel, payload)
            return
        except Exception:
            # Drop broken client for this loop and fall back to local publish.
            try:
                loop = asyncio.get_running_loop()
                _redis_by_loop.pop(id(loop), None)
            except Exception:
                pass

    queues = _local_subscribers.get(channel, set())
    for queue in queues:
        await queue.put(payload)


async def subscribe(channel: str) -> AsyncIterator[str]:
    queue: asyncio.Queue = asyncio.Queue()
    _local_subscribers.setdefault(channel, set()).add(queue)
    try:
        if not settings.redis_url:
            while True:
                payload = await queue.get()
                yield payload

        backoff = 1.0
        while True:
            redis = await _get_redis()
            if redis:
                pubsub = redis.pubsub()
                try:
                    await pubsub.subscribe(channel)
                    backoff = 1.0
                    async for msg in pubsub.listen():
                        if msg.get("type") == "message":
                            data = msg.get("data")
                            if isinstance(data, bytes):
                                yield data.decode("utf-8")
                            else:
                                yield str(data)
                except Exception:
                    try:
                        loop = asyncio.get_running_loop()
                        _redis_by_loop.pop(id(loop), None)
                    except Exception:
                        pass
                    await asyncio.sleep(backoff)
                    backoff = min(backoff * 2, 5.0)
                finally:
                    try:
                        await pubsub.unsubscribe(channel)
                        await pubsub.close()
                    except Exception:
                        pass
                continue

            # Redis unavailable; fall back to local queue with periodic retry.
            try:
                payload = await asyncio.wait_for(queue.get(), timeout=backoff)
                yield payload
            except asyncio.TimeoutError:
                backoff = min(backoff * 2, 5.0)
                continue
    finally:
        _local_subscribers.get(channel, set()).discard(queue)
