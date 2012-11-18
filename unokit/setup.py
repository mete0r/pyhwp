import os
import os.path
cwd = os.getcwd()
os.chdir(os.path.dirname(__file__))
try:
    from setuptools import setup, find_packages
    setup(name='unokit',
          packages=find_packages())
finally:
    os.chdir(cwd)
