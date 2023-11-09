import multiprocessing

from .base import BaseStorageBackend


class MemoryStorage(BaseStorageBackend):
    def __init__(self, **kwargs):
        self.__storage = dict(**kwargs)

    def set(self, k, v):
        self.__storage[k] = v

    def get(self, k):
        return self.__storage.get(k)

    def pop(self, k, default=None):
        return self.__storage.pop(k, default)

    def exists(self, k):
        return k in self.__storage

    def size(self):
        return len(self.__storage)

    def keys(self):
        return self.__storage.keys()


if __name__ == '__main__':
    a = MemoryStorage(a=1, b=2)
    b = MemoryStorage(a=3, b=4)
    print(b.size())
    for k in a:
        print(k, a[k], b[k])
