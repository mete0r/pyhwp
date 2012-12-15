from setuptools import setup
setup(name='pyhwp.dev.constants',
      py_modules=['pyhwp_dev_constants'],
      entry_points={'zc.buildout': ['default = pyhwp_dev_constants:Recipe']})
