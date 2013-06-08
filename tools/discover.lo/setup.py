from distutils.core import setup
setup(name='discover.lo',
      py_modules=['discover_lo'],
      entry_points={'zc.buildout': ['default = discover_lo:Discover']},
      install_requires=['discover.jre'])
