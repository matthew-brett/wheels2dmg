#!/usr/bin/env python
""" setup script for wheels2dmg package """
import sys
from os.path import join as pjoin

# For some commands, use setuptools.
if len(set(('develop', 'bdist_egg', 'bdist_rpm', 'bdist', 'bdist_dumb',
            'install_egg_info', 'egg_info', 'easy_install', 'bdist_wheel',
            'bdist_mpkg')).intersection(sys.argv)) > 0:
    import setuptools

from distutils.core import setup
import versioneer

versioneer.VCS = 'git'
versioneer.versionfile_source = pjoin('wheels2dmg', '_version.py')
versioneer.versionfile_build = pjoin('wheels2dmg', '_version.py')
versioneer.tag_prefix = ''
versioneer.parentdir_prefix = 'wheels2dmg-'

setuptools_args = {}
if 'setuptools' in sys.modules:
    setuptools_args['install_requires'] = ['jinja2',
                                           'wheel',
                                           'delocate>=0.6.0']

setup(name='wheels2dmg',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Make pkg installer and dmg from wheels',
      author='Matthew Brett',
      maintainer='Matthew Brett',
      author_email='matthew.brett@gmail.com',
      url='http://github.com/matthew-brett/wheels2dmg',
      packages=['wheels2dmg', 'wheels2dmg.tests'],
      package_data = {
          'wheels2dmg': [pjoin('templates', '*')],
          'wheels2dmg.tests': [pjoin('data', '*.txt')],
      },
      scripts = [pjoin('scripts', f) for f in (
          'wheels2dmg',
      )],
      license='BSD license',
      classifiers = ['Intended Audience :: Developers',
                     "Environment :: Console",
                     'License :: OSI Approved :: BSD License',
                     'Programming Language :: Python',
                     'Operating System :: MacOS :: MacOS X',
                     'Development Status :: 3 - Alpha',
                     'Topic :: Software Development :: Libraries :: '
                     'Python Modules',
                     'Topic :: Software Development :: Build Tools'],
      long_description = open('README.rst', 'rt').read(),
      **setuptools_args
     )
