from distutils.core import setup
setup(name='recipe.jre',
      py_modules=['recipe_jre'],
      entry_points={'zc.buildout': ['default = recipe_jre:Discover']})
