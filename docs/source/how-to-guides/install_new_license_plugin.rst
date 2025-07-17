.. _install_external_licenses:

How to Install External Licenses to Use in License Detection
============================================================

Users can install external licenses and rules in the form of:

1. reusable plugins
2. license directories

These licenses and rules are then used in license detection.

.. _install_new_license_plugin:

How to install a plugin containing external licenses and/or rules
-----------------------------------------------------------------

To create a plugin with external licenses or rules, we must create a Python package
containing the license and/or rule files. Python packages can have many different
file structures. You can find an example package in:

``tests/licensedcode/data/additional_licenses/additional_plugin_1``.

This is the basic structure of the example plugin::

    licenses_to_install1/
    ├── src/
    │   └── licenses_to_install1/
    │       ├── licenses/
    │       │   ├── example-installed-1.LICENSE
    |       ├── rules/
    │       │   ├── example-installed-1.RULE
    │       └── __init__.py
    ├── apache-2.0.LICENSE
    ├── MANIFEST.in
    ├── setup.cfg
    └── setup.py

Entry points definition in ``setup.py``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, in ``setup.py``, you must provide an entry point called ``scancode_location_provider``.
This allows ScanCode-Toolkit to discover the plugin and use it in license detection.
Here is the definition of ``entry_points`` in ``setup.py``::

    entry_points={
            'scancode_location_provider': [
                'licenses_to_install1 = licenses_to_install1:LicensesToInstall1Paths',
            ],
        },

The ``scancode_location_provider`` entry point maps to a list with information about the plugin.
The variable ``licenses_to_install1`` is the name of the entry point. All entry point names
**must** start with the prefix ``licenses``, or else ScanCode-Toolkit will not use them in
license detection.

Directory structure
^^^^^^^^^^^^^^^^^^^

``licenses_to_install1`` is set to ``licenses_to_install1:LicensesToInstall1Paths``.
Note that in ``src``, we have another directory called ``licenses_to_install1`` and in
``licenses_to_install1/__init__.py``, we define the class ``LicensesToInstall1Paths``.
These two values make up the entry point definition.

``LicensesToInstall1Paths`` is a subclass of ``LocationProviderPlugin`` and
implements the method ``get_locations()``. The class you define in ``__init__.py``
must also subclass ``LocationProviderPlugin`` and implement this method.

Finally, the same directory containing the class definition must also contain the
licenses and/or rules. Licenses must be contained in a directory called ``licenses`` and rules
must be contained in a directory called ``rules``.

See :ref:`add_new_license_for_det` and :ref:`add_new_license_det_rule` to understand
the structure of license and rule files, respectively.

After creating this plugin, you can upload it to PyPI so that others can use it, or you can
leave it as a local directory.

Installing and using the plugin
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To use the plugin in license detection, all you need to do is:

1. Configure the scancode-toolkit virtualenv and activate.
2. Install the package with `pip` like the following:
   ``pip install tests/licensedcode/data/additional_licenses/additional_plugin_2/``
3. Reindex licenses using `scancode-reindex-licenses`.

.. include::  /rst_snippets/note_snippets/license_plugin_needs_reindex.rst

Once it is installed, the contained licenses and rules will automatically be used in
license detection assuming the plugin follows the correct directory structure conventions.

Writing tests for new installed licenses
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Look at ``tests/licensedcode/data/example_external_licenses/licenses_to_install1`` to see
an example of a plugin with tests. The tests are contained in the ``tests`` directory::

    licenses_to_install1/
    ├── src/
    │   └── licenses_to_install1/
    │       ├── licenses/
    │       │   ├── example-installed-1.LICENSE
    │       ├── rules/
    │       │   ├── example-installed-1.RULE
    │       └── __init__.py/
    ├── tests/
    │    ├── data/
    │    │   ├── example-installed-1.txt
    │    │   └── example-installed-1.txt.yml
    │    └── test_detection_datadriven.py
    ├── apache-2.0.LICENSE
    ├── MANIFEST.in
    ├── setup.cfg
    └── setup.py

To write your own tests, first make sure ``setup.py`` includes ``scancode-toolkit``
as a dependency::

    ...
    install_requires=[
        'scancode-toolkit',
    ],
    ...

Then you can define a test class and call the ``build_tests`` method defined in
``licensedcode_test_utils``, passing in the test directory and the test class as parameters::

    TEST_DIR = abspath(join(dirname(__file__), 'data'))


    class TestLicenseDataDriven1(unittest.TestCase):
        pass


    licensedcode_test_utils.build_tests(
        TEST_DIR,
        clazz=TestLicenseDataDriven1, regen=scancode_config.REGEN_TEST_FIXTURES)

The ``tests/data`` directory contains one file for each license:
a license text file with a YAML frontmatter specifying the expected license expression
from the test.

Finally, install the plugin and run the test:

``pytest -vvs tests/test_detection_datadriven.py``.

.. include::  /rst_snippets/note_snippets/license_plugin_delete.rst

----

.. _add_new_license_directory:

How to add external licenses and/or rules from a directory
----------------------------------------------------------

This is the basic structure of the example license directory::

    additional_license_directory/
    ├── licenses/
    │   ├── example-installed-1.LICENSE
    ├── rules/
    │   ├── example-installed-1.RULE

Adding the licenses to the index
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To add the licenses in the directory to the index, all you need to do is:

1. Configure the scancode-toolkit virtualenv and activate.
2. Run ``scancode-reindex-licenses`` with:

   ``--additional-directory tests/licensedcode/data/additional_licenses/additional_dir/``

.. include::  /rst_snippets/note_snippets/additional_directory_is_temp.rst


Once the licenses/rules are in the index, they will automatically be used in license detection.

----

.. include::  /rst_snippets/scancode-reindex-licenses.rst
