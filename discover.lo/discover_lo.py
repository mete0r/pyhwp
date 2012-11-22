# -*- coding: utf-8 -*-

import os
import os.path
import sys
import logging
from discover_jre import executable_in_dir
from discover_jre import expose_options


logger = logging.getLogger(__name__)


def wellknown_locations():
    if sys.platform == 'win32':
        program_files = 'c:\\program files'
        if os.path.exists(program_files):
            for name in os.listdir(program_files):
                yield os.path.join(program_files, name)
    if sys.platform.startswith('linux'):
        yield '/usr/lib/libreoffice'  # ubuntu


def discover_lo(in_wellknown=True, in_path=True):
    if in_wellknown:
        for installation in discover_in_wellknown_locations():
            yield installation

    if in_path:
        for installation in discover_in_path():
            yield installation


def discover_in_wellknown_locations():
    for location in wellknown_locations():
        installation = contains_program(location)
        if installation:
            yield installation


def discover_in_path():
    if 'PATH' in os.environ:
        path = os.environ['PATH']
        path = path.split(os.pathsep)
        for dir in path:
            libreoffice = contains_libreoffice(dir)
            if libreoffice:
                entry = dict(libreoffice=libreoffice, through='PATH')

                # resolve symlinks
                resolved = os.path.realpath(libreoffice)
                location = os.path.dirname(os.path.dirname(resolved))
                installation = contains_program(location)
                if installation:
                    entry.update(installation)

                uno_python = python_import_uno(sys.executable)
                if uno_python:
                    entry.update(get_uno_python(uno_python))

                yield entry


def contains_libreoffice(dir):
    return executable_in_dir('libreoffice', dir)


def contains_program(location):
    program_dir = os.path.join(location, 'program')
    if os.path.isdir(program_dir):
        installation = dict(location=location, program=program_dir)
        soffice = executable_in_dir('soffice', program_dir)
        if soffice:
            installation['soffice'] = soffice
        unopkg = executable_in_dir('unopkg', program_dir)
        if unopkg:
            installation['unopkg'] = unopkg

        program_python = executable_in_dir('python', program_dir)
        if program_python:
            uno_python = python_import_uno(program_python)
        else:
            uno_python = python_import_uno(sys.executable)

        if uno_python:
            installation.update(get_uno_python(uno_python))

        basis_link = os.path.join(location, 'basis-link')
        if os.path.islink(basis_link):
            location = os.path.realpath(basis_link)

        ure = find_ure(location)
        if ure:
            installation['ure'] = ure

        return installation


def find_ure(location):
    ure_link = os.path.join(location, 'ure-link')
    if os.path.islink(ure_link):
        ure = os.path.realpath(ure_link)
        if os.path.isdir(ure):
            return ure

    # win32
    ure = os.path.join(location, 'ure')
    if os.path.isdir(ure):
        return ure


def python_import_uno(python):
    import subprocess
    cmd = [python, '-c', 'import uno, unohelper']
    ret = subprocess.call(cmd)
    if ret == 0:
        return python


def get_uno_python(uno_python):
    uno_python_core, modules = get_uno_locations(uno_python,
                                            ['uno', 'pyuno',
                                             'unohelper'])

    yield 'uno_python', uno_python
    yield 'uno_python_core', uno_python_core

    uno_pythonpath = set(os.path.dirname(modules[name])
                         for name in ['uno', 'unohelper'])
    uno_pythonpath = os.pathsep.join(list(uno_pythonpath))
    yield 'uno_pythonpath', uno_pythonpath

    for name in modules:
        yield name, modules[name]


def get_uno_locations(python, modules):
    statements = ['print __import__("sys").executable']
    statements.extend('print __import__("%s").__file__' % name
                      for name in modules)
    statements = ';'.join(statements)
    cmd = [python, '-c', statements]
    lines = subprocess_check_output(cmd)
    lines = lines.strip()
    lines = lines.split('\n')
    return lines[0], dict(zip(modules, lines[1:]))


def subprocess_check_output(cmd):
    import tempfile
    fd, name = tempfile.mkstemp()
    f = os.fdopen(fd, 'r+')
    try:
        import subprocess
        ret = subprocess.call(cmd, stdout=f)
        if ret != 0:
            logger.error('%d returned: %s', ret, ' '.join(cmd))
            raise Exception('%s exit with %d' % (cmd[0], ret))
        f.seek(0)
        return f.read()
    finally:
        f.close()
        os.unlink(name)


LO_VARS = ('libreoffice'
           ' location program soffice unopkg'
           ' ure'
           ' uno_python uno_python_core uno_pythonpath uno pyuno unohelper').split(' ')


def log_discovered(installations):
    for installation in installations:
        msg = 'discovered:'
        for name in LO_VARS:
            if name in installation:
                msg += ' ' + name + '=' + installation[name]
        logger.info(msg)
        yield installation


class Discover(object):
    ''' Discover a LibreOffice installation and provide its location.
    '''

    def __init__(self, buildout, name, options):
        self.__logger = logger = logging.getLogger(name)
        for k, v in options.items():
            logger.info('%s: %r', k, v)

        self.__recipe = options['recipe']
        self.__generate_stub = None

        # special marker
        not_found = options.get('not-found', 'not-found')

        # expose platform-specific path seperator for convinience
        options['pathsep'] = os.pathsep

        if 'location' in options:
            # if location is explicitly specified, it must contains java
            # executable.
            discovered = contains_program(options['location'])
            if discovered:
                # LO found, no further operation required.
                expose_options(options, LO_VARS, discovered,
                               not_found=not_found, logger=logger)
                return
            from zc.buildout import UserError
            raise UserError('LO not found at %s' % options['location'])

        in_wellknown = options.get('search-in-wellknown-places',
                                   'true').lower().strip()
        in_wellknown = in_wellknown in ('true', 'yes', '1')
        in_path = options.get('search-in-path', 'true').lower().strip()
        in_path = in_path in ('true', 'yes', '1')

        # location is not specified: try to discover a LO installation
        discovered = discover_lo(in_wellknown, in_path)
        discovered = log_discovered(discovered)
        discovered = list(discovered)

        if discovered:
            discovered = discovered[0]
            logger.info('following LO installation will be used:')
            expose_options(options, LO_VARS, discovered, not_found=not_found,
                           logger=logger)
            return

        expose_options(options, LO_VARS, dict(), not_found=not_found,
                       logger=logger)
        return

        # no LO found: stub generation
        parts_dir = buildout['buildout']['parts-directory']
        self.__generate_stub = os.path.join(parts_dir, name)
        options['location'] = self.__generate_stub
        logger.info('LO not found: a dummy LO will be generated')
        logger.info('location = %s (updating)', self.__generate_stub)

    def install(self):
        location = self.__generate_stub
        if location is None:
            return

        if not os.path.exists(location):
            os.makedirs(location)
        yield location
        self.__logger.info('A dummy LO has been generated: %s', location)

    update = install
