############################
 {{ info.pkg_name }} README
############################

This installer will install the following Python packages on your system, with
their dependencies:

{% for item in info.get_requirement_strings() %}
* {{ item }}
{% endfor %}

If you don't have it already, the installer will also install ``pip`` - the
standard Python Installer Program (see https://pypi.python.org/pip).

****************************
To do a standard GUI install
****************************

The GUI installs packages into a Python setup from the main Python website at
http://python.org.

* If you have not already installed Python {{ info.pyv_m_m }} from
  http://python.org, then double click on the ``Install Python
  {{ info.pyv_m_m }}`` file to open the installer, and install Python.
* Double click on the ``{{ info.pkg_name_pyv_version }}.pkg`` file to run the
  install of {{ info.pkg_name }}.

*******************
Manual installation
*******************

You might want to do a manual installation if the GUI installer fails for some
reason, or you prefer manual installs, or you are using Python from Macports
or Homebrew.

Manual install into Python.org Python
=====================================

Make sure you have installed Python {{ info.pyv_m_m }} from http://python.org.
You can get this by following links from the main website, or double clicking
the ``Install Python {{ info.pyv_m_m }}`` file on this disk image.  If you are
navigating the Python.org website, you need the version for Snow Leopard or
later (downloads ending in ``macosx10.6.dmg``).

After you have installed Python, open Terminal.app.  At the prompt type::

    which python{{ info.pyv_m_m }}

You should get something like this::

    {{ info.py_org_base }}/{{ info.pyv_m_m }}/bin/python{{ info.pyv_m_m }}

If not, you could try closing Terminal.app, opening it again, and retrying
``which python{{ info.pyv_m_m }}``.  If that doesn't give an answer like the
one above, consider reinstalling Python from the Python.org installer.

Once you are happy that you have the right Python, open Terminal.app and
change directory to this disk image, with something like::

    cd /Volumes/{{ info.pkg_name_pyv_version }}

Install / update pip::

    python{{ info.pyv_m_m }} {{ info.wheel_sdir }}/get-pip.py

Finally, install the Python packages from {{ info.pkg_name }}::

    pip{{ info.pyv_m_m }} install -f {{ info.wheel_sdir }} --no-index -U -r {{ info.wheel_sdir }}/{{ info.pkg_name_version }}.txt

Manual install into homebrew Python
===================================

You will probably already have installed Python version {{ info.pyv_m_m }}
into homebrew, with ``brew install python{% if info.pyv_m == 3 %}3{% endif
%}``.

Then change directory to this disk image, with something like::

    cd /Volumes/{{ info.pkg_name_pyv_version }}

Homebrew installs ``pip`` with Python, so now you can install the Python
packages from {{ info.pkg_name }}::

    pip{{ info.pyv_m }} install -f {{ info.wheel_sdir }} --no-index -U -r {{ info.wheel_sdir }}/{{ info.pkg_name_version }}.txt

Manual install into Macports Python
===================================

You have probably installed Python {{ info.pyv_m_m }} with something like
``sudo port install python{{ info.pyv_mm }}``.

Install ``pip`` with::

    sudo port install py{{ info.pyv_mm }}-pip

Then change directory to this disk image, with something like::

    cd /Volumes/{{ info.pkg_name_pyv_version }}

You can now install the Python packages from {{ info.pkg_name }}::

    sudo pip-{{ info.pyv_m_m }} install -f {{ info.wheel_sdir }} --no-index -U -r {{ info.wheel_sdir }}/{{ info.pkg_name_version }}.txt
