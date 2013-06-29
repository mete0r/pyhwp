# -*- coding: utf-8 -*-
from __future__ import with_statement

import logging
import sys
import os.path

import colorama
from colorama import Fore, Back, Style
from docopt import docopt

from jxml.etree import XSLTCoverage
from jxml.etree import xsltcoverage


def colorama_init(f):
    def wrapper(*args, **kwargs):
        colorama.init()
        try:
            return f(*args, **kwargs)
        finally:
            colorama.deinit()
    return wrapper


@colorama_init
def annotate_main():
    __doc__ = '''
    Usage: jxml-annotate [options] <xml-file>...

    <xml-file>  Cobertura-compatible coverage data file
    --color=[auto|yes|no]    Output with colors

    Example:
        jxml-annotate --color=yes coverage.xml | less -R
    '''
    args = docopt(__doc__)

    logging.basicConfig()
    logger = logging.getLogger('jxml.annotate')

    use_color = args['--color'] == 'yes'
    if args['--color'] in ('auto', None):
        use_color = sys.stdout.isatty()

    coverage = XSLTCoverage()
    for arg in args['<xml-file>']:
        coverage.read_from(arg)

    traces = coverage.traces
    for filename in sorted(traces):
        covered_lines = traces[filename]
        if not os.path.exists(filename):
            logger.info('skipping %s: not exists', filename)
            continue
        print filename

        with open(filename) as f:
            for line_no, line in enumerate(f):
                line_no += 1
                count = covered_lines.get(line_no, 0)
                annotated = '%8d: %s' % (count, line)

                if use_color:
                    if count == 0:
                        color = Fore.RED
                    else:
                        color = Fore.RESET
                    annotated = color + annotated + Fore.RESET
                sys.stdout.write(annotated)

    print ''


def load_tests(filenames):
    import unittest
    ts = unittest.TestSuite()
    testloader = unittest.defaultTestLoader
    for filename in filenames:
        d = dict()
        execfile(filename, d)
        for name in d:
            x = d[name]
            if isinstance(x, type) and issubclass(x, unittest.TestCase):
                ts.addTests(testloader.loadTestsFromTestCase(x))
    return ts


def cov_test_main():
    __doc__ = '''
    Usage: jxml-cov-test [options] <output-file> <unittest-file>...

    <output-file>       Cobertura-compatible coverage data file.
    <unittest-file>     unittest files.

    Example:
        jxml-cov-test coverage.xml test1.py test2.py
    '''
    args = docopt(__doc__)

    logging.basicConfig()
    logger = logging.getLogger('jxml.cov-test')

    from java.lang import System
    import unittest

    props = System.getProperties()
    props['javax.xml.transform.TransformerFactory'] = 'org.apache.xalan.processor.TransformerFactoryImpl'
    props['javax.xml.parsers.DocumentBuilderFactory'] = 'org.apache.xerces.jaxp.DocumentBuilderFactoryImpl'
    props['javax.xml.parsers.SAXParserFactory'] = 'org.apache.xerces.jaxp.SAXParserFactoryImpl'

    output_name = args['<output-file>']
    test_filenames = args['<unittest-file>']
    ts = load_tests(test_filenames)
    runner = unittest.TextTestRunner()
    with xsltcoverage(output_name) as coverage:
        runner.run(ts)
