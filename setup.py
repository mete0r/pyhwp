from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata as DistMeta
    DistMeta.classifiers = None
    DistMeta.download_url = None


import versioneer
versioneer.versionfile_source = 'pyhwp/hwp5/_version.py'
versioneer.versionfile_build = 'hwp5/_version.py'
versioneer.tag_prefix = ''
versioneer.parentdir_prefix = 'pyhwp-'


def read(filename):
    import os.path
    filename = os.path.join(os.path.dirname(__file__), filename)
    f = file(filename, 'r')
    try:
        return f.read()
    finally:
        f.close()

from setuptools import setup, find_packages
setup(
        name='pyhwp',
        version=versioneer.get_version(),
        cmdclass=versioneer.get_cmdclass(),
        license='GNU Affero GPL v3',
        description = 'hwp file format parser',
        long_description=read('README'),
        author = 'mete0r',
        author_email = 'mete0r@sarangbang.or.kr',
        url='http://github.com/mete0r/pyhwp',
        packages = find_packages('pyhwp'),
        package_dir={'': 'pyhwp'},
        package_data = dict(hwp5=['xsl/*.xsl', 'odf-relaxng/OpenDocument-v1.2-os-*.rng']),

        install_requires=['OleFileIO_PL >=0.20', 'simplejson', 'docopt >= 0.3',
                          'hypua2jamo'],
        extras_require=dict(test=['lxml']),

        entry_points = {
            'console_scripts': [
                'hwp5spec = hwp5.binspec:main',
                'hwp5proc = hwp5.proc:main',
                'hwp5odt = hwp5.hwp5odt:main',
                'hwp5txt = hwp5.hwp5txt:main',
                ]
            },

        test_suite='hwp5.tests.test_suite',

        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU Affero General Public License v3',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Text Processing',
            'Topic :: Text Processing :: Filters',
            ],
        )
