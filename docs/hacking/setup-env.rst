=============================
Setup development environment
=============================

`pyhwp <https://github.com/mete0r/pyhwp>`_ project uses `zc.buildout
<http://pypi.python.org/pypi/zc.buildout>`_ to manage the development
environment. If you want to learn more about it, see `buildout
<http://www.buildout.org>`_.

1. Install prerequisites
------------------------

* CPython >= 2.6

  Although pyhwp_ itself can be working with CPython 2.5, various development
  helper scripts require CPython >= 2.6.

  In many GNU/Linux systems you can just install CPython with underlying
  package management system, e.g. ::

      sudo apt-get install python  # Debian/Ubuntu

  In MS-Windows systems, See `Download Python <http://www.python.org/download/>`_.
   
* `lxml <http://pypi.python.org/pypi/lxml/>`_

  In many GNU/Linux systems you can just install lxml_ with underlying
  package management system, e.g. ::

     sudo apt-get install python-lxml  # Debian/Ubuntu

  Or if your system has appropriate compilers, it will be installed
  automatically in later steps.
   
  In a MS-Windows system, you'll need install it manually.  See `Installing
  lxml <http://lxml.de/installation.html>`_.

  Note that this requirement will be removed in the future. See `Issue #101
  <https://github.com/mete0r/pyhwp/issues/101>`_.

* (optional) `tox <http://tox.testrun.org>`_

  If you want to run full-blown tests, install tox_.

2. Clone the source repository
------------------------------

::

   $ git clone https://github.com/mete0r/pyhwp.git

3. Initialize the environment
------------------------------

Bootstrap buildout_ environment::

   $ python bootstrap_me.py
   $ python bootstrap.py  # bootstrap the buildout environment

Now there will be generated a :command:`buildout` executable in the :file:`bin/`
directory.

.. note::

   Bootstrapping the environment is required just only once for the first time.

.. _invoke-buildout:

Then run it to setup the environment::

   $ bin/buildout

:program:`buildout` will do following tasks:

* install development version of ``pyhwp`` scripts into the :file:`bin/`
* generate configuration files for build/testing
* generate build/testing helper scripts
* ...

.. note::

   Whenever the input configuration files (e.g. :file:`buildout.cfg`,
   :file:`tox.ini.in`, :file:`setup.py`) get modified, you need to run
   :command:`buildout` to update the environment again. However it's not
   required when the main source files get modified, i.e. the files under the
   :file:`pyhwp/` directory and it's subdirectories.

.. note::

   In this step, some optional components (e.g. JRE, multiple versions of Python
   installations) will be discovered and used by the relevant recipe and scripts.

4. Check basic stuffs
---------------------

Run :program:`hwp5proc`::

   $ bin/hwp5proc --help

Do a quick test::

   $ bin/test-core
