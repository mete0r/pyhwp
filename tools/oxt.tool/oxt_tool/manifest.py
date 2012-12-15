# -*- coding: utf-8 -*-
from __future__ import with_statement
import logging


logger = logging.getLogger(__name__)


NS_URI = 'urn:oasis:names:tc:opendocument:xmlns:manifest:1.0'
NS_URI = 'http://openoffice.org/2001/manifest'
NS_PREFIX = 'manifest'


class Manifest(object):
    ''' Represent ``META-INF/manifest.xml`` file.
    '''

    def __init__(self, namespace_uri=NS_URI):
        self.entries = dict()
        self.NS_URI = namespace_uri

    @property
    def NS(self):
        return '{' + self.NS_URI + '}'

    def __setitem__(self, full_path, value):
        if isinstance(value, basestring):
            value = {'media-type': value}
        self.entries[full_path] = value

    def __getitem__(self, full_path):
        return self.entries[full_path]

    def __delitem__(self, full_path):
        del self.entries[full_path]

    def __iter__(self):
        for full_path in sorted(self.entries):
            yield full_path
    
    def add_file(self, full_path, media_type):
        self[full_path] = {'media-type': media_type}

    def load(self, f):
        if isinstance(f, basestring):
            with file(f) as f:
                return self.load(f)
        import xml.etree.ElementTree as ET

        doc = ET.parse(f)
        root = doc.getroot()
        NS = self.NS
        for e in root.findall(NS + 'file-entry'):
            self.add_file(e.get(NS + 'full-path'),
                          e.get(NS + 'media-type'))

    def dump(self, f):
        import xml.etree.ElementTree as ET

        root = ET.Element(NS_PREFIX + ':manifest',
                          {'xmlns:' + NS_PREFIX: self.NS_URI})
        doc = ET.ElementTree(root)
        for path in self:
            e = self.entries[path]
            attrs = dict((NS_PREFIX + ':' + k, v)
                         for k, v in e.items())
            attrs[NS_PREFIX + ':full-path'] = path
            ET.SubElement(root, NS_PREFIX + ':file-entry', attrs)

        f.write('<?xml version="1.0" encoding="utf-8"?>')
        doc.write(f, encoding='utf-8')

    def save(self, path):
        with file(path, 'w') as f:
            self.dump(f)


def init_main():
    doc = '''Usage: oxt-manifest-init [options] <manifest-file>

    --help          Show this screen.
    '''
    from docopt import docopt
    args = docopt(doc)
    logging.basicConfig(level=logging.INFO)

    with file(args['<manifest-file>'], 'w') as f:
        manifest = Manifest()
        manifest.dump(f)


def ls_main():
    doc = '''Usage: oxt-manifest-ls [options] <manifest-file>

    --help          Show this screen.
    '''
    from docopt import docopt
    args = docopt(doc)
    logging.basicConfig(level=logging.INFO)

    with file(args['<manifest-file>']) as f:
        manifest = Manifest()
        manifest.load(f)

    for path in manifest:
        e = manifest[path]
        print ' '.join([path, e['media-type']])


def add_main():
    doc = '''Usage: oxt-manifest-add [options] <manifest-file> <file> <media-type>

    --help          Show this screen.

    '''
    from docopt import docopt

    args = docopt(doc)
    logging.basicConfig(level=logging.INFO)

    with file(args['<manifest-file>']) as f:
        manifest = Manifest()
        manifest.load(f)

    media_type = args['<media-type>']
    path = args['<file>']

    manifest[path] = media_type
    logger.info('Add %s: %s', path, media_type)

    with file(args['<manifest-file>'], 'w') as f:
        manifest.dump(f)


def rm_main():
    doc = '''Usage: oxt-manifest-rm [options] <manifest-file> <files>...

    -r <root-dir>   Project root. If omitted, current directory will be used.
    --help          Show this screen.

    '''
    from docopt import docopt

    args = docopt(doc)
    logging.basicConfig(level=logging.INFO)

    with file(args['<manifest-file>']) as f:
        manifest = Manifest()
        manifest.load(f)

    for path in args['<files>']:
        if path in manifest:
            del manifest[path]
            logger.info('RM %s', path)
        else:
            logger.warning('Skip %s; not found', path)

    with file(args['<manifest-file>'], 'w') as f:
        manifest.dump(f)
