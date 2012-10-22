# -*- coding: utf-8 -*-

import logging
import os
import os.path
import sys
from zc.buildout import easy_install
from zc.buildout import UserError


def is_jre(dir):
    java_path = os.path.join(dir, 'bin', 'java')
    return os.path.exists(java_path)


def discover_jre():
    if 'JAVA_HOME' in os.environ:
        location = os.environ['JAVA_HOME']
        if is_jre(location):
            return location

    if 'PATH' in os.environ:
        path = os.environ['PATH']
        path = path.split(os.pathsep)
        for bin_dir in path:
            executable = executable_in_dir('java', bin_dir)
            if executable:
                executable = os.path.realpath(executable)
                return os.path.dirname(os.path.dirname(executable))


def executable_in_dir(name, dir):
    assert name == os.path.basename(name)
    path = os.path.join(dir, name)
    if not os.path.exists(path):
        path = os.path.join(dir, name+'.exe')
        if not os.path.exists(path):
            return
    return path


class Discover(object):
    ''' Discover JRE and provide its location.
    '''

    def __init__(self, buildout, name, options):
        self.__logger = logger = logging.getLogger(name)
        for k, v in options.items():
            logger.info('%s: %r', k, v)

        self.__recipe = options['recipe']
        self.__generate_stub = None

        if 'location' in options:
            # if location is explicitly specified, it must contains java
            # executable.
            if is_jre(options['location']):
                # JRE found, no further operation required.
                return
            raise UserError('JRE not found at %s' % options['location'])

        # location is not specified: try to discover a JRE installation
        discovered = discover_jre()
        if discovered:
            logger.info('JRE discovered: %s', discovered)
            logger.info('location = %s (updating)', discovered)
            options['location'] = discovered
            return

        # no JRE found: stub generation is required
        parts_dir = buildout['buildout']['parts-directory']
        self.__generate_stub = os.path.join(parts_dir, name)
        options['location'] = self.__generate_stub
        logger.info('JRE not found: a dummy JRE will be generated')
        logger.info('location = %s (updating)', self.__generate_stub)

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
        # dummy executable
        easy_install.scripts([('java', 'sys', 'exit')],
                             ws, sys.executable, bin_dir,
                             arguments='0')
        yield os.path.join(bin_dir, 'java')
        self.__logger.info('A dummy JRE has been generated: %s', location)

    update = install
