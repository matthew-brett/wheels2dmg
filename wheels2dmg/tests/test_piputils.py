""" Testing piputils module
"""

from os.path import join as pjoin, split as psplit, abspath, dirname

from pip.exceptions import InstallationError
from ..piputils import (recon_pip_args, get_requirements, get_req_strings)
from ..wheels2dmg_cmd import get_parser
from ..tmpdirs import InTemporaryDirectory

from nose.tools import (assert_true, assert_false, assert_raises,
                        assert_equal, assert_not_equal)


DATA_PATH = pjoin(abspath(dirname(__file__)), 'data')

SCIPY_STACK_NAMES = [
    'pip>=1.5.4',
    'numpy>=1.6',
    'scipy>=0.10',
    'pytz',
    'tornado',
    'python-dateutil',
    'matplotlib>=1.1',
    'pyzmq',
    'ipython[notebook,test]>=0.13',
    'numexpr',
    'pandas>=0.8',
    'sympy>=0.7',
    'nose>=1.1']

SCIPY_STATS_DATA_NAMES = SCIPY_STACK_NAMES + [
    'scikit-learn',
    'scikit-image',
    'patsy',
    'statsmodels',
    'h5py',
    'Pillow']


def test_reconstruct_pip_args():
    # Function to reconstruct pip command line arguments
    class A():
        requirement = None
        index_url = None
        extra_index_url = None
        no_index = None
        find_links = None
    args = A()
    assert_equal(recon_pip_args(args), [])
    args.requirement = ()
    assert_equal(recon_pip_args(args), [])
    args.requirement = ('file1.txt', 'file2.txt')
    exp_params = ['--requirement=file1.txt', '--requirement=file2.txt']
    assert_equal(recon_pip_args(args), exp_params)
    args.index_url = 'http://matthew.dynevor.org'
    exp_params.append('--index-url=http://matthew.dynevor.org')
    assert_equal(recon_pip_args(args), exp_params)
    args.extra_index_url = ()
    assert_equal(recon_pip_args(args), exp_params)
    extra_urls = ('http://www.python.org', 'http://wheels.scikit-image.org')
    args.extra_index_url = extra_urls
    exp_params += ['--extra-index-url=' + u for u in extra_urls]
    assert_equal(recon_pip_args(args), exp_params)
    # False does not trigger --no-index
    args.no_index = False
    assert_equal(recon_pip_args(args), exp_params)
    args.no_index = True
    exp_params += ['--no-index']
    assert_equal(recon_pip_args(args), exp_params)
    args.find_links = ()
    assert_equal(recon_pip_args(args), exp_params)
    link_urls = ('http://nipy.org', 'http://nipy.org/nibabel')
    args.find_links = link_urls
    exp_params += ['--find-links=' + u for u in link_urls]
    assert_equal(recon_pip_args(args), exp_params)


def test_parser_reconstruct_pip():
    # Check roundtrip using our parser and recon_pip_args
    parser = get_parser()
    args = ['pkg_name', '1.0']
    for in_out_args in [
        # arguments to parser, [expected arguments to send to pip]
        # If second element missing assume input + output same
        ([],),
        (['--requirement=file1.txt'],),
        (['-r', 'file1.txt'], ['--requirement=file1.txt']),
        (['--requirement=file1.txt', '--requirement=file2.txt'],),
        (['-r', 'file1.txt', '-r', 'file2.txt'],
         ['--requirement=file1.txt', '--requirement=file2.txt']),
        (['--index-url=http://www.foo.com'],),
        (['-i', 'http://www.foo.com'], ['--index-url=http://www.foo.com']),
        (['--extra-index-url=http://www.foo.com'],),
        (['--extra-index-url=http://www.foo.com'],),
        (['--extra-index-url=http://www.foo.com',
          '--extra-index-url=http://bar.org'],),
        (['--no-index'],),
        (['--find-links=http://www.foo.com'],),
        (['--find-links=http://www.foo.com',
          '--find-links=http://bar.org'],),
        (['-f', 'http://www.foo.com', '--find-links=http://bar.org'],
         ['--find-links=http://www.foo.com',
          '--find-links=http://bar.org'],),
    ]:
        if len(in_out_args) == 1:
            in_args = in_out_args[0]
            out_args = in_args
        else:
            in_args, out_args = in_out_args
        parsed = parser.parse_args(args + in_args)
        assert_equal(recon_pip_args(parsed), out_args)


def assert_names_equal(req_set, names):
    assert_equal(names, get_req_strings(req_set))


def test_get_requirements():
    # Test get_requirements function
    # Gets list of pip requiremnts from input arguments
    assert_names_equal(get_requirements([]), [])
    assert_names_equal(get_requirements(['one']), ['one'])
    assert_names_equal(get_requirements(['one', 'two==1.2']),
                       ['one', 'two==1.2'])
    assert_names_equal(get_requirements(['one', 'two==1.2,<1.3']),
                       ['one', 'two==1.2,<1.3'])
    sps_file = pjoin(DATA_PATH, 'scipy-stack-1.0-plus.txt')
    assert_names_equal(get_requirements([], [sps_file]), SCIPY_STACK_NAMES)
    assert_names_equal(get_requirements(['three', 'four==5'], [sps_file]), 
                       ['three', 'four==5'] + SCIPY_STACK_NAMES)
    # Duplicate requirements cause an error
    assert_raises(InstallationError, get_requirements, ['three', 'three'])
    assert_raises(InstallationError, get_requirements, ['three', 'three==5.0'])
    assert_raises(InstallationError, get_requirements, ['numpy'], [sps_file])
    # A requirements file embedding a requirements file
    with InTemporaryDirectory():
        with open('more_required.txt', 'wt') as fobj:
            fobj.write("""
# A comment
# An unused URL
-f https://nipy.bic.berkeley.edu/scipy_installers
-r {0}
scikit-learn
scikit-image
patsy
statsmodels
h5py
Pillow
""".format(sps_file))
        assert_names_equal(get_requirements([], ['more_required.txt']),
                            SCIPY_STATS_DATA_NAMES)
