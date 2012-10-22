# -*- coding: utf-8 -*-

import logging
import os
import os.path
import sys
from zc.buildout import easy_install


def is_jre(dir):
    java_path = os.path.join(dir, 'bin', 'java')
    return os.path.exists(java_path)


def discover():
    if 'JAVA_HOME' in os.environ:
        return os.environ['JAVA_HOME']


def routes_to(actual_executable):
    cmd = [actual_executable] + [('"%s"' % x) for x in sys.argv[1:]]
    cmd = ' '.join(cmd)
    sys.exit(os.system(cmd))


class Discover(object):
    ''' Discover and provide location.
    '''

    def __init__(self, buildout, name, options):
        self.__logger = logger = logging.getLogger(name)
        for k, v in options.items():
            logger.info('%s: %r', k, v)

        self.__recipe = options['recipe']

        if 'location' in options:
            self.__location = options['location']
        else:
            parts_dir = buildout['buildout']['parts-directory']
            self.__location = os.path.join(parts_dir, name)

        # discover java
        self.__discovered = discover()
        if self.__discovered:
            logger.info('JRE discovered: %s', self.__discovered)
            options['location'] = self.__discovered

    def install(self):
        discovered = self.__discovered

        location = self.__location
        if not os.path.exists(location):
            os.makedirs(location)
        yield location

        bin_dir = os.path.join(location, 'bin')
        if not os.path.exists(bin_dir):
            os.mkdir(bin_dir)
            yield bin_dir

        import pkg_resources
        ws = [pkg_resources.get_distribution(self.__recipe)]
        if discovered:
            discovered_java_path = os.path.join(discovered, 'bin', 'java')
            # routes to the actual java executable
            arguments = ('" ".join(["%s"] + '
                         '[\'"\'+x+\'"\' for x in sys.argv[1:]])' %
                         discovered_java_path)
            easy_install.scripts([('java', 'os', 'system')],
                                 ws, sys.executable, bin_dir,
                                 arguments=arguments)
        else:
            # dummy executable
            easy_install.scripts([('java', 'sys', 'exit')],
                                 ws, sys.executable, bin_dir,
                                 arguments='0')
        yield os.path.join(bin_dir, 'java')

    update = install
