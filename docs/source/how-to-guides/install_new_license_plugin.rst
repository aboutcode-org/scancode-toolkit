.. _install_new_license_plugin:

How to Install External License Plugins to Use in License Detection
===================================================================

Users can install external licenses and rules in the form of plugins. These
licenses and rules are then used in license detection.

How to create a plugin containing external licenses and/or rules
----------------------------------------------------------------

To create a plugin with external licenses or rules, we must create a Python package
containing the license and/or rule files. Python packages can have many different
file structures. You can find an example package in
``tests/licensedcode/data/example_external_licenses/licenses_to_install1``.

This is the basic structure of the example plugin::

    licenses_to_install1/
    ├── src/
    │   └── licenses_to_install1/
    │       ├── licenses/
    │       │   ├── example_installed_1.LICENSE
    │       │   └── example_installed_1.yaml
    |       ├── rules/
    │       │   ├── example_installed_1.RULE
    │       │   └── example_installed_1.yaml
    │       └── __init__.py
    ├── gpl-1.0.LICENSE
    ├── MANIFEST.in
    ├── setup.cfg
    └── setup.py

Key points to note
------------------

Entry points definition in ``setup.py``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, in ``setup.py``, you must provide an entry point called ``scancode_location_provider``.
This allows ScanCode Toolkit to discover the plugin and use it in license detection.
Here is the definition of ``entry_points`` in ``setup.py``::

    entry_points={
            'scancode_location_provider': [
                'licenses_to_install1 = licenses_to_install1:LicensesToInstall1Paths',
            ],
        },

The ``scancode_location_provider`` entry point maps to a list with information about the plugin.
The variable ``licenses_to_install1`` is the name of the entry point. All entry point names
**must** start with the prefix ``licenses``, or else ScanCode Toolkit will not use them in
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
-------------------------------
To use the plugin in license detection, all you need to do is install it using ``pip``.
Once it is installed, the contained licenses and rules will automatically be used in
license detection assuming the plugin follows the correct directory structure conventions.
