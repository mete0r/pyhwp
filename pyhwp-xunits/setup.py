import os.path
import os
cwd = os.getcwd()
setup_dir = os.path.dirname(__file__)
os.chdir(setup_dir)
try:
    from setuptools import setup
    setup(name='pyhwp-xunits',
          py_modules=['hwp5_xunits'],
          install_requires=['pyhwp', 'docopt'],
          entry_points={
              'console_scripts': [
                  'hwp5-xunits-prepare = hwp5_xunits:prepare'
              ]
          })
finally:
    os.chdir(cwd)
