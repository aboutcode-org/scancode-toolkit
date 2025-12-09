.. _license-policy-plugin:

License policy plugin
=====================

This plugin allows the user to apply policy details to a scancode scan, depending on which
licenses are detected in a particular file. If a license specified in the policy file is
detected by scancode, this plugin will apply that policy information to the resource as a new
attribute: ``license_policy``.

Policy file specification
-------------------------
The policy file is a YAML (``.yml``) document with the following structure

.. code-block:: yaml

  license_policies:
  -   license_key: mit
      label: Approved License
      color_code: '#00800'
      icon: icon-ok-circle
  -   license_key: agpl-3.0
      label: Approved License
      color_code: '#008000'
      icon: icon-ok-circle
  -   license_key: broadcom-commercial
      label: Restricted License
      color_code: '#FFcc33'
      icon: icon-warning-sign

The only required key is ``license_key``, which represents the ScanCode license key to match
against the detected licenses in the scan results.

In the above example, a descriptive label is added along with a color code and CSS ``id`` name
for potential visual display.

Using the plugin
----------------

To apply license policies during a ScanCode scan, specify the ``--license-policy`` option.

For example, use the following command to run a File Info and License scan on
``/path/to/codebase/``, using a License Policy file found at ``~/path/to/policy-file.yml``

.. code-block:: shell

  scancode -clipeu /path/to/codebase/ --license-policy ~/path/to/policy-file.yml --json-pp
    ~/path/to/scan-output.json

**Example**

.. code-block:: none

  {
    "path": "samples/zlib/deflate.c",
    "type": "file",
    "detected_license_expression": "zlib",
    "detected_license_expression_spdx": "Zlib",
    "license_detections": [
      {
        "license-expression": "zlib",
        ...
        ...
        ...
      }
    ],
    "license_policy": {
      "license_key": "zlib",
      "label": "Approved License",
      "color_code": "#00800",
      "icon": "icon-ok-circle"
    },
    "scan_errors": []
  }
