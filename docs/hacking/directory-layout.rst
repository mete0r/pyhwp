================
Directory Layout
================

::

   pyhwp                   Project Root
     |
     +-- pyhwp/            Source packages root
     |     |
     |     +-- hwp5/       Source package
     |
     +-- pyhwp-tests/      Test packages root
     |     |
     |     +-- hwp5_tests/ Test package
     |
     +-- docs/             Documentations, i.e. this document!
     |
     +-- bin/              hwp5proc, hwp5odt, build/testing scripts, etc.,
     |
     +-- etc/              development configuration files
     |
     +-- misc/             development configuration templates / helper scripts
     |
     +-- tools/            development helper packages
     |
     .
     . (various directories)
     .

After the initial :ref:`invocation of buildout <invoke-buildout>` completes
successfully, your directory will have a few more new generated directories,
e.g. :file:`bin/`, :file:`develop-eggs/`. These are the standard buildout
directories, which we will not cover the every details of them here. For general
information, see `Directory Structure of a Buildout
<http://www.buildout.org/docs/dirstruct.html>`_.

Followings are ``pyhwp`` specific informations:

.. include:: directory-layout/root.rst

.. include:: directory-layout/bin.rst

.. include:: directory-layout/pyhwp.rst

.. include:: directory-layout/pyhwp-tests.rst

.. include:: directory-layout/tools.rst
