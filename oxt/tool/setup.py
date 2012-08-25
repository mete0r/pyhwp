from setuptools import setup
setup(name='oxttool',
      install_requires=['unokit'],
      py_modules=['oxttool'],
      entry_points = {
          'console_scripts': [
              'oxt-test = oxttool:test',
              'oxt-console= oxttool:console',
              ]
          })
