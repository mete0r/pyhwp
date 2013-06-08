===========
Hack & Test
===========

If you modify some modules in ``hwp5`` package in the ``pyhwp/`` directory, you
can test the modification with the ``hwp5proc`` script in the ``bin/``
directory.

You can test the ``hwp5`` package by executing ``bin/test-core``, but it's just
a quick test and not a complete test suite.  If you want to run a full-blown
test suite, run ``tox``, which tries to test ``pyhwp`` in various
`virtualenv <http://pypi.python.org/pypi/virtualenv>`_-isolated python
platforms, including Python 2.5, 2.6, 2.7, Jython 2.5 and PyPy.

::

   $ bin/buildout

   (...)

   $ vim pyhwp/hwp5/proc/__init__.py

   (HACK HACK HACK)

   $ bin/test-core

   $ bin/hwp5proc ...

   $ bin/tox
