# -*- coding: utf-8 -*-
from __future__ import with_statement
import logging
import os
import os.path
from discover_python import expose_options
from discover_python import log_discovered


logger = logging.getLogger(__name__)


EXPOSE_NAMES = ('location', 'version')


FIND_SOURCE = '''
import os
import os.path
import sys
try:
    from pkg_resources import get_distribution
except ImportError:
    sys.stderr.write('pkg_resources is not found' + os.linesep)
    try:
        import lxml
    except ImportError:
        sys.stderr.write('lxml is not found' + os.linesep)
        raise SystemExit(1)
    else:
        print(os.path.dirname(lxml.__path__[0]))
        print('')
        raise SystemExit(0)

try:
    dist = get_distribution('lxml')
except Exception, e:
    sys.stderr.write(repr(e))
    sys.stderr.write(os.linesep)
    raise SystemExit(1)
else:
    print(dist.location)
    print(dist.version)
'''


def discover_lxml(executable):
    import tempfile
    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(FIND_SOURCE)

        from subprocess import Popen
        from subprocess import PIPE
        args = [executable, path]
        env = dict(os.environ)
        for k in ('PYTHONPATH', 'PYTHONHOME'):
            if k in env:
                del env[k]
        try:
            p = Popen(args, stdout=PIPE, env=env)
        except Exception, e:
            logger.exception(e)
            return
        else:
            try:
                lines = list(p.stdout)
            finally:
                p.wait()
    finally:
        os.unlink(path)

    if p.returncode == 0:
        location = lines[0].strip()
        version = lines[1].strip()
        yield dict(location=location,
                   version=version)


class DiscoverRecipe(object):
    ''' Discover lxml and provide its location.
    '''

    def __init__(self, buildout, name, options):
        self.__logger = logger = logging.getLogger(name)
        for k, v in options.items():
            logger.info('%s: %r', k, v)

        self.__recipe = options['recipe']

        not_found = options.get('not-found', 'not-found')
        executable = options.get('python', 'python').strip()
        #version = options.get('version', '').strip()

        founds = discover_lxml(executable=executable)
        founds = log_discovered('matching', founds, EXPOSE_NAMES,
                                log=logger.info)
        founds = list(founds)

        # location is not specified: try to discover a Python installation
        if founds:
            found = founds[0]
            logger.info('the first-found one will be used:')
            expose_options(options, EXPOSE_NAMES, found,
                           not_found=not_found, logger=logger)
            return

        # ensure executable publishes not-found marker
        expose_options(options, ['location'], dict(), not_found=not_found,
                       logger=logger)
        logger.warning('lxml not found')
        return

    def install(self):
        return []

    update = install
