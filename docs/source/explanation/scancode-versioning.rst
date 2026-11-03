.. _scancode-versioning:


ScanCode versioning
===================

ScanCode is composed of code and data (mostly license data used for license
detection). In the past, we have tried using calver for code versioning to also
convey that the data contained in ScanCode was updated but it proved to be not
as clear and as effective as planned so we are switching back to semver which is
simpler and overall more useful for users. We also want to provide hints about
JSON output data format changes.

Therefore, this is our versioning approach starting with version 30.0.0:

- ScanCode releases are versioned using semver as documented at
  https://semver.org using major.minor.patch versioning.

- Significant changes to the data (license or copyright detection) is considered
  a major version change even if there are no code changes. The rationale is
  that in our case the data has the same impact as the code. Using outdated data
  is like using old code and means that several licenses may not be detected
  correctly. Any data change triggers at least a minor version change.

- We will signal separately to users with warnings messages when ScanCode needs
  to be upgraded because its data and/or code are out of date.


In addition to the main code version, we also maintain a secondary output data
format version using also semver with two segments. The versioning approach is
adapted for data this way:

- The first segment --the major version-- is incremented when data attributes
  that are removed, renamed, changed or moved (but not reordered) in the JSON
  output. Reordering the attributes of a JSON object is not considered as a
  change and does not trigger a version change.

- The second segment --the minor version-- of the output format is incremented
  for an addition of attributes to the JSON output.

- We store the output format version string in the JSON output object as the
  first attribute and display that also in the help.

- This output format versioning applies only to the JSON, pretty-printed JSON,
  YAML and JSON lines formats. It does not apply to CSV and any other formats.
  For these other formats there is no versioning and guaranteed format stability
  (or there may be some other rationale and convention for versioning like for
  SPDX).

- The output format version is incremented by when a new ScanCode tagged release
  is published

- We document in the CHANGELOG the output format changes in any new format version.

- For any format version changes, we will provide a documentation on the format
  and its updates using JSON examples and a comprehensive and updated data
  dictionary. See https://github.com/aboutcode-org/scancode-toolkit/issues/2008 for details.

Output data format version history
----------------------------------

The output data format version has changed in these releases:

- ``1.0.0`` - ScanCode v30.0.0 (September 23, 2021). The semver-based JSON
  output format version is introduced, together with the versioning approach
  documented above.

- ``2.0.0`` - ScanCode v31.0.0 (August 17, 2022). Major changes: the
  resource-level attribute ``packages`` is renamed to ``package_data``, the
  top-level attributes ``packages`` and ``dependencies`` are added, the
  resource-level attribute ``for_packages`` is added, the ``package_data``
  attribute ``root_path`` is removed, and the license clarity scoring fields
  are replaced.

- ``3.0.0`` - ScanCode v32.0.0 (May 23, 2023). Major changes to the licenses
  and packages output, including the ``todo`` codebase-level attribute.

- ``3.1.0`` - ScanCode v32.1.0 (March 23, 2024). New license match
  attributes, including ``from_file`` and ``matched_text_diagnostics``.

- ``3.2.0`` - ScanCode v32.2.0 (June 19, 2024). New package and dependency
  attributes: ``is_direct`` in DependentPackage, and ``is_private`` and
  ``is_virtual`` in PackageData.

- ``4.0.0`` - ScanCode v32.3.0 (October 21, 2024). Attribute renames:
  ``is_resolved`` is renamed to ``is_pinned`` for dependencies, and
  ``spdx_license_expression`` is renamed to ``license_expression_spdx`` for
  license matches.

- ``4.1.0`` - ScanCode v32.4.0 (June 26, 2025). New resource-level attribute
  ``sha1_git``.

See the `CHANGELOG
<https://github.com/aboutcode-org/scancode-toolkit/blob/develop/CHANGELOG.rst>`_
for the details of each release.
