#! -*- coding: utf-8 -*-

class Jing(object):

    def __init__(self, executable='jing'):
        ''' External Jing executable

        :param executable: path to jing executable. Default: jing
        '''
        self.executable = executable

    def __call__(self, *args, **kwargs):
        args = list(args)

        import subprocess
        if isinstance(self.executable, basestring):
            args[0:0] = [self.executable]
        else:
            args[0:0] = self.executable

        p = subprocess.Popen(args, stdout=subprocess.PIPE, **kwargs)
        for line in p.stdout:
            filename, line, column, level, msg = line.split(':', 4)
            level = level.strip()
            msg = msg.strip()
            yield dict(filename=filename,
                       line=line, column=column,
                       level=level, msg=msg)
        p.wait()
        yield p.returncode

    def validate(self, options, rngfile, xmlfile):
        args = options + [rngfile, xmlfile]
        return self(*args)

class JingODF(Jing):
    def validate_manifest_xml(self, version, xmlfile):
        rng_files = {
            '1.0': 'OpenDocument-manifest-schema-v1.0-os.rng',
            '1.1': 'OpenDocument-manifest-schema-v1.1.rng',
            '1.2': 'OpenDocument-v1.2-os-manifest-schema.rng',
        }

        import pkg_resources
        rng_filename = rng_files[version]
        rng_file = pkg_resources.resource_filename('jingodf',
                                                   'schema/'+rng_filename)
        return self.validate(['-i'], rng_file, xmlfile)

    def validate_opendocument_xml(self, version, xmlfile):
        rng_files = {
            '1.0': 'OpenDocument-schema-v1.0-os.rng',
            '1.1': 'OpenDocument-schema-v1.1.rng',
            '1.2': 'OpenDocument-v1.2-os-schema.rng',
        }
        import pkg_resources
        rng_filename = rng_files[version]
        rng_file = pkg_resources.resource_filename('jingodf',
                                                   'schema/'+rng_filename)
        return self.validate(['-i'], rng_file, xmlfile)

    def validate_odf(self, version, odffile):

        import os.path
        from zipfile import ZipFile
        zipfile = ZipFile(odffile, 'r')
        try:
            import tempfile
            tmpdir = tempfile.mkdtemp()
            try:
                path = 'META-INF/manifest.xml'
                zipfile.extract(path, tmpdir)
                results = self.validate_manifest_xml(version,
                                                     os.path.join(tmpdir, path))
                for result in results:
                    if isinstance(result, dict):
                        result['filename'] = path
                    yield result

                path = 'styles.xml'
                zipfile.extract(path, tmpdir)
                results = self.validate_opendocument_xml(version,
                                                         os.path.join(tmpdir, path))
                for result in results:
                    if isinstance(result, dict):
                        result['filename'] = path
                    yield result

                path = 'content.xml'
                zipfile.extract(path, tmpdir)
                results = self.validate_opendocument_xml(version,
                                                         os.path.join(tmpdir, path))
                for result in results:
                    if isinstance(result, dict):
                        result['filename'] = path
                    yield result

            finally:
                import shutil
                shutil.rmtree(tmpdir)
        finally:
            zipfile.close()

def main():
    jingodf = JingODF()
    import sys
    results = jingodf.validate_odf('1.2', sys.argv[1])

    def print_result(result):
        if isinstance(result, dict):
            print '%(filename)s:%(line)s:%(column)s: %(level)s: %(msg)s'%result

    for result in results:
        print_result(result)
