# -*- coding: utf-8 -*-
from __future__ import with_statement
import logging


logger = logging.getLogger(__name__)


NS_URI = 'http://openoffice.org/extensions/description/2006'
NS_URI_DEP = 'http://openoffice.org/extensions/description/2006'
NS_URI_XLINK = 'http://www.w3.org/1999/xlink'

NS = '{' + NS_URI + '}'
NS_DEP = '{' + NS_URI_DEP + '}'
NS_XLINK = '{' + NS_URI_XLINK + '}'


def as_dict(f):
    def wrapper(*args, **kwargs):
        return dict(f(*args, **kwargs))
    wrapper.items = f
    return wrapper


@as_dict
def get_display_name(doc):
    root = doc.getroot()
    for elt in root.findall(NS + 'display-name/' + NS + 'name'):
        yield elt.get('lang'), elt.text


def set_display_name(doc, display_name):
    import xml.etree.ElementTree as ET
    root = doc.getroot()
    dispname = ET.SubElement(root, 'display-name')
    for lang, name in display_name.items():
        elt = ET.SubElement(dispname, 'name')
        elt.set('lang', lang)
        elt.text = name


@as_dict
def get_extension_description(doc):
    root = doc.getroot()
    for elt in root.findall(NS + 'extension-description/' + NS + 'src'):
        yield elt.get('lang'), elt.get(NS_XLINK + 'href')


def set_extension_description(doc, description):
    import xml.etree.ElementTree as ET
    root = doc.getroot()
    desc = ET.SubElement(root, 'extension-description')
    for lang, url in description.items():
        elt = ET.SubElement(desc, 'src')
        elt.set('lang', lang)
        elt.set('xlink:href', url)


@as_dict
def get_publisher(doc):
    root = doc.getroot()
    for elt in root.findall(NS + 'publisher/' + NS + 'name'):
        yield elt.get('lang'), dict(name=elt.text,
                                    url=elt.get(NS_XLINK + 'href'))


def set_publisher(doc, publisher):
    import xml.etree.ElementTree as ET
    root = doc.getroot()
    pub = ET.SubElement(root, 'publisher')
    for lang, dct in publisher.items():
        elt = ET.SubElement(pub, 'name')
        elt.set('lang', lang)
        elt.set('xlink:href', dct['url'])
        elt.text = dct['name']


def get_license_accept_by(doc):
    root = doc.getroot()
    for elt in root.findall(NS + 'registration/' + NS + 'simple-license'):
        accept_by = elt.get('accept-by')
        if accept_by:
            return accept_by


def get_license(doc):
    root = doc.getroot()
    for elt in root.findall(NS + 'registration/' + NS + 'simple-license'):
        return dict((elt.get('lang'), elt.get(NS_XLINK + 'href'))
                    for elt in elt.findall(NS + 'license-text'))
    return dict()


def get_oo_min_version(doc):
    root = doc.getroot()
    for dep in root.findall(NS + 'dependencies'):
        for elt in dep.findall(NS + 'OpenOffice.org-minimal-version'):
            return elt.get('value')


class Description(object):

    @classmethod
    def parse(cls, f):
        import xml.etree.ElementTree as ET

        doc = ET.parse(f)
        root = doc.getroot()

        def getvalue(xpath, default=None):
            for elt in root.findall(xpath):
                value = elt.get('value', default)
                if value:
                    return value
            return default

        return cls(identifier=getvalue(NS + 'identifier'),
                   version=getvalue(NS + 'version'),
                   platform=getvalue(NS + 'platform', 'all'),
                   display_name=get_display_name(doc),
                   description=get_extension_description(doc),
                   publisher=get_publisher(doc),
                   license_accept_by=get_license_accept_by(doc),
                   license=get_license(doc),
                   oo_min_version=get_oo_min_version(doc))

    def __init__(self,
                 identifier='noname',
                 version='0.0',
                 platform='all',
                 display_name=dict(),
                 description=dict(),
                 publisher=dict(),
                 license_accept_by='admin',
                 license=dict(),
                 oo_min_version=None):
        ''' Generate description.xml

        :param f: output file
        :param identifier: extension identifier
        :param version: extension version
        :param platform: target platform
        :param display_name: localizations of display name
        :param description: localizations of extension description
        :param publisher: localizations of publisher
        :param license_accept_by: who is supposed to accept the license
        :param license: localization of license
        :param oo_min_version: minimal version of LibreOffice

        Each localization parameters are dicts, whose keys are language identifiers
        defined in RFC 3066.

        ``identifier`` specifies `Extension Identifier
        <http://wiki.openoffice.org/wiki/Documentation/DevGuide/Extensions/Extension_Identifiers>`_.

        ``version`` specifies `Extension Version
        <http://wiki.openoffice.org/wiki/Documentation/DevGuide/Extensions/Extension_Versions>`_.

        ``platform`` specifies supposed `Target Platform
        <http://wiki.openoffice.org/wiki/Documentation/DevGuide/Extensions/Target_Platform>`_  on which this extension
        runs. Default value is ``all``.

        ``display_name`` specifies localized `Display Names
        <http://wiki.openoffice.org/wiki/Documentation/DevGuide/Extensions/Display_Name>`_.
        It's a localization dict whose values are localized unicode strings, e.g.::

            display_name = {
                'en': 'Example Filter',
                'ko': u'예제 필터'
            }

        Values of ``description`` is a URL of description file, e.g.::

            description = {
                'en': 'description/en.txt',
                'ko': 'description/ko.txt'
            }

        ``publisher`` specifies `Publisher Information
        <http://wiki.openoffice.org/wiki/Documentation/DevGuide/Extensions/Publisher_Information>`_.
        It's a localization dict whose values are dicts themselves, which have
        ``name`` and ``url``.  ``name`` is a localized name of the publisher and
        ``url`` is a URL of the publisher. For example::

            publisher = {
                'en': {
                    'name': 'John Doe',
                    'url': 'http://example.tld'
                },
                'ko': {
                    'name': u'홍길동',
                    'url': 'http://example.tld'
                }
            }

        Optional ``license_accept_by`` specifies who is supposed to accept the
        license. ``admin`` or ``user``. Default value is 'admin'.

        Optional ``license`` is a localization dict whose values are an URL of
        license file. For example::

            license = {
                'en': 'registration/COPYING'
            }

        See `Simple License
        <http://wiki.openoffice.org/wiki/Documentation/DevGuide/Extensions/Simple_License>`_.
        '''
        self.identifier = identifier
        self.version = version
        self.platform = platform
        self.display_name = display_name
        self.description = description
        self.publisher = publisher
        self.license_accept_by = license_accept_by
        self.license = license
        self.oo_min_version = oo_min_version

    def write(self, f):

        # see http://wiki.openoffice.org/wiki/Documentation/DevGuide/Extensions/Description_of_XML_Elements

        import xml.etree.ElementTree as ET

        root = ET.Element('description', {'xmlns': NS_URI,
                                          'xmlns:dep': NS_URI_DEP,
                                          'xmlns:xlink': NS_URI_XLINK})
        doc = ET.ElementTree(root)

        ET.SubElement(root, 'identifier').set('value', self.identifier)
        ET.SubElement(root, 'version').set('value', self.version)
        ET.SubElement(root, 'platform').set('value', self.platform)

        set_display_name(doc, self.display_name)

        set_extension_description(doc, self.description)

        set_publisher(doc, self.publisher)

        if self.license:
            reg = ET.SubElement(root, 'registration')
            lic = ET.SubElement(reg, 'simple-license')
            lic.set('accept-by', self.license_accept_by)
            for lang, url in self.license.items():
                elt = ET.SubElement(lic, 'license-text')
                elt.set('lang', lang)
                elt.set('xlink:href', url)

        if self.oo_min_version is not None:
            dep = ET.SubElement(root, 'dependencies')
            minver = ET.SubElement(dep, 'OpenOffice.org-minimal-version')
            minver.set('dep:name', 'LibreOffice ' + self.oo_min_version)
            minver.set('value', self.oo_min_version)

        f.write('<?xml version="1.0" encoding="utf-8"?>')
        doc.write(f, encoding='utf-8')

    def required_files(self):
        for url in self.description.values():
            yield url
        for url in self.license.values():
            yield url


