from setuptools import setup, find_packages
import os.path
import os
setup_dir = os.path.dirname(__file__)
os.chdir(setup_dir)
setup(name='xunit',
      packages=find_packages(),
      # TODO: lxml is required, but we omit it to make buildout process
      # successful without it. This workaround should be resolved with Issue
      # #101.
      install_requires=['pyhwp', 'docopt'],
      entry_points={
          'console_scripts': [
              'xunit = xunit:main'
          ]
      })
