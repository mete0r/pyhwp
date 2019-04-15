# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2015 mete0r <mete0r@sarangbang.or.kr>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from argparse import ArgumentParser
from contextlib import contextmanager
from contextlib import closing
from functools import partial
from io import BytesIO
import gettext
import io
import logging
import os.path
import sys

from zope.interface.registry import Components

from . import __version__ as version
from .cli import init_logger
from .cli import init_with_environ
from .cli import init_olestorage_opener
from .cli import init_temp_stream_factory
from .cli import init_relaxng
from .cli import init_xslt
from .cli import update_settings_from_environ
from .filestructure import Hwp5FileOpener
from .interfaces import IStorageOpener
from .interfaces import IRelaxNGFactory
from .interfaces import IXSLTFactory
from .utils import mkstemp_open
from .utils import hwp5_resources_path
from .transforms import BaseTransform
from .utils import cached_property


PY3 = sys.version_info.major == 3
if PY3:
    basestring = str
    unicode = str
logger = logging.getLogger(__name__)
locale_dir = os.path.join(os.path.dirname(__file__), 'locale')
locale_dir = os.path.abspath(locale_dir)
t = gettext.translation('hwp5odt', locale_dir, fallback=True)
if PY3:
    _ = t.gettext
else:
    _ = t.ugettext


RESOURCE_PATH_RNG = 'odf-relaxng/OpenDocument-v1.2-os-schema.rng'
RESOURCE_PATH_XSL_SINGLE_DOCUMENT = 'xsl/odt/document.xsl'
RESOURCE_PATH_XSL_STYLE = 'xsl/odt/styles.xsl'
RESOURCE_PATH_XSL_CONTENT = 'xsl/odt/content.xsl'


class ODFValidate:

    def __init__(self, relaxng_factory=None):
        '''
        >>> V = ODFValidate(relaxng_factory)
        '''
        self.relaxng_factory = relaxng_factory

    @cached_property
    def odf_validator(self):
        '''
        >>> with V.odf_validator(sys.stdout) as output:
        ...     output.write(xml)
        '''
        return self.make_odf_validator()

    def make_odf_validator(self):
        if self.relaxng_factory:
            with hwp5_resources_path(RESOURCE_PATH_RNG) as rng_path:
                return self.relaxng_factory.relaxng_validator_from_file(
                    rng_path
                )


