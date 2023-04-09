# -*- coding: utf-8 -*-
from setuptools import setup

version = '0.0dev'
classifiers = [
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Programming Language :: Python :: 2',
]


def read(filename):
    f = open(filename)
    try:
        return f.read()
    finally:
        f.close()


setup(name='pyhwp.zestreleaser.cmds',
      version=version,
      description='A zest.releaser plugin to provide command hooks',
      long_description=read('README.rst'),
      author='mete0r',
      author_email='https://github.com/mete0r',
      license='GNU GPL v3+',
      keywords='zest.releaser plugin',
      py_modules=['pyhwp_zestreleaser_cmds'],
      entry_points={
          'zest.releaser.prereleaser.before': [
              'pre.before = pyhwp_zestreleaser_cmds:prerelease_before'
          ],
          'zest.releaser.prereleaser.middle': [
              'pre.middle = pyhwp_zestreleaser_cmds:prerelease_middle'
          ],
          'zest.releaser.prereleaser.after': [
              'pre.after = pyhwp_zestreleaser_cmds:prerelease_after'
          ],
          'zest.releaser.releaser.before': [
              'rel.before = pyhwp_zestreleaser_cmds:release_before'
          ],
          'zest.releaser.releaser.middle': [
              'rel.middle = pyhwp_zestreleaser_cmds:release_middle'
          ],
          'zest.releaser.releaser.after': [
              'rel.after = pyhwp_zestreleaser_cmds:release_after'
          ],
          'zest.releaser.postreleaser.before': [
              'post.before = pyhwp_zestreleaser_cmds:postrelease_before'
          ],
          'zest.releaser.postreleaser.middle': [
              'post.middle = pyhwp_zestreleaser_cmds:postrelease_middle'
          ],
          'zest.releaser.postreleaser.after': [
              'post.after = pyhwp_zestreleaser_cmds:postrelease_after'
          ],
      },
      classifiers=classifiers)
