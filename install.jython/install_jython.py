# -*- coding: utf-8 -*-

import os.path
import logging


logger = logging.getLogger(__name__)


class Install(object):

    def __init__(self, buildout, name, options):
        self.__logger = logging.getLogger(name)

        if 'java' not in options:
            from zc.buildout import UserError
            raise UserError('option "java" is required')
        java = options['java']

        if not os.path.exists(java):
            self.__skip = True
            self.__logger.info('java not found at: %s', java)
            self.__logger.info('installation will be skipped')

            # ensure location/executable publishes special marker
            not_installed = options.get('not-installed', 'not-installed')
            options['location'] = not_installed
            self.__logger.debug('(exposing) location = %s', not_installed)
            options['executable'] = not_installed
            self.__logger.debug('(exposing) executable = %s', not_installed)
            return

        from sk.recipe.jython import Recipe
        self.__wrapped = Recipe(buildout, name, options)
        self.__skip = False
        self.__logger.debug('location = %s', options['location'])

    def install(self):
        if self.__skip:
            self.__logger.info('skipped')
            return []
        return self.__wrapped.install()

    def update(self):
        if self.__skip:
            self.__logger.info('skipped')
            return []
        return self.__wrapped.update()
