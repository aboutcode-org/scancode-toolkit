Other available CLIs
====================

.. _other_cli:

----

.. include::  /rst_snippets/scancode-reindex-licenses.rst

----

.. include::  /rst_snippets/extract.rst

----

``scancode-reindex-licenses`` command
-------------------------------------

ScanCode maintains a license index to search for and detect licenses. When ScanCode is
configured for the first time, a license index is built and used in every scan thereafter.

This ``scancode-reindex-licenses`` command rebuilds the license index. Running this command
displays the following message to the terminal::

    Checking and rebuilding the license index...

This has several CLI options as follows:

``--additional-directory`` Option:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``--additional-directory`` option allows the user to include additional directories
of licenses to use in license detection.

This command only needs to be run once for each set of additional directories, in all subsequent
runs of ScanCode with the same directories all the licenses in the directories will be cached
and used in License detection. But reindexing removes these directories, if they aren't
reintroduced as additional directories.

The directory structure should look something like this::

    additional_license_directory/
    ├── licenses/
    │   ├── example-installed-1.LICENSE
    │   └── example-installed-1.yaml
    ├── rules/
    │   ├── example-installed-1.RULE
    │   └── example-installed-1.yaml

Here is an example of reindexing the license cache using the ``--additional-directory PATH`` option
with a single directory::

    scancode-reindex-licenses --additional-directory tests/licensedcode/data/additional_licenses/additional_dir/

You can also include multiple directories like so::

    scancode-reindex-licenses --additional-directory /home/user/external_licenses/external1 --additional-directory /home/user/external_licenses/external2

If you want to continue running scans with ``/home/user/external_licenses/external1`` and
``/home/user/external_licenses/external2``, you can simply run scans after the command above
reindexing with those directories and they will be included. ::

    scancode -l --license-text --json-pp output.json samples

However, if you wanted to run a scan with a new set of directories, such as
``home/user/external_licenses/external1`` and ``home/user/external_licenses/external3``, you would
need to reindex the license index with those directories as parameters::

    scancode --additional-directory /home/user/external_licenses/external1 --additional-directory /home/user/external_licenses/external3

.. include::  /rst_snippets/note_snippets/additional_directory_is_temp.rst


.. note::

    You can also install external licenses through a plugin for
    better reproducibility and distribution of those license/rules
    for use in conjunction with scancode-toolkit licenses.
    See :ref:`install_new_license_plugin`


``--only-builtin`` Option:
^^^^^^^^^^^^^^^^^^^^^^^^^^

Rebuild the license index excluding any additional license directory or additional
license plugins which were added previously, i.e. with only builtin scancode license and rules.

This is applicable when there are additional license plugins installed already and you want to
reindex the licenses without these licenses from the additional plugins.

.. note::

    Running the ``--only-builtin`` command won't get rid of the installed license plugins, it
    would just reindex without the licenses from these plugins for once. Another reindex afterwards
    without this option would bring back the licenses from the plugins again in the index.


``--all-languages`` Option:
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Rebuild the license index including texts all languages (and not only
English) and exit. This is an EXPERIMENTAL option.


``--load-dump`` Option
^^^^^^^^^^^^^^^^^^^^^^

Load all licenses and rules from their respective files and then dump them
to their respective files. This is done to make small formatting changes across
all licenses and rules, to be consistent across them.
