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
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
from contextlib import closing
from contextlib import contextmanager
from tempfile import mkdtemp
import gettext
import io
import logging
import os.path
import shutil
import sys
import urllib

from docopt import docopt

from hwp5 import __version__ as version
from hwp5.proc import rest_to_docopt
from hwp5.proc import init_logger
from hwp5.xmlmodel import Hwp5File
from hwp5.hwp5html import HTMLTransform


PY3 = sys.version_info.major == 3
logger = logging.getLogger(__name__)
locale_dir = os.path.join(os.path.dirname(__file__), '..', 'locale')
locale_dir = os.path.abspath(locale_dir)
t = gettext.translation('hwp5view', locale_dir, fallback=True)
if PY3:
    _ = t.gettext
else:
    _ = t.ugettext


def main():
    doc = rest_to_docopt(__doc__)
    args = docopt(doc, version=version)
    init_logger(args)

    runner = runner_factory()

    with make_temporary_directory() as out_dir:
        with hwp5html(args['<hwp5file>'], out_dir) as index_path:
            runner(args, index_path, out_dir)


def runner_factory():
    try:
        return runner_factory_gi()
    except ImportError:
        pass

    try:
        return runner_factory_pyside()
    except ImportError:
        pass

    raise NotImplementedError(
        'Neither gi.repository.WebKit nor pyside is found'
    )


def runner_factory_gi():
    from gi.repository import Gtk
    from gi.repository import WebKit

    def runner(args, index_path, out_dir):
        base_uri = fspath2url(out_dir) + '/'
        # index_uri = fspath2url(index_path)
        with io.open(index_path, 'rb') as f:
            content = f.read()

        view = WebKit.WebView()
        # view.load_uri(index_uri)
        view.load_string(content, 'text/html', 'utf-8', base_uri)

        def on_load(webview, webframe):
            script = ('window.location.href = "dimension:" '
                      '+ document.body.scrollWidth + "x"'
                      '+ document.body.scrollHeight')
            webview.execute_script(script)

        MIN_WIDTH = 300
        MIN_HEIGHT = 400
        MAX_WIDTH = 1024
        MAX_HEIGHT = 800

        view.connect('load-finished', on_load)

        def on_navigation_requested(webview, frame, req, data=None):
            uri = req.get_uri()
            scheme, path = uri.split(':', 1)
            if scheme == 'dimension':
                width, height = path.split('x', 1)
                width = int(width)
                height = int(height)
                width = min(width, MAX_WIDTH)
                height = min(height, MAX_HEIGHT)
                width = max(width, MIN_WIDTH)
                height = max(height, MIN_HEIGHT)
                window.resize(width + 4, height)
                return True
            return False

        view.connect('navigation-requested', on_navigation_requested)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(view)

        vbox = Gtk.VBox()
        vbox.pack_start(scrolled_window, expand=True, fill=True, padding=0)

        window = Gtk.Window()
        window.add(vbox)
        window.connect('delete-event', Gtk.main_quit)
        window.set_default_size(600, 800)
        window.show_all()

        Gtk.main()

    return runner


def runner_factory_pyside():
    from PySide.QtCore import QUrl
    from PySide.QtGui import QApplication
    from PySide.QtGui import QMainWindow
    from PySide.QtWebKit import QWebView

    class MainWindow(QMainWindow):
        pass

    def runner(args, index_path, out_dir):
        app = QApplication(sys.argv)

        frame = MainWindow()
        frame.setWindowTitle('hwp5view')
        frame.setMinimumWidth(400)

        url = fspath2url(index_path)
        url = QUrl(url)
        view = QWebView(frame)

        logger.info('Loading...')
        view.load(url)

        @view.loadFinished.connect
        def onLoadFinished():
            frame.show()

        frame.setCentralWidget(view)

        app.exec_()

    return runner


@contextmanager
def make_temporary_directory(*args, **kwargs):
    path = mkdtemp(*args, **kwargs)
    try:
        logger.warning('temporary directory for contents: %s', path)
        yield path
    finally:
        shutil.rmtree(path)


@contextmanager
def hwp5html(filename, out_dir):
    with closing(Hwp5File(filename)) as hwp5file:
        HTMLTransform().transform_hwp5_to_dir(hwp5file, out_dir)
        yield os.path.join(out_dir, 'index.xhtml')


def fspath2url(path):
    path = os.path.abspath(path)
    return 'file://' + urllib.pathname2url(path)
