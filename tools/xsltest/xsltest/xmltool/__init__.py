# -*- coding: utf-8 -*-
from __future__ import with_statement
import sys
import logging

from docopt import docopt

__version__ = '0.0'

doc = ''' XML Tools

Usage:
    xmltool <command> [<args>...]
    xmltool [--version]
    xmltool [--help]
    xmltool [--help-commands]

       --version        Show version and copyright information.
    -h --help           Show help messages.
       --help-commands  Show available commands.
'''

subcommands = ['subtree', 'wrap', 'xslt']

help_commands = '''Available <command> values:

    ''' + '\n    '.join(subcommands) + '''

See 'xmltool <command> --help' for more information on a specific command.'''


def main():
    logging.basicConfig(level=logging.DEBUG)
    args = docopt(doc, version=__version__, help=False, options_first=True)

    if args['--help-commands']:
        print doc,
        print help_commands
        return 0

    command = args['<command>']
    if command not in subcommands:
        print(doc.strip())
        return 1

    argv = [command] + args['<args>']
    mod = __import__('xsltest.xmltool.'+command.replace('-', '_'), fromlist=['main'])
    old_argv = sys.argv
    sys.argv = argv
    try:
        return mod.main()
    finally:
        sys.argv = old_argv
