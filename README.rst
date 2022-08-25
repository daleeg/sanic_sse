sanic_sse
########


1. 安装
==========

.. code-block:: shell

   pip install sanic-sse-py3

2. 示例
==========

- 2.1 代码

.. code-block:: python

    import os
    import sys
    from sanic import Sanic
    from sanic.response import html
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


- 2.2 接口

.. code-block:: shell

    GET /sse/event/send?event=test
    GET /sse/event/listen?event=test&client_id=
    GET /sse/event/terminate?event=test&client_id=



