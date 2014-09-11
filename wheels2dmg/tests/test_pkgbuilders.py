""" Testing pkgbuilders module
"""

from os.path import basename, abspath, expanduser, relpath, join as pjoin

from ..pkgbuilders import get_get_pip, write_requires

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
