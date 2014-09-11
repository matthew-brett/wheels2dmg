""" Utilities for building pkg installer and disk image from wheels
"""
from __future__ import division, print_function

import os
from os.path import exists, join as pjoin, abspath, expanduser, dirname
import shutil
from subprocess import check_call
try:
    from urllib2 import urlopen # Python 2
    from urlparse import urlparse
except ImportError:
    from urllib.request import urlopen # Python 3
    from urllib.parse import urlparse

from jinja2 import Environment, FileSystemLoader

JINJA_LOADER = FileSystemLoader(pjoin(dirname(__file__), 'templates'))
JINJA_ENV = Environment(loader=JINJA_LOADER, trim_blocks=True)

from .tmpdirs import TemporaryDirectory

# Installed location of Python.org Python
PY_ORG_BASE='/Library/Frameworks/Python.framework/Versions'


def get_get_pip(get_pip_url, out_dir):
    """ Get ``get-pip.py`` from file or URL `get_pip_url`, write to `out_dir`

    Parameters
    ----------
    get_pip_url : str
        File path or URL pointing to ``get-pip.py`` installer.  File path can
        contain ``~`` for home directory.
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
        gpp_path = expanduser(get_pip_url)
        shutil.copyfile(gpp_path, get_pip_path)
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


def write_requires(requirement_strings,
                   pkg_name_version,
                   out_dir,
                   template_fname = 'requirements.txt'):
    """ Write a pip requirements file with given requirements

    Parameters
    ----------
    requirement_strings : sequence
        List of strings to be written as lines to requirement file
    pkg_name_version : str
        Package name combined with version string.  Will be used to form output
        file name
    out_dir : str
        Directory to which to write requirements file
    template_fname : str, optional
        Template filename, to be fetched from the global ``JINJA_LOADER``

    Returns
    -------
    out_fname : str
        Full path to written file
    """
    out_fname = pjoin(out_dir, pkg_name_version + '.txt')
    template = JINJA_ENV.get_template(template_fname)
    with open(out_fname, 'wt') as fobj:
        fobj.write(template.render(**locals()))
    return out_fname


def write_post(py_version,
               out_dir,
               pkg_name_version,
               pkg_sdir='packages',
               template_fname='postinstall'):
    """ Write ``postinstall`` file

    Parameters
    ----------
    py_version : str
        Python major.minor version e.g. ``3.4``
    pkg_name_version : str
        Package name plus version
    out_dir : str
        Directory to which to write file
    pkg_sdir  : str, optional
        Subdirector relative to ``$PACKAGE_PATH`` containing wheels
    template_fname : str, optional
        Name of jinja2 template
    """
    out_fname = pjoin(out_dir, 'postinstall')
    template = JINJA_ENV.get_template(template_fname)
    with open(out_fname, 'wt') as fobj:
        fobj.write(template.render(
            py_version = py_version,
            pkg_name_version = pkg_name_version,
            pkg_sdir = pkg_sdir,
            py_org_base = PY_ORG_BASE))
    check_call(['chmod', 'a+x', out_fname])
    return out_fname


def write_pkg(py_version, out_dir, pkg_sdir, identifier, version):
    out_dir = abspath(out_dir)
    pkg_name_version =  '{0}-{1}'.format(identifier, version)
    with TemporaryDirectory() as scripts:
        write_post(py_version, scripts, pkg_name_version, pkg_sdir)
        pkg_fname = pjoin(out_dir, pkg_name_version + '.pkg')
        check_call(['pkgbuild',
                    '--nopayload',
                    '--scripts', scripts,
                    '--identifier', identifier,
                    '--version', version,
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
