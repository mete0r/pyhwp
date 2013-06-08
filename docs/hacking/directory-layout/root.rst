``/`` - project root directory
------------------------------

The project root directory contains project configuration files.

:file:`buildout.cfg`
   `buildout <http://www.buildout.org>`_ configuration file.

:file:`setup.py`, :file:`setup.cfg`
   ``pyhwp`` setup files.

:file:`tox.ini`
   `tox <http://tox.testrun.org>`_ configuration file. This file will be
   automatically generated from :file:`tox.ini.in` by :program:`bin/buildout`.
   See ``[tox]`` parts in :file:`buildout.cfg`.

:file:`tox.ini.in`
   tox_ configuration template file.  If you want to modify tox_ configuration,
   edit this file and run :program:`bin/buildout` again.
