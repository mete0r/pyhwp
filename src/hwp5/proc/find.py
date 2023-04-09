# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2023 mete0r <https://github.com/mete0r>
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
''' Find record models with specified predicates.

Usage::

    hwp5proc find [--model=<model-name> | --tag=<hwptag>]
                  [--incomplete] [--dump] [--format=<format>]
                  [--loglevel=<loglevel>] [--logfile=<logfile>]
                  (--from-stdin | <hwp5files>...)
    hwp5proc find --help

Options::

    -h --help               Show this screen
       --loglevel=<level>   Set log level.
       --logfile=<file>     Set log file.

       --from-stdin         get filenames fro stdin

       --model=<model-name> filter with record model name
       --tag=<hwptag>       filter with record HWPTAG
       --incomplete         filter with incompletely parsed content

       --format=<format>    record output format
                            %(filename)s %(stream)s %(seqno)s %(type)s
       --dump               dump record

    <hwp5files>...          HWPv5 files (*.hwp)

Example: Find paragraphs::

    $ hwp5proc find --model=Paragraph samples/*.hwp
    $ hwp5proc find --tag=HWPTAG_PARA_TEXT samples/*.hwp
    $ hwp5proc find --tag=66 samples/*.hwp

Example: Find and dump records of ``HWPTAG_LIST_HEADER`` which is parsed
incompletely::

    $ hwp5proc find --tag=HWPTAG_LIST_HEADER --incomplete --dump samples/*.hwp

'''
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from functools import partial
import logging
import itertools
import sys

from ..binmodel import Hwp5File
from ..binmodel import model_to_json
from ..bintype import log_events
from ..dataio import ParseError
from ..tagids import tagnames


PY2 = sys.version_info.major == 2
if PY2:
    ifilter = itertools.ifilter
    imap = itertools.imap
else:
    ifilter = filter
    imap = map


logger = logging.getLogger(__name__)


def main(args):
    filenames = filenames_from_args(args)

    conditions = list(conditions_from_args(args))
    filter_conditions = partial(
        ifilter, lambda m: all(condition(m) for condition in conditions)
    )

    print_model = printer_from_args(args)

    for filename in filenames:
        try:
            models = hwp5file_models(filename)
            models = filter_conditions(models)
            for model in models:
                print_model(model)
        except ParseError as e:
            logger.error('---- On processing %s:', filename)
            e.print_to_logger(logger)


def find_argparser(subparsers, _):
    parser = subparsers.add_parser(
        'find',
        help=_(
            'Find record models with specified predicates.'
        ),
        description=_(
            'Find record models with specified predicates.'
        ),
    )
    parser.add_argument(
        'hwp5files',
        nargs='*',
        metavar='<hwp5files>',
        help=_('.hwp files to analyze'),
    )
    parser.add_argument(
        '--from-stdin',
        action='store_true',
        help=_('get filenames from stdin'),
    )
    filter_group = parser.add_mutually_exclusive_group()
    filter_group.add_argument(
        '--model',
        metavar='<model-name>',
        help=_(
            'filter with record model name'
        ),
    )
    filter_group.add_argument(
        '--tag',
        metavar='<hwptag>',
        help=_(
            'filter with record HWPTAG'
        ),
    )
    parser.add_argument(
        '--incomplete',
        action='store_true',
        help=_('filter with incompletely parsed content'),
    )
    parser.add_argument(
        '--format',
        metavar='<format>',
        help=_(
            'record output format'
        ),
    )
    parser.add_argument(
        '--dump',
        action='store_true',
        help=_('dump record'),
    )
    parser.set_defaults(func=main)
    return parser


def filenames_from_args(args):
    if args.from_stdin:
        return filenames_from_stdin(args)
    return args.hwp5files


def filenames_from_stdin(args):
    return imap(lambda line: line[:-1], sys.stdin)


def conditions_from_args(args):

    if args.model:
        def with_model_name(model):
            return args.model == model['type'].__name__
        yield with_model_name

    if args.tag:
        tag = args.tag
        try:
            tag = int(tag)
        except ValueError:
            pass
        else:
            tag = tagnames[tag]

        def with_tag(model):
            return model['tagname'] == tag
        yield with_tag

    if args.incomplete:
        def with_incomplete(model):
            return 'unparsed' in model
        yield with_incomplete


def hwp5file_models(filename):
    hwp5file = Hwp5File(filename)
    for model in flat_models(hwp5file):
        model['filename'] = filename
        yield model


def flat_models(hwp5file, **kwargs):
    for model in hwp5file.docinfo.models(**kwargs):
        model['stream'] = 'DocInfo'
        yield model

    for section in hwp5file.bodytext:
        for model in hwp5file.bodytext[section].models(**kwargs):
            model['stream'] = 'BodyText/' + section
            yield model


def printer_from_args(args):

    if args.format:
        fmt = args.format
    else:
        fmt = '%(filename)s %(stream)s %(seqno)s %(tagname)s %(type)s'

    dump = args.dump

    def print_model(model):
        printable_model = dict(model, type=model['type'].__name__)
        print(fmt % printable_model)
        if dump:
            print(model_to_json(model, sort_keys=True, indent=2))

            def print_log(fmt, *args):
                print(fmt % args)
            list(log_events(model['binevents'], print_log))
    return print_model