class ODTTransform(BaseTransform, ODFValidate):

    def __init__(self, xsltfactory, relaxng_factory,
                 embedbin=False):
        '''
        >>> from hwp5.hwp5odt import ODTTransform
        >>> T = ODTTransform(xsltfactory, relaxng_factory)
        '''
        BaseTransform.__init__(self, xsltfactory, embedbin=embedbin)
        ODFValidate.__init__(self, relaxng_factory)

    @property
    def transform_hwp5_to_styles(self):
        '''
        >>> with io.open('styles.xml', 'wb') as f:
        ...     T.transform_hwp5_to_styles(hwp5file, f)
        '''
        transform_xhwp5 = self.transform_xhwp5_to_styles
        return self.make_transform_hwp5(transform_xhwp5)

    @property
    def transform_hwp5_to_content(self):
        '''
        >>> with io.open('content.xml', 'wb') as f:
        ...     T.transform_hwp5_to_content(hwp5file, f)
        '''
        transform_xhwp5 = self.transform_xhwp5_to_content
        return self.make_transform_hwp5(transform_xhwp5)

    @property
    def transform_hwp5_to_single_document(self):
        '''
        >>> with io.open('transformed.fodt', 'wb') as f:
        ...     T.transform_hwp5_to_single_document(hwp5file, f)
        '''
        transform_xhwp5 = self.transform_xhwp5_to_single_document
        return self.make_transform_hwp5(transform_xhwp5)

    def transform_hwp5_to_package(self, hwp5file, odtpkg):
        '''
        >>> with open_odtpkg('transformed.odt') as odtpkg:
        ...    T.transform_hwp5_to_package(hwp5file, odtpkg)
        '''
        with self.transformed_xhwp5_at_temp(hwp5file) as xml_path:
            self.transform_xhwp5_into_package(xml_path, odtpkg)

        if 'BinData' in hwp5file:
            bindata = hwp5file['BinData']
            for name in bindata:
                f = bindata[name].open()
                path = 'bindata/' + name
                mimetype = 'application/octet-stream'
                odtpkg.insert_stream(f, path, mimetype)

    @cached_property
    def transform_xhwp5_to_styles(self):
        '''
        >>> with io.open('styles.xml', 'wb') as f:
        ...     T.transform_xhwp5_to_styles('input.xml', f)
        '''
        resource_path = RESOURCE_PATH_XSL_STYLE
        return self.make_odf_transform(resource_path)

    @cached_property
    def transform_xhwp5_to_content(self):
        '''
        >>> with io.open('content.xml', 'wb') as f:
        ...     T.transform_xhwp5_to_content('input.xml', f)
        '''
        resource_path = RESOURCE_PATH_XSL_CONTENT
        return self.make_odf_transform(resource_path)

    @cached_property
    def transform_xhwp5_to_single_document(self):
        '''
        >>> with io.open('transformed.fodf', 'wb') as f:
        ...     T.transform_xhwp5_to_single_document('input.xml', f)
        '''
        resource_path = RESOURCE_PATH_XSL_SINGLE_DOCUMENT
        return self.make_odf_transform(resource_path)

    @property
    def transform_xhwp5_into_package(self):
        '''
        >>> with open_odtpkg('transformed.odt') as odtpkg:
        >>>     T.transform_xhwp5_into_package('input.xml', odtpkg)
        '''
        def transform(xhwp5path, odtpkg):
            with self.transformed_styles_at_temp(xhwp5path) as path:
                odtpkg.insert_path(path, 'styles.xml', 'text/xml')
            with self.transformed_content_at_temp(xhwp5path) as path:
                odtpkg.insert_path(path, 'content.xml', 'text/xml')

            rdf = BytesIO()
            manifest_rdf(rdf)
            rdf.seek(0)
            odtpkg.insert_stream(rdf, 'manifest.rdf',
                                 'application/rdf+xml')
        return transform

    def transformed_styles_at_temp(self, xhwp5path):
        '''
        >>> with T.transformed_styles_at_temp('input.xml') as styles_path:
        ...     pass
        '''
        transform_xhwp5 = self.transform_xhwp5_to_styles
        return transformed_at_temp_path(xhwp5path, transform_xhwp5)

    def transformed_content_at_temp(self, xhwp5path):
        '''
        >>> with T.transformed_content_at_temp('input.xml') as content_path:
        ...     pass
        '''
        transform_xhwp5 = self.transform_xhwp5_to_content
        return transformed_at_temp_path(xhwp5path, transform_xhwp5)

    def transformed_single_document_at_temp(self, xhwp5path):
        '''
        >>> with T.transformed_single_document_at_temp('input.xml') as path:
        ...     pass
        '''
        transform_xhwp5 = self.transform_xhwp5_to_single_document
        return transformed_at_temp_path(xhwp5path, transform_xhwp5)

    def make_odf_transform(self, resource_path):
        transform = self.make_xsl_transform(resource_path)
        validator = self.odf_validator
        if validator:
            def validating_transform(input, output):
                with validator.validating_output(output) as output:
                    transform(input, output)
            return validating_transform
        else:
            return transform


@contextmanager
def transformed_at_temp_path(inp_path, transform):
    with mkstemp_open() as (tmp_path, f):
        transform(inp_path, f)
        f.flush()
        yield tmp_path


class ODTPackage(object):
    def __init__(self, path_or_zipfile):
        self.files = []

        if isinstance(path_or_zipfile, basestring):
            from zipfile import ZipFile
            zipfile = ZipFile(path_or_zipfile, 'w')
        else:
            zipfile = path_or_zipfile
        self.zf = zipfile

    def insert_path(self, src_path, path, media_type):
        with io.open(src_path, 'rb') as f:
            self.insert_stream(f, path, media_type)

    def insert_stream(self, f, path, media_type):
        if not isinstance(path, unicode):
            path = path.decode('utf-8')
        self.zf.writestr(path, f.read())
        self.files.append(dict(full_path=path, media_type=media_type))

    def close(self):

        manifest = BytesIO()
        manifest_xml(manifest, self.files)
        manifest.seek(0)
        self.zf.writestr('META-INF/manifest.xml', manifest.getvalue())
        self.zf.writestr('mimetype', 'application/vnd.oasis.opendocument.text')

        self.zf.close()


def manifest_xml(f, files):
    from xml.sax.saxutils import XMLGenerator
    xml = XMLGenerator(f, 'utf-8')
    xml.startDocument()

    uri = 'urn:oasis:names:tc:opendocument:xmlns:manifest:1.0'
    prefix = 'manifest'
    xml.startPrefixMapping(prefix, uri)

    def startElement(name, attrs):
        attrs = dict(((uri, n), v) for n, v in attrs.items())
        xml.startElementNS((uri, name), prefix + ':' + name, attrs)

    def endElement(name):
        xml.endElementNS((uri, name), prefix + ':' + name)

    def file_entry(full_path, media_type, **kwargs):
        attrs = {'media-type': media_type, 'full-path': full_path}
        attrs.update(dict((n.replace('_', '-'), v)
                          for n, v in kwargs.items()))
        startElement('file-entry', attrs)
        endElement('file-entry')

    startElement('manifest', dict(version='1.2'))
    file_entry('/', 'application/vnd.oasis.opendocument.text', version='1.2')
    for e in files:
        e = dict(e)
        full_path = e.pop('full_path')
        media_type = e.pop('media_type', 'application/octet-stream')
        file_entry(full_path, media_type)
    endElement('manifest')

    xml.endPrefixMapping(prefix)
    xml.endDocument()


