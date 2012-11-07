from distutils.core import setup
setup(name='discover.jre',
      py_modules=['discover_jre'],
      entry_points={'zc.buildout': ['default = discover_jre:Discover']})
