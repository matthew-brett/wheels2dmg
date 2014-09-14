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
from tempfile import mkdtemp
import re

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from .piputils import (make_pip_parser, recon_pip_args, get_requirements,
                       get_req_strings)

JINJA_LOADER = FileSystemLoader(pjoin(dirname(__file__), 'templates'))
JINJA_ENV = Environment(loader=JINJA_LOADER, trim_blocks=True)

# Installed location of Python.org Python
PY_ORG_BASE='/Library/Frameworks/Python.framework/Versions'

# Canonical get-pip.py URL
GET_PIP_URL = 'https://bootstrap.pypa.io/get-pip.py'
PKG_ID_ROOT = 'com.github.MacPython'

# Full Python version checker
PY_VERSION_RE = re.compile(r'\d\.\d\.\d+')


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


def get_python_path(pyv_m_m):
    """ Return path to Python.org python or raise error

    Parameters
    ----------
    pyv_m_m : str
        Python version in major.minor format (e.g. "2.7")

    Returns
    -------
    python_path : str
        Path to Python.org Python executable
    """
    python_path = '{0}/{1}/bin/python{1}'.format(PY_ORG_BASE, pyv_m_m, pyv_m_m)
    if not exists(python_path):
        raise RuntimeError('Need to install Python.org python version ' +
                           pyv_m_m)
    return python_path


def upgrade_pip(get_pip_path, pyv_m_m, pip_params):
    """ Upgrade pip with ``git-pip.py`` script, install ``wheel``

    Installs pip for Python.org Python if not present. Upgrades if necessary.
    Install ``wheel`` if necessary.

    Parameters
    ----------
    get_pip_path : str
        Path to local copy of ``get-pip.py``
    pyv_m_m : str
        Python version in major.minor format (e.g. "2.7")
    pip_params : sequence
        Parameters to pass to pip when installing

    Returns
    -------
    pip_exe : str
        Path to ``pip`` executable
    """
    python_path = get_python_path(pyv_m_m)
    # Upgrade pip
    check_call([python_path, get_pip_path] + pip_params)
    pip_exe = '{0}/{1}/bin/pip{1}'.format(PY_ORG_BASE, pyv_m_m, pyv_m_m)
    if not exists(pip_exe):
        raise RuntimeError('Expected to find pip at {0}, but not so'.format(
            pip_exe))
    # Install wheel
    check_call([pip_exe, 'install', '--upgrade'] + pip_params + ['wheel'])
    return pip_exe


def _safe_mkdirs(path):
    if not exists(path):
        os.makedirs(path)
    return path


