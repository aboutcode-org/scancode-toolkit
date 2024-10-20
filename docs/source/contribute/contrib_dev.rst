.. _contrib_code_dev:

Contributing to Code Development
================================

TL;DR:

- Contributions comes as bugs/questions/issues and as pull requests.
- Source code and runtime data are in the /src/ directory.
- Test code and test data are in the /tests/ directory.
- Datasets (inluding licenses) and test data are in /data/ sub-directories.
- We use DCO signoff in commit messages, like Linux does.
- Porting ScanCode to other OS (FreeBSD is supported, etc.) is possible. Enter an issue for help.

See `CONTRIBUTING.rst <https://github.com/aboutcode-org/scancode-toolkit/blob/develop/CONTRIBUTING.rst>`_
for details.


.. _contrib_code_conven:

Code layout and conventions
---------------------------

Source code is in the ``src/`` directory, tests are in the ``tests/`` directory.
Miscellaneous scripts and configuration files are in the ``etc/`` directory.

There is one Python package for each major feature under ``src/`` and a
corresponding directory with the same name under ``tests`` (but this is not a
package by design as it would not make sense to have a top level "tests" package
which is a name that's too common).

Each test script is named ``test_XXXX``; we prefer organizing tests in subclasses
of the standard library ``unittest`` module. But we also use plain functions
that are discovered nicely by ``pytest``.

When source or tests need data files, we store these in a ``data`` subdirectory.
This is used extensively in tests and also in source code for the reference
license texts and data and license detection rules files.

We use PEP8 conventions with a relaxed line length that can be up to 90'ish
characters long when needed to keep the code clear and readable.

We write tests, a lot of tests, thousands of tests.  When finding bugs or adding
new features, we add tests. See existing test code for examples which form also
a good specification for the supported features.

The tests should pass on Linux 64 bits, Windows 64 bits and on
macOS 10.14 and up. We maintain multiple CI loops with Azure (all OSes)
at https://dev.azure.com/nexB/scancode-toolkit/_build and Appveyor (Windows) at
https://ci.appveyor.com/project/nexB/scancode-toolkit .


Several tests are data-driven and use data files as test input and sometimes
data files as test expectation (in this case using either JSON or YAML files);
a large number of copyright, license and package manifest parsing tests are such
data-driven tests.


.. _scancode_toolkit_development_running_tests:

Running tests
-------------

ScanCode comes with over 29,000 unit tests to ensure detection accuracy and
stability across Linux, Windows and macOS OSes: we kinda love tests, do we?

We use pytest to run the tests: call the ``pytest`` script to run the whole
test suite. This is installed with the ``pytest`` package which is installed
when you run ``./configure --dev``).

If you are running from a fresh git clone and you run ``./configure`` and then
``source venv/bin/activate`` the ``pytest`` command will be available in your path.

Alternatively, if you have already configured but are not in an activated
"virtualenv" the ``pytest`` command is available under
``<root of your checkout>/venv/bin/pytest``

(Note: paths here are for POSIX, but mostly the same applies to Windows)

If you have a multiprocessor machine you might want to run the tests in parallel
(and faster). For instance: ``pytest -n4`` runs the tests on 4 CPUs. We
typically run the tests in verbose mode with ``pytest -vvs -n4``.

You can also run a subset of the test suite as shown in the CI configs
https://github.com/aboutcode-org/scancode-toolkit/blob/develop/azure-pipelines.yml e,g,
``pytest -n 2 -vvs tests/scancode`` runs only the test scripts present in the
``tests/scancode`` directory. (You can give the path to a specific test script
file there too).

See also https://docs.pytest.org for details or use the ``pytest -h`` command
to show the many other options available.

One useful option is to run a select subset of the test functions matching a
pattern with the ``-k`` option, for instance: ``pytest -vvs -k tcpdump`` would
only run test functions that contain the string "tcpdump" in their name or their
class name or module name.

Another useful option after a test run with some failures is to re-run only the
failed tests with the ``--lf`` option, for instance: ``pytest -vvs --lf`` would
only run only test functions that failed in the previous run.

Because we have a lot of tests (over 29,000), we organized theses in test suites
using pytest markers that are defined in the ``conftest.py`` pytest plugin.
These are enabled by adding a ``--test-suite`` option to the pytest command.

