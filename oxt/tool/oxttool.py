# -*- coding: utf-8 -*-

import unokit.services
import unokit.remote
import unokit.contexts

def runtest(working_directory):
    hwp5 = unokit.services.NamespaceNode('hwp5')

    testjob = hwp5.TestJob()
    testjob.trigger(working_directory)


def test():
    import sys

    with unokit.remote.new_remote_context():
        runtest(sys.argv[1])


def console():
    import uno
    with unokit.remote.new_remote_context() as context:
        desktop = unokit.services.css.frame.Desktop()
        def new_textdoc():
            return desktop.loadComponentFromURL('private:factory/swriter',
                                                '_blank', 0, tuple())
        from unokit.util import dump, dumpdir
        local = dict(uno=uno, context=context,
                     css=unokit.services.css, dump=dump, dumpdir=dumpdir,
                     desktop=desktop, new_textdoc=new_textdoc)
        __import__('code').interact(banner='oxt-console', local=local)
