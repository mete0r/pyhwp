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
