from collections import namedtuple

from sse.core.event import ControlEvent, DataEvent

InnerMessage = namedtuple("Message", ["category", "data"]) # ._asdict()


class MessageFactory(object):
    CATEGORY_CONTROL = "control"
    CATEGORY_DATA = "data"

    @classmethod
    def load(cls, category, event):
        return InnerMessage(category=category, data=event.to_dict)

    @classmethod
    def dump(cls, message):
        category = message.category
        if category == cls.CATEGORY_CONTROL:
            event = ControlEvent(**message.data)
        else:
            event = DataEvent(**message.data)
        return category, event
