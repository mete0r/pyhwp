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
import code
import logging
import os
import textwrap

from zope.interface.registry import Components

from .filestructure import Hwp5FileOpener
from .interfaces import IStorageOpener
from .interfaces import ITemporaryStreamFactory
from .interfaces import IRelaxNGFactory
from .interfaces import IXSLTFactory
from .plat import createOleStorageOpener
from .plat import _lxml
from .plat import javax_transform
from .plat import _uno
from .plat import xsltproc
from .plat import xmllint
from .storage import ExtraItemStorage
from .storage import open_storage_item
from .utilities import TemporaryStreamFactory
from .xmlmodel import Hwp5File


logger = logging.getLogger(__name__)


def init_logger(args):
    logger = logging.getLogger('hwp5')
    try:
        from colorlog import ColoredFormatter
    except ImportError:
        formatter = None
    else:
        formatter = ColoredFormatter(
            '%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s',
            datefmt=None, reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red'
            }
        )

    loglevel = args.loglevel
    if not loglevel:
        loglevel = os.environ.get('PYHWP_LOGLEVEL')
    if loglevel:
        levels = dict(debug=logging.DEBUG,
                      info=logging.INFO,
                      warning=logging.WARNING,
                      error=logging.ERROR,
                      critical=logging.CRITICAL)
        loglevel = loglevel.lower()
        loglevel = levels.get(loglevel, logging.WARNING)
        logger.setLevel(loglevel)

    logfile = args.logfile
    if not logfile:
        logfile = os.environ.get('PYHWP_LOGFILE')
    if logfile:
        handler = logging.FileHandler(logfile)
    else:
        handler = logging.StreamHandler()
    if formatter:
        handler.setFormatter(formatter)
    logger.addHandler(handler)


def init_with_environ():
    if 'PYHWP_XSLTPROC' in os.environ:
        xsltproc.executable = os.environ['PYHWP_XSLTPROC']
        xsltproc.enable()

    if 'PYHWP_XMLLINT' in os.environ:
        xmllint.executable = os.environ['PYHWP_XMLLINT']
        xmllint.enable()


def update_settings_from_environ(settings):
    if 'PYHWP_XSLTPROC' in os.environ:
        settings['xsltproc.path'] = os.environ['PYHWP_XSLTPROC']
    if 'PYHWP_XMLLINT' in os.environ:
        settings['xmllint.path'] = os.environ['PYHWP_XMLLINT']


def init_temp_stream_factory(registry, **settings):
    factory = TemporaryStreamFactory()
    registry.registerUtility(factory, ITemporaryStreamFactory)


def init_olestorage_opener(registry, **settings):
    opener = create_olestorage_opener(registry, **settings)
    if opener is None:
        logger.warning('olestorage: No implementation is available.')
        return
    registry.registerUtility(opener, IStorageOpener)


def create_olestorage_opener(registry, **settings):
    return createOleStorageOpener(registry, **settings)


def init_xslt(registry, **settings):
    factory = create_xslt_factory(registry, **settings)
    if factory is None:
        logger.warning('XSLT: No implementation is available.')
        return
    registry.registerUtility(factory, IXSLTFactory)


def create_xslt_factory(registry, **settings):
    try:
        factory = _lxml.createXSLTFactory(registry, **settings)
    except Exception:
        logger.debug('XSLT: lxml is not available.')
    else:
        logger.info('XSLT: lxml')
        return factory

    try:
        factory = javax_transform.createXSLTFactory(registry, **settings)
    except Exception:
        logger.debug('XSLT: javax.xml.transform is not available.')
    else:
        logger.info('XSLT: javax.xml.transform')
        return factory

    try:
        factory = _uno.createXSLTFactory(registry, **settings)
    except Exception:
        logger.debug('XSLT: uno is not available.')
    else:
        logger.info('XSLT: uno')
        return factory

    try:
        factory = xsltproc.createXSLTFactory(registry, **settings)
    except Exception:
        logger.debug('XSLT: xsltproc is not available.')
    else:
        logger.info('XSLT: xsltproc')
        return factory


def init_relaxng(registry, **settings):
    relaxng_factory = create_relaxng_factory(registry, **settings)
    if relaxng_factory is None:
        logger.warning('RelaxNG: No implementation is available.')
        return
    registry.registerUtility(relaxng_factory, IRelaxNGFactory)


def create_relaxng_factory(registry, **settings):
    try:
        factory = _lxml.createRelaxNGFactory(registry, **settings)
    except Exception as e:
        logger.debug('RelaxNG: lxml is not available.')
        logger.debug('RelaxNG: (%s)', e)
    else:
        logger.info('RelaxNG: lxml')
        return factory

    try:
        factory = xmllint.createRelaxNGFactory(registry, **settings)
    except Exception as e:
        logger.debug('RelaxNG: xmllint is not available.')
        logger.debug('RelaxNG: (%s)', e)
    else:
        logger.info('RelaxNG: xmllint')
        return factory


def open_hwpfile(registry, args):
    filename = args.hwp5file
    olestorage_opener = registry.getUtility(IStorageOpener)
    olestorage = olestorage_opener.open_storage(filename)

    if args.ole:
        return olestorage

    hwpfile = Hwp5File(olestorage)
    if args.vstreams:
        hwpfile = ExtraItemStorage(hwpfile)
    return hwpfile


def parse_recordstream_name(hwpfile, streamname):
    if streamname == 'docinfo':
        return hwpfile.docinfo
    segments = streamname.split('/')
    if len(segments) == 2:
        if segments[0] == 'bodytext':
            try:
                idx = int(segments[1])
                return hwpfile.bodytext.section(idx)
            except ValueError:
                pass
    return open_storage_item(hwpfile, streamname)


def hwp5shell():
    argparser = hwp5shell_argparser()
    args = argparser.parse_args()
    init_logger(args)

    registry = Components()
    init_olestorage_opener(registry)
    olestorage_opener = registry.getUtility(IStorageOpener)
    hwp5file_opener = Hwp5FileOpener(olestorage_opener, Hwp5File)
    namespace = {
        'registry': registry,
        'open_ole': olestorage_opener.open_storage,
        'open_hwp': hwp5file_opener.open_hwp5file,
        'Hwp5File': Hwp5File,
        'Hwp5FileOpener': Hwp5FileOpener,
    }
    if args.hwp5file is not None:
        hwp5file = hwp5file_opener.open_hwp5file(args.hwp5file)
        namespace['hwp5file'] = hwp5file

    banner = textwrap.dedent(
        '''
        --------------------------------
        hwp5shell
        --------------------------------
        registry:
            the component registry.

        open_ole(filename) -> IStorage:
            open an OLE Compound File.

        open_hwp(filename) -> IHwp5File:
            open a .hwp(v5) file.
        '''
    ).strip()
    code.interact(banner=banner, local=namespace)


def hwp5shell_argparser():
    from . import __version__ as version

    def _(s):
        return s

    parser = ArgumentParser(
        prog='hwp5txt',
        description=_('HWPv5 to txt converter'),
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
        'hwp5file',
        nargs='?',
        metavar='<hwp5file>',
        help=_('.hwp file to convert'),
    )
    return parser
