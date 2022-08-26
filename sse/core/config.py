import os
from collections import namedtuple

Config = namedtuple("Config", ["ping_interval", "pubsub_options"])


def load_config(app):
    sse_config = getattr(app.ctx, "sse_config", None) or {}
    app.ctx.sse_config = merge_config(sse_config)
    return app.ctx.sse_config


def merge_config(config):
    pubsub_options = config.get("pubsub_options", {})
    pubsub_options["host"] = pubsub_options.pop("redis_host", os.getenv("SSE_REDIS_HOST", "127.0.0.1"))
    pubsub_options["port"] = int(pubsub_options.pop("redis_port", os.getenv("SSE_REDIS_PORT", 16379)))
    pubsub_options["password"] = pubsub_options.pop("redis_passwd", os.getenv("SSE_REDIS_PASSWD", ""))

    return Config(
        ping_interval=config.get("ping_interval", int(os.getenv("SSE_PING_INTERVAL", 10))),
        pubsub_options=pubsub_options
    )
