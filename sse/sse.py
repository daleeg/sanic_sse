import asyncio
import contextlib
import os

from aiopubsub import Pubsub
from sanic import Sanic
import logging

try:
    from sanic.response import ResponseStream
except ImportError:
    from sanic.response import stream as ResponseStream

from sse.core.channel import EventRegister
from sse.core.event import DataEvent, ControlEvent
from sse.core.message import MessageFactory, InnerMessage
from sse.core.config import load_config
from sse.core.storage import ShareMemoryStory

LOG = logging.getLogger(__name__)


class SseApp(object):
    _HEADERS = {"Cache-Control": "no-cache"}

    def __init__(self, app: Sanic = None, ):
        self.config = load_config(app)
        self._ping_task = None
        self._pubsub = Pubsub(**self.config.pubsub_options)
        self._register = EventRegister(storage=ShareMemoryStory())
        if app is not None:
            self.init_app(app)

    @classmethod
    def gen_pub_event_topic(cls, event, client_id=None):
        if client_id:
            return f"{event}:{client_id}"
        return f"{event}:"

    @classmethod
    def parse_topic(cls, topic):
        return topic.rsplit(":", maxsplit=2)

    @classmethod
    def gen_sub_event_topic(cls, event):
        return f"{event}:*"

    def is_registered(self, event, client_id, group=None):
        return self._register.is_registered(event, client_id, group)

    async def terminate(self, event, client_id):
        message = MessageFactory.load(MessageFactory.CATEGORY_CONTROL, ControlEvent(ControlEvent.EVENT_TERMINATION))
        async with self._pubsub.get_pub() as _pub:
            return await _pub.publish(self.gen_pub_event_topic(event=event, client_id=client_id),
                                      data=message._asdict())

    async def ping(self, event):
        message = MessageFactory.load(MessageFactory.CATEGORY_CONTROL, ControlEvent(ControlEvent.EVENT_PING))
        async with self._pubsub.get_pub() as _pub:
            return await _pub.publish(self.gen_pub_event_topic(event=event), data=message._asdict())

    @staticmethod
    def is_termination(event):
        return event.check_event(ControlEvent.EVENT_TERMINATION)

    async def _ping(self):
        while True:
            await asyncio.sleep(self.config.ping_interval)
            for event in self._register.get_events():
                await self.ping(event)

    async def send(self, data: str, event: str = None, client_id=None, event_id: str = None, retry: int = None):
        message = MessageFactory.load(MessageFactory.CATEGORY_DATA,
                                      DataEvent(data, event=event, event_id=event_id, retry=retry))
        async with self._pubsub.get_pub() as _pub:
            return await _pub.publish(self.gen_pub_event_topic(event, client_id), message._asdict())

    def init_app(self, app: Sanic):

        @app.listener("after_server_start")
        def _on_start(_, loop):
            self._ping_task = loop.create_task(self._ping())

        @app.listener("before_server_stop")
        async def _on_stop(_, __):
            self._ping_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._ping_task
            await self._pubsub.close()

        app.ctx.sse_send = self.send
        app.ctx.sse = self

    async def process_message(self, message, response, group, client_id):
        _type = message["type"]
        category, event_body = MessageFactory.dump(InnerMessage(**message["data"]))
        if category == MessageFactory.CATEGORY_CONTROL:
            if self.is_termination(event_body):
                return True
        else:
            event, _client_id = self.parse_topic(message["channel"])
            if _client_id and _client_id != client_id:
                return False
            if not self.is_registered(event, _client_id, group):
                return False
            LOG.info(f"event:{event}, client_id:{client_id}")
        resp = event_body.to_string
        await response.write(resp)
        LOG.info(f"message: [{resp}]")
        return False

    def sse_stream(self, event, client_id, group):
        self._register.register(event, client_id, group)

        async def streaming_fn(response):
            LOG.info(f"pid:{os.getpid()}, events:{self._register.get_events()}")
            try:
                async with self._pubsub.get_sub() as _sub:
                    _conn = await self._pubsub.psubscribe(self.gen_sub_event_topic(event), _conn=_sub.conn)
                    async for k in self._pubsub.listen(_conn=_conn):
                        is_termination = await self.process_message(k, response, client_id, group)
                        if is_termination:
                            break
            finally:
                self._register.unregister(event, client_id)

        return ResponseStream(
            streaming_fn, headers=self._HEADERS, content_type="text/event-stream"
        )
