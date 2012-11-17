# -*- coding: utf-8 -*-
import logging


def console(soffice='soffice'):
    import uno
    import unokit.contexts
    import unokit.services
    import oxt_tool.remote

    with oxt_tool.remote.new_remote_context(soffice=soffice) as context:
        desktop = unokit.services.css.frame.Desktop()
        def new_textdoc():
            return desktop.loadComponentFromURL('private:factory/swriter',
                                                '_blank', 0, tuple())
        from unokit.util import dump, dumpdir
        local = dict(uno=uno, context=context,
                     css=unokit.services.css, dump=dump, dumpdir=dumpdir,
                     desktop=desktop, new_textdoc=new_textdoc)
        __import__('code').interact(banner='oxt-console', local=local)


def dict_to_namedvalue(d):
    import uno
    nv = list()
    for n, v in d.items():
        if isinstance(v, dict):
            v = dict_to_namedvalue(v)
        item = uno.createUnoStruct('com.sun.star.beans.NamedValue')
        item.Name = n
        item.Value = v
        nv.append(item)
    return tuple(nv)


def test_remotely(soffice, discover_dirs, extra_path, logconf_path):
    import sys
    import os
    import os.path
    import discover
    import oxt_tool.remote

    logger = logging.getLogger('unokit')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    logfmt = logging.Formatter(('frontend %5d ' % os.getpid())
                               +'%(message)s')
    logchn = logging.StreamHandler()
    logchn.setFormatter(logfmt)
    logger = logging.getLogger('frontend')
    logger.addHandler(logchn)
    logger.setLevel(logging.INFO)

    working_dir = sys.argv[1]
    working_dir = os.path.abspath(working_dir)

    for path in sys.path:
        logger.info('sys.path: %s', path)

    if logconf_path:
        logconf_path = os.path.abspath(logconf_path)

    backend_path = sys.modules['oxt_tool'].__file__
    backend_path = os.path.dirname(backend_path)
    backend_path = os.path.join(backend_path, 'backend.py')
    backend_name = 'backend.TestRunnerJob'

    tss = []
    for d in discover_dirs:
        d = os.path.abspath(d)
        logger.info('discover tests: %s', d)
        testloader = discover.DiscoveringTestLoader()
        testsuite = testloader.discover(d)
        tss.append(testsuite)
    import unittest
    testsuite = unittest.TestSuite(tss)

    with oxt_tool.remote.new_remote_context(soffice=soffice) as context:
        logger.info('remote context created')
        factory = load_component(backend_path, backend_name)
        if factory:
            backendjob = factory.createInstanceWithContext(context)
            if backendjob:
                import cPickle
                from unokit.adapters import OutputStreamToFileLike
                pickled_testsuite = cPickle.dumps(testsuite)
                outputstream = OutputStreamToFileLike(sys.stderr)
                logstream = OutputStreamToFileLike(sys.stderr)
                args = dict(outputstream=outputstream,
                            logstream=logstream,
                            pickled_testsuite=pickled_testsuite,
                            extra_path=tuple(extra_path),
                            logconf_path=logconf_path,
                            working_dir=working_dir)
                args = dict_to_namedvalue(args)
                result = backendjob.execute(args)
                result = str(result)
                result = cPickle.loads(result)
                return 0 if result['successful'] else 1
    return -1


def load_component(component_path, component_name):
    import os
    import os.path
    import uno
    from unokit.services import css
    loader = css.loader.Python()
    if loader:
        component_path = os.path.abspath(component_path)
        component_url = uno.systemPathToFileUrl(component_path)

        return loader.activate(component_name, '',
                               component_url, None)


def console_in_proc(soffice='soffice'):
    import os
    import unohelper
    from com.sun.star.task import XJob
    import oxt_tool.remote

    logfmt = logging.Formatter(('frontend %5d ' % os.getpid())
                               +'%(message)s')
    logchn = logging.StreamHandler()
    logchn.setFormatter(logfmt)
    logger = logging.getLogger('frontend')
    logger.addHandler(logchn)
    logger.setLevel(logging.INFO)

    class ConsoleInput(unohelper.Base, XJob):

        def __init__(self, context):
            self.context = context

        def execute(self, arguments):
            prompt, = arguments
            try:
                return raw_input(prompt.Value)
            except EOFError:
                return None

    import sys
    import os.path
    backend_path = sys.modules['oxt_tool'].__file__
    backend_path = os.path.dirname(backend_path)
    backend_path = os.path.join(backend_path, 'backend.py')
    backend_name = 'backend.ConsoleJob'

    with oxt_tool.remote.new_remote_context(soffice=soffice) as context:
        logger.info('remote context created')
        factory = load_component(backend_path, backend_name)
        if factory:
            backendjob = factory.createInstanceWithContext(context)
            if backendjob:
                from unokit.adapters import OutputStreamToFileLike
                outstream = OutputStreamToFileLike(sys.stderr)
                args = dict(inp=ConsoleInput(context),
                            outstream=outstream)
                args = dict_to_namedvalue(args)
                backendjob.execute(args)


