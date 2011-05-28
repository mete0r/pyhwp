class NIL: pass
class cached_property(object):

    def __init__(self, func):
        self.func = func
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, NIL)
        if value is NIL:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value

    def __set__(self, obj, value):
        obj.__dict__[self.__name__] = value
