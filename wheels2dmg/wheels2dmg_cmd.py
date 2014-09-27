""" wheels2dmg command module
"""
from __future__ import division, print_function

import sys
import os
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from .piputils import make_pip_parser, recon_pip_args
from .pkgbuilders import (insert_template_path, PkgWriter)

# Defaults
PYTHON_VERSION='2.7.8'


def get_parser():
    parser = ArgumentParser(
        description=
"Make dmg installer for Python.org Python from Python wheels",
        epilog=
"""Make DMG installer from wheels

* Collect ``get-pip.py`` installer script;
* Collect needed wheels using "pip wheel" command, including pip, setuptools;
* Write directory to DMG containing wheel packages;
* Write "postinstall" script to install pip, then install wheels;
* Fold "postinstall" script into ".pkg" double click installer;
* Package wheel directory and pkg installer into DMG file.

There must be at least one REQ_SPEC or REQUIREMENT.
""",
        formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('pkg_name', type=str, help='root name of installer')
    parser.add_argument('pkg_version', type=str, help='version of installer')
    parser.add_argument('--python-version',  type=str, default=PYTHON_VERSION,
                        help='Python version in major.minor.extr format, '
                        'e.g "3.4.1"')
    parser.add_argument('--get-pip-url', type=str,
                        help='URL or local path to "get-pip.py" (default is '
                        'to download from canonical URL')
    parser.add_argument('--dmg-build-dir', type=str,
                        help='Path to write dmg contents to (default is to '
                        'use a temporary directory)')
    parser.add_argument('--scratch-dir', type=str,
                        help='Path to write scratch files to '
                        'default is to use a temporary directory)')
    parser.add_argument('--dmg-out-dir', type=str, default=os.getcwd(),
                        help='Directory to which we write dmg disk image '
                        '(default is current directory)')
    parser.add_argument('--template-dir', type=str,
                        help='Alternative directory containing jinja '
                        'templates for installer files')
    parser.add_argument('--pkg-id-root', type=str,
                        help='Package id root for installing package receipt '
                        '(default is "com.github.MacPython")')
    parser.add_argument('--delocate-wheels', action='store_true',
                        help='Automatically delocate libraries in wheels')
    return make_pip_parser(parser)


def main():
    # parse the command line
    parser = get_parser()
    args = parser.parse_args()
    # Split pip command line options into requirements and other parameters
    req_params, fetch_params = recon_pip_args(args)
    # We need at least one requirement
    if len(req_params) == 0:
        parser.print_help()
        sys.exit(12)
    if not args.template_dir is None:
        insert_template_path(args.template_dir)
    pkg_writer = PkgWriter(args.pkg_name,
                           args.pkg_version,
                           args.python_version,
                           req_params + fetch_params,
                           args.get_pip_url,
                           args.dmg_build_dir,
                           args.scratch_dir,
                           pkg_id_root = args.pkg_id_root,
                           delocate_wheels = args.delocate_wheels)
    pkg_writer.write_dmg(args.dmg_out_dir)