def iter_package_files():
    import os
    import os.path

    # from description.xml
    filenames = []
    filenames += ['description.xml',
                  'registration/COPYING.txt',
                  'description/desc_ko.txt',
                  'description/desc_en.txt']
    for x in filenames:
        yield x

    # from META-INF/manifest.xml
    filenames = []
    filenames += ['META-INF/manifest.xml',
                  'components.py',
                  'Types.xcu',
                  'Filter.xcu']
    for x in filenames:
        yield x

    # from pythonpath
    for dirpath, dirnames, filenames in os.walk('pythonpath',
                                                followlinks=True):
        for filename in filenames:
            if filename.endswith('.pyc'):
                continue
            if filename.endswith('$py.class'):
                continue
            if filename.startswith('.'):
                continue
            yield os.path.join(dirpath, filename)


def make_package(oxt_path, src_dir=None):
    if src_dir is not None:
        import os
        old_wd = os.getcwd()
        os.chdir(src_dir)
        try:
            return make_package(oxt_path)
        finally:
            os.chdir(old_wd)

    filenames = iter_package_files()

    from zipfile import ZipFile, ZIP_DEFLATED
    zf = ZipFile(oxt_path, 'w', ZIP_DEFLATED)
    try:
        for filename in filenames:
            print filename
            zf.write(filename)
    finally:
        zf.close()


def make():
    import sys
    import os.path
    oxt_path = os.path.abspath(sys.argv[1])
    src_dir = os.path.abspath(sys.argv[2])
    make_package(oxt_path, src_dir)


def install(unopkg='unopkg'):
    import sys
    cmd = [unopkg, 'add', '-v', '-s']
    cmd.extend(sys.argv[1:])
    cmd = [('"%s"' % x) if ' ' not in x else x
            for x in cmd]
    cmd = ' '.join(cmd)
    import os
    return os.system(cmd)


class Console(object):
    def __init__(self, buildout, name, options):
        import os.path
        self.__name = name
        self.__logger = logging.getLogger(name)
        self.__bindir = buildout['buildout']['bin-directory']

        soffice = options.get('soffice', 'soffice').strip()
        if not os.path.exists(soffice):
            self.__skip = True
            self.__logger.info('soffice not found at: %s', soffice)
            self.__logger.info('installation will be skipped')
            return

        in_proc = options.get('in_proc', 'true').strip().lower()
        in_proc = in_proc in ['true', 'yes', '1']

        self.__python = options.get('python', '').strip()
        self.__soffice = soffice
        self.__in_proc = in_proc
        self.__skip = False

    def install(self):
        if self.__skip:
            self.__logger.info('skipped')
            return []

        from zc.buildout import easy_install
        import pkg_resources
        import sys
        ws = [pkg_resources.get_distribution(dist)
              for dist in ['unokit', 'oxt.tool']]
        if self.__in_proc:
            func = 'console_in_proc'
        else:
            func = 'console'
        entrypoints = [(self.__name, 'oxt_tool', func)]
        arguments = '%r' % self.__soffice
        if self.__python:
            python = self.__python
        else:
            python = sys.executable
        return easy_install.scripts(entrypoints,
                                    ws, python, self.__bindir,
                                    arguments=arguments)

    update = install


class TestRunner(object):
    def __init__(self, buildout, name, options):
        import os.path
        self.__name = name
        self.__logger = logging.getLogger(name)
        self.__bindir = buildout['buildout']['bin-directory']
        self.__skip = False
        self.__python = options.get('python', '').strip()

        self.__soffice = options.get('soffice', 'soffice').strip()
        if not os.path.exists(self.__soffice):
            self.__skip = True
            self.__logger.info('soffice not found at: %s', self.__soffice)
            self.__logger.info('installation will be skipped')
            return
        self.__discover = options['discover'].split()
        self.__extra_path = options['extra_path'].split()
        self.__logconf_path = options.get('logconf_path')

    def install(self):
        if self.__skip:
            self.__logger.info('skipped')
            return []

        from zc.buildout import easy_install
        import pkg_resources
        import sys
        ws = [pkg_resources.get_distribution(dist)
              for dist in ['unokit', 'oxt.tool', 'discover']]
        entrypoints = [(self.__name, 'oxt_tool', 'test_remotely')]
        arguments = '%r, %r, %r, %r'
        arguments = arguments % (self.__soffice,
                                 self.__discover,
                                 self.__extra_path,
                                 self.__logconf_path)
        if self.__python:
            python = self.__python
        else:
            python = sys.executable
        return easy_install.scripts(entrypoints,
                                    ws, python, self.__bindir,
                                    arguments=arguments)

    update = install


class Installer(object):
    def __init__(self, buildout, name, options):
        import os.path
        self.__name = name
        self.__logger = logging.getLogger(name)
        self.__bindir = buildout['buildout']['bin-directory']

        unopkg = options.get('unopkg', 'unopkg').strip()
        if not os.path.exists(unopkg):
            self.__skip = True
            self.__logger.info('unopkg not found at: %s', unopkg)
            self.__logger.info('installation will be skipped')
            return

        self.__unopkg = unopkg
        self.__skip = False

    def install(self):
        if self.__skip:
            self.__logger.info('skipped')
            return []

        from zc.buildout import easy_install
        import pkg_resources
        import sys
        ws = [pkg_resources.get_distribution(dist)
              for dist in ['unokit', 'oxt.tool']]
        entrypoints = [(self.__name, 'oxt_tool', 'install')]
        arguments = '%r' % self.__unopkg
        return easy_install.scripts(entrypoints,
                                    ws, sys.executable, self.__bindir,
                                    arguments=arguments)

    update = install
