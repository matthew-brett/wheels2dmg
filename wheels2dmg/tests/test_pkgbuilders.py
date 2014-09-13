""" Testing pkgbuilders module
"""

from os.path import (basename, dirname, abspath, expanduser, relpath,
                     join as pjoin)

from ..pkgbuilders import (get_get_pip, insert_template_path,
                           pop_template_path, get_template,
                           PkgWriter)

from ..tmpdirs import TemporaryDirectory

from nose.tools import (assert_true, assert_false, assert_raises,
                        assert_equal, assert_not_equal)

TEMPLATE_PATH = abspath(pjoin(dirname(__file__), '..', 'templates'))


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


def test_write_requires():
    # Test write_require function
    pkg_writer = PkgWriter('test', '1', '2.7', ['foo', 'bar'])
    exp_out = pjoin(pkg_writer.wheel_build_dir, 'test-1.txt')
    assert_equal(pkg_writer.write_requires(), exp_out)
    assert_file_equal_string(exp_out,
"""# Requirements file for test-1
#
# Use with:
#
#     pip install -r test-1.txt

foo
bar
""")
    pkg_writer = PkgWriter('another', '2.0', '3.4', ['baf==1.0', 'whack<2.1'])
    exp_out = pjoin(pkg_writer.wheel_build_dir, 'another-2.0.txt')
    assert_equal(pkg_writer.write_requires(), exp_out)
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
    pkg_writer = PkgWriter('test', '1', '3.4', ['foo', 'bar'],
                           wheel_sdir = 'pkgs')
    with TemporaryDirectory() as tmpdir:
        exp_out = pjoin(tmpdir, 'postinstall')
        assert_equal(pkg_writer.write_post(tmpdir), exp_out)
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
python_path = python_bin + '/python3.4'
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


def test_chatty_names():
    # Test existing chatty names property
    pkg_writer = PkgWriter('test', '1', '3.4', ['foo', 'bar'])
    assert_equal(pkg_writer.existing_chatty_names,
                 ('welcome.html', 'license.html'))


def test_template_override():
    # Check that we can override a template
    original_fname = pjoin(TEMPLATE_PATH, 'requirements.txt')
    with TemporaryDirectory() as tmpdir:
        new_fname = pjoin(tmpdir, 'requirements.txt')
        with open(new_fname, 'wt') as fobj:
            fobj.write('Nothing much')
        tpl = get_template('requirements.txt')
        assert_equal(tpl.filename, original_fname)
        insert_template_path(tmpdir)
        try:
            tpl = get_template('requirements.txt')
            assert_equal(tpl.filename, new_fname)
            assert_file_equal_string(new_fname, tpl.render())
        finally:
            pop_template_path()
        tpl = get_template('requirements.txt')
        assert_equal(tpl.filename, original_fname)


def test_get_template():
    tpl_fname = pjoin(TEMPLATE_PATH, 'requirements.txt')
    assert_equal(get_template('requirements.txt').filename, tpl_fname)
    assert_equal(get_template('unlikely_name.foo'), None)
