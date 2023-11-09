class BaseStorageBackend(object):

    def set(self, k, v):
        raise NotImplementedError("set method must be implemented")

    def get(self, k):
        raise NotImplementedError("get method must be implemented")

    def pop(self, k, default=None):
        raise NotImplementedError("pop method must be implemented")

    def exists(self, k):
        raise NotImplementedError("exists method must be implemented")

    def keys(self):
        raise NotImplementedError("keys method must be implemented")

    def size(self):
        raise NotImplementedError("size method must be implemented")

    def setdefault(self, key, default=None):
        if key in self:
            return self[key]
        self[key] = default
        return default

    def __contains__(self, k):
        return self.exists(k)

    def __iter__(self):
        return iter(self.keys())

    def __getitem__(self, k):
        return self.get(k)

    def __setitem__(self, k, v):
        self.set(k, v)

    def __delitem__(self, k):
        return self.pop(k)
