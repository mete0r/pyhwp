import logging
import sys
import os

logfmt = logging.Formatter((' backend %5d ' % os.getpid())
                           +'%(message)s')
logchn = logging.StreamHandler()
logchn.setFormatter(logfmt)
logger = logging.getLogger('backend')
logger.addHandler(logchn)
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
        import cPickle
        args = dict((nv.Name, nv.Value) for nv in arguments)

        logger.info('current dir: %s', os.getcwd())
        logger.info('sys.path:')
        for x in sys.path:
            logger.info('- %s', x)

        outstream = args.get('outputstream')
        outstream = FileFromStream(outstream)

        extra_path = args.get('extra_path')
        if extra_path:
            logger.info('extra_path: %s', ' '.join(extra_path))
            sys.path.extend(extra_path)

        logconf = args.get('logging')
        if logconf:
            levels = dict(debug=logging.DEBUG,
                          info=logging.INFO,
                          warning=logging.WARNING,
                          error=logging.ERROR,
                          critical=logging.CRITICAL)
            logconf = dict((nv.Name, nv.Value) for nv in logconf)
            for name, conf in logconf.items():
                _logger = logging.getLogger(name)
                conf = dict((nv.Name, nv.Value) for nv in conf)
                level = conf.get('level')
                if level:
                    level = levels.get(level.lower(), logging.INFO)
                    _logger.setLevel(level)
                _logger.addHandler(logging.StreamHandler(outstream))

        from hwp5.storage.ole import uno_olesimplestorage
        uno_olesimplestorage.enable(self.context)

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


class FileFromStream(object):
    ''' A file-like object based on XInputStream/XOuputStream/XSeekable

    :param stream: a stream object which implements
    com.sun.star.io.XInputStream, com.sun.star.io.XOutputStream or
    com.sun.star.io.XSeekable
    '''
    def __init__(self, stream):
        import uno
        self.stream = stream

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
