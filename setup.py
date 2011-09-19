import os
from setuptools import setup, find_packages

version = "0.1"

description = """"""

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
    
long_description = read('README.rst')
    

setup(name='ConfTools',
      author="Andrea Censi",
      author_email="andrea@cds.caltech.edu",
      url='http://www.cds.caltech.edu/~andrea/',
      
      description=description,
      long_description=long_description,
      keywords="configuration",
      license="LGPL",
      
      classifiers=[
        'Development Status :: 4 - Beta',
      ],

	  version=version,
      download_url='http://github.com/AndreaCensi/conf_tools/tarball/%s' % version,
      
      package_dir={'':'src'},
      packages=find_packages('src'),
      install_requires=[ 'PyYAML', 'PyContracts'],
      tests_require=['nose'],
      entry_points={},
)