def print_human_readable(desc, root_stg=None):
    ''' Print summary in human readable form.

    :param desc: an instance of Description
    :param root_stg: root storage of description.xml
    '''
    from storage import resolve_path
    print 'identifier:', desc.identifier
    print 'version:', desc.version
    print 'platform:', desc.platform

    print 'display-name:'
    for lang, name in desc.display_name.items():
        print '  [%s] %s' % (lang, name)

    print 'extension-description:'
    for lang, url in desc.description.items():
        if not root_stg or resolve_path(root_stg, url):
            state = ''
        else:
            state = ' -- MISSING'
        print '  [%s] %s%s' % (lang, url, state)

    print 'publisher:'
    for lang, publisher in desc.publisher.items():
        print '  [%s] %s (%s)' % (lang,
                                       publisher['name'],
                                       publisher['url'])
    if desc.license:
        print 'license: accept-by', desc.license_accept_by
        for lang, url in desc.license.items():
            if not root_stg or resolve_path(root_stg, url):
                state = ''
            else:
                state = ' -- MISSING'
            print '  [%s] %s%s' % (lang, url, state)

    if desc.oo_min_version:
        print 'dependencies:'
        print '  LibreOffice minimal version:', desc.oo_min_version


def init_main():
    doc = '''Usage: oxt-desc-init [options] <desc-file>

    --help      Print this screen.
    '''

    from docopt import docopt
    args = docopt(doc)
    logging.basicConfig(level=logging.INFO)

    description = Description(identifier='tld.example',
                              version='0.1',
                              display_name=dict(en='Example extension'),
                              publisher=dict(en=dict(name='Publisher Name',
                                                     url='http://example.tld')),
                              license=dict(url=dict(en='COPYING')),
                              description=dict(en='description/en.txt'))
    with file(args['<desc-file>'], 'w') as f:
        description.write(f)


def show_main():
    doc = '''Usage: oxt-desc-show [options] <desc-file>

    --help      Show this screen.
    '''
    from docopt import docopt
    args = docopt(doc)
    logging.basicConfig(level=logging.INFO)

    with file(args['<desc-file>']) as f:
        desc = Description.parse(f)

    print_human_readable(desc)


def version_main():
    doc = '''Usage: oxt-desc-version [options] <desc-file> [<new-version>]

    --help      Show this screen.
    '''
    from docopt import docopt
    args = docopt(doc)
    logging.basicConfig(level=logging.INFO)

    with file(args['<desc-file>'], 'r') as f:
        desc = Description.parse(f)

    new_version = args['<new-version>']
    if new_version is not None:
        logger.info('old: %s', desc.version)
        desc.version = new_version
        logger.info('new: %s', desc.version)
        with file(args['<desc-file>'], 'w') as f:
            desc.write(f)
    else:
        print desc.version


def ls_main():
    doc = '''Usage: oxt-desc-ls [options] <desc-file>

    --help      Show this screen.
    '''
    from docopt import docopt
    args = docopt(doc)
    logging.basicConfig(level=logging.INFO)

    with file(args['<desc-file>']) as f:
        desc = Description.parse(f)

    for path in desc.required_files():
        print path
