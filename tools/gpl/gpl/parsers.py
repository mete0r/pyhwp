# -*- coding: utf-8 -*-


from gpl.Pysec import Record
from gpl.Pysec import one_of
from gpl.Pysec import none_of
from gpl.Pysec import between
from gpl.Pysec import digits
from gpl.Pysec import match
from gpl.Pysec import sep_by
from gpl.Pysec import pair
from gpl.Pysec import Parser
from gpl.Pysec import until_one_of
from gpl.Pysec import option
from gpl.Pysec import space
from gpl.Pysec import spaces
from gpl.Pysec import quoted
#from gpl.Pysec import quoted_chars
from gpl.Pysec import char_range
from gpl.Pysec import many_chars
from gpl.Pysec import group_chars
from gpl.Pysec import skip_before
from gpl.Pysec import skip_after
from gpl.Pysec import skip_many
from gpl.Pysec import many
from gpl.Pysec import group
from gpl.Pysec import parser
from gpl.Pysec import ParseFailed

lift = Parser.lift

inline_space  = one_of(" \v\f\t\r")
inline_spaces = skip_many(inline_space)
meaningful_spaces = many_chars(space)

def quoted_chars_inline(start, end):
    return quoted(start, many_chars(none_of(end+'\n')), end)


def until_one_of_inline(chars):
    return until_one_of(chars+'\n')


def skip_tailspace_of_line(parser):
    return skip_after(parser,
                      inline_spaces & option(None, match('\n')))


@parser
def until_not_but(state0, should_not, but):
    state = state0
    values = []
    while True:
        try:
            should_not_value, next_state = should_not(state)
            return values, state
        except ParseFailed:
            value, state = but(state)
            values.append(value)


def py_comment(parser):
    return inline_spaces & match('#') & parser


class Project(Record('name', 'description')):

    @classmethod
    def prepare(cls, name, description=None):
        name = name.strip()
        if description is not None:
            description = description.strip()
        return name, description

    def __str__(self):
        return self.name + (' : ' + self.description
                            if self.description
                            else '')


alphabet = char_range('a', 'z') + char_range('A', 'Z')
PROJECT_NAME = (group_chars([one_of(alphabet),
                             many_chars(one_of(alphabet + char_range('0', '9') + '-_'), 1)])
                >> lift(str.strip))
PROJECT_NAME = skip_after(PROJECT_NAME, option(None, inline_spaces))
PROJECT_DESC = until_one_of('\n') >> lift(str.strip)
PROJECT_LINE = pair(PROJECT_NAME,
                    option(None, match(':') & PROJECT_DESC))
PROJECT_LINE = PROJECT_LINE >> lift(lambda seq: Project(*seq))
PROJECT_LINE = skip_before(inline_spaces, PROJECT_LINE)
PROJECT_LINE = skip_tailspace_of_line(PROJECT_LINE)


COPYRIGHT_SIGN = match('Copyright (C)')

class Span(Record('start', 'end')):

    @classmethod
    def prepare(cls, start, end=None):
        if end is None:
            end = start
        assert start <= end
        return start, end

    def as_set(self):
        return set(range(self.start, self.end + 1))

    @classmethod
    def from_set(cls, valueset):
        span = None
        for value in sorted(valueset):
            if span is None:
                # at first
                span = Span(value, value)
            elif value == span.end + 1:
                # continue current span
                span = span.setEnd(value)
            else:
                # end current and start next span
                yield span
                span = Span(value, value)
        if span is not None:
            yield span

    def __str__(self):
        if self.start == self.end:
            return str(self.start)
        return '%d-%d' % self


YEAR = digits >> lift(int)
TAIL = option(None, match('-') & YEAR)
YEAR_SPAN = (pair(YEAR, TAIL) >> lift(lambda pair: Span(*pair)))
YEARS = (sep_by(YEAR_SPAN, match(','))
         >> lift(lambda spans: reduce(set.union,
                                      (span.as_set() for span in spans))))

class Author(Record('name', 'email')):

    @classmethod
    def prepare(self, name, email=None):
        if not name and not email:
            raise ValueError('either of name and email should not be empty')
        return (name.strip() if name else None,
                email.strip() if email else None)

    def __str__(self):
        name = self.name or ''
        email = ('<' + self.email + '>') if self.email else ''
        if not email:
            return name
        if not name:
            return email
        return name + ' ' + email


AUTHOR_NAME = until_one_of('<,\n') >> lift(str.strip)
AUTHOR_EMAIL = quoted_chars_inline('<', '>')
AUTHOR = (pair(option(None, AUTHOR_NAME), option(None, AUTHOR_EMAIL))
          >> lift(lambda author: Author(*author)))
joiner = between(spaces, match(","), spaces)
AUTHORS = sep_by(AUTHOR, joiner)


class Copyright(Record('years', 'authors')):
    def __str__(self):
        years = ','.join(str(span) for span in Span.from_set(self.years))
        authors = ', '.join(str(author) for author in self.authors)
        return 'Copyright (C) %s %s' % (years, authors)


COPYRIGHT_LINE = (COPYRIGHT_SIGN & inline_spaces &
                  pair(YEARS, inline_spaces & AUTHORS))
COPYRIGHT_LINE = skip_before(inline_spaces, COPYRIGHT_LINE)
COPYRIGHT_LINE = skip_tailspace_of_line(COPYRIGHT_LINE)
COPYRIGHT_LINE = COPYRIGHT_LINE >> lift(lambda seq: Copyright(*seq))

GENERIC_LINE = skip_after(many_chars(none_of('\n')), match('\n'))


class License(Record('prolog', 'project', 'copyright', 'epilog')):

    def __str__(self):
        return '\n'.join(self.prolog +
                         ['#   ' + str(self.project),
                          '#   ' + str(self.copyright)] +
                         self.epilog + [''])


PROLOG = until_not_but(py_comment(PROJECT_LINE), GENERIC_LINE)
EPILOG = many(GENERIC_LINE)
LICENSE = (group([PROLOG,
                  py_comment(PROJECT_LINE),
                  py_comment(COPYRIGHT_LINE),
                  EPILOG])
           >> lift(lambda seq: License(*seq)))


def parse_file(path):
    with file(path) as f:
        text = f.read()
        return LICENSE.parseString(text)
