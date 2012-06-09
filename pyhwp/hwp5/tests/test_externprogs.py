# -*- coding: utf-8 -*-
from __future__ import with_statement
from unittest import TestCase
from hwp5.utils import cached_property

from hwp5.externprogs import FileWrapper
from hwp5.externprogs import SubprocessError
from hwp5.externprogs import SubprocessReadable
from hwp5.externprogs import ProgramNotFound
from hwp5.externprogs import xmllint
from hwp5.externprogs import xmllint_readable

class TestFileWrapper(TestCase):

    def test_iter(self):
        from StringIO import StringIO
        f = StringIO('abcd\nefgh')
        wrapper = FileWrapper(f)
        lines = list(wrapper)
        self.assertEquals(['abcd\n', 'efgh'], lines)

    def test_read(self):
        from StringIO import StringIO
        f = StringIO('0123456789')
        wrapper = FileWrapper(f)
        self.assertEquals('012', wrapper.read(3))
        self.assertEquals('3456789', wrapper.read())

    def test_close(self):
        from StringIO import StringIO
        f = StringIO()
        wrapper = FileWrapper(f)
        wrapper.close()


class TestSubprocessReadable(TestCase):

    pass


class TestXmlLint(TestCase):

    @cached_property
    def xmllint(self):
        return xmllint()

    def test_xmlint_notfound(self):
        transform = xmllint(xmllint_path='xmllint-nonexistent')
        try:
            transform()
            self.fail('ProgramNotFound expected')
        except ProgramNotFound:
            pass

    def test_readable(self):
        r, w = self.xmllint()
        self.assertTrue(isinstance(r, SubprocessReadable))

        def run():
            try:
                with w:
                    w.write('<doc/>')
            finally:
                w.close()
        import threading
        threading.Thread(target=run).start()

        with r:
            transformed = r.read()
        self.assertEquals('<?xml version="1.0"?>\n<doc/>\n', transformed)

    def test_readable_failed(self):
        r, w = self.xmllint()
        def run():
            try:
                with w:
                    w.write('<doc></nondoc>')
            finally:
                w.close()
        import threading
        threading.Thread(target=run).start()

        with r:
            self.assertRaises(SubprocessError, r.read)
        self.assertEquals(1, r.subprocess.wait())

    def test_returncode_ok(self):

        transform = xmllint()

        with file(self.id(), 'w') as f:
            f.write('<doc></doc>')
        with file(self.id(), 'r') as f:
            with file('/dev/null', 'w') as g:
                returncode = transform(infile=f, outfile=g)
                self.assertEquals(0, returncode)

    def test_returncode_fail(self):

        transform = xmllint()

        with file(self.id(), 'w') as f:
            f.write('<doc></nondoc>')
        with file(self.id(), 'r') as f:
            with file('/dev/null', 'w') as g:
                returncode = transform(infile=f, outfile=g)
                self.assertEquals(1, returncode)


class TestXmlLintReadable(TestCase):

    def test_xmllint_readable(self):
        from StringIO import StringIO
        f = StringIO('<doc/>')
        with xmllint_readable(f) as g:
            assert isinstance(g, SubprocessReadable)
            linted = g.read()
        self.assertEquals(0, g.subprocess.wait())
        self.assertEquals('<?xml version="1.0"?>\n<doc/>\n', linted)

    def test_xmllint_readable_returns_origianal_if_xmllint_not_found(self):
        from StringIO import StringIO
        f = StringIO('<doc/>')
        g = xmllint_readable(f, xmllint_path='xmllint-nonexistent')
        try:
            self.assertTrue(g is f)
        finally:
            g.close()

    def test_xmllint_readable_error(self):
        from StringIO import StringIO
        f = StringIO('<doc></nondoc>')
        with xmllint_readable(f) as g:
            try:
                g.read()
            except SubprocessError, e:
                self.assertEquals((1,), e.args)


