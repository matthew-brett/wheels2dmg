.. image:: https://travis-ci.org/matthew-brett/wheels2dmg.svg?branch=master
    :target: https://travis-ci.org/matthew-brett/wheels2dmg

##########
wheels2dmg
##########

A Python utility to build an OSX disk image and ``.pkg`` installer to install
a given set of wheels.

The idea is that any package that can be installed via pip can also have a
safe dmg installer, because we use pip to install the wheels, and pip will
manage the dependencies.

The installer only installs into Python.org Python, but includes instructions
on how to install manually into macports and homebrew.

Here's how to make an installer for matplotlib 1.4.0::

    wheels2dmg matplotlib 1.4.0 matplotlib --python-version 3.4.1

Or for more than one package::

    wheels2dmg scipy-stack 1.0 scipy matplotlib ipython[notebook] \
        pandas numexpr sympy --python-version 2.7.8

.. warning::

    Please be careful - this software is alpha quality and has not been much
    tested in the wild.  I'd love to get feedback if you have problems, and
    I'd be very happy to have pull requests to this repo too.

****
Code
****

See https://github.com/matthew-brett/wheels2dmg

Released under the BSD two-clause license - see the file ``LICENSE`` in the
source distribution.

`travis-ci <https://travis-ci.org/matthew-brett/wheels2dmg>`_ kindly tests the
code automatically under Python 2.7, 3.3 and 3.4.

The latest released version is at https://pypi.python.org/pypi/wheels2dmg

*******
Support
*******

Please put up issues on the `wheels2dmg issue tracker
<https://github.com/matthew-brett/wheels2dmg/issues>`_.