- ``--test-suite=standard`` is the default and runs a decent but basic test suite
- ``--test-suite=all`` runs the ``standard`` test and adds a comprehensive test suite
- ``--test-suite=validate`` runs the ``standra`` and ``all`` test and adds
  extensive data-driven and data validations (for package, copyright and license
  detection)

In some cases we need to regenerate test data when expected behavious/result data
structures change, and we have an environement variable to regenerate test data.
`SCANCODE_REGEN_TEST_FIXTURES` is present in `scancode_config` and this can be
set to regenerate test data for specific tests like this:

``SCANCODE_REGEN_TEST_FIXTURES=yes pytest -vvs tests/packagedcode/test_package_models.py``

This command will only regenerate test data for only the tests in `test_package_models.py`,
and we can further specify the tests to regen by using more pytest options like `--lf` and
`-k test_instances`.

If test data is regenerated, it is important to review the diff for test files and
carefully go through all of it to make sure there are no unintended changes there,
and then commit all the regenerated test data.

To help debug in scancode, we use logging. There are different environement variables
you need to set to turn on logging. In packagedcode::

``SCANCODE_DEBUG_PACKAGE=yes pytest -vvs tests/packagedcode/ --lf``

Or set the ``TRACE`` variable to ``True``. This enables ``logger_debug`` functions
logging variables and shows code execution paths by logging and printing the logs
in the terminal. If debugging full scans run by click, you have to raise exceptions
in addition to setting the TRACE to enable logging.

.. _scancode_toolkit_development_thirdparty_libraries:

Thirdparty libraries and dependencies management
-----------------------------------------------------

ScanCode uses the ``configure`` and ``configure.bat`` scripts to install a
`virtualenv <https://virtualenv.pypa.io/en/stable/>`_ , install required
packaged dependencies using  `setuptools <https://github.com/pypa/setuptools>`_
and such that ScanCode can be installed in a repeatable and consistent manner on
all OSes and Python versions.

For this we maintain a ``setup.cfg`` with our direct dependencies with loose
minimum version constraints; and we keep pinned exact versions of these
dependencies in the ``requirements.txt`` and ``requirements-dev.txt`` (for
testing and development).

Note: we also have a ``setup-mini.cfg`` used to create a ScanCode PyPI package
with minimal dependencies (and limited features). This is mostly duplicated
from ``setup.cfg``.

And to ensure that we also all use well known version of the core virtualenv,
pip, setuptools and wheel libraries, we use the ``virtualenv.pyz`` Python
zipp app from https://github.com/pypa/get-virtualenv/tree/main/public and
store it in the Git repo in the ``etc/thirdparty`` directory.

We bundle pre-built bundled native binaries as plugins which are installed as
wheels. These binaries are organized by OS and architecture; they ensure that
ScanCode works out of the box either using a checkout or a download, without
needing a compiler and toolchain to be installed.

The corresponding source code and build scripts for all for the
pre-built binaries are stored in a separate repository at
https://github.com/aboutcode-org/scancode-plugins

ScanCode app archives should not require network access for installation or
configuration of its third-party libraries and dependencies. To enable this,
we store bundled thirdparty components and  libraries in the ``thirdparty``
directory of released app archives; this is done at build time.
These dependencies are stored as pre-built wheels. These wheels are sometimes
built by us when there is no wheel available upstream on PyPI. We store all
these prebuilt wheels with corresponding .ABOUT and .LICENSE files in
https://github.com/nexB/thirdparty-packages/tree/main/pypi which is published
for download at  https://thirdparty.aboutcode.org/pypi/

Because this is used by the configure script, all the thirdparty dependencies
used in ScanCode MUST be available there first. Therefore adding a new
dependency means requesting a merge/PR in
https://github.com/nexB/thirdparty-packages/ first that contains all the
recursive dependencies.

There are utility scripts in ``etc/release`` that can help with the dependencies
management process in particular to build or update wheels with native code for
multiple OSes (Linux, macOS and Windows) and multiple Python versions (3.9+),
which is not a completely simple operation (and requires eventually 12 wheels
and one source distribution to be published as we support 3 OSes and 5 Python
versions).


Using ScanCode as a Python library
----------------------------------

ScanCode can be used also as a Python library and is available as a
Python wheel in PyPi and installed with ``pip install scancode-toolkit`` or
``pip install scancode-toolkit-mini``.

.. _note:

   Since we do not pin dependencies to avoid dependency resolution conflicts
   for downstream users, there are possibilities of issues arising from
   dependencies silently changing API/functions which scancode uses.
