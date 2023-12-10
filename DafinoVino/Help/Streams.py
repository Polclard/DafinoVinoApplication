from collections import UserList


class Stream(UserList):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.iter = None

    def stream(self):
        self.iter = None
        return self

    def filter(self, function):
        self.iter = filter(function, self if self.iter is None else self.iter)
        return self

    def map(self, function):
        self.iter = map(function, self if self.iter is None else self.iter)
        return self

    def collect(self, collection_class=None):
        if collection_class is None:
            if self.iter is not None:
                ret = Stream(self.iter)
                self.iter = None
                return ret
            return Stream(self)
        return collection_class(self if self.iter is None else self.iter)
