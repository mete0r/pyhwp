# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010 https://github.com/mete0r
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
from __future__ import with_statement
import contextlib
import logging


logger = logging.getLogger(__name__)


@contextlib.contextmanager
def soffice_subprocess(**kwargs):
    ''' Create an remote instance of soffice '''

    args = [kwargs.get('soffice', 'soffice')]

    if 'accept' in kwargs:
        args.append('--accept=%s' % kwargs['accept'])
    
    if kwargs.get('headless', True):
        args.append('--headless')

    if kwargs.get('invisible', True):
        args.append('--invisible')

    if kwargs.get('nologo', True):
        args.append('--nologo')

    if kwargs.get('norestore', True):
        args.append('--norestore')

    if kwargs.get('nodefault', True):
        args.append('--nodefault')

    if kwargs.get('nofirstwizard', True):
        args.append('--nofirstwizard')

    import subprocess
    p = subprocess.Popen(args)
    pid = p.pid
    logger.info('soffice(%s) has been started.', pid)
    try:
        yield p
    finally:
        import time
        n = 0
        p.poll()
        while p.returncode is None:
            n += 1
            if n > 3:
                p.kill()
                logger.info('trying to kill soffice(%s)', pid)
                return
            p.terminate()
            time.sleep(1)
            p.poll()
        logger.info('soffice(%s) has been terminated with exit code %d',
                    pid, p.returncode)


def connect_remote_context(uno_link, max_tries=10):
    ''' Connect to the remote soffice instance and get the context. '''

    from unokit.services import css
    resolver = css.bridge.UnoUrlResolver()
    uno_url = 'uno:'+uno_link+'StarOffice.ComponentContext'
    logger.info('uno_url: %s', uno_url)
    from com.sun.star.connection import NoConnectException
    while True:
        max_tries -= 1

        try:
            return resolver.resolve(uno_url)
        except NoConnectException, e:
            if max_tries <= 0:
                raise
            logger.info('%s - retrying', type(e).__name__)

            import time
            time.sleep(1)
            continue


@contextlib.contextmanager
def new_remote_context(pipe='oxt.tool', retry=3, make_current=True, **kwargs):
    ''' Create a remote soffice instance and get its context

    :param pipe: connection pipe name
    :param retry: connect retry count; default True.
    :param make_current: whether the remote context would be pushed to be
        current context; default True.
    :param **kwargs: arguments to soffice_subprocess()
    :returns: remote context
    '''
    uno_link = 'pipe,name=%s;urp;' % pipe

    logger.debug('uno_link: %s', uno_link)

    kwargs['accept'] = uno_link
    while retry >= 0:
        with soffice_subprocess(**kwargs):
            import time
            time.sleep(1)
            try:
                context = connect_remote_context(uno_link, max_tries=10)
            except Exception, e:
                logger.exception(e)
                retry -= 1
                continue

            if make_current:
                import unokit.contexts
                unokit.contexts.push(context)
                try:
                    yield context
                finally:
                    unokit.contexts.pop()
            else:
                yield context
            return


class RemoteContextLayer:

    @classmethod
    def setUp(cls):
        cls.context = new_remote_context()
        cls.context.__enter__()

    @classmethod
    def tearDown(cls):
        cls.context.__exit__(None, None, None)

