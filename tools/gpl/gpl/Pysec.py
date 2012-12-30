# -*- coding: utf-8 -*-
# originally authored by Peter Thatcher, Public Domain
# See http://www.valuedlessons.com/2008/02/pysec-monadic-combinatoric-parsing-in.html

def Record(*props):
    class cls(RecordBase):
        pass

    cls.setProps(props)

    return cls


class RecordBase(tuple):
    PROPS = ()

    def __new__(cls, *values):
        if cls.prepare != RecordBase.prepare:
            values = cls.prepare(*values)
        return cls.fromValues(values)

    @classmethod
    def fromValues(cls, values):
        return tuple.__new__(cls, values)

    def __repr__(self):
        return self.__class__.__name__ + tuple.__repr__(self)

    ## overridable
    @classmethod
    def prepare(cls, *args):
        return args

    ## setting up getters and setters
    @classmethod
    def setProps(cls, props):
        for index, prop in enumerate(props):
            cls.setProp(index, prop)
        cls.PROPS = props

    @classmethod
    def setProp(cls, index, prop):
        getter_name = prop
        setter_name = "set" + prop[0].upper() + prop[1:]

        setattr(cls, getter_name, cls.makeGetter(index, prop))
        setattr(cls, setter_name, cls.makeSetter(index, prop))

    @classmethod
    def makeGetter(cls, index, prop):
        return property(fget = lambda self : self[index])

    @classmethod
    def makeSetter(cls, index, prop):
        def setter(self, value):
            values = (value if current_index == index
                            else current_value
                      for current_index, current_value
                      in enumerate(self))
            return self.fromValues(values)
        return setter


class ByteStream(Record("bytes", "index")):
    @classmethod
    def prepare(cls, bytes, index = 0):
        return (bytes, index)

    def get(self, count):
        start = self.index
        end   = start + count
        bytes = self.bytes[start : end]
        return bytes, (self.setIndex(end) if bytes else self)


def make_decorator(func, *dec_args):
    def decorator(undecorated):
        def decorated(*args, **kargs):
            return func(undecorated, args, kargs, *dec_args) 
        
        decorated.__name__ = undecorated.__name__
        return decorated
    
    decorator.__name__ = func.__name__
    return decorator


decorator = make_decorator


class Monad:
    ## Must be overridden
    def bind(self, func):
        raise NotImplementedError

    @classmethod
    def unit(cls, val):
        raise NotImplementedError

    @classmethod
    def lift(cls, func):
        return (lambda val : cls.unit(func(val)))

    ## useful defaults that should probably NOT be overridden
    def __rshift__(self, bindee):
        return self.bind(bindee)

    def __and__(self, monad):
        return self.shove(monad)
        
    ## could be overridden if useful or if more efficient
    def shove(self, monad):
        return self.bind(lambda _ : monad)


class StateChanger(Record("changer", "bindees"), Monad):
    @classmethod
    def prepare(cls, changer, bindees = ()):
        return (changer, bindees)

    # binding can be slow since it happens at bind time rather than at run time
    def bind(self, bindee):
        return self.setBindees(self.bindees + (bindee,))

    def __call__(self, state):
        return self.run(state)

    def run(self, state0):
        value, state = self.changer(state0) if callable(self.changer) else self.changer
        state        = state0 if state is None else state

        for bindee in self.bindees:
            value, state = bindee(value).run(state)
        return (value, state)

    @classmethod
    def unit(cls, value):
        return cls((value, None))


######## Parser Monad ###########


class ParserState(Record("stream", "position")):
    @classmethod
    def prepare(cls, stream, position = 0):
        return (stream, position)

    def read(self, count):
        collection, stream = self.stream.get(count)
        return collection, self.fromValues((stream, self.position + count))


class Parser(StateChanger):
    def parseString(self, bytes):
        return self.parseStream(ByteStream(bytes))
        
    def parseStream(self, stream):
        state = ParserState(stream)
        value, state = self.run(state)
        return value


class ParseFailed(Exception):
    def __init__(self, message, state):
        self.message = message
        self.state   = state
        Exception.__init__(self, message)


@decorator
def parser(func, func_args, func_kargs):
    def changer(state):
        return func(state, *func_args, **func_kargs)
    changer.__name__ = func.__name__
    return Parser(changer)


##### combinatoric functions #########


@parser
def tokens(state0, count, process):
    tokens, state1 = state0.read(count)

    passed, value = process(tokens)
    if passed:
        return (value, state1)
    else:
        raise ParseFailed(value, state0)
    

def read(count):
    return tokens(count, lambda values : (True, values))


@parser
def skip(state0, parser):
    value, state1 = parser(state0)
    return (None, state1)


@parser
def option(state, default_value, parser):
    try:
        return parser(state)
    except ParseFailed, failure:
        if failure.state == state:
            return (default_value, state)
        else:
            raise
        

@parser
def choice(state, parsers):
    for parser in parsers:
        try:
            return parser(state)
        except ParseFailed, failure:
            if failure.state != state:
                raise failure
    raise ParseFailed("no choices were found", state)


@parser
def match(state0, expected):
    actual, state1 = read(len(expected))(state0)
    if actual == expected:
        return actual, state1
    else:
        raise ParseFailed("expected %r, actual %r" % (expected, actual), state0)


def between(before, inner, after):
    return before & inner >> (lambda value : after & Parser.unit(value))


