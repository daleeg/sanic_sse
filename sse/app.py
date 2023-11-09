import asyncio
import contextlib
import logging
import os

import async_timeout
from aiopubsub import Pubsub, PubsubRole
from sanic import Sanic

try:
    from sanic.response import ResponseStream
except ImportError:
    from sanic.response import stream as ResponseStream

from sse.core.channel import EventRegister
from sse.core.event import DataEvent, ControlEvent
from sse.core.message import MessageFactory, InnerMessage
from sse.core.config import load_config
from sse.core.storage import BaseStorageBackend

LOG = logging.getLogger(__name__)


class SseApp(object):
    _HEADERS = {"Cache-Control": "no-cache"}

    def __init__(self, app: Sanic, storage: BaseStorageBackend):
        self.config = load_config(app)
        self._ping_task = None
        self._pub_options = dict(**self.config.pubsub_options, role=PubsubRole.PUB)
        self._sub_options = dict(**self.config.pubsub_options, role=PubsubRole.SUB)
        self._register = EventRegister(storage=storage)
        if app is not None:
            self.init_app(app)

    @classmethod
    def gen_pub_event_topic(cls, event, client_id=None):
        _pid = f"{os.getpid()}"
        if client_id:
            return f"{event}:{client_id}:{_pid}"
        return f"{event}::{_pid}"

    @classmethod
    def parse_topic(cls, topic):
        return topic.rsplit(":", maxsplit=2)

    @classmethod
    def gen_sub_event_topic(cls, event):
        return f"{event}:*"

    def is_registered(self, event, client_id, group=None):
        return self._register.is_registered(event, client_id, group)

    async def terminate(self, event, client_id=None):
        async with Pubsub(**self._pub_options) as _pub:
            return await self._terminate(_pub, event, client_id)

    async def _terminate(self, _pub, event, client_id=None):
        message = MessageFactory.load(MessageFactory.CATEGORY_CONTROL, ControlEvent(ControlEvent.EVENT_TERMINATION))
        return await _pub.publish(self.gen_pub_event_topic(event=event, client_id=client_id),
                                  data=message._asdict())

    async def ping(self, _pub, event):
        message = MessageFactory.load(MessageFactory.CATEGORY_CONTROL, ControlEvent(ControlEvent.EVENT_PING))
        topic = self.gen_pub_event_topic(event=event)
        return await _pub.publish(topic, data=message._asdict())

    @staticmethod
    def is_termination(event):
        return event.check_event(ControlEvent.EVENT_TERMINATION)

    async def _ping(self):
        while True:
            await asyncio.sleep(self.config.ping_interval)
            events = self._register.get_events()
            LOG.debug(f"ping listens: {os.getpid()} - {events}")
            async with Pubsub(**self._pub_options) as _pub:
                for event in events:
                    ret = await self.ping(_pub, event)
                    if not ret:
                        self._register.unregister(event)

    async def send(self, data: str, event: str = None, client_id=None, event_id: str = None, retry: int = None):
        message = MessageFactory.load(MessageFactory.CATEGORY_DATA,
                                      DataEvent(data, event=event, event_id=event_id, retry=retry))
        async with Pubsub(**self._pub_options) as _pub:
            return await _pub.publish(self.gen_pub_event_topic(event, client_id), message._asdict())

    async def wait_no_stream(self):
        try:
            async with async_timeout.timeout(5):
                while True:
                    if self._register.no_events():
                        return
                    await asyncio.sleep(0.1)
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError(f"wait stream closed timeout: {self._register.get_events()}")

    def init_app(self, app: Sanic):

        @app.listener("after_server_start")
        def _on_start(_, loop):
            LOG.info(f"pid:{os.getpid()} start")
            self._ping_task = loop.create_task(self._ping())

        @app.listener("before_server_stop")
        async def _on_stop(_, __):
            LOG.info(f"pid:{os.getpid()} stop")
            self._ping_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._ping_task

            async with Pubsub(**self._pub_options) as _pub:
                for event in self._register.get_events():
                    await self._terminate(_pub, event)
            await self.wait_no_stream()

        app.ctx.sse_send = self.send
        app.ctx.sse = self

    async def process_message(self, message, response, event, group, client_id):
        _type = message["type"]
        category, event_body = MessageFactory.dump(InnerMessage(**message["data"]))
        _event, _client_id, _pid = self.parse_topic(message["channel"])
        if category == MessageFactory.CATEGORY_CONTROL:
            if self.is_termination(event_body):
                return True
            if _pid and _pid != f"{os.getpid()}":
                return False
        else:
            if _client_id and _client_id != client_id:
                return False
            if _event and _event != event:
                return False
            if not self.is_registered(_event, _client_id, group):
                return False
        LOG.info(f"process pid:{os.getpid()}, event:{_event}, client_id:{client_id} group:{group}")
        resp = event_body.to_string
        await response.write(resp)
        return False

    def sse_stream(self, event, client_id, group):

        async def streaming_fn(response):
            self._register.register(event, client_id, group)
            LOG.info(f"register [{os.getpid()}]event:{event}")
            try:
                async with Pubsub(**self._sub_options) as _sub:
                    await _sub.psubscribe(self.gen_sub_event_topic(event))
                    async for k in _sub.listen():
                        is_termination = await self.process_message(k, response, event, group, client_id)
                        if is_termination:
                            break
            finally:
                self._register.unregister(event, client_id)

        return ResponseStream(
            streaming_fn, headers=self._HEADERS, content_type="text/event-stream"
        )
