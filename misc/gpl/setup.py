from setuptools import setup
setup(name='gpl',
      py_modules=['gpl'],
      install_requires=['docopt'],
      entry_points = {
          'console_scripts': [
              'gpl = gpl:main'
          ]
      })
