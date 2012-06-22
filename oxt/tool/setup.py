from setuptools import setup
setup(name='oxttool',
      py_modules=['oxttool'],
      entry_points = {
          'console_scripts': [
              'oxt-test = oxttool:test',
              'oxt-console= oxttool:console',
              ]
          })
