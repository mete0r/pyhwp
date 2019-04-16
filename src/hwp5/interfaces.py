# -*- coding: utf-8 -*-
#
#   pyhwp : hwp file format parser in python
#   Copyright (C) 2010-2019 mete0r <mete0r@sarangbang.or.kr>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from zope.interface import Attribute
from zope.interface import Interface


class ILocation(Interface):

    __parent__ = Attribute('')
    __name__ = Attribute('')


class IStorageOpener(Interface):

    def is_storage(path):
        '''
        Detect if the given path is a openable storage.

        :param str path:
            path to a storage
        :returns:
            True if it's a storage or False
        :rtype:
            bool
        '''

    def open_storage(path):
        '''
        Open a storage.

        :param str path:
            path to a storage
        :returns:
            a storage
        :rtype:
            IStorage
        '''


class IStorageNode(ILocation):
    '''
    '''


class IStorageStreamNode(IStorageNode):
    '''
    '''


class IStorageDirectoryNode(IStorageNode):

    def __iter__():
        '''
        Return an iterator of item names.

        :return:
            an iterator of item names.
        '''

    def __getitem__(name):
        '''
        Return the item node.

        :return:
            an item node
        :rtype:
            IStorageDirectoryNode or IStorageStreamNode
        '''


class IStorage(IStorageDirectoryNode):

    def close():
        '''
        Close this storage.
        '''


class IStorageTreeEventGenerator(Interface):

    def generate(storage_node):
        '''
        Generate storage events.

        For example::
            (STARTEVENT, name, directorynode1)
            (None, name, streamnode1)
            (None, name, streamnode2)
            (STARTEVENT, name, directorynode2)
            (None, name, streamnode3)
            (ENDEVENT, name, directorynode2)
            (None, name, streamnode4)
            (ENDEVENT, name, directorynode1)

        :param storage_node:
            storage node to generate events based on
        :type storage_node:
            IStorageNode
        :return:
            iterator of (event type, node name, node)
        '''


class IStorageTreeEventUnpacker(Interface):

    def unpack_from_tree_events(tree_events, out_directory):
        pass


class IHwp5File(IStorage):

    header = Attribute('')
    fileheader = Attribute('')
    summaryinfo = Attribute('')
    docinfo = Attribute('')
    preview_text = Attribute('')
    bodytext = Attribute('')
    viewtext = Attribute('')
    text = Attribute('')


class ITemporaryStreamFactory(Interface):

    def temporary_stream():
        '''
        Return temporary byte-oriented stream.

        :returns:
            a temporary byte-oriented stream.
        :rtype:
            a byte-oriented file-like object.

        >>> with F.temporary_stream() as fp:
                fp.write(b'foo')
        '''


class IAES128ECB(Interface):

    def decrypt(key, ciphertext):
        '''
        Decrypt AES-128-ECB data

        :param bytes key:
            AES 128 key
        :param bytes ciphertext:
            data to decrypt
        :returns:
            data decrypted
        :rtype:
            bytes
        '''


class IRelaxNG(Interface):

    def validating_output(output_stream):
        '''
        Return validating output stream on the given output stream.

        :param output_stream:
            output stream
        :type output_stream:
            byte-oriented file-like object.

        >>> with R.validating_output(sys.stdout.buffer) as fp:
                doc.dump(fp)
        '''

    def validate(input_path):
        '''
        Validate input file.

        :param str input_path:
            input file to validate.
        :return bool:
            True if validation succeeds.

        >>> success = V.validate('input.xml')
        '''


class IRelaxNGFactory(Interface):

    def relaxng_validator_from_file(rng_path):
        '''
        Create a RelaxNG validator from a file.

        :param str rng_path:
            RelaxNG file path.
        :returns:
            RelaxNG validator
        :rtype:
            IRelaxNG

        >>> V = F.relaxng_validator_from_file('validator.rng')
        '''


class IXSLT(Interface):

    def transform(input, output):
        '''
        Transform input file to output file.

        :param str input:
            input filename.
        :param str output:
            output filename.

        >>> T.transform('input.xml', 'output.xml')
        '''

    def transform_into_stream(input, output_stream):
        '''
        Transform input file to output stream.

        :param str input:
            input filename.
        :param output_stream:
            output stream.
        :type output_stream:
            byte-oriented file-like object.

        >>> T.transform_into_stream('input.xml', sys.stdout.buffer)
        '''


class IXSLTFactory(Interface):

    def xslt_from_file(xsl_path):
        '''
        Create an XSL Transformer from a file.

        :param str xsl_path:
            .xsl file path
        :return:
            an instance of XSL Transformer
        :rtype:
            IXSLT

        >>> T = F.xslt_from_file('transform.xsl')
        '''
