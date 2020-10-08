import threading
from pprint import pprint


class SafeDict:
    def __init__(self, name=None):
        self.lock = threading.Lock()
        self.shared_dict = {}
        self.name = name

    def add(self, key, value):
        with self.lock:
            self.shared_dict[key] = value

        return self

    def get(self, key):
        with self.lock:
            if key in self.shared_dict:
                return self.shared_dict[key]
            else:
                return None

    def get_and_remove(self, key):
        with self.lock:
            if key in self.shared_dict:
                value = self.shared_dict[key]
                del self.shared_dict[key]
                return value
            else:
                return None

    def remove(self, key):
        with self.lock:
            if key in self.shared_dict:
                del self.shared_dict[key]

        return self

    def safe_modify(self, callback):
        with self.lock:
            callback(self.shared_dict)
        return self

    def __str__(self):
        return str({'name': self.name, 'data': self.shared_dict})
