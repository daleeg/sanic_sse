import os
import sys

from sanic import Sanic, Blueprint
from sanic.response import html
from sanic.worker.loader import AppLoader

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
from sse.core.storage import MemoryStorage
from sse.api.urls import sse_bgp
from sse import SseApp

SSE_CONFIG = {
    "pubsub_options": {
        "redis_host": os.getenv("SSE_REDIS_HOST", "127.0.0.1"),
        "redis_port": int(os.getenv("SSE_REDIS_PORT", "16379")),
        "redis_passwd": os.getenv("SSE_REDIS_PASSWD", ""),
    },
    "ping_interval": int(os.getenv("SSE_PING_INTERVAL", 30)),

}

root_ = Blueprint("root_")


def init_app():
    _app = Sanic(name="sse")
    _app.ctx.sse_config = SSE_CONFIG
    storage = MemoryStorage()
    _app.blueprint(root_)
    _app.blueprint(sse_bgp)
    SseApp(_app, storage)
    return _app


@root_.route("/index", methods=["GET"])
async def index(request):
    event = request.args.get("event", "test")
    url = f"sse/event/listen?event={event}"
    d = """
        <!DOCTYPE html>
        <html>
        <body>
          <h1>Getting server updates</h1>
          <ul></ul>
          <div id="response"></div>
          <script>
            var source = new EventSource("%s");
            console.log("withCredentials:", source.withCredentials);
            console.log("readyState:", source.readyState);
            console.log("url:", source.url);
            const eventList = document.querySelector("ul");
            
            source.onopen = function () {
                console.log("服务连接成功.");
            };
            source.onmessage = function(event) {
                console.log("收到消息" + event);
                const newElement = document.createElement("li");
                newElement.textContent = "message: " + event.data;
                eventList.appendChild(newElement);
                document.getElementById("response").innerHTML += event.data + "<br>";
            };
            source.onerror = function () {
              console.log("EventSource failed.");
            };
            source.addEventListener("%s", function(event) {
               console.log("get_event", event);
            });
                
          </script>
        </body>
    </html>
    """ % (url, url)
    return html(body=d)


if __name__ == "__main__":
    loader = AppLoader(factory=init_app)
    app = loader.load()
    app.prepare(host="0.0.0.0", port=8008, workers=2, debug=True)
    Sanic.serve(primary=app, app_loader=loader)
