.. _install-scancode-using-pip:

Install ScanCode using pip
==========================

ScanCode can be installed from the public PyPI repository using ``pip`` which
the standard Python package management tool.

.. NOTE::

    Note that `pip` installation method does work on ARM chips, i.e. Linux/MacOS on
    Apple M1 chips, as some non-native dependencies do not have pre-built wheels
    for ARM (like py-ahocorasick, intbitset). See :ref:`install-scancode-installation-prerequisites` for
    more information. See related issues for more info:

    - `Fallback pure-python deps <https://github.com/aboutcode-org/scancode-toolkit/issues/3210>`_
    - `pip install failing on Apple M1 Macs <https://github.com/aboutcode-org/scancode-toolkit/issues/3205>`_

The steps are:

#. Create a Python virtual environment

    .. code-block:: shell

        /usr/bin/python3 -m venv venv

    To learn more about Python virtualenv, including installation and usage see this
    `tutorial <https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv>`_.

#. Activate the virtual environment you just created

    .. code-block:: shell

        source venv/bin/activate

#. Run ``pip`` to install the latest versions of base utilities

    .. code-block:: shell

        pip install --upgrade pip setuptools wheel

#. Install the latest version of ScanCode

    .. code-block:: shell

        pip install scancode-toolkit

#. No errors? Congratulations! You are good to go to :ref:`running-a-scan`.

.. NOTE::

    For advanced usage, ``scancode-toolkit-mini`` is an alternative package with
    no default dependencies on pre-built binaries. This may come handy for some
    special use cases such as packaging for a Linux or FreeBSD distro.


Uninstalling ScanCode
---------------------

To uninstall ScanCode, run the following command.

.. code-block:: shell

    pip uninstall scancode-toolkit
