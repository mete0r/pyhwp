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


def generate_json_array(tokens):
    ''' generate json array with given tokens '''
    first = True
    for token in tokens:
        if first:
            yield '[\n'
            first = False
        else:
            yield ',\n'
        yield token
    yield '\n]'


class JsonObjects(object):

    def __init__(self, objects, object_to_json):
        self.objects = objects
        self.object_to_json = object_to_json

    def generate(self, **kwargs):
        kwargs.setdefault('sort_keys', True)
        kwargs.setdefault('indent', 2)

        tokens = (self.object_to_json(obj, **kwargs)
                  for obj in self.objects)
        return generate_json_array(tokens)

    def open(self, **kwargs):
        from .filestructure import GeneratorReader
        return GeneratorReader(self.generate(**kwargs))

    def dump(self, outfile, **kwargs):
        for s in self.generate(**kwargs):
            outfile.write(s)
