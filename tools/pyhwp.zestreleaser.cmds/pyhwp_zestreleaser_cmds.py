# -*- coding: utf-8 -*-
#   pyhwp.zestreleaser.cmds: A zest.releaser plugin to provide command hooks
#   Copyright (C) 2013  mete0r@sarangbang.or.kr
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os.path
import subprocess
import logging


logger = logging.getLogger(__name__)


RELEASE_HOOKS_DIR = 'release-hooks'


def call_hooks(hooks_root, hook_type):
    hooks_dir = os.path.join(hooks_root, hook_type)
    if os.path.isdir(hooks_dir):
        hooks = sorted(os.listdir(hooks_dir))
        for hook in hooks:
            hook_path = os.path.join(hooks_dir, hook)
            if os.path.isfile(hook_path) and os.access(hook_path, os.X_OK):
                logger.info('%s: %s', hook_type, hook_path)
                subprocess.check_call([hook_path])


def prerelease_before(data):
    logger.debug('data: %r', data)
    call_hooks(RELEASE_HOOKS_DIR, 'prerelease.before')


def prerelease_middle(data):
    logger.debug('data: %r', data)
    call_hooks(RELEASE_HOOKS_DIR, 'prerelease.middle')


def prerelease_after(data):
    logger.debug('data: %r', data)
    call_hooks(RELEASE_HOOKS_DIR, 'prerelease.after')


def release_before(data):
    logger.debug('data: %r', data)
    call_hooks(RELEASE_HOOKS_DIR, 'release.before')


def release_middle(data):
    logger.debug('data: %r', data)
    call_hooks(RELEASE_HOOKS_DIR, 'release.middle')


def release_after(data):
    logger.debug('data: %r', data)
    call_hooks(RELEASE_HOOKS_DIR, 'release.after')


def postrelease_before(data):
    logger.debug('data: %r', data)
    call_hooks(RELEASE_HOOKS_DIR, 'postrelease.before')


def postrelease_middle(data):
    logger.debug('data: %r', data)
    call_hooks(RELEASE_HOOKS_DIR, 'postrelease.middle')


def postrelease_after(data):
    logger.debug('data: %r', data)
    call_hooks(RELEASE_HOOKS_DIR, 'postrelease.after')
