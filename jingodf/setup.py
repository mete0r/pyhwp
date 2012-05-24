from setuptools import setup

setup(name='jingodf',
      version='0.0',
      license='GNU Affero GPL v3',
      author = 'mete0r',
      author_email = 'mete0r@sarangbang.or.kr',
      packages = ['jingodf'],
      package_data = dict(jingodf=['schema/*']),
      install_requires=['opster == 3.7'],
      entry_points = {
          'console_scripts': ['jingodf = jingodf:main']
      })
