#!/usr/bin/python
# -*- coding: utf-8 -*-

def with_soffice_headless(f):
    uno_url = 'pipe,name=pyhwp;urp;'
    args = ['soffice', '--nologo', '--headless', '--invisible','--norestore',
            '--nodefault', '--nolockcheck', '--nofirstwizard',
            '--accept=%s' % uno_url]
    import subprocess
    p = subprocess.Popen(args)
    try:
        # waiting for soffice to be ready (guessed)
        import time
        trycount = 0
        while trycount < 3:
            trycount += 1
            try:
                f(uno_url)
                break
            except Exception, e:
                name = type(e).__name__
                print name
                noconnect = 'com.sun.star.connection.NoConnectException'
                if name == noconnect:
                    time.sleep(2)
                    continue
                raise
    finally:
        p.terminate()

def runtest(uno_url):
    import uno
    localcontext = uno.getComponentContext()
    localsm = localcontext.ServiceManager
    resolver_name = 'com.sun.star.bridge.UnoUrlResolver'
    resolver = localsm.createInstanceWithContext(resolver_name, localcontext)

    context = resolver.resolve('uno:'+uno_url+'StarOffice.ComponentContext')
    sm = context.ServiceManager

    testjob = sm.createInstanceWithContext('pyhwp.TestJob', context)
    testjob.trigger('${buildout:parts-directory}/test')

def main():
    with_soffice_headless(runtest)

if __name__ == '__main__':
    main()
