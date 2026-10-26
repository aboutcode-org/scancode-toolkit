.. _cli-scancode-reindex-licenses:

ScanCode reindex licenses CLI
=============================

ScanCode maintains a license index to search for and detect licenses. When ScanCode is
configured for the first time, a license index is built and used in every scan thereafter.
The ``scancode-reindex-licenses`` command rebuilds the license index.

Usage: ``scancode-reindex-licenses [OPTIONS]``

Quick Reference
---------------

  --all-languages             [EXPERIMENTAL] Rebuild the license index
                              including texts all languages (and not only
                              English) and exit.
  --only-builtin              Rebuild the license index excluding any
                              additional license directory or additional
                              license plugins which were added previously, i.e.
                              with only builtin scancode license and rules.
  --additional-directory DIR  Include this directory with additional custom
                              licenses and license rules in the license
                              detection index.
  --load-dump                 Load all license and rules from their respective
                              files and then dump them back to those same files.
  -h, --help                  Shows the options and explanations.

----

.. _cli-scancode-reindex-licenses-additional-directory-option:

``--additional-directory`` option
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``--additional-directory`` option allows the user to include additional directories
of licenses to use in license detection.

This command only needs to be run once for each set of additional directories, in all subsequent
runs of ScanCode with the same directories all the licenses in the directories will be cached
and used in License detection. But reindexing removes these directories, if they aren't
reintroduced as additional directories.

The directory structure should look something like this

.. code-block:: none

    additional_license_directory/
    ├── licenses/
    │   ├── example-installed-1.LICENSE
    │   └── example-installed-1.yaml
    ├── rules/
    │   ├── example-installed-1.RULE
    │   └── example-installed-1.yaml

**Example**

.. code-block:: shell

    scancode-reindex-licenses --additional-directory tests/licensedcode/data/additional_licenses/additional_dir/

You can also include multiple directories like so

.. code-block:: shell

    scancode-reindex-licenses --additional-directory /home/user/external_licenses/external1 --additional-directory /home/user/external_licenses/external2

If you want to continue running scans with ``/home/user/external_licenses/external1`` and
``/home/user/external_licenses/external2``, you can simply run scans after the command above
reindexing with those directories and they will be included. ::

    scancode -l --license-text --json-pp output.json samples

However, if you wanted to run a scan with a new set of directories, such as
``home/user/external_licenses/external1`` and ``home/user/external_licenses/external3``, you would
need to reindex the license index with those directories as parameters::

    scancode --additional-directory /home/user/external_licenses/external1 --additional-directory /home/user/external_licenses/external3

.. include::  /rst-snippets/note-snippets/add-licenses-or-rules-from-additional-directory-is-temporary.rst


.. note::

    You can also install external licenses through a plugin for
    better reproducibility and distribution of those license/rules
    for use in conjunction with scancode-toolkit licenses.
    See :ref:`how-to-install-new-license-plugin`

.. _cli-scancode-reindex-licenses-only-builtin-option:

``--only-builtin`` option
^^^^^^^^^^^^^^^^^^^^^^^^^

Rebuild the license index excluding any additional license directory or additional
license plugins which were added previously, i.e. with only builtin scancode license and rules.

This is applicable when there are additional license plugins installed already and you want to
reindex the licenses without these licenses from the additional plugins.

.. note::

    Running the ``--only-builtin`` command won't get rid of the installed license plugins, it
    would just reindex without the licenses from these plugins for once. Another reindex afterwards
    without this option would bring back the licenses from the plugins again in the index.

.. _cli-scancode-reindex-licenses-all-languages-option:

``--all-languages`` option
^^^^^^^^^^^^^^^^^^^^^^^^^^

Rebuild the license index including texts all languages (and not only
English) and exit. This is an EXPERIMENTAL option.

.. _cli-scancode-reindex-licenses-load-dump-option:

``--load-dump`` option
^^^^^^^^^^^^^^^^^^^^^^

Load all licenses and rules from their respective files and then dump them
to their respective files. This is done to make small formatting changes across
all licenses and rules, to be consistent across them.
