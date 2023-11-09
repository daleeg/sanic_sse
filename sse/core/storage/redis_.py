import asyncio
import base64

import redis.asyncio as aioredis
import ujson

from sse.core.storage.base import BaseStorageBackend
from sse.utils import sync_func


def get_redis_func(redis_: aioredis.client.Redis, name):
    hset = sync_func(redis_.hset, name)
    hget = sync_func(redis_.hget, name)
    hdel = sync_func(redis_.hdel, name)
    hexists = sync_func(redis_.hexists, name)
    hlen = sync_func(redis_.hlen, name)
    hkeys = sync_func(redis_.hkeys, name)
    return hset, hget, hdel, hexists, hlen, hkeys


class JsonSerializer(object):
    @classmethod
    def dumps(cls, value):
        return base64.b64encode(ujson.dumps(value).encode()).decode()

    @classmethod
    def loads(cls, value):
        if value is None:
            return None
        return ujson.loads(base64.b64decode(value).decode())


class RedisStorage(BaseStorageBackend):
    def __init__(self, redis_: aioredis.client.Redis, name: str = None, **kwargs):
        self.name = f"S:{name or self.__class__.__name__}"
        self._hset, self._hget, self._hdel, self._hexists, self._hlen, self._hkeys = get_redis_func(redis_, self.name)
        self._loads, self._dumps = JsonSerializer.loads, JsonSerializer.dumps

    def set(self, k, v):
        self._hset(self._dumps(k), self._dumps(v))

    def get(self, k):
        k = self._dumps(k)
        return self._loads(self._hget(k))

    def pop(self, k, default=None):
        value = self.get(self._dumps(k)) or default
        self._hdel(self._dumps(k))
        return value

    def exists(self, k):
        return self._hexists(self._dumps(k))

    def size(self):
        return self._hlen()

    def keys(self):
        result = []
        for key in self._hkeys():
            try:
                key = self._loads(key)
                result.append(key)
            except Exception:
                self._hdel(key)
        return result


async def main():
    url = "redis://127.0.0.1:16379"
    redis_ = aioredis.from_url(url)
    d = RedisStorage(redis_)
    d[0], d[1] = 1, [2]
    print(d[0], d[1])
    print (0 in d)


if __name__ == '__main__':
    asyncio.run(main())
