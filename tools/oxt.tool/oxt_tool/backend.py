# -*- coding: utf-8 -*-
import logging
import sys
import os

logfmt = logging.Formatter((' backend %5d ' % os.getpid())
                           +'%(message)s')
logger = logging.getLogger('backend')
logger.setLevel(logging.INFO)


logger.info('backend: %s', os.getpid())
logger.info('sys.executable = %s', sys.executable)

import unohelper
g_ImplementationHelper = unohelper.ImplementationHelper()

def implementation(component_name, *services):
    def decorator(cls):
        g_ImplementationHelper.addImplementation(cls, component_name, services)
        return cls
    return decorator


from com.sun.star.task import XJob

@implementation('backend.TestRunnerJob')
class TestRunnerJob(unohelper.Base, XJob):

    def __init__(self, context):
        self.context = context

    def execute(self, arguments):
        import sys
        args = dict((nv.Name, nv.Value) for nv in arguments)

        cwd = os.getcwd()
        working_dir = args['working_dir']
        os.chdir(working_dir)
        try:
            logstream = args['logstream']
            logstream = FileFromStream(logstream)
            loghandler = logging.StreamHandler(logstream)
            loghandler.setFormatter(logfmt)
            logger.addHandler(loghandler)
            try:
                logger.info('current dir: %s', cwd)
                logger.info('working dir: %s', working_dir)
                logger.info('sys.path:')
                for x in sys.path:
                    logger.info('- %s', x)
                return self.run(args)
            finally:
                logger.removeHandler(loghandler)
        finally:
            os.chdir(cwd)

    def run(self, args):
        import cPickle
        outstream = args.get('outputstream')
        outstream = FileFromStream(outstream)

        extra_path = args.get('extra_path')
        if extra_path:
            logger.info('extra_path: %s', ' '.join(extra_path))
            sys.path.extend(extra_path)

        logconf_path = args.get('logconf_path')
        if logconf_path:
            import logging.config
            logging.config.fileConfig(logconf_path)

        from hwp5.plat import _uno
        _uno.enable()

        pickled_testsuite = args.get('pickled_testsuite')
        if not pickled_testsuite:
            logger.error('pickled_testsuite is required')
            return cPickle.dumps(dict(successful=False, tests=0, failures=0,
                                      errors=0))

        pickled_testsuite = str(pickled_testsuite)
        testsuite = cPickle.loads(pickled_testsuite)
        logger.info('Test Suite Unpickled')

        from unittest import TextTestRunner
        testrunner = TextTestRunner(stream=outstream)
        result = testrunner.run(testsuite)
        result = dict(successful=result.wasSuccessful(),
                      tests=result.testsRun,
                      failures=list(str(x) for x in result.failures),
                      errors=list(str(x) for x in result.errors))
        return cPickle.dumps(result)


import contextlib


@contextlib.contextmanager
def sandbox(working_dir, **kwargs):
    import os
    import sys

    backup = dict()
    class NOTHING:
        pass
    if not hasattr(sys, 'argv'):
        sys.argv = NOTHING

    NAMES = ['path', 'argv', 'stdin', 'stdout', 'stderr']
    for x in NAMES:
        assert x in kwargs

    backup['cwd'] = os.getcwd()
    os.chdir(working_dir)
    for x in NAMES:
        backup[x] = getattr(sys, x)
        setattr(sys, x, kwargs[x])

    try:
        yield
    finally:
        for x in NAMES:
            setattr(sys, x, backup[x])
        os.chdir(backup['cwd'])

        if sys.argv is NOTHING:
            del sys.argv


@implementation('backend.RemoteRunJob')
class RemoteRunJob(unohelper.Base, XJob):

    def __init__(self, context):
        self.context = context

    def execute(self, arguments):
        args = dict((nv.Name, nv.Value) for nv in arguments)

        logpath = args.get('logfile')
        if logpath is not None:
            logfile = file(logpath, 'a')
            loghandler = logging.StreamHandler(logfile)
            logger.addHandler(loghandler)

        import datetime
        logger.info('-'*10 + (' start at %s' % datetime.datetime.now()) + '-'*10)
        try:
            return self.run(args)
        finally:
            logger.info('-'*10 + (' stop at %s' % datetime.datetime.now()) + '-'*10)
            if logpath is not None:
                logger.removeHandler(loghandler)

    def run(self, args):
        import cPickle

        working_dir = args['working_dir']
        path = cPickle.loads(str(args['path']))
        argv = cPickle.loads(str(args['argv']))
        stdin = FileFromStream(args['stdin'])
        stdout = FileFromStream(args['stdout'])
        stderr = FileFromStream(args['stderr'])

        script = argv[0]
        with sandbox(working_dir, path=path, argv=argv, stdin=stdin,
                     stdout=stdout, stderr=stderr):
            g = dict(__name__='__main__')
            try:
                execfile(script, g)
            except SystemExit, e:
                return e.code
            except Exception, e:
                logger.exception(e)
                raise
            except:
                import traceback
                logger.error('%s' % traceback.format_exc())
                raise


