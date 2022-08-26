from .storage import BaseStorageBackend


class EventRegister(object):
    def __init__(self, storage: BaseStorageBackend):
        self._storage = storage

    def register(self, event, client_id, group):
        if event in self._storage:
            event_info = self._storage[event]
        else:
            event_info = {}
        event_info[client_id] = group
        self._storage.set(event, event_info)

    def unregister(self, event, client_id):
        if event not in self._storage:
            return
        event_info = self._storage[event]
        info = event_info.pop(client_id, None)
        if event_info:
            self._storage.set(event, event_info)
        else:
            self._storage.pop(event)
        return info

    def is_registered(self, event, client_id, group):
        if event not in self._storage:
            return False
        event_info = self._storage[event]
        return not client_id or event_info.get(client_id) == group

    def no_events(self):
        return not self.get_events()

    def get_events(self):
        return self._storage.keys()

    def get_clients(self):
        clients = set()
        for event in self.get_events():
            event_info = self._storage[event]
            for c in event_info.keys():
                clients.add(c)
        return list(clients)

    def get_event_clients(self):
        result = []
        for event in self.get_events():
            event_info = self._storage[event]
            for c in event_info.keys():
                result.append([event, c])
        return result
