import os
import os.path
cwd = os.getcwd()
os.chdir(os.path.dirname(__file__))
try:
    from setuptools import setup, find_packages
    setup(name='oxt.tool',
          install_requires=['unokit', 'discover'],
          packages=find_packages(),
          entry_points = {
              'console_scripts': [
                  'oxt-make = oxt_tool:make',
                  'run-in-lo = oxt_tool:run_in_lo'
              ],
              'zc.buildout': [
                  'installer = oxt_tool:Installer'
                  ,'console = oxt_tool:Console'
                  ,'test = oxt_tool:TestRunner'
              ]
          })
finally:
    os.chdir(cwd)