def quoted(before, inner, after):
    return between(match(before), inner, match(after))


def quoted_collection(start, space, inner, joiner, end):
    return quoted(start, space & sep_end_by(inner, joiner), end)


@parser
def many(state, parser, min_count = 0):
    values = []

    try:
        while True:
            value, state = parser(state)
            values.append(value)
    except ParseFailed:
        if len(values) < min_count:
            raise

    return values, state
    

@parser
def group(state, parsers):
    values = []

    for parser in parsers:
        value, state = parser(state)
        values.append(value)

    return values, state


def pair(parser1, parser2):
    # return group((parser1, parser2))
    return parser1 >> (lambda value1 : parser2 >> (lambda value2 : Parser.unit((value1, value2))))


@parser
def skip_many(state, parser):
    try:
        while True:
            value, state = parser(state)
    except ParseFailed:
        return (None, state)


def skip_before(before, parser):
    return skip(before) & parser


@parser
def skip_after(state0, parser, after):
    value, state1 = parser(state0)
    _,     state2 = after(state1)
    return value, state2


@parser
def option_many(state0, first, repeated, min_count = 0):
    try:
        first_value, state1 = first(state0)
    except ParseFailed:
        if min_count > 0:
            raise
        else:
            return [], state0
    else:
        values, state2 = many(repeated, min_count-1)(state1)
        values.insert(0, first_value)
        return values, state2


# parser separated and ended by sep
def end_by(parser, sep_parser, min_count = 0):
    return many(skip_after(parser, sep_parser), min_count)


# parser separated by sep
def sep_by(parser, sep_parser, min_count = 0):
    return option_many(parser, skip_before(sep_parser, parser), min_count)
    

# parser separated and optionally ended by sep
def sep_end_by(parser, sep_parser, min_count = 0):
    return skip_after(sep_by(parser, sep_parser, min_count), option(None, sep_parser))


##### char-specific parsing ###########


def satisfy(name, passes):
    return tokens(1, lambda char : (True, char) if passes(char) else (False, "not " + name))


def one_of(chars):
    char_set = frozenset(chars)
    return satisfy("one of %r" % chars, lambda char : char in char_set)


def none_of(chars):
    char_set = frozenset(chars)
    return satisfy("not one of %r" % chars, lambda char : char and char not in char_set)


def maybe_match_parser(parser):
    return match(parser) if isinstance(parser, str) else parser


def maybe_match_parsers(parsers):
    return tuple(maybe_match_parser(parser) for parser in parsers)


def many_chars(parser, min_count = 0):
    return join_chars(many(parser, min_count))


def option_chars(parsers):
    return option("", group_chars(parsers))


def group_chars(parsers):
    return join_chars(group(maybe_match_parsers(parsers)))
    #return join_chars(group(parsers))


def join_chars(parser):
    return parser >> Parser.lift("".join)


def while_one_of(chars, min_count = 0):
    return many_chars(one_of(chars), min_count)


def until_one_of(chars, min_count = 0):
    return many_chars(none_of(chars), min_count)


def char_range(begin, end):
    return "".join(chr(num) for num in xrange(ord(begin), ord(end)))


def quoted_chars(start, end):
    assert len(end) == 1, "end string must be exactly 1 character"
    return quoted(start, many_chars(none_of(end)), end)


digit  = one_of(char_range("0", "9"))
digits = many_chars(digit, min_count = 1)
space  = one_of(" \v\f\t\r\n")
spaces = skip_many(space)


############# simplified JSON ########################

#from Pysec import Parser, choice, quoted_chars, group_chars, option_chars, digits, between, pair, spaces, match, quoted_collection, sep_end_by

#HACK: json_choices is used to get around mutual recursion 
#a json is value is one of text, number, mapping, and collection, which we define later 
json_choices = []
json         = choice(json_choices)

#text is any characters between quotes
text         = quoted_chars("'", "'")

#sort of like the regular expression -?[0-9]+(\.[0-9]+)?
#in case you're unfamiliar with monads, "parser >> Parser.lift(func)" means "pass the parsed value into func but give me a new Parser back"
number       = group_chars([option_chars(["-"]), digits, option_chars([".", digits])]) >> Parser.lift(float)

#quoted_collection(start, space, inner, joiner, end) means "a list of inner separated by joiner surrounded by start and end"
#also, we have to put a lot of spaces in there since JSON allows lot of optional whitespace
joiner       = between(spaces, match(","), spaces)
mapping_pair = pair(text, spaces & match(":") & spaces & json)
collection   = quoted_collection("[", spaces, json,         joiner, "]") >> Parser.lift(list)
mapping      = quoted_collection("{", spaces, mapping_pair, joiner, "}") >> Parser.lift(dict)

#HACK: finish the work around mutual recursion
json_choices.extend([text, number, mapping, collection])


############# simplified CSV ########################

def line(cell):
    return sep_end_by(cell, match(","))

def csv(cell):
    return sep_end_by(line(cell), match("\n"))

############# testing ####################

if __name__ == '__main__':
    print json.parseString("{'a' : -1.0, 'b' : 2.0, 'z' : {'c' : [1.0, [2.0, [3.0]]]}}")
    print csv(number).parseString("1,2,3\n4,5,6")
    print csv(json).parseString("{'a' : 'A'},[1, 2, 3],'zzz'\n-1.0,2.0,-3.0")