@implementation('backend.ConsoleJob')
class ConsoleJob(unohelper.Base, XJob):

    def __init__(self, context):
        self.context = context

    def execute(self, arguments):
        args = dict((nv.Name, nv.Value) for nv in arguments)

        cwd = os.getcwd()
        try:
            inp = args['inp']
            outstream = args['outstream']

            outfile = FileFromStream(outstream)

            import sys
            orig = sys.stdout, sys.stderr
            sys.stdout = sys.stderr = outfile
            try:
                console = Console(inp, outfile)
                try:
                    console.interact('LibreOffice Python Console (pid: %s)' %
                                     os.getpid())
                    return 0
                except SystemExit, e:
                    return e.code
            finally:
                sys.stdout, sys.stderr = orig
        finally:
            os.chdir(cwd)


from code import InteractiveConsole
class Console(InteractiveConsole):

    def __init__(self, inp, outfile):
        InteractiveConsole.__init__(self)
        self.inp = inp
        self.outfile = outfile

    def write(self, data):
        self.outfile.write(data)
        self.outfile.flush()

    def raw_input(self, prompt=''):
        import uno
        arg = uno.createUnoStruct('com.sun.star.beans.NamedValue')
        arg.Name = 'prompt'
        arg.Value = prompt
        args = arg,
        result = self.inp.execute(args)
        if result is None:
            raise EOFError()
        return result


class FileFromStream(object):
    ''' A file-like object based on XInputStream/XOuputStream/XSeekable

    :param stream: a stream object which implements
    com.sun.star.io.XInputStream, com.sun.star.io.XOutputStream or
    com.sun.star.io.XSeekable
    '''
    def __init__(self, stream, encoding='utf-8'):
        import uno
        self.stream = stream
        self.encoding = encoding

        if hasattr(stream, 'readBytes'):
            def read(size=None):
                if size is None:
                    data = ''
                    while True:
                        bytes = uno.ByteSequence('')
                        n_read, bytes = stream.readBytes(bytes, 4096)
                        if n_read == 0:
                            return data
                        data += bytes.value
                bytes = uno.ByteSequence('')
                n_read, bytes = stream.readBytes(bytes, size)
                return bytes.value
            self.read = read

        if hasattr(stream, 'seek'):
            self.tell = stream.getPosition

            def seek(offset, whence=0):
                if whence == 0:
                    pass
                elif whence == 1:
                    offset += stream.getPosition()
                elif whence == 2:
                    offset += stream.getLength()
                stream.seek(offset)
            self.seek = seek

        if hasattr(stream, 'writeBytes'):
            def write(s):
                if isinstance(s, unicode):
                    s = s.encode(self.encoding)
                stream.writeBytes(uno.ByteSequence(s))
            self.write = write

            def flush():
                stream.flush()
            self.flush = flush

    def close(self):
        if hasattr(self.stream, 'closeInput'):
            self.stream.closeInput()
        elif hasattr(self.stream, 'closeOutput'):
            self.stream.closeOutput()


'''
import os.path
from uno import systemPathToFileUrl
from unokit.ucb import open_url
from unokit.services import css

path = os.path.abspath('samples/sample-5017.hwp')
print path
url = systemPathToFileUrl(path)
print url
inp = open_url(url)
print inp

# 여기서 segfault
stg = css.embed.OLESimpleStorage(inp)
print stg
'''


'''
SegFault가 나는 stacktrace는 다음과 같다

StgDirEntry::StgDirEntry
    sot/source/sdstor/
StgEntry::Load
    sot/source/sdstor/
ToUpperUnicode
    sot/source/sdstor/stgelem.cxx
CharClass
    unotools/source/i18n/charclass.cxx
intl_createInstance
    unotools/source/i18n/instance.hxx

여기서 ::comphelper::getProcessServiceFactory로 얻은 XMultiServiceFactory가
null 값인 것 같다.

----

uno를 사용하는 프로그램들 (desktop app/unopkg, 각종 unittest 프로그램)은
처음 실행 시 다음과 같은 과정을 거치는 듯 하다.

1. ::cppu::defaultBootstrap_InitialComponentContext()을 호출, local context 생성
   - unorc 등을 검색, application.rdb, user.rdb 등에 접근

   - pyuno.so 의 getComponentContext()에서 수행: PYUNOLIBDIR 즉 pyuno.so가 있는
     디렉토리에서 pyuno.rc가 있으면 그것으로 초기화)
   - desktop app: appinit.cxx의 CreateApplicationServiceManager()에서 수행
   - unopkg: unopkg_misc.cxx의 bootstrapStandAlone()에서 수행.
     ucbhelper::ContentBroker도 함께 초기화한다.

2. 이렇게 생성한 local context로부터 ServiceManager를 얻어
   ::comphelper::setProcessServiceFactory()를 사용하여 프로세스 전역 service
   factory로 등록

   - uno.py와 pyuno.so는 이 작업을 하지 않는다.
   - desktop app: app.cxx의 ensureProcessServiceFactory()에서 수행
   - unopkg: unopkg_misc.cxx의 bootstrapStandAlone()에서 함께 수행.


* desktop app: desktop/source/app/
* unopkg: desktop/source/pkgchk/unopkg/

'''

logger.info('%s: end of file', __name__)
