import uuid

from sanic.request import Request
from sanic.views import HTTPMethodView
from sanic.response import json

from sse.core.request import get_group_id


class EventListenView(HTTPMethodView):
    async def get(self, request: Request):
        sse = request.app.ctx.sse
        event = request.args.get("event")
        if not event:
            return json({"code": 1, "msg": "no event"})
        client_id = uuid.uuid4()
        group_id = get_group_id(request)
        return sse.sse_stream(event, client_id, group_id)


class EventSendView(HTTPMethodView):
    async def get(self, request: Request):
        sse = request.app.ctx.sse
        event = request.args.get("event")
        if not event:
            return json({"code": 1, "msg": "no event"})
        group_id = get_group_id(request)
        client_id = request.args.get("client_id")
        if not sse.is_registered(event, client_id, group_id):
            return json({"code": 1, "msg": "not registered"})
        data = {
            "info": f"hello, {event}"
        }
        event_id = uuid.uuid4().hex
        await sse.send(data, event=event, client_id=client_id, event_id=event_id)
        print(sse._register.get_events())
        return json({"code": 0, "data": {"event": event, "data": data, "event_id": event_id}})


class EventTerminateView(HTTPMethodView):
    async def get(self, request: Request):
        sse = request.app.ctx.sse
        event = request.args.get("event")
        if not event:
            return json({"code": 1, "msg": "no event"})
        client_id = request.args.get("client_id")
        group_id = get_group_id(request)
        if not sse.is_registered(event, client_id, group_id):
            return json({"code": 1, "msg": "not registered"})
        await sse.terminate(event=event, client_id=client_id)
        return json({"code": 0, "msg": "success"})
