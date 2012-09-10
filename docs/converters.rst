Converters (*Experimental*)
===========================

Convert HWPv5 documents into other document formats.

Requirements
------------
The conversions are performed with `XSLT <http://www.w3.org/TR/xslt>`_
internally and verified with `Relax NG <http://relaxng.org/>`_ if possible.

For these processing, the converters requires
`lxml <http://pypi.python.org/pypi/lxml>`_ (`homepage <http://lxml.de>`_) or
`libxml2 <http://www.xmlsoft.org/>`_'s
`xsltproc <http://xmlsoft.org/XSLT/xsltproc2.html>`_ /
`xmllint <http://infohost.nmt.edu/tcc/help/xml/lint.html>`_ programs.

For lxml installation::

   pip install --user lxml # install to user directory
   pip install lxml        # install with virtualenv

or see `Installing lxml <http://lxml.de/installation.html>`_.

(Currently conversions with lxml 2.3.5 is tested and verified to be working.
lxml versions below that may work too, but those are not tested.)

For ``xsltproc`` / ``xmllint`` installation::

   sudo apt-get install xsltproc libxml2-utils  # Debian/Ubuntu

Optional environment variables ``PYHWP_XSLTPROC`` and ``PYHWP_XMLLINT``
specifies the paths of the each programs. (If not set, ``xsltproc`` and/or
``xmllint`` should be in the one of the directories specified in ``PATH``.)

``hwp5odt``: ODT conversion
---------------------------
.. automodule:: hwp5.hwp5odt

``hwp5html``: HTML conversion
-----------------------------
.. automodule:: hwp5.hwp5html

``hwp5txt``: text conversion
----------------------------
.. automodule:: hwp5.hwp5txt
