import os

from setuptools import setup, find_packages


def get_version(filename):
    import ast
    version = None
    with open(filename) as f:
        for line in f:
            if line.startswith('__version__'):
                version = ast.parse(line).body[0].value.s
                break
        else:
            raise ValueError('No version found in %r.' % filename)
    if version is None:
        raise ValueError(filename)
    return version


version = get_version(filename='src/conf_tools/__init__.py')

description = """"""


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


long_description = read('README.md')

setup(name='ConfTools',
      author="Andrea Censi",
      author_email="censi@mit.edu",
      url='http://github.com/AndreaCensi/conf_tools/',

      description=description,
      long_description=long_description,
      keywords="configuration",
      license="LGPL",

      classifiers=[
          'Development Status :: 4 - Beta',
      ],

      version=version,
      download_url='http://github.com/AndreaCensi/conf_tools/tarball/%s' % version,

      package_dir={'': 'src'},
      packages=find_packages('src'),
      install_requires=[
          'PyYAML',
          'PyContracts>=1.2,<2',
      ],
      tests_require=['nose'],
      entry_points={},
      )
