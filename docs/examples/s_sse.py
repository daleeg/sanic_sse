import os
import sys
from sanic import Sanic
from sanic.response import html

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

from sse.api.urls import sse_bgp
from sse import SseApp

app = Sanic(name="sse")

SSE_CONFIG = {
    "pubsub_options": {
        "redis_host": os.getenv("SSE_REDIS_HOST", "127.0.0.1"),
        "redis_port": int(os.getenv("SSE_REDIS_PORT", "16379")),
        "redis_passwd": os.getenv("SSE_REDIS_PASSWD", ""),
    },
    "ping_interval": int(os.getenv("SSE_PING_INTERVAL", 10)),

}


def init_app(_app):
    _app.ctx.sse_config = SSE_CONFIG
    SseApp(_app)
    _app.blueprint(sse_bgp)


@app.route("/index", methods=["GET"])
async def index(request):
    event = request.args.get("event", "test")
    url = f"sse/event/listen?event={event}"
    d = """
        <html>
        <body>
          <script>
                var source = new EventSource("%s");
                source.onmessage = function(e) {
                    console.log("xxxxxxx");
                    document.getElementById('response').innerHTML + e.data + "<br>";
                }
          </script>
          <h1>Getting server updates</h1>
          <div id="response"></div>
        </body>
    </html>
    """ % url
    return html(body=d)


if __name__ == "__main__":
    init_app(app)
    app.run(host="0.0.0.0", port=8008, workers=10)
