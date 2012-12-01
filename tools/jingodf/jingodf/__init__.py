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

    def validate(self, rngfile, xmlfile):
        return self('-i', rngfile, xmlfile)


class XmlLint(object):
    def __init__(self, executable='xmllint'):
        ''' External xmllint executable

        :param executable: path to xmllint executable. Default: xmllint
        '''
        self.executable = executable

    def __call__(self, *args, **kwargs):
        args = list(args)

        import subprocess
        if isinstance(self.executable, basestring):
            args[0:0] = [self.executable]
        else:
            args[0:0] = self.executable

        p = subprocess.Popen(args, stderr=subprocess.PIPE, **kwargs)
        import re
        regex = re.compile('(.*)Relax-NG validity error : (.*)')
        for line in p.stderr:
            if line.endswith(' validates\n'):
                continue
            elif line.endswith(' fails to validate\n'):
                continue
            line = line.strip()
            m = regex.match(line)
            if m:
                location = m.group(1)
                msg = m.group(2)
                if location:
                    filename, line_no, element, _ = line.split(':', 3)
                    element = element.strip()
                level = 'error'
                msg = msg.strip()
                yield dict(filename=filename,
                           line=line_no, column=element,
                           level=level, msg=msg)
            else:
                print '*', line
        p.wait()
        yield p.returncode

    def validate(self, rngfile, xmlfile):
        return self('--noout', '--relaxng', rngfile, xmlfile)


class ODFValidator(object):
    def __init__(self, engine):
        self.engine = engine

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
        return self.engine.validate(rng_file, xmlfile)

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
        return self.engine.validate(rng_file, xmlfile)

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

from opster import command

@command()
def validate(odf_file,
             odf_version=('', '1.2', 'OpenDocument specification version'),
             engine=('', 'jing', 'Relax-NG Validator engine')):
    ''' Validate an ODF file against the OpenDocument Relax-NG Schema. '''

    engines = dict(jing=Jing, xmllint=XmlLint)
    engine_class = engines.get(engine, Jing)
    engine = engine_class()
    odf_validator = ODFValidator(engine)
    results = odf_validator.validate_odf(odf_version, odf_file)

    def print_result(result):
        if isinstance(result, dict):
            print '%(filename)s:%(line)s:%(column)s: %(level)s: %(msg)s'%result

    for result in results:
        print_result(result)

def main():
    validate.command()
