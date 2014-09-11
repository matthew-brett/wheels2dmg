""" Testing pkgbuilders module
"""

from os.path import basename, abspath, expanduser, relpath, join as pjoin

from ..pkgbuilders import get_get_pip, write_requires, write_post

from ..tmpdirs import TemporaryDirectory

from nose.tools import (assert_true, assert_false, assert_raises,
                        assert_equal, assert_not_equal)


def assert_file_equal(file1, file2):
    with open(file1, 'rb') as fobj:
        contents1 = fobj.read()
    with open(file2, 'rb') as fobj:
        contents2 = fobj.read()
    assert_equal(contents1, contents2)


def assert_file_equal_string(fname, text):
    with open(fname, 'rt') as fobj:
        contents = fobj.read()
    assert_equal(contents, text)


def test_get_get_pip():
    # Test get_get_pip function
    with TemporaryDirectory() as tmpdir:
        gpp = get_get_pip(__file__, tmpdir)
        assert_equal(basename(gpp), 'get-pip.py')
        assert_file_equal(__file__, gpp)
    with TemporaryDirectory() as tmpdir:
        url = 'file://' + abspath(__file__)
        gpp = get_get_pip(url, tmpdir)
        assert_file_equal(__file__, gpp)
    # Check get_pip file can contain tilde
    home = expanduser('~')
    me_homed = pjoin('~', relpath(__file__, home))
    with TemporaryDirectory() as tmpdir:
        gpp = get_get_pip(me_homed, tmpdir)
        assert_file_equal(__file__, gpp)


def test_write_require():
    # Test write_require function
    with TemporaryDirectory() as tmpdir:
        exp_out = pjoin(tmpdir, 'test-1.txt')
        assert_equal(write_requires(['foo', 'bar'], 'test-1', tmpdir), exp_out)
        assert_file_equal_string(exp_out,
"""# Requirements file for test-1
#
# Use with:
#
#     pip install -r test-1.txt

foo
bar
""")
        exp_out = pjoin(tmpdir, 'another-2.0.txt')
        assert_equal(
            write_requires(['baf==1.0', 'whack<2.1'], 'another-2.0', tmpdir),
            exp_out)
        assert_file_equal_string(exp_out,
"""# Requirements file for another-2.0
#
# Use with:
#
#     pip install -r another-2.0.txt

baf==1.0
whack<2.1
""")


def test_write_post():
    # Test write_post function
    with TemporaryDirectory() as tmpdir:
        exp_out = pjoin(tmpdir, 'postinstall')
        assert_equal(write_post('3.4', tmpdir, 'test-1', 'pkgs'), exp_out)
        assert_file_equal_string(exp_out,
"""#!/usr/bin/env python
# Install into Python.org python
# vim ft:python
import sys
import os
from os.path import exists, dirname
from subprocess import check_call

# Find disk image files
package_path = os.environ.get('PACKAGE_PATH')
if package_path is None:
    sys.exit(10)
package_dir = dirname(package_path)
wheelhouse = package_dir + '/pkgs'
# Find Python.org Python
python_bin = '/Library/Frameworks/Python.framework/Versions/3.4/bin'
python_path = python_bin +  '/python3.4'
if not exists(python_path):
    sys.exit(20)
# Install pip
check_call([python_path,
            wheelhouse + '/get-pip.py',
            '-f', wheelhouse,
            '--no-index'])
# Find pip
expected_pip = python_bin + '/pip3.4'
if not exists(expected_pip):
    sys.exit(30)
check_call([expected_pip, 'install',
            '--no-index', '--upgrade',
            '--find-links', wheelhouse,
            '-r', wheelhouse + '/test-1.txt'])""")
