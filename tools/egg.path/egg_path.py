# -*- coding: utf-8 -*-
import logging


class EggPath(object):
    def __init__(self, buildout, name, options):
        self.__name = name
        self.__logger = logging.getLogger(name)

        eggs = options['eggs']
        eggs = eggs.split('\n')
        eggs = list(egg.strip() for egg in eggs)
        for egg in eggs:
            self.__logger.info('egg: %s', egg)

        from zc.recipe.egg.egg import Eggs
        eggs_recipe = Eggs(buildout, name, options)
        req, ws = eggs_recipe.working_set()
        for dist in ws:
            self.__logger.debug('dist: %s %s at %s', dist, dist.key, dist.location)
        dist_locations = dict((dist.key, dist.location) for dist in ws)
        egg_path = list(dist_locations[egg] for egg in eggs)
        for p in egg_path:
            self.__logger.info('egg-path: %s', p)
        options['egg-path'] = ' '.join(egg_path)

    def install(self):
        return []

    update = install
