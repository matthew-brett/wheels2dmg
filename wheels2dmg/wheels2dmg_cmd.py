""" wheels2dmg command module
"""
from __future__ import division, print_function

import os
from os.path import abspath
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from .piputils import recon_pip_args
from .pkgbuilders import (get_get_pip, upgrade_pip, get_wheels, write_pkg,
                          write_dmg)
from .tmpdirs import (InGivenDirectory, InTemporaryDirectory)

# Defaults
PYTHON_VERSION='2.7'
# get-pip.py URL
GET_PIP_URL = 'https://bootstrap.pypa.io/get-pip.py'

# Subdirectory containing wheels and source packages
PKG_SDIR = 'packages'


def get_parser():
    parser = ArgumentParser(
        description=
"Make dmg installer for Python.org Python from Python wheels",
        epilog=
"""Make DMG installer from wheels

* Collect source packages for pip, setuptools
* Collect needed wheels using "pip wheel" command
* Write directory to DMG containing source and wheel packages
* Write "postinstall" script to install setuptools, pip, then install wheels
* Write "postinstall" script in ".pkg" double click installer
* Package result into DMG file.

There must be at least one REQ_SPEC or REQUIREMENT
""",
        formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('pkg_name', type=str, help='root name of installer')
    parser.add_argument('pkg_version', type=str, help='version of installer')
    parser.add_argument('req_specs', type=str, nargs='*', default=[],
                        help='pip requirement specifiers', metavar='REQ_SPEC')
    parser.add_argument('--python-version',  type=str, default=PYTHON_VERSION,
                        help='Python version in major.minor format, e.g "3.4"')
    parser.add_argument('--get-pip-url', type=str, default=GET_PIP_URL,
                        help='URL or local path to "get-pip.py" (default is '
                        'to download from canonical URL')
    parser.add_argument('--dmg-in-dir', type=str,
                        help='Path to write dmg contents to (default is to '
                        'use a temporary directory)')
    parser.add_argument('--dmg-out-dir', type=str, default=os.getcwd(),
                        help='Directory to which we write dmg disk image '
                        '(default is current directory)')
    # The rest of the arguments are destined for pip wheel / install calls
    parser.add_argument('--requirement', '-r', type=str, action='append',
                        help='pip requirement file(s)', metavar='REQUIREMENT')
    parser.add_argument('--index-url', '-i', type=str,
                        help='base URL of Python index (see pip install)')
    parser.add_argument('--extra-index-url', type=str, action='append',
                        help='extra URLs of Python indices (see pip)')
    parser.add_argument('--no-index',  action='store_true',
                        help='disable search of pip indices when fetching '
                        'packages to make installer')
    parser.add_argument('--find-links', '-f', type=str, action='append',
                        help='locations to find packages to make installer')
    return parser


def main():
    # parse the command line
    parser = get_parser()
    args = parser.parse_args()
    reqs = get_requirements(args.req_specs, args.requirement)
    if not reqs.has_requirements:
        parser.print_help()
        return 1
    pip_params = recon_pip_args(args)
    dmg_out_dir = abspath(args.dmg_out_dir)
    if args.dmg_in_dir is None:
        ctx_mgr = InTemporaryDirectory
    else:
        ctx_mgr = lambda : InGivenDirectory(args.dmg_in_dir)
    with ctx_mgr():
        os.mkdir(PKG_SDIR)
        get_pip_path = get_get_pip(args.get_pip_url, PKG_SDIR)
        pip_exe = upgrade_pip(get_pip_path, args.python_version, pip_params)
        get_wheels(pip_exe, pip_params, args.requirements, PKG_SDIR)
        write_pkg(args.python_version, args.requirements, 
                  '.', PKG_SDIR, args.pkg_name, args.pkg_version)
        write_dmg('.', dmg_out_dir,
                  args.pkg_name, args.python_version, args.pkg_version)
