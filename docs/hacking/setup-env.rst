=============================
Setup development environment
=============================

1. Install prerequisites
------------------------

* CPython 2.7
* `virtualenv`
* GNU `Make`


2. Clone the source repository
------------------------------

::

   $ git clone https://github.com/mete0r/pyhwp.git

3. Initialize the environment
------------------------------

Bootstrap development environment::

   $ make bootstrap
   $ . bin/activate

4. Check basic stuffs
---------------------

Run `hwp5proc`::

   $ hwp5proc --help

To run tests::

   $ tox
