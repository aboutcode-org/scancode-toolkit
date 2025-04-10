.. _add_new_license_for_det:

How To Add a New License for Detection
======================================

How to add a new license for detection?
---------------------------------------

To add a new license, you first need to select a new and unique license `key`
(``mit`` and ``gpl-2.0`` are some of the existing license keys).

The key name can contain only these symbols:

- lowercase letters from a to z,
- numbers from 0 to 9,
- dash - and . period signs. No spaces or underscore.

The license key also has to be fewer than 50 characters (same for `short_name`).

We also have to add a `spdx_license_key` which is either a valid SPDX license key at
` The SPDX license list <https://spdx.org/licenses/>`_, or a `Licenseref-scancode-<key>`.

All licenses are stored as a plain text file in the `src/licensedcode/data/licenses`
directory using their key as base for the file name. For example the filename for a
license with `key: mit` would be `mit.LICENSE`.

You need to create a file with:

- the text of the license saved in plain text. We usually get rid of HTML tags or
  other special characters. We also remove copyrights and only keep the original
  text as is, with the original formatting intact.

- the data attributes for the license in YAML format as
  `YAML frontmatter <https://python-frontmatter.readthedocs.io/en/latest/>`_.

See an example license: `apache-2.0.LICENSE <https://github.com/aboutcode-org/scancode-toolkit/tree/develop/src/licensedcode/data/licenses/apache-2.0.LICENSE>`_

There are a couple of mandatory attributes:

- `key`
- `spdx_license_key`
- `short_name`
- `name`
- `category` (Use "Unstated License" if not known)
- `owner` (Use "Unspecified" if not known)

And more attributes which are not mandatory but always nice to have (if applicable):

- `other_spdx_license_keys`
- `osi_license_key`
- `minimum_coverage`
- `standard_notice`
- `notes`

We want to use `minimum_coverage` when there are other licenses that are very similar
and we want to make sure we match these licenses correctly, and `notes` for interesting
cases of licenses with descriptions to help identify origin, similarities to other licenses,
notes about the SPDX keys and others.

Some URLs:

- `homepage_url`
- `text_urls`
- `osi_url`
- `faq_url`
- `other_urls`

Also attributes having ignorables in the license text:

- `ignorable_urls`
- `ignorable_copyrights`
- `ignorable_authors`
- `ignorable_holders`
- `ignorable_emails`

See the ``src/licensedcode/data/licenses/`` directory for many more examples.

.. note::

    Add licenses in a local development installation and run `scancode-reindex-licenses`
    to make sure we reindex the licenses and this validates the new licenses.
