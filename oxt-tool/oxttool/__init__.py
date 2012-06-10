# -*- coding: utf-8 -*-

from contextlib import contextmanager

def get_remote_context(uno_link, max_tries=3):
    import uno
    import time
    while True:
        max_tries -= 1
        try:
            localcontext = uno.getComponentContext()
            localsm = localcontext.ServiceManager
            resolver_name = 'com.sun.star.bridge.UnoUrlResolver'
            resolver = localsm.createInstanceWithContext(resolver_name, localcontext)

            return resolver.resolve('uno:'+uno_link+'StarOffice.ComponentContext')
        except Exception, e:
            name = type(e).__name__
            noconnect = 'com.sun.star.connection.NoConnectException'
            if name == noconnect:
                if max_tries <= 0:
                    raise
                print name, '- retrying'
                time.sleep(2)
                continue
            raise


@contextmanager
def soffice(**kwargs):
    args = ['soffice', '--nologo', '--norestore', '--nodefault',
            '--nofirstwizard']

    if 'pipe' in kwargs:
        pipe = kwargs['pipe']
    else:
        pipe = 'pyhwp'
    uno_link = 'pipe,name={0};urp;'.format(pipe)
    args.append('--accept={0}'.format(uno_link))
    
    if kwargs.get('headless', True):
        args.extend(['--headless', '--invisible'])

    import subprocess
    p = subprocess.Popen(args)
    yield get_remote_context(uno_link)
    p.terminate()


def runtest(context, working_directory):
    sm = context.ServiceManager

    testjob = sm.createInstanceWithContext('pyhwp.TestJob', context)
    testjob.trigger(working_directory)


def test():
    import sys
    with soffice() as context:
        runtest(context, working_directory=sys.argv[1])


def console():
    import uno
    with soffice(headless=False) as context:
        local=dict(uno=uno, context=context)
        __import__('code').interact(banner='oxt-console', local=local)
