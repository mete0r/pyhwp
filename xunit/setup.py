from setuptools import setup, find_packages
import os.path
import os
setup_dir = os.path.dirname(__file__)
os.chdir(setup_dir)
setup(name='xunit',
      packages=find_packages(),
      install_requires=['pyhwp', 'lxml', 'docopt'],
      entry_points={
          'console_scripts': [
              'xunit = xunit:main'
          ]
      })
