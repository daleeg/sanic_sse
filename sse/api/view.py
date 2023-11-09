import uuid

from sanic.request import Request
from sanic.response import json
from sanic.views import HTTPMethodView

from sse.core.request import get_group_id


class EventListenView(HTTPMethodView):
    async def get(self, request: Request):
        sse = request.app.ctx.sse
        event = request.args.get("event")
        if not event:
            return json({"code": 1, "msg": "no event"})
        client_id = request.args.get("client_id", uuid.uuid4())
        group_id = get_group_id(request)
        return sse.sse_stream(event, client_id, group_id)


class EventSendView(HTTPMethodView):
    async def get(self, request: Request):
        sse = request.app.ctx.sse
        event = request.args.get("event")
        if not event:
            return json({"code": 1, "msg": "no event"})
        client_id = request.args.get("client_id")
        data = {
            "info": f"hello, {event}"
        }
        event_id = uuid.uuid4().hex
        await sse.send(data, event=event, client_id=client_id, event_id=event_id)
        return json({"code": 0, "data": {"event": event, "data": data, "event_id": event_id}})


class EventTerminateView(HTTPMethodView):
    async def get(self, request: Request):
        sse = request.app.ctx.sse
        event = request.args.get("event")
        if not event:
            return json({"code": 1, "msg": "no event"})
        client_id = request.args.get("client_id")
        await sse.terminate(event=event, client_id=client_id)
        return json({"code": 0, "msg": "success"})
