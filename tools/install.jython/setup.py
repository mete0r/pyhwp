from distutils.core import setup
setup(name='install.jython',
      py_modules=['install_jython'],
      entry_points={'zc.buildout': ['default = install_jython:Install']},
      install_requires=['sk.recipe.jython == 0.0.0'])
