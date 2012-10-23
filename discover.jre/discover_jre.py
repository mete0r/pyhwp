# -*- coding: utf-8 -*-

import logging
import os
import os.path
import sys


logger = logging.getLogger(__name__)


def wellknown_locations():
    if sys.platform == 'win32':
        java_dir = 'c:\\'+os.path.join('program files', 'java')
        if os.path.isdir(java_dir):
            for name in os.listdir(java_dir):
                location = os.path.join(java_dir, name)
                if os.path.isdir(location):
                    yield location


def discover_jre(in_envar=True, in_wellknown=True, in_path=True):
    if in_envar:
        for jre in search_in_java_home_envar():
            yield jre

    if in_wellknown:
        for jre in search_in_wellknown_locations():
            yield jre

    if in_path:
        for jre in search_in_path():
            yield jre


def search_in_java_home_envar():
    if 'JAVA_HOME' in os.environ:
        location = os.environ['JAVA_HOME']
        java = contains_java_in_bin(location)
        if java:
            java['jre'] = location
            java['through'] = 'JAVA_HOME'
            yield java


def search_in_wellknown_locations():
    for location in wellknown_locations():
        java = contains_java_in_bin(location)
        if java:
            java['jre'] = location
            java['through'] = 'WELLKNOWN_LOCATION'
            yield java


def search_in_path():
    if 'PATH' in os.environ:
        path = os.environ['PATH']
        path = path.split(os.pathsep)
        for dir in path:
            java = contains_java(dir)
            if java:
                java['through'] = 'PATH'

                # resolve symlinks
                resolved_java = os.path.realpath(java['java'])
                bindir = os.path.dirname(resolved_java)
                if os.path.basename(bindir).lower() == 'bin':
                    java['jre'] = os.path.dirname(bindir)

                yield java


def contains_java_in_bin(dir):
    bindir = os.path.join(dir, 'bin')
    return contains_java(bindir)


def contains_java(dir):
    executable = executable_in_dir('java', dir)
    if executable:
        return executable_is_java(executable)


def executable_in_dir(name, dir):
    assert name == os.path.basename(name)
    if sys.platform == 'win32':
        name += '.exe'
    path = os.path.join(dir, name)
    if not os.path.exists(path):
        return
    return path


def executable_is_java(executable):
    import os
    import tempfile
    import subprocess
    fd, name = tempfile.mkstemp()
    out = os.fdopen(fd, 'r+')
    try:
        ret = subprocess.call([executable, '-version'], stderr=out)
        logger.debug('%s -version: exit %d', executable, ret)
        if ret == 0:
            out.seek(0)
            output = out.read()
            logger.debug(output)
            import re
            m = re.match('java version "(.*)"', output)
            if m:
                return dict(java=executable, version=m.group(1))
    except Exception, e:
        logger.error('%s -version: failed', executable)
        logger.exception(e)
    finally:
        out.close()
        os.unlink(name)


def log_discovered(discovered):
    for item in discovered:
        msg = 'discovered:'
        if 'jre' in item:
            msg += ' location=%s' % item['jre']
        if 'java' in item:
            msg += ' java=%s' % item['java']
        if 'version' in item:
            msg += ' version=%s' % item['version']
        if 'through' in item:
            msg += ' through=%s' % item['through']
        logger.info(msg)
        yield item


def expose_options(options, names, discovered, not_found, logger=logger):
    for name in names:
        if name in discovered:
            value = discovered[name]
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
    ''' Discover JRE and provide its location.
    '''

    def __init__(self, buildout, name, options):
        from zc.buildout import UserError
        self.__logger = logger = logging.getLogger(name)
        for k, v in options.items():
            logger.info('%s: %r', k, v)

        self.__recipe = options['recipe']
        self.__generate_stub = None

        not_found = options.get('not-found', 'not-found')

        if 'location' in options:
            # if location is explicitly specified, it must contains java
            # executable.
            java = contains_java_in_bin(options['location'])
            if java:
                # JRE found, no further discovery required.
                options['java'] = java['java']
                return
            raise UserError('JRE not found at %s' % options['location'])

        in_envar = options.get('search-in-envar', 'true').lower().strip()
        in_envar = in_envar in ('true', 'yes', '1')
        in_wellknown = options.get('search-in-wellknown-places',
                                   'true').lower().strip()
        in_wellknown = in_wellknown in ('true', 'yes', '1') 
        in_path = options.get('search-in-path', 'true').lower().strip()
        in_path = in_path in ('true', 'yes', '1')

        discovered = discover_jre(in_envar=in_envar, in_wellknown=in_wellknown,
                                  in_path=in_path)
        discovered = log_discovered(discovered)
        discovered = list(discovered)

        # location is not specified: try to discover a JRE installation
        if discovered:
            discovered = discovered[0]
            logger.info('the first JRE will be used:')
            expose_options(options, ['jre', 'java'], discovered,
                           not_found=not_found, logger=logger)
            return

        # ensure jre/java publishes not-found marker
        expose_options(options, ['jre', 'java'], dict(), not_found=not_found,
                       logger=logger)
        return

        # no JRE found: stub generation is required
        parts_dir = buildout['buildout']['parts-directory']
        self.__generate_stub = jre = os.path.join(parts_dir, name)
        options['location'] = jre
        options['java'] = java = os.path.join(jre, 'bin', 'java')
        logger.info('JRE not found: a dummy JRE will be generated')
        logger.info('location = %s (updating)', jre)
        logger.info('java = %s (updating)', java)

    def install(self):
        location = self.__generate_stub
        if location is None:
            return

        if not os.path.exists(location):
            os.makedirs(location)
        yield location

        bin_dir = os.path.join(location, 'bin')
        if not os.path.exists(bin_dir):
            os.mkdir(bin_dir)
            yield bin_dir

        import pkg_resources
        ws = [pkg_resources.get_distribution(self.__recipe)]
        from zc.buildout import easy_install
        # dummy executable
        easy_install.scripts([('java', 'sys', 'exit')],
                             ws, sys.executable, bin_dir,
                             arguments='0')
        yield os.path.join(bin_dir, 'java')
        self.__logger.info('A dummy JRE has been generated: %s', location)

    update = install
