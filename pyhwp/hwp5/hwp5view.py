# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2014 mete0r <mete0r@sarangbang.or.kr>
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
'''HWP5 viewer (Experimental, gtk only)

Usage::

    hwp5view [options] <hwp5file>
    hwp5view -h | --help
    hwp5view --version

Options::

    -h --help           Show this screen
    --version           Show version
    --loglevel=<level>  Set log level.
    --logfile=<file>    Set log file.
'''
from __future__ import with_statement
from contextlib import closing
from contextlib import contextmanager
from tempfile import mkdtemp
import logging
import os.path
import shutil
import urllib

from gi.repository import Gtk
from gi.repository import WebKit
from docopt import docopt

from hwp5 import __version__ as version
from hwp5.proc import rest_to_docopt
from hwp5.proc import init_logger
from hwp5.xmlmodel import Hwp5File
from hwp5.hwp5html import generate_htmldir


logger = logging.getLogger(__name__)


def main():
    doc = rest_to_docopt(__doc__)
    args = docopt(doc, version=version)
    init_logger(args)

    with make_temporary_directory() as out_dir:
        with hwp5html(args['<hwp5file>'], out_dir) as index_path:
            base_uri = fspath2url(out_dir) + '/'
            # index_uri = fspath2url(index_path)
            with file(index_path) as f:
                content = f.read()

            view = WebKit.WebView()
            # view.load_uri(index_uri)
            view.load_string(content, 'text/html', 'utf-8', base_uri)

            scrolled_window = Gtk.ScrolledWindow()
            scrolled_window.add(view)

            vbox = Gtk.VBox()
            vbox.pack_start(scrolled_window, expand=True, fill=True, padding=0)

            window = Gtk.Window()
            window.add(vbox)
            window.connect('delete-event', Gtk.main_quit)
            window.set_default_size(600, 400)
            window.show_all()

            Gtk.main()


@contextmanager
def make_temporary_directory(*args, **kwargs):
    path = mkdtemp(*args, **kwargs)
    try:
        yield path
    finally:
        shutil.rmtree(path)


@contextmanager
def hwp5html(filename, out_dir):
    with closing(Hwp5File(filename)) as hwp5file:
        generate_htmldir(hwp5file, out_dir)
        yield os.path.join(out_dir, 'index.xhtml')


def fspath2url(path):
    path = os.path.abspath(path)
    return 'file://' + urllib.pathname2url(path)
