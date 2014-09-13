""" Utilities for building pkg installer and disk image from wheels
"""
from __future__ import division, print_function

from argparse import ArgumentParser

from pip.req import InstallRequirement, RequirementSet, parse_requirements
from pip.download import PipSession


def make_pip_parser(parser = None):
    """ Add (some) pip arguments to a Argparse `parser`

    Parameters
    ----------
    parser : None or :class:`argparse.ArgumentParser` instance
        Parser to which to add arguments.  If None, make a new empty
        parser. If not None, parser modified in-place
    """
    if parser is None:
        parser = ArgumentParser()
    # Arguments for pip wheel / install calls
    parser.add_argument('req_specs', type=str, nargs='*', default=[],
                        help='pip requirement specifiers', metavar='REQ_SPEC')
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


def recon_pip_args(args):
    """ Reconstruct known pip command-line parameters from argument object

    Split parameters into parameters specifying requirements, and parameters
    not specifying requirements

    Positional arguments to command line found in ``args.req_specs``
    (requirement specifiers).

    Parameters
    ----------
    args : object
        Arguments object returned from command line processing by argparse
    with_reqs : bool, optional
        If True, return pip arguments giving install requirements (positional
        arguments in ``args.req_specs``, requirement files in
        ``args.requirements``).  Otherwise, omit these.

    Returns
    -------
    req_params : list
        Command line parameters for pip that specify requirements
    other_params : list
        Command line parameters for pip that do not specify requirements
    """
    req_params = [] if args.req_specs is None else list(args.req_specs)
    if not args.requirement is None:
        for requirement in args.requirement:
            req_params.append('--requirement=' + requirement)
    other_params = []
    if not args.index_url is None:
        other_params.append('--index-url=' + args.index_url)
    if not args.extra_index_url is None:
        for extra_index_url in args.extra_index_url:
            other_params.append('--extra-index-url=' + extra_index_url)
    if args.no_index:
        other_params.append('--no-index')
    if not args.find_links is None:
        for link in args.find_links:
            other_params.append('--find-links=' + link)
    return req_params, other_params


def get_requirements(req_specs, requirement_files=None):
    """ Get set of requirements from pip-like input arguments

    Parameters
    ----------
    req_specs : sequence
        sequence of requirement specifiers, maybe with versions
    requirement_files : None or sequence, optional
        sequence of filenames or URLs with requirements

    Returns
    -------
    requirement_set : RequiremenSet instance
        Pip requirements set
    """
    if requirement_files is None:
        requirement_files = []
    session = PipSession()
    requirement_set = RequirementSet(
        build_dir=None,
        src_dir=None,
        download_dir=None,
        session=session,
    )
    for name in req_specs:
        requirement_set.add_requirement(
            InstallRequirement.from_line(name))
    for filename in requirement_files:
        for req in parse_requirements(filename, session=session):
            requirement_set.add_requirement(req)
    return requirement_set


def get_req_strings(req_set, extras=True, versions=True):
    """ Get requirement strings from a RequirementSet

    Parameters
    ----------
    req_set : RequirementSet instance
    extras : bool, optional
        If True, append extras specifications to requirement name
    versions : bool, optional
        If True, append version specifications to requirement name

    Returns
    -------
    req_strings : list
        list of string corresponding to the requirements in `req_set`
    """
    req_strings = []
    reqs = req_set.requirements
    for name in reqs.keys():
        req = reqs[name]
        req_str = req.name
        if extras and req.extras:
            req_str += '[{0}]'.format(','.join(req.extras))
        if versions and req.req.specs:
            req_str += ','.join([''.join(s) for s in req.req.specs])
        req_strings.append(req_str)
    return req_strings
