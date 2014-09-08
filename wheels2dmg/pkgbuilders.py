""" Utilities for building pkg installer and disk image from wheels
"""
from __future__ import division, print_function

import os
from os.path import exists, join as pjoin, abspath
import shutil
from subprocess import check_call
try:
    from urllib2 import urlopen # Python 2
    from urlparse import urlparse
except ImportError:
    from urllib.request import urlopen # Python 3
    from urllib.parse import urlparse


from .tmpdirs import TemporaryDirectory

# Installed location of Python.org Python
PY_ORG_BASE='/Library/Frameworks/Python.framework/Versions/'


def get_pip_params(args):
    """ Get known pip command-line parameters from argument object

    Parameters
    ----------
    args : object
        Arguments object returned from command line processing by argparse

    Returns
    -------
    params : list
        Command line parameters for pip
    """
    params = '--no-index' if args.no_index else []
    for link in args.find_links:
        params.append('--find-links=' + link)
    return params


def get_get_pip(get_pip_url, out_dir):
    """ Get ``get-pip.py`` from file or URL `get_pip_url`, write to `out_dir`

    Parameters
    ----------
    get_pip_url : str
        File path or URL pointing to ``get-pip.py`` installer.
    out_dir : str
        Directory to which to write copy of ``get-pip.py``

    Returns
    -------
    get_pip_path : str
        Path to written ``get-pip.py``
    """
    parsed = urlparse(get_pip_url)
    get_pip_path = pjoin(out_dir, 'get-pip.py')
    if parsed.scheme == '': # File path
        shutil.copyfile(get_pip_url, get_pip_path)
    else: # URL
        url_obj = urlopen(get_pip_url)
        with open(get_pip_path, 'wt') as fobj:
            fobj.write(url_obj.read())
    return get_pip_path


def get_python_path(version):
    python_path = '{0}/{1}/bin/python{1}'.format(PY_ORG_BASE, version, version)
    if not exists(python_path):
        raise RuntimeError('Need to install Python.org python version ' +
                           version)
    return python_path


def upgrade_pip(get_pip_path, py_version, pip_params):
    python_path = get_python_path(py_version)
    # Upgrade pip
    check_call([python_path, get_pip_path] + pip_params)
    pip_exe = '{0}/{1}/bin/pip{1}'.format(PY_ORG_BASE, py_version, py_version)
    if not exists(pip_exe):
        raise RuntimeError('Expected to find pip at {0}, but not so'.format(
            pip_exe))
    # Install wheel
    check_call([pip_exe, 'install', '--upgrade'] + pip_params + ['wheel'])
    return pip_exe


def get_wheels(pip_exe, pip_params, requirements, out_dir):
    # Get wheels for pip and setuptools
    pip_wheel = [pip_exe, 'wheel', '-w', out_dir] + pip_params
    check_call(pip_wheel + ['pip', 'setuptools'])
    check_call(pip_wheel + list(requirements))


def write_post(py_version, requirements, pkg_sdir, scripts_dir):
    to_install = ', '.join(['"{0}"'.format(r) for r in requirements])
    fname = pjoin(scripts_dir, 'postinstall')
    with open(fname, 'wt') as fobj:
        fobj.write(
r"""#!/usr/bin/env python
# Install into Python.org python
import sys
import os
from os.path import exists, dirname
from subprocess import check_call

# Find disk image files
package_path = os.environ.get('PACKAGE_PATH')
if package_path is None:
    sys.exit(10)
package_dir = dirname(package_path)
wheelhouse = package_dir + '/{pkg_sdir}'
# Find Python.org Python
python_bin = '{py_org_base}/{py_version}/bin'
python_path = python_bin +  '/python{py_version}'
if not exists(python_path):
    sys.exit(20)
# Install pip
check_call([python_path, wheelhouse + '/get-pip.py', '-f', wheelhouse,
            '--no-setuptools'])
# Find pip
expected_pip = python_bin + '/pip{py_version}'
if not exists(expected_pip):
    sys.exit(30)
pip_cmd = [expected_pip, 'install', '--no-index', '--upgrade',
           '--find-links', wheelhouse]
check_call(pip_cmd + ['setuptools'])
check_call(pip_cmd + [{to_install}])
""".format(py_org_base = PY_ORG_BASE,
           py_version = py_version,
           to_install = to_install,
           pkg_sdir = pkg_sdir,
          ))
    check_call(['chmod', 'a+x', fname])


def write_pkg(py_version, requirements, out_dir, pkg_sdir, identifier, version):
    out_dir = abspath(out_dir)
    with TemporaryDirectory() as scripts:
        write_post(py_version, requirements, pkg_sdir, scripts)
        pkg_fname = pjoin(out_dir, '{0}-{1}.pkg'.format(identifier, version))
        check_call(['pkgbuild',
                    '--nopayload',
                    '--scripts', scripts,
                    '--identifier', identifier, '--version', version,
                    pkg_fname])
    return pkg_fname


def write_dmg(dmg_in_dir, dmg_out_dir, identifier, py_version, pkg_version):
    if not exists(dmg_out_dir):
        os.mkdir(dmg_out_dir)
    dmg_name = '{0}-py{1}-{2}'.format(
        identifier,
        py_version.replace('.', ''),
        pkg_version)
    dmg_fname = pjoin(dmg_out_dir, dmg_name + '.dmg')
    check_call(['hdiutil', 'create', '-srcfolder', dmg_in_dir,
                '-volname', dmg_name, dmg_fname])
