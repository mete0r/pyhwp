from setuptools import setup
import os.path
import os
setup_dir = os.path.dirname(__file__)
os.chdir(setup_dir)
setup(name='pyhwp-xunits',
      py_modules=['hwp5_xunits'],
      install_requires=['pyhwp', 'docopt'],
      entry_points={
          'console_scripts': [
              'hwp5-xunits-prepare = hwp5_xunits:prepare'
          ]
      })
