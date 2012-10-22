# -*- coding: utf-8 -*-

import logging
import os
import os.path
import sys
from zc.buildout import easy_install


def discover():
    if 'JAVA_HOME' in os.environ:
        return os.path.join(os.environ['JAVA_HOME'], 'bin', 'java')


def routes_to(actual_executable):
    cmd = [actual_executable] + [('"%s"' % x) for x in sys.argv[1:]]
    cmd = ' '.join(cmd)
    sys.exit(os.system(cmd))


class Discover(object):

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
        self.__discovered_java_path = discover()
        if self.__discovered_java_path:
            logger.info('JRE discovered: %s', self.__discovered_java_path)

    def install(self):
        discovered_java_path = self.__discovered_java_path

        location = self.__location
        if not os.path.exists(location):
            os.makedirs(location)
        yield location

        import pkg_resources
        ws = [pkg_resources.get_distribution(self.__recipe)]
        if discovered_java_path:
            # routes to the actual java executable
            arguments = ('" ".join(["%s"] + '
                         '[\'"\'+x+\'"\' for x in sys.argv[1:]])' %
                         discovered_java_path)
            easy_install.scripts([('java', 'os', 'system')],
                                 ws, sys.executable, location,
                                 arguments=arguments)
        else:
            # dummy executable
            easy_install.scripts([('java', 'sys', 'exit')],
                                 ws, sys.executable, location,
                                 arguments='0')
        yield os.path.join(location, 'java')

    update = install
