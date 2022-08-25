from sanic import Blueprint

from .view import EventListenView, EventSendView, EventTerminateView


__all__=["sse_bgp"]

sse_bp = Blueprint("sse_bp")
sse_bp.add_route(EventListenView.as_view(), "/event/listen")
sse_bp.add_route(EventSendView.as_view(), "/event/send")
sse_bp.add_route(EventTerminateView.as_view(), "/event/terminate")


blueprints = [
    sse_bp,
]

sse_bgp = Blueprint.group(*blueprints, url_prefix="/sse")