def manifest_rdf(f):
    f.write(b'''<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:pkg="http://docs.oasis-open.org/ns/office/1.2/meta/pkg#"
    xmlns:odf="http://docs.oasis-open.org/ns/office/1.2/meta/odf#">
    <pkg:Document rdf:about="">
        <pkg:hasPart rdf:resource="content.xml"/>
        <pkg:hasPart rdf:resource="styles.xml"/>
    </pkg:Document>
    <odf:ContentFile rdf:about="content.xml"/>
    <odf:StylesFile rdf:about="styles.xml"/>
</rdf:RDF>''')


def main():
    from .dataio import ParseError
    from .errors import InvalidHwp5FileError
    from .utils import make_open_dest_file
    from .xmlmodel import Hwp5File

    argparser = main_argparser()
    args = argparser.parse_args()
    init_logger(args)

    init_with_environ()

    settings = {}
    registry = Components()
    update_settings_from_environ(settings)
    init_olestorage_opener(registry, **settings)
    init_temp_stream_factory(registry, **settings)
    init_xslt(registry, **settings)
    init_relaxng(registry, **settings)

    olestorage_opener = registry.getUtility(IStorageOpener)
    hwp5file_opener = Hwp5FileOpener(olestorage_opener, Hwp5File)

    hwp5path = args.hwp5file

    xsltfactory = registry.getUtility(IXSLTFactory)
    relaxng_factory = registry.getUtility(IRelaxNGFactory)
    odt_transform = ODTTransform(xsltfactory, relaxng_factory)

    open_dest = make_open_dest_file(args.output)
    if args.document:
        odt_transform.embedbin = not args.no_embed_image
        transform = odt_transform.transform_hwp5_to_single_document
        open_dest = wrap_for_xml(open_dest)
    elif args.styles:
        odt_transform.embedbin = args.embed_image
        transform = odt_transform.transform_hwp5_to_styles
        open_dest = wrap_for_xml(open_dest)
    elif args.content:
        odt_transform.embedbin = args.embed_image
        transform = odt_transform.transform_hwp5_to_content
        open_dest = wrap_for_xml(open_dest)
    else:
        odt_transform.embedbin = args.embed_image
        transform = odt_transform.transform_hwp5_to_package
        dest_path = args.output
        dest_path = dest_path or replace_ext(hwp5path, '.odt')
        open_dest = partial(open_odtpkg, dest_path)

    try:
        with closing(hwp5file_opener.open_hwp5file(hwp5path)) as hwp5file:
            with open_dest() as dest:
                transform(hwp5file, dest)
    except ParseError as e:
        e.print_to_logger(logger)
    except InvalidHwp5FileError as e:
        logger.error('%s', e)
        sys.exit(1)


def main_argparser():
    parser = ArgumentParser(
        prog='hwp5odt',
        description=_('HWPv5 to odt converter'),
    )
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {}'.format(version)
    )
    parser.add_argument(
        '--loglevel',
        help=_('Set log level.'),
    )
    parser.add_argument(
        '--logfile',
        help=_('Set log file.'),
    )
    parser.add_argument(
        '--output',
        help=_('Output file'),
    )
    parser.add_argument(
        'hwp5file',
        metavar='<hwp5file>',
        help=_('.hwp file to convert'),
    )
    generator_group = parser.add_mutually_exclusive_group()
    generator_group.add_argument(
        '--styles',
        action='store_true',
        help=_('Generate styles.xml'),
    )
    generator_group.add_argument(
        '--content',
        action='store_true',
        help=_('Generate content.xml'),
    )
    generator_group.add_argument(
        '--document',
        action='store_true',
        help=_('Generate .fodt'),
    )
    embedimage = parser.add_mutually_exclusive_group()
    embedimage.add_argument(
        '--embed-image',
        action='store_true',
        help=_('Embed images in output xml.'),
    )
    embedimage.add_argument(
        '--no-embed-image',
        action='store_true',
        help=_('Do not embed images in output xml.'),
    )
    return parser


def replace_ext(path, ext):
    name = os.path.basename(path)
    root = os.path.splitext(name)[0]
    return root + ext


@contextmanager
def open_odtpkg(path):
    odtpkg = ODTPackage(path)
    with closing(odtpkg):
        yield odtpkg


def wrap_for_xml(open_dest):
    from .utils import wrap_open_dest_for_tty
    from .utils import pager
    from .utils import syntaxhighlight
    from .utils import xmllint
    return wrap_open_dest_for_tty(open_dest, [
        pager(),
        syntaxhighlight('application/xml'),
        xmllint(format=True),
    ])
