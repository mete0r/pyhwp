from setuptools import setup
setup(name='egg.path',
      install_requires=['zc.recipe.egg'],
      py_modules=['egg_path'],
      entry_points = {
          'zc.buildout': [
              'default = egg_path:EggPath'
          ]
      })
