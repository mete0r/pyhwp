from setuptools import setup, find_packages
setup(name='gpl',
      packages=find_packages(),
      install_requires=['docopt'],
      entry_points={
          'console_scripts': [
              'gpl = gpl:main'
          ]
      })
