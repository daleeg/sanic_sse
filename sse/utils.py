import asyncio
import atexit
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from inspect import isawaitable


class Sync(object):
    _executor: ThreadPoolExecutor = None
    _loop: asyncio.get_event_loop() = None

    @classmethod
    def executor(cls):
        if not cls._executor:
            cls._executor = ThreadPoolExecutor(5)
        return cls._executor

    @classmethod
    def loop(cls):
        if not cls._loop:
            cls._loop = asyncio.new_event_loop()
        return cls._loop

    @classmethod
    def run(cls, future):
        _executor, _loop = cls.executor(), cls.loop()
        task = _executor.submit(_loop.run_until_complete, future)
        return task.result()

    @classmethod
    def cleanup(cls):
        if cls._executor:
            cls._executor.shutdown()
            cls._executor = None
        if cls._loop:
            cls._loop.close()
            cls._loop = None


atexit.register(Sync.cleanup)


def sync_func(func, name):
    async def wrapper(*args, **kwargs):
        result = func(name, *args, **kwargs)
        if isawaitable(result):
            result = await result
        return result

    @wraps(func)
    def sync_call(*args, **kwargs):
        return Sync.run(wrapper(*args, **kwargs))

    return sync_call
