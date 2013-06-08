# -*- coding: utf-8 -*-
from __future__ import with_statement
import logging
import os.path
from storage import open_storage
from storage import resolve_path
from storage import makedirs_to_file
from storage import put_file
from storage import copy_file
from storage import iterate_files_recursively
from storage._zipfile import ZipFileStorage
from storage.fs import FileSystemStorage
from manifest import Manifest
from description import Description


logger = logging.getLogger(__name__)


def is_package(folder):
    if 'META-INF' not in folder:
        return False
    if 'manifest.xml' not in folder['META-INF']:
        return False
    return True


MANIFEST_PATH = os.path.join('META-INF', 'manifest.xml')
DESCRIPTION_PATH = 'description.xml'


def add_file(stg, manifest, path, full_path, media_type):
    ''' add a file into the storage and manifest.

    :param stg: a storage
    :param manifest: an instance of Manifest
    :param path: path to the file on the filesystem.
    :param full_path: ``manifest:full-path`` value of ``manifest:file-entry``
    :param media_type: ``manifest:media-type`` value of ``manifest:file-entry``
    '''
    node = makedirs_to_file(stg, full_path)
    put_file(node, path)
    manifest[full_path] = media_type
    return node


def add_component_file(stg, manifest, path, full_path, type, platform=None):
    ''' add a component file.

    :param stg: a storage
    :param manifest: an instance of Manifest
    :param path: path to the file on the filesystem.
    :param full_path: ``manifest:full-path`` value of ``manifest:file-entry``
    :param type: ``native``, ``Java``, ``Python`` or None
    :param platform: supposed platform to run this component.

    if ``type`` is None, this component is meant to be registered with
    `Passive Component Registration
    <http://wiki.openoffice.org/wiki/Documentation/DevGuide/Extensions/Passive_Component_Registration>`_
    and the file specified with ``path`` should be an XML file, which is
    defined in the document above.

    For more informations, see `File Format
    <http://wiki.openoffice.org/wiki/Documentation/DevGuide/Extensions/File_Format>`_.
    '''
    mimetype = 'application/vnd.sun.star.uno-component'
    if type:
        mimetype += '; ' + type
    if platform:
        mimetype += '; ' + platform
    return add_file(stg, manifest, path, full_path, mimetype=mimetype)


def add_type_library(stg, manifest, path, full_path, type):
    ''' add a UNO type library.

    :param stg: a storage
    :param manifest: an instance of Manifest
    :param type: ``RDB`` or ``Java``
    '''

    typelib_extensions = dict(RDB='.rdb', Java='.jar')

    if type not in typelib_extensions.keys():
        raise ValueError('type: unsupported value of %r' % type)

    if not full_path.lower().endswith(typelib_extensions[type]):
        msg = 'adding %r type library %r with name %r: really intended?'
        logger.warning(msg, type, path, full_path)

    mimetype = 'application/vnd.sun.star.uno-typelibrary'
    mimetype += '; type=' + type
    return add_file(stg, manifest, path, full_path, mimetype)


def add_basic_library(stg, manifest, path, full_path):
    ''' add a basic library

    :param stg: a storage
    :param manifest: an instance of Manifest
    '''
    mimetype = 'application/vnd.sun.star.basic-library'
    return add_file(stg, manifest, path, full_path, mimetype=mimetype)


def add_dialog_library(stg, manifest, path, full_path):
    ''' add a dialog library

    :param stg: a storage
    :param manifest: an instance of Manifest
    '''
    mimetype = 'application/vnd.sun.star.dialog-library'
    return add_file(stg, manifest, path, full_path, mimetype=mimetype)


def add_configuration_data_file(stg, manifest, path, full_path):
    ''' add a configuration data file.

    :param stg: a storage
    :param manifest: an instance of Manifest
    '''
    mimetype = 'application/vnd.sun.star.configuration-data'
    return add_file(stg, manifest, path, full_path, mimetype=mimetype)


def add_configuration_schema_file(stg, manifest, path, full_path):
    ''' add a configuration schema file.

    :param stg: a storage
    :param manifest: an instance of Manifest
    '''
    mimetype = 'application/vnd.sun.star.configuration-schema'
    return add_file(stg, manifest, path, full_path, mimetype=mimetype)


def build(package_path, manifest, description, files=dict(),
          storage_factory=ZipFileStorage):
    ''' Build a OXT Package.

    :param package_path: path to an .oxt package to be built
    :param manifest: an instance of Manifest
    :param description: an instance of Description
    :param files: package files, in a form of (path, node) dict
    :param storage_factory: storage factory for the package.
                            Default to ZipFileStorage
    '''

    assert not any(node is None for node in files.values())
    assert all(path in files for path in manifest)
    assert all(path in files for path in description.required_files())

    logger.info('creating %s', package_path)
    with storage_factory(package_path, 'w') as stg:
        logger.info('writing %s', MANIFEST_PATH)
        manifest_node = makedirs_to_file(stg, MANIFEST_PATH)
        with manifest_node.open('w') as f:
            manifest.dump(f)

        logger.info('writing %s', DESCRIPTION_PATH)
        desc_node = makedirs_to_file(stg, DESCRIPTION_PATH)
        with desc_node.open('w') as f:
            description.write(f)

        for path in sorted(files):
            node = files[path]
            logger.info('writing %s', path)
            dest = makedirs_to_file(stg, path)
            copy_file(node, dest)


