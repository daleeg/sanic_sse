import multiprocessing


class BaseStorageBackend(object):
    def __init__(self, **kwargs):
        self.__storage = dict()
        raise NotImplementedError("__init__ method must be implemented")

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

    # def __getattr__(self, attr):
    #     if attr not in self.__dict__:
    #         return getattr(self.__storage, attr)
    #     return self.__dict__[attr]


class ShareMemoryStory(BaseStorageBackend):
    def __init__(self, **kwargs):
        self.__manager = multiprocessing.Manager()
        self.__storage = self.__manager.dict(**kwargs)

    def set(self, k, v):
        self.__storage[k] = v

    def get(self, k):
        return self.__storage[k]

    def pop(self, k, default=None):
        return self.__storage.pop(k, default)

    def exists(self, k):
        return k in self.__storage

    def size(self):
        return len(self.__storage)

    def keys(self):
        return self.__storage.keys()


if __name__ == '__main__':
    a = ShareMemoryStory(a=1, b=2)
    b = ShareMemoryStory(a=3, b=4)
    print(b.size())
    for k in a:
        print(k)
