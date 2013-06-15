
# -*- coding: utf-8 -*-
import os
import sys
import logging

from docopt import docopt
from lxml import etree

from xsltest.xmltool import __version__
from xsltest import context_xslt

logger = logging.getLogger(__name__)


doc = ''' xmltool xslt

Usage:
    xmltool-xslt [--wrap=WRAP --mode=MODE --select=SELECT] <stylesheet>
    xmltool-xslt --help

Options:

    -h --help               Show this screen

'''


def main():
    logger.debug('argv: %r', sys.argv)
    args = docopt(doc, version=__version__)
    logger.debug('args: %r', args)

    stylesheet_path = os.path.abspath(args['<stylesheet>'])
    params = dict(stylesheet_path=stylesheet_path,
                  wrap=args['--wrap'], mode=args['--mode'],
                  select=args['--select'])
    # TODO: workaround
    params['sourceline'] = 0

    execute = context_xslt(params)

    xmldoc = etree.parse(sys.stdin)
    result = execute(xmldoc.getroot())
    result = etree.tostring(result, xml_declaration=True, encoding='utf-8')
    sys.stdout.write(result)