def build_from(package_path,
               src_folder,
               manifest_path=None,
               description_path=None,
               files=[],
               excludes=[],
               storage_factory=ZipFileStorage):

    if manifest_path:
        with file(manifest_path) as f:
            manifest = Manifest()
            manifest.load(f)
    else:
        node = resolve_path(src_folder, MANIFEST_PATH)
        if node:
            with node.open() as f:
                manifest = Manifest()
                manifest.load(f)
        else:
            logger.error('%s: not found' % MANIFEST_PATH)
            raise IOError('%s: not found' % MANIFEST_PATH)

    if description_path:
        with file(description_path) as f:
            description = Description.parse(f)
    else:
        node = resolve_path(src_folder, DESCRIPTION_PATH)
        if node:
            with node.open() as f:
                description = Description.parse(f)
        else:
            raise IOError('%s: not found' % DESCRIPTION_PATH)

    package_path = make_output_path(package_path, description)
    package_files = dict()

    from itertools import chain
    required_files = chain(manifest, description.required_files())
    for path in required_files:
        node = resolve_path(src_folder, path)
        if node is None:
            raise IOError('%s: not found' % path)
        package_files[path] = node

    files = ((path, resolve_path(src_folder, path)) for path in files)
    files = expand_folders(files)
    files = exclude_files(excludes, files)
    package_files.update(files)

    return build(package_path, manifest, description, package_files,
                 storage_factory=storage_factory)


def make_output_path(path, desc=None):
    if os.path.isdir(path):
        dirname = path
        name = ''
    else:
        dirname, name = os.path.split(path)

    # default name will be used if not given
    if name == '':
        if desc is None:
            raise ValueError('%s: invalid path' % path)
        name = package_name_from_desc(desc)

    return os.path.join(dirname, name)


def package_name_from_desc(desc):
    id = desc.identifier
    version = desc.version
    if version:
        return '-'.join([id, version]) + '.oxt'
    else:
        return id + '.oxt'


def expand_folders(resolved_nodes):
    for path, node in resolved_nodes:
        if hasattr(node, '__iter__'):
            for path, node in iterate_files_recursively(node, path):
                yield path, node
        else:
            yield path, node


def exclude_files(patterns, resolved_nodes):
    from fnmatch import fnmatch
    for path, node in resolved_nodes:
        excluded = False
        for pat in patterns:
            if fnmatch(path, pat):
                logger.info('exclude %s (by %s)', path, pat)
                excluded = True
        if not excluded:
            yield path, node


def init_main():
    doc = '''Usage: oxt-pkg-init [options] <package-path>

    --help      Print this screen.
    '''

    from docopt import docopt
    args = docopt(doc)
    logging.basicConfig(level=logging.INFO)

    package_path = args['<package-path>']

    manifest = Manifest()
    description = Description()

    with open_storage(package_path, 'w') as stg:
        with makedirs_to_file(stg, MANIFEST_PATH).open('w') as f:
            manifest.dump(f)
        with makedirs_to_file(stg, DESCRIPTION_PATH).open('w') as f:
            description.write(f)


def show_main():
    doc = '''Usage: oxt-pkg-show [options] <package-path>

    --help      Print this screen.
    '''

    from docopt import docopt
    args = docopt(doc)
    logging.basicConfig(level=logging.INFO)

    package_path = args['<package-path>']
    with open_storage(package_path) as pkg:
        with resolve_path(pkg, MANIFEST_PATH).open() as f:
            manifest = Manifest()
            manifest.load(f)

        with resolve_path(pkg, DESCRIPTION_PATH).open() as f:
            description = Description.parse(f)

        from description import print_human_readable
        print_human_readable(description, pkg)

        for path in manifest:
            item = manifest[path]
            print path, item['media-type'],
            node = resolve_path(pkg, path)
            if node:
                print '-- OK'
            else:
                print '-- MISSING'


def build_main():
    doc = '''Usage: oxt-pkg-build [options] <src-folder> <add-files>...

    -o OUTPUT-PATH                  Output path
    -m MANIFEST                     META-INF/manifest.xml
    -d DESCRIPT                     description.xml
    -E EXCLUDE, --exclude=EXCLUDE   exclude patterns; separated by %r.
                --help              Print this screen.

    <src-folder>                    root folder containing package files
    <add-files>                     additional files (relative to <src-folder>)
    ''' % os.pathsep

    from docopt import docopt
    args = docopt(doc)
    logging.basicConfig(level=logging.INFO)

    src_folder_path = args['<src-folder>']
    add_files = args['<add-files>']
    output_path = args['-o'] or '.'
    manifest_path = args['-m']
    description_path = args['-d']
    excludes = args['--exclude'] or ''
    excludes = excludes.strip().split(os.pathsep)

    with FileSystemStorage(src_folder_path) as src_folder:
        build_from(output_path,
                   src_folder,
                   manifest_path=manifest_path,
                   description_path=description_path,
                   files=add_files,
                   excludes=excludes)


def check_main():
    doc = '''Usage: oxt-pkg-show [options] <package-path>

    --help      Print this screen.
    '''

    from docopt import docopt
    args = docopt(doc)
    logging.basicConfig(level=logging.INFO)

    package_path = args['<package-path>']
    with open_storage(package_path) as pkg:
        with resolve_path(pkg, MANIFEST_PATH).open() as f:
            manifest = Manifest()
            manifest.load(f)

        with resolve_path(pkg, DESCRIPTION_PATH).open() as f:
            description = Description.parse(f)

        missing = dict()

        for path in manifest:
            node = resolve_path(pkg, path)
            if node is None:
                missing[path] = MANIFEST_PATH

        for path in description.required_files():
            node = resolve_path(pkg, path)
            if node is None:
                missing[path] = DESCRIPTION_PATH

        if missing:
            for path in sorted(missing):
                referer = missing[path]
                logger.error('%s: MISSING (refered in %s)',
                             path, referer)
            raise SystemExit(1)
        else:
            logger.info('%s: OK, identifier=%s, version=%s', package_path,
                        description.identifier, description.version)
