# -*- coding: utf-8 -*-

import logging
import os
import os.path
import sys
import re


logger = logging.getLogger(__name__)


EXPOSE_NAMES = ('executable', 'version', 'prefix', 'exec_prefix', 'through')


def wellknown_locations():
    if sys.platform == 'win32':
        base = 'c:\\'
        for name in os.listdir(base):
            name = name.lower()
            if name.startswith('python'):
                shortversion = name[len('python'):]
                m = re.match('[23][0-9]', shortversion)
                if m:
                    yield base + name
    elif 'PYTHONZ_ROOT' in os.environ:
        pythonz_root = os.environ['PYTHONZ_ROOT']
        pythons = os.path.join(pythonz_root, 'pythons')
        for item in os.listdir(pythons):
            yield os.path.join(pythons, item)


def discover_python(in_wellknown=True, in_path=True):

    if in_wellknown:
        for found in search_in_wellknown_locations():
            yield found

    if in_path:
        for found in search_in_path():
            yield found


def search_in_wellknown_locations():
    for location in wellknown_locations():
        if sys.platform == 'win32':
            founds = contains_python(location)
        else:
            founds = contains_python_in_bin(location)

        for found in founds:
            found['through'] = 'WELLKNOWN_LOCATION'
            yield found


def search_in_path():
    if 'PATH' in os.environ:
        path = os.environ['PATH']
        path = path.split(os.pathsep)
        for dir in path:
            for found in contains_python(dir):
                found['through'] = 'PATH'

                # resolve symlinks
                resolved = os.path.realpath(found['executable'])
                found['executable'] = resolved
                yield found


def contains_python_in_bin(dir):
    bindir = os.path.join(dir, 'bin')
    return contains_python(bindir)


def contains_python(dir):
    vers = {
        2: [3, 4, 5, 6, 7],
        3: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    }
    names = (('python%d.%d' % (major, minor))
             for major in reversed(sorted(vers))
             for minor in reversed(sorted(vers[major])))
    names = list(names) + ['python']
    for name in names:
        executable = executable_in_dir(name, dir)
        if executable:
            found = executable_is_python(executable)
            if found:
                yield found


def executable_in_dir(name, dir):
    assert name == os.path.basename(name)
    if sys.platform == 'win32':
        name += '.exe'
    path = os.path.join(dir, name)
    if not os.path.exists(path):
        return
    return path


def executable_is_python(executable):
    from subprocess import Popen
    from subprocess import PIPE
    cmd = '''
    import os, sys
    print(sys.hexversion)
    print(os.pathsep.join([sys.prefix, sys.exec_prefix]))
    '''.strip().replace('\n', ';')
    args = [executable, '-c', cmd]
    env = dict(os.environ)
    for k in ('PYTHONPATH', 'PYTHONHOME'):
        if k in env:
            del env[k]
    try:
        p = Popen(args, stdout=PIPE, env=env)
        lines = p.stdout.read().split('\n')
        p.wait()
        ver = int(lines[0])
        ver_major = str(ver >> 24 & 0xff)
        ver_minor = str(ver >> 16 & 0xff)
        ver_patch = str(ver >> 8  & 0xff)
        ver = ver_major, ver_minor, ver_patch
        version = '.'.join(ver)
        prefix, exec_prefix = lines[1].split(os.pathsep)
        return dict(executable=executable, version=version,
                    prefix=prefix, exec_prefix=exec_prefix)
    except Exception, e:
        logger.error('popen failed: %s', args)
        logger.exception(e)


def log_discovered(qualify, found, names, log=logger.info):
    for item in found:
        msg = qualify + ':'
        for name in names:
            if name in item:
                msg += ' %s=%s' % (name, item[name])
        log(msg)
        yield item


def expose_options(options, names, found, not_found, logger=logger):
    for name in names:
        if name in found:
            value = found[name]
            if name in options:
                if value != options[name]:
                    logger.info('(updating) %s = %s', name, value)
                    options[name] = value
                else:
                    logger.info('(preserving) %s = %s', name, value)
            else:
                logger.info('(exposing) %s = %s', name, value)
                options[name] = value
        else:
            if name not in options:
                options[name] = value = not_found
                logger.info('(exposing) %s = %s', name, value)


class Discover(object):
    ''' Discover Python and provide its location.
    '''

    def __init__(self, buildout, name, options):
        from zc.buildout import UserError
        self.__logger = logger = logging.getLogger(name)
        for k, v in options.items():
            logger.info('%s: %r', k, v)

        self.__recipe = options['recipe']

        not_found = options.get('not-found', 'not-found')
        version = options.get('version', '').strip()

        if 'location' in options:
            # if location is explicitly specified, it must contains java
            # executable.
            for found in contains_python_in_bin(options['location']):
                if not version or found['version'].startswith(version):
                    # Python found, no further discovery required.
                    options['executable'] = found['executable']
                    return
            raise UserError('Python not found at %s' % options['location'])

        in_wellknown = options.get('search-in-wellknown-places',
                                   'true').lower().strip()
        in_wellknown = in_wellknown in ('true', 'yes', '1') 
        in_path = options.get('search-in-path', 'true').lower().strip()
        in_path = in_path in ('true', 'yes', '1')

        founds = discover_python(in_wellknown=in_wellknown,
                                 in_path=in_path)
        founds = log_discovered('candidates', founds, EXPOSE_NAMES,
                                log=logger.debug)
        if version:
            # filter with version
            founds = (found for found in founds
                      if found['version'].startswith(version))
        founds = log_discovered('matching', founds, EXPOSE_NAMES,
                                log=logger.info)
        founds = list(founds)

        # location is not specified: try to discover a Python installation
        if founds:
            found = founds[0]
            logger.info('the first-matching one will be used:')
            expose_options(options, EXPOSE_NAMES, found,
                           not_found=not_found, logger=logger)
            return

        # ensure executable publishes not-found marker
        expose_options(options, ['executable'], dict(), not_found=not_found,
                       logger=logger)
        logger.warning('Python not found')
        return

    def install(self):
        return []

    update = install
