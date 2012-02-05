# -*- coding: utf-8 -*-
import sys
from . import filestructure
from OleFileIO_PL import OleFileIO
from .filestructure import OleStorage

class Context(object):
    def __init__(self, sys):
        self.sys = sys

    @property
    def prog(self):
        return self.sys.argv[0]

    @property
    def progname(self):
        import os.path
        return os.path.split(self.prog)[-1]

    @property
    def args_options(self):
        options = dict()
        args = list()
        for arg in self.sys.argv[1:]:
            if arg.startswith('--'):
                option = arg[2:].split('=', 1)
                if len(option) == 1:
                    k = option[0]
                    v = '1'
                else:
                    k, v = option
                options[k] = v
            else:
                args.append(arg)
        return args, options

    @property
    def args(self):
        return self.args_options[0]

    @property
    def options(self):
        return self.args_options[1]

    def shift(self):
        return self.sys.argv.pop(0)


class ProcContext(Context):

    @property
    def filename(self):
        if len(self.args) == 0:
            raise 'Filename is required'
        return self.args[0]

    @property
    def olefile(self):
        return OleFileIO(self.filename)

    @property
    def olestorage(self):
        return OleStorage(self.olefile)

    @property
    def hwp5file_fs(self):
        return filestructure.Hwp5File(self.olestorage)

    @property
    def hwp5file_rec(self):
        from . import recordstream
        return recordstream.Hwp5File(self.olestorage)

    @property
    def hwp5file_bin(self):
        from . import binmodel
        return binmodel.Hwp5File(self.olestorage)

    @property
    def hwp5file_xml(self):
        from . import xmlmodel
        return xmlmodel.Hwp5File(self.olestorage)

    hwp5file = hwp5file_xml

    @property
    def storage(self):
        layer = self.options.get('layer')
        if layer == 'ole':
            return self.olestorage
        elif layer == 'fs':
            return self.hwp5file_fs
        elif layer == 'rec':
            return self.hwp5file_rec
        elif layer == 'bin':
            return self.hwp5file_bin
        elif layer == 'xml':
            return self.hwp5file_xml
        return self.hwp5file

    @property
    def stream(self):
        from .storage import open_storage_item
        return open_storage_item(self.storage, self.args[1])

    @property
    def outdir_or_operand_root(self):
        outdir = self.options.get('outdir', None)
        if outdir:
            return outdir

        import os.path
        outdir, ext = os.path.splitext(os.path.basename(self.filename))
        return outdir


context = ProcContext(sys)

def main():
    if context.progname == 'hwp5proc':
        context.shift()

    if context.progname == 'version':
        program = version
    elif context.progname == 'unpack':
        program = unpack
    elif context.progname == 'ls':
        program = ls
    elif context.progname == 'cat':
        program = cat
    else:
        print 'unknown command: ', context.progname
        help()
        return

    program()


def help():
    print 'help'


def version():
    filename = context.args[0]

    olefile = OleFileIO(filename)
    olestg = OleStorage(olefile)
    hwp5file = filestructure.Hwp5File(olestg)

    h = hwp5file.header
    print h.signature.replace('\x00', ''), '%d.%d.%d.%d'%h.version


def unpack():
    outdir = context.outdir_or_operand_root

    import os, os.path
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    filestructure.unpack(context.storage, outdir)


def ls():
    from .storage import Storage
    def printstorage(stg, basepath=''):
        names = list(stg)
        names.sort()
        for name in names:
            path = basepath + name
            item = stg[name]
            if isinstance(item, Storage):
                printstorage(item, path+'/')
            if hasattr(item, 'read'):
                print path

    printstorage(context.storage)


def cat():
    f = context.stream
    try:
        if hasattr(f, 'read'):
            while True:
                data = f.read(4096)
                if data:
                    sys.stdout.write(data)
                else:
                    return
    finally:
        if hasattr(f, 'close'):
            f.close()
