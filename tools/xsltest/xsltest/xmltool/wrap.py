# -*- coding: utf-8 -*-
import sys
import logging

from docopt import docopt
from lxml import etree

from xsltest.xmltool import __version__
from xsltest import context_wrap_subnodes

logger = logging.getLogger(__name__)


doc = ''' xmltool wrap

Usage:
    xmltool-wrap <xpath>
    xmltool-wrap --help

Options:

    -h --help               Show this screen

'''


def main():
    logger.debug('argv: %r', sys.argv)
    args = docopt(doc, version=__version__)
    logger.debug('args: %r', args)

    params = dict(xpath=args['<xpath>'])
    # TODO: workaround
    params['sourceline'] = 0

    execute = context_wrap_subnodes(params)

    xmldoc = etree.parse(sys.stdin)
    result = execute(xmldoc.getroot())
    result = etree.tostring(result, xml_declaration=True, encoding='utf-8')
    sys.stdout.write(result)
