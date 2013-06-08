# -*- coding: utf-8 -*-
from unittest import TestCase


class SpanTest(TestCase):

    def test_from_set(self):
        from gpl.parsers import Span
        self.assertEquals([Span(1)],
                          list(Span.from_set([1])))
        self.assertEquals([Span(1, 2)],
                          list(Span.from_set([1, 2])))
        self.assertEquals([Span(1, 2), Span(4)],
                          list(Span.from_set([1, 2, 4])))
        self.assertEquals([Span(1, 2), Span(4, 6)],
                          list(Span.from_set([1, 2, 4, 5, 6])))

    def test_str(self):
        from gpl.parsers import Span
        self.assertEquals('3', str(Span(3)))
        self.assertEquals('3-4', str(Span(3, 4)))
        self.assertEquals('3-6', str(Span(3, 6)))


project_line = '   pyhwp : hwp file format parser in python'
copyright_line = '    Copyright (C) 2010-2012 mete0r  '
generic_line = '   abc   '
LF = '\n'


class ProjectTest(TestCase):

    def test_project_name(self):
        from gpl.parsers import PROJECT_NAME
        self.assertEquals('pyhwp', PROJECT_NAME.parseString('pyhwp  :'))

    def test_project_desc(self):
        from gpl.parsers import PROJECT_DESC
        self.assertEquals('hwp file format parser in python',
                          PROJECT_DESC.parseString('   hwp file format parser in python  '))

    def test_project_line_with_lf(self):
        from gpl.parsers import Project
        from gpl.parsers import PROJECT_LINE

        # ok with LF
        self.assertEquals(Project('pyhwp', 'hwp file format parser in python'),
                          PROJECT_LINE.parseString(project_line + LF))
        self.assertEquals(Project('pyhwp'),
                          PROJECT_LINE.parseString('   pyhwp   ' + LF))

    def test_project_line_without_lf(self):
        from gpl.parsers import Project
        from gpl.parsers import PROJECT_LINE

        # ok without LF
        self.assertEquals(Project('pyhwp', 'hwp file format parser in python'),
                          PROJECT_LINE.parseString(project_line))
        self.assertEquals(Project('pyhwp'),
                          PROJECT_LINE.parseString('   pyhwp   '))

    def test_project_line_parser_doesnt_consume_after_lf(self):
        from gpl.parsers import PROJECT_LINE
        # make sure that the parser does not consume after LF
        from gpl.Pysec import match
        self.assertEquals(' NEXTLINE',
                          (PROJECT_LINE & match(' NEXTLINE')).parseString(project_line
                                                                          + LF + ' NEXTLINE'))


class CopyrightTest(TestCase):

    def test_stringify_years(self):
        from gpl import stringify_years
        self.assertEquals('2011-2012',
                          stringify_years([2011, 2012]))
        self.assertEquals('2011-2013',
                          stringify_years([2011, 2012, 2013]))
        self.assertEquals('2011-2013,2015',
                          stringify_years([2011, 2012, 2013, 2015]))
        self.assertEquals('2009,2011-2013,2015',
                          stringify_years([2009, 2011, 2012, 2013, 2015]))

    def test_copyright(self):
        from gpl.parsers import COPYRIGHT_SIGN
        self.assertTrue(COPYRIGHT_SIGN.parseString('Copyright (C)'))

        from gpl.parsers import Span
        self.assertEquals('2010', str(Span(2010)))
        self.assertEquals('2010-2012', str(Span(2010, 2012)))

        from gpl.parsers import YEAR_SPAN
        self.assertEquals(Span(2010, 2012),
                          YEAR_SPAN.parseString('2010-2012'))
        self.assertEquals(Span(2010, 2010),
                          YEAR_SPAN.parseString('2010'))

        from gpl.parsers import YEARS
        self.assertEquals(set([2010]),
                          YEARS.parseString('2010'))
        self.assertEquals(set([2010, 2011]),
                          YEARS.parseString('2010,2011'))
        self.assertEquals(set([2010, 2011, 2012]),
                          YEARS.parseString('2010-2012'))
        self.assertEquals(set([2010, 2011, 2013, 2014, 2015, 2017]),
                          YEARS.parseString('2010,2011,2013-2015,2017'))

        from gpl.parsers import AUTHOR_NAME
        self.assertEquals('Hello World',
                          AUTHOR_NAME.parseString('Hello World'))
        self.assertEquals('Hello World',
                          AUTHOR_NAME.parseString('Hello World <'))

        from gpl.parsers import AUTHOR_EMAIL
        self.assertEquals('user@example.tld',
                          AUTHOR_EMAIL.parseString('<user@example.tld>'))

        from gpl.parsers import Author
        from gpl.parsers import AUTHOR
        self.assertEquals(Author('hong gil-dong', 'hongd@example.tld'),
                          AUTHOR.parseString('hong gil-dong <hongd@example.tld>'))
        self.assertEquals(Author('hong gil-dong'),
                          (AUTHOR.parseString('hong gil-dong')))
        self.assertEquals(Author(None, 'hongd@example.tld'),
                          (AUTHOR.parseString('<hongd@example.tld>')))

        from gpl.parsers import AUTHORS
        self.assertEquals([Author('mete0r'),
                           Author('hong gil-dong', 'hongd@ex.tld')],
                          AUTHORS.parseString('mete0r, hong gil-dong <hongd@ex.tld>'))

        from gpl.parsers import Copyright
        from gpl.parsers import COPYRIGHT_LINE
        # ok with LF
        self.assertEquals(Copyright(set([2010, 2011, 2012]),
                                    [Author('mete0r')]),
                          (COPYRIGHT_LINE.parseString(copyright_line + LF)))

        # ok without LF
        self.assertEquals(Copyright(set([2010, 2011, 2012]),
                                    [Author('mete0r')]),
                          (COPYRIGHT_LINE.parseString(copyright_line)))

        # make sure that the parser does not consume after the LF
        from gpl.Pysec import match
        self.assertEquals(' NEXTLINE',
                          (COPYRIGHT_LINE & match(' NEXTLINE')).parseString(copyright_line + LF + ' NEXTLINE'))

    def test_generic_line(self):
        from gpl.parsers import GENERIC_LINE
        self.assertEquals(generic_line,
                          GENERIC_LINE.parseString(generic_line + LF))


class LicenseTest(TestCase):
    def test_license(self):
        from gpl.parsers import LICENSE

        text = '''#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# ''' + project_line + '''
# ''' + copyright_line + '''
#
#    This file is part of pyhwp project.
#
#   license text.

import unittest
'''
        print LICENSE.parseString(text)
