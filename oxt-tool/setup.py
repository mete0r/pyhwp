from setuptools import setup
setup(name='oxt-tool',
      packages=['oxttool'],
      entry_points = {
          'console_scripts': [
              'oxt-test = oxttool:test',
              'oxt-console= oxttool:console',
              ]
          })
