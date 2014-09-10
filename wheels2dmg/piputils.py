""" Utilities for building pkg installer and disk image from wheels
"""
from __future__ import division, print_function

from copy import copy
from pip.req import InstallRequirement, RequirementSet, parse_requirements
from pip.download import PipSession


def recon_pip_args(args, with_reqs=True):
    """ Reconstruct known pip command-line parameters from argument object

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
    params : list
        Command line parameters for pip
    """
    if not with_reqs:
        args = copy(args)
        args.req_specs = None
        args.requirement = None
    params = [] if args.req_specs is None else list(args.req_specs)
    if not args.requirement is None:
        for requirement in args.requirement:
            params.append('--requirement=' + requirement)
    if not args.index_url is None:
        params.append('--index-url=' + args.index_url)
    if not args.extra_index_url is None:
        for extra_index_url in args.extra_index_url:
            params.append('--extra-index-url=' + extra_index_url)
    if args.no_index:
        params.append('--no-index')
    if not args.find_links is None:
        for link in args.find_links:
            params.append('--find-links=' + link)
    return params


def get_requirements(requirements, requirement_files = ()):
    """ Get set of requirements from pip-like input arguments

    Parameters
    ----------
    requirements : sequence
        sequence of requirement names, maybe with versions
    requirement_files : sequence
        sequence of filenames or URLs with requirements

    Returns
    -------
    requirement_set : RequiremenSet instance
        Pip requirements set
    """
    session = PipSession()
    requirement_set = RequirementSet(
        build_dir=None,
        src_dir=None,
        download_dir=None,
        session=session,
    )
    for name in requirements:
        requirement_set.add_requirement(
            InstallRequirement.from_line(name))
    for filename in requirement_files:
        for req in parse_requirements(filename, session=session):
            requirement_set.add_requirement(req)
    return requirement_set


def get_req_strings(req_set):
    """ Get requirement strings from a RequirementSet

    Parameters
    ----------
    req_set : RequirementSet instance

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
        if req.extras:
            req_str += '[{0}]'.format(','.join(req.extras))
        if req.req.specs:
            req_str += ','.join([''.join(s) for s in req.req.specs])
        req_strings.append(req_str)
    return req_strings
