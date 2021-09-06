.. _add_new_license_for_det:

How To Add a New License for Detection
======================================

How to add a new license for detection?
---------------------------------------

To add new license, you first need to select a new and unique license key (mit
and gpl-2.0 are some of the existing license keys). All licenses are stored as
plain text files in the src/licensedcode/data/licenses directory using their key
as base for the file name(s).

You need to create a pair of files:

- a file with the text of the license saved in a plain text file named
  key.LICENSE

- a small text data file (in YAML format) named key.yml that contains license
  information such as::

    key: my-license
    name: My License

The key name can contain only these symbols:

- lowercase letters from a to z,
- numbers from 0 to 9,and
- dash - and . period signs. No spaces.

Save these two files in the ``src/licensedcode/data/licenses/`` directory.

Done!

See the ``src/licensedcode/data/licenses/`` directory for many examples.
