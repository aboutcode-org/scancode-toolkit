``scancode-license-data`` Usage
-------------------------------

Usage: ``scancode-license-data [OPTIONS]``

  Dump scancode license data in various formats, and the licenseDB static
  website at `path`.

Options:
  --path DIR  Dump the license data in this directory in the LicenseDB format
              and exit. Creates the directory if it does not exist.
  -h, --help  Show this message and exit.


``--path`` Option:
^^^^^^^^^^^^^^^^^^

The ``--path`` option is mandatory and defines the directory where the
license data will be stored.

Here is an example of dumping license data with the ``--path DIR`` option::

    scancode-license-data --path ~/licenses

    Dumping license data to: /home/user/licenses
    Done dumping #2465 licenses.

Each of the licenses contains four files: '.LICENSE', '.html', '.json', and '.yml'.

The dumped licenses directory look like this::

    licenses/
    ├── 389-exception.LICENSE
    ├── 389-exception.html
    ├── 389-exception.json
    ├── 389-exception.yml
    ├── 3com-microcodeLICENSE
    ├── 3com-microcode.html
    ├── 3com-microcode.json
    ├── 3com-microcode.yml
    .
    .
    .