class PkgWriter(object):

    py_org_base = PY_ORG_BASE
    pip_parser = make_pip_parser()
    chatty_names = ('welcome.html', 'readme.html', 'license.html')

    def __init__(self,
                 pkg_name,
                 pkg_version,
                 full_py_version,
                 pip_params,
                 get_pip_url = None,
                 dmg_build_dir = None,
                 scratch_dir = None,
                 pkg_id_root = None,
                 wheel_sdir = 'wheels',
                 wheel_component_name = 'wheel-installer'
                ):
        self.do_init()
        self.pkg_name = pkg_name
        self.pkg_version = pkg_version
        if not PY_VERSION_RE.match(full_py_version):
            raise ValueError('Need full Python version of form '
                             'major.minor.extra - e.g. "3.4.1"')
        self.full_py_version = full_py_version
        self.pip_params = pip_params
        self.get_pip_url = GET_PIP_URL if get_pip_url is None else get_pip_url
        self.dmg_build_dir = self._working_dir(dmg_build_dir)
        self.scratch_dir = self._working_dir(scratch_dir)
        self.pkg_id_root = PKG_ID_ROOT if pkg_id_root is None else pkg_id_root
        self.wheel_sdir = wheel_sdir
        self.wheel_component_name = wheel_component_name

    def do_init(self):
        self._to_delete = []

    def _working_dir(self, work_dir):
        """ Make working directory `work_dir`, return absolute path

        Parameters
        ----------
        work_dir : None or str
            If str, directory to create if it doesn't exist. If None, make a
            temporary directory and return that, noting that we have to delete
            when we've finished.

        Returns
        -------
        abs_work_dir : str
            Absolute path to working directory
        """
        if work_dir is None:
            work_dir  = mkdtemp()
            self._to_delete.append(work_dir)
        else:
            _safe_mkdirs(work_dir)
        return abspath(work_dir)

    def __del__(self):
        for pth in self._to_delete:
            shutil.rmtree(pth)

    # Versions of the python version string
    @property
    def pyv_m_m_e(self):
        """ Full version, e.g "3.4.1" """
        return self.full_py_version

    @property
    def pyv_m_m(self):
        """ Major.minor version, e.g "3.4" """
        return self.full_py_version[:3]

    @property
    def pyv_mm(self):
        """ Major,minor version with no dot e.g "34" """
        return self.full_py_version.replace('.', '')[:2]

    @property
    def pyv_m(self):
        """ Major version e.g "3" """
        return self.full_py_version[0]

    @property
    def pkg_name_version(self):
        return '{0}-{1}'.format(self.pkg_name, self.pkg_version)

    @property
    def pkg_name_pyv_version(self):
        return '{0}-py{1}-{2}'.format(
            self.pkg_name,
            self.pyv_mm,
            self.pkg_version)

    @property
    def wheel_build_dir(self):
        return pjoin(self.dmg_build_dir, self.wheel_sdir)

    @property
    def existing_chatty_names(self):
        return tuple(name for name in self.chatty_names
                     if not get_template(name) is None)

    def get_requirement_strings(self, extras=True, versions=True):
        """ Return list of requirement strings for requirements in `self`

        Parameters
        ----------
        extras : bool, optional
            If True, append extras specifications to requirement name
        versions : bool, optional
            If True, append version specifications to requirement name

        Returns
        -------
        req_strings : list
            list of string corresponding to the requirements `self`
        """
        args = self.pip_parser.parse_args(self.pip_params)
        req_set = get_requirements(args.req_specs, args.requirement)
        return get_req_strings(req_set, extras, versions)

    def get_wheels(self):
        """ Upgrade pip and get wheels for this install
        """
        wheelhouse = _safe_mkdirs(self.wheel_build_dir)
        # Get get-pip.py
        get_pip_path = get_get_pip(self.get_pip_url, wheelhouse)
        # Get pip arguments
        pip_args = self.pip_parser.parse_args(self.pip_params)
        req_params, fetch_params = recon_pip_args(pip_args)
        # Find or install pip, install wheel, for given Python.org Python
        pip_exe = upgrade_pip(get_pip_path, self.pyv_m_m, fetch_params)
        # Fetch the wheels we need
        check_call([pip_exe, 'wheel',
                    '-w', wheelhouse,
                    'pip', 'setuptools'] +
                   req_params + fetch_params)

    def write_requires(self):
        """ Write a pip requirements file with given requirements

        Returns
        -------
        requires_fname : str
            Filename of written requirements file
        """
        requires_fname = pjoin(_safe_mkdirs(self.wheel_build_dir),
                               self.pkg_name_version + '.txt')
        template = get_template('requirements.txt')
        with open(requires_fname, 'wt') as fobj:
            fobj.write(template.render(info = self))
        return requires_fname

    def write_wheelhouse(self):
        """ Write wheels, requirements into wheelhouse directory
        """
        self.get_wheels()
        self.write_requires()

    def write_post(self, out_dir):
        """ Write ``postinstall`` file

        Parameters
        ----------
        out_dir : str
            Directory to which to write file

        Returns
        -------
        post_fname : str
            Filename of written file
        """
        post_fname = pjoin(out_dir, 'postinstall')
        template = get_template('postinstall')
        with open(post_fname, 'wt') as fobj:
            fobj.write(template.render(info = self))
        check_call(['chmod', 'a+x', post_fname])
        return post_fname

    def write_webloc(self):
        """ Write webloc link to Python installer
        """
        template = get_template('first_install_python.webloc')
        froot = 'Install Python {0}.webloc'.format(self.pyv_m_m)
        webloc_fname = pjoin(self.dmg_build_dir, froot)
        with open(webloc_fname, 'wt') as fobj:
            fobj.write(template.render(info = self))
        check_call(['SetFile', '-a', 'E', webloc_fname])
        return webloc_fname

    def write_component_pkg(self):
        """ Write component package to install wheels

        Returns
        -------
        component_pkg_fname : str
            Filename of written compoent package
        """
        pkg_fname = pjoin(self.scratch_dir, self.wheel_component_name + '.pkg')
        identifier = '{0}.{1}'.format(self.pkg_id_root,
                                      self.pkg_name_pyv_version)
        scripts = pjoin(self.scratch_dir, 'scripts')
        _safe_mkdirs(scripts)
        self.write_post(scripts)
        check_call(['pkgbuild',
                    '--nopayload',
                    '--scripts', scripts,
                    '--identifier', identifier,
                    '--version', self.pkg_version,
                    pkg_fname])
        return pkg_fname

    def write_distribution(self):
        """ Write Distribution XML for product archive
        """
        template = get_template('Distribution')
        out_fname = pjoin(self.scratch_dir, 'Distribution')
        with open(out_fname, 'wt') as fobj:
            fobj.write(template.render(info = self))
        return out_fname

    def write_resources(self):
        """ Write contents of resources directory

        Returns
        -------
        resources : str
            Path of resources directory
        """
        resources = pjoin(self.scratch_dir, 'resources')
        en_resources = pjoin(resources, 'en.lproj')
        _safe_mkdirs(en_resources)
        for name in self.existing_chatty_names:
            out_fname = pjoin(en_resources, name)
            with open(out_fname, 'wt') as fobj:
                fobj.write(get_template(name).render(info = self))
        return resources

    def write_product_archive(self):
        """ Write product archive
        """
        distribution = self.write_distribution()
        self.write_component_pkg()
        resources = self.write_resources()
        product_fname = pjoin(self.dmg_build_dir,
                              self.pkg_name_pyv_version + '.pkg')
        check_call(['productbuild',
                    '--distribution', distribution,
                    '--resources', resources,
                    '--package-path', self.scratch_dir,
                    product_fname])

    def write_dmg(self, out_path):
        self.write_webloc()
        self.write_wheelhouse()
        self.write_product_archive()
        dmg_fname = pjoin(out_path, self.pkg_name_pyv_version + '.dmg')
        check_call(['hdiutil', 'create',
                    '-srcfolder', self.dmg_build_dir,
                    '-volname', self.pkg_name_pyv_version,
                    dmg_fname])
        return dmg_fname


def insert_template_path(path):
    """ Insert new path into jinja environment global

    Parameters
    ----------
    path : str
        Path to insert at beginning of template search order
    """
    JINJA_ENV.cache.clear()
    JINJA_LOADER.searchpath.insert(0, path)


def pop_template_path():
    """ Remove first path from jinja environment global

    Usually this is after using :func:`insert_templat_path`
    """
    JINJA_LOADER.searchpath.pop(0)
    JINJA_ENV.cache.clear()


def get_template(*args, **kwargs):
    """ Get template from jinja environment global

    Return None if template not found
    """
    try:
        return JINJA_ENV.get_template(*args, **kwargs)
    except TemplateNotFound:
        return None
