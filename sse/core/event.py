import json
from collections import OrderedDict


class SseEvent(object):
    def __init__(self, event=None):
        self.data = None
        self.options = OrderedDict({
            "event": event,
        })

    @property
    def to_string(self):
        raise NotImplementedError("to_string method must be implemented")

    @property
    def to_dict(self):
        return dict(**self.options)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.to_string == other.to_string

    def __repr__(self):
        kwargs_repr = ", ".join(
            [f"{key}={value!r}" for key, value in self.options.items() if value is not None]
        )
        return f"{self.__class__.__name__}({kwargs_repr})"

    def __str__(self):
        return self.to_string

    def clone(self):
        return self.__class__(**self.to_dict)

    def check_event(self, event):
        return self.options["event"] == event


class DataEvent(SseEvent):
    mapping = OrderedDict(
        event=lambda e: f"event: {e}",
        data=lambda d: f"data: {json.dumps(d)}",
        event_id=lambda i: f"id: {i}",
        retry=lambda r: f"retry: {r}"
    )

    def __init__(self, data, event=None, event_id=None, retry=None):
        if not data:
            raise ValueError(f"data cannot be None")
        self.data = data
        self.options = OrderedDict({
            "event": event,
            "event_id": event_id,
            "retry": retry,
        })

    @property
    def to_dict(self):
        return dict(data=self.data, **self.options)

    @property
    def to_string(self):
        info = self.to_dict
        lines = []
        for key, transfer in self.mapping.items():
            value = info.get(key)
            if not value:
                continue
            lines.append(transfer(value))
        return "\n".join(lines) + "\n\n"

    def __repr__(self):
        kwargs_repr = ", ".join(
            [f"{key}={value!r}" for key, value in self.options.items() if value is not None]
        )
        return f"{self.__class__.__name__}(data={self.data!r}, {kwargs_repr})"


class ControlEvent(SseEvent):
    EVENT_PING = "ping"
    EVENT_TERMINATION = "termination"

    @property
    def to_string(self):
        event = self.options['event']
        if event == self.EVENT_PING:
            return f": {event}\n\n"
        return f"event: {event}\n\n"


def test_event():
    e1 = DataEvent({"test": 1}, "fetch", "f1")
    print(repr(e1))
    e2 = e1.clone()
    print(e1 == e2)
    print(e2.to_string)

    ping_event = ControlEvent(ControlEvent.EVENT_PING)
    print(ping_event.clone().to_string)

    termination_event = ControlEvent(ControlEvent.EVENT_TERMINATION)
    print(repr(termination_event))
    print(termination_event.clone().to_string)


if __name__ == '__main__':
    test_event()
