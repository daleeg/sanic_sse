import os
import sys
from sanic import Sanic
from sanic.response import html

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

from sse.api.urls import sse_bgp
from sse import SseApp

app = Sanic(name="sse")


def init_app(_app):
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
    app.run(host="0.0.0.0", port=8000, workers=10)
