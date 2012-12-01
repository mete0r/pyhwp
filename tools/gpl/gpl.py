# -*- coding: utf-8 -*-
'''
Usage:
    gpl [options] <files>...
    gpl -h | --help
    gpl --version

Options:
    -h --help           Show this screen
    --version           Show version
    --year=<year>       Add release year
'''
import re
import os
import shutil
import logging
import tempfile


logger = logging.getLogger(__name__)


def main():
    from docopt import docopt
    args = docopt(__doc__, version='0.0.0')

    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())

    filters = []

    year = args['--year']
    if year is not None:
        year = year.strip()
        year = int(year)
        filter = copyright_filter(Copyright.add_years, year)
        filters.append(filter)

    filenames = args['<files>']

    if len(filters) > 0:
        for filename in filenames:
            logger.info('filename: %s', filename)
            try:
                with file(filename) as f:
                    lines = f
                    for filt in filters:
                        lines = filt(lines)
                    lines = list(lines)
            except IOError, e:
                logger.exception(e)

            temp_fd, tempname = tempfile.mkstemp()
            try:
                with os.fdopen(temp_fd, 'w') as tmpf:
                    for line in lines:
                        tmpf.write(line)
                shutil.copyfile(tempname, filename)
            finally:
                os.unlink(tempname)


RE_COPYRIGHT = re.compile(r'(.*)Copyright +\(C\) +([0-9,]+) +(.*)')


class Copyright(object):

    def __init__(self, years, authors):
        self.years = set(years)
        self.authors = list(authors)

    def generate(self):
        years = ','.join(str(x) for x in sorted(self.years))
        authors = ', '.join(self.authors)
        yield 'Copyright (C) ' + years + ' ' + authors + '\n'

    def add_years(self, *years):
        for year in years:
            self.years.add(year)
        return self


def copyright_filter(handler, *args, **kwargs):
    def filter(lines):
        for line in lines:
            m = RE_COPYRIGHT.match(line)
            if m:
                prefix = m.group(1)
                years = m.group(2).strip().split(',')
                years = set(int(x) for x in years)
                authors = m.group(3).strip().split(',')
                logger.info('year: %s, authors: %s', years, authors)
                copyright = Copyright(years, authors)
                copyright = handler(copyright, *args, **kwargs)
                for line in copyright.generate():
                    yield prefix + line
            else:
                yield line
    return filter
