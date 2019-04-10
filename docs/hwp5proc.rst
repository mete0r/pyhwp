``hwp5proc``: HWPv5 processor
=============================

.. argparse::
   :module: hwp5.hwp5proc
   :func: main_argparser
   :prog: hwp5proc
   :nosubcommands:

Subcommands
===========

version
-------

Print the file format version of .hwp files.

.. argparse::
   :module: hwp5.hwp5proc
   :func: main_argparser
   :prog: hwp5proc
   :path: version


header
------

Print file headers of .hwp files.

.. argparse::
   :module: hwp5.hwp5proc
   :func: main_argparser
   :prog: hwp5proc
   :path: header


summaryinfo
-----------

Print summary informations of .hwp files.

.. argparse::
   :module: hwp5.hwp5proc
   :func: main_argparser
   :prog: hwp5proc
   :path: summaryinfo


ls
--
List streams in .hwp files.

.. argparse::
   :module: hwp5.hwp5proc
   :func: main_argparser
   :prog: hwp5proc
   :path: ls


cat
---

Extract out internal streams of .hwp files

.. argparse::
   :module: hwp5.hwp5proc
   :func: main_argparser
   :prog: hwp5proc
   :path: cat

Example::

    $ hwp5proc cat samples/sample-5017.hwp BinData/BIN0002.jpg | file -

    $ hwp5proc cat samples/sample-5017.hwp BinData/BIN0002.jpg > BIN0002.jpg

    $ hwp5proc cat samples/sample-5017.hwp PrvText | iconv -f utf-16le -t utf-8

    $ hwp5proc cat --vstreams samples/sample-5017.hwp PrvText.utf8

    $ hwp5proc cat --vstreams samples/sample-5017.hwp FileHeader.txt

    ccl: 0
    cert_drm: 0
    cert_encrypted: 0
    cert_signature_extra: 0
    cert_signed: 0
    compressed: 1
    distributable: 0
    drm: 0
    history: 0
    password: 0
    script: 0
    signature: HWP Document File
    version: 5.0.1.7
    xmltemplate_storage: 0

unpack
------

Extract out internal streams of .hwp files into a directory.

.. argparse::
   :module: hwp5.hwp5proc
   :func: main_argparser
   :prog: hwp5proc
   :path: unpack

Example::

    $ hwp5proc unpack samples/sample-5017.hwp
    $ ls sample-5017

Example::

    $ hwp5proc unpack --vstreams samples/sample-5017.hwp
    $ cat sample-5017/PrvText.utf8

records
-------

Print the record structure of .hwp file record streams.

.. argparse::
   :module: hwp5.hwp5proc
   :func: main_argparser
   :prog: hwp5proc
   :path: records

Example::

    $ hwp5proc records samples/sample-5017.hwp DocInfo

Example::

    $ hwp5proc records samples/sample-5017.hwp DocInfo --range=0-2

If neither <hwp5file> nor <record-stream> is specified, the record stream is
read from the standard input with an assumption that the input is in the format
version specified by -V option.

Example::

    $ hwp5proc records --raw samples/sample-5017.hwp DocInfo --range=0-2 \
> tmp.rec
    $ hwp5proc records < tmp.rec

models
-------

Print parsed binary models of .hwp file record streams.

.. argparse::
   :module: hwp5.hwp5proc
   :func: main_argparser
   :prog: hwp5proc
   :path: models

Example::

    $ hwp5proc models samples/sample-5017.hwp DocInfo
    $ hwp5proc models samples/sample-5017.hwp BodyText/Section0

    $ hwp5proc models samples/sample-5017.hwp docinfo
    $ hwp5proc models samples/sample-5017.hwp bodytext/0

Example::

    $ hwp5proc models --simple samples/sample-5017.hwp bodytext/0
    $ hwp5proc models --format='%(level)s %(tagname)s\\n' \\
            samples/sample-5017.hwp bodytext/0

Example::

    $ hwp5proc models --simple --treegroup=1 samples/sample-5017.hwp bodytext/0
    $ hwp5proc models --simple --seqno=4 samples/sample-5017.hwp bodytext/0

If neither <hwp5file> nor <record-stream> is specified, the record stream is
read from the standard input with an assumption that the input is in the format
version specified by -V option.

Example::

    $ hwp5proc cat samples/sample-5017.hwp BodyText/Section0 > Section0.bin
    $ hwp5proc models -V 5.0.1.7 < Section0.bin

find
----

Find record models with specified predicates.

.. argparse::
   :module: hwp5.hwp5proc
   :func: main_argparser
   :prog: hwp5proc
   :path: find

Example: Find paragraphs::

    $ hwp5proc find --model=Paragraph samples/*.hwp
    $ hwp5proc find --tag=HWPTAG_PARA_TEXT samples/*.hwp
    $ hwp5proc find --tag=66 samples/*.hwp

Example: Find and dump records of ``HWPTAG_LIST_HEADER`` which is parsed
incompletely::

    $ hwp5proc find --tag=HWPTAG_LIST_HEADER --incomplete --dump samples/*.hwp

xml
---

Transform .hwp files into an XML.

.. argparse::
   :module: hwp5.hwp5proc
   :func: main_argparser
   :prog: hwp5proc
   :path: xml

Example::

    $ hwp5proc xml samples/sample-5017.hwp > sample-5017.xml
    $ xmllint --format sample-5017.xml

With ``--embedbin`` option, you can embed base64-encoded ``BinData/*`` files in
the output XML.

Example::

    $ hwp5proc xml --embedbin samples/sample-5017.hwp > sample-5017.xml
    $ xmllint --format sample-5017.xml

rawunz
------

Deflate an headerless zlib-compressed stream.

.. argparse::
   :module: hwp5.hwp5proc
   :func: main_argparser
   :prog: hwp5proc
   :path: rawunz

diststream
----------

Decode a distribute document stream.

.. argparse::
   :module: hwp5.hwp5proc
   :func: main_argparser
   :prog: hwp5proc
   :path: diststream
