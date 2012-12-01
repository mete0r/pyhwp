import os.path
import os
cwd = os.getcwd()
setup_dir = os.path.dirname(__file__)
os.chdir(setup_dir)
try:
    from setuptools import setup
    setup(name='pyhwp-xsltests',
          py_modules=['hwp5_xsltests'],
          install_requires=['pyhwp', 'docopt'],
          entry_points={
              'console_scripts': [
                  'prepare-hwp5-xsltests = hwp5_xsltests:prepare'
              ]
          })
finally:
    os.chdir(cwd)
