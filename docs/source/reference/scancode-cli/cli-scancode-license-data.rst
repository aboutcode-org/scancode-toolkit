.. _cli-scancode-license-data:

scancode license data CLI
=========================

Scancode includes the license data for all the licenses in detects
as scancode-licensedb with the license texts and other reference data
like license category, authors, and reference links.

``scancode-license-data`` is a CLI command to provide this license data
in a structured format that is API, and this includes:

- all the license details, without license text, in one JSON/YAML file
- all the individual licenses, with license text, in JSON/YAML files
- locally built HTML page with a searchable table of all licenses
- locally built HTML pages for all individual licenses with its text and details

The data and HTML pages are dumped into a folder specified by the required
CLI option ``--path``.

The licensedb is also hosted at https://scancode-licensedb.aboutcode.org/ and is
updated daily from the latest added licenses from the scancode ``develop`` branch
using the ``scancode-license-data`` CLI option.

Usage: ``scancode-license-data [OPTIONS]``

**Quick Reference**
-------------------

--path DIR      Dump the license data in this directory in the LicenseDB format
                and exit. Creates the directory if it does not exist.
                [required]
-h, --help      Show this message and exit.

