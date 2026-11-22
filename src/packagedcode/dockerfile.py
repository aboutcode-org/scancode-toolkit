#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from dockerfile_parse import DockerfileParser

from commoncode import fileutils
from packagedcode import cargo
from packagedcode import models

"""
Handle Dockerfile and Containerfile as "non-assembled" package data, collecting
OCI image labels.

See https://github.com/aboutcode-org/scancode-toolkit/issues/3561
"""

OCI_LABEL_PREFIX = 'org.opencontainers.image.'

# OCI annotation key suffix mapped to a PackageData field name.
# Keys handled separately below are not listed here: `documentation`
# (extra_data, see below), `authors` and `vendor` (parties), `licenses`
# (extracted_license_statement), `created` (release_date), `revision`,
# `ref.name`, `base.digest` and `base.name` (extra_data).
LABEL_FIELD_BY_OCI_KEY = {
    'title': 'name',
    'version': 'version',
    'description': 'description',
    'url': 'homepage_url',
    'source': 'vcs_url',
}


class DockerfileHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'dockerfile'
    default_package_type = 'docker'
    path_patterns = (
        '*/Dockerfile',
        '*/Dockerfile.*',
        '*/Containerfile',
        '*/Containerfile.*',
    )
    description = 'Dockerfile or Containerfile with OCI image labels'
    documentation_url = 'https://github.com/opencontainers/image-spec/blob/main/annotations.md'

    @classmethod
    def parse(cls, location, package_only=False):
        try:
            # DockerfileParser only accepts a path ending in "Dockerfile": any
            # other path is treated as a directory holding a file named
            # "Dockerfile". Pass the content via `fileobj` instead so that
            # Containerfile and suffixed names (Dockerfile.dev, ...) work too.
            with open(location, 'rb') as loc:
                parser = DockerfileParser(fileobj=loc)
                labels = dict(parser.labels)
                base_image = parser.baseimage
        except Exception:
            # Unparseable content: yield nothing, do not raise.
            return

        if not labels and not base_image:
            # A file with neither a FROM instruction nor labels is not a
            # Dockerfile: yield nothing.
            return

        yield build_package_data(location, labels, base_image, package_only)


def build_package_data(location, labels, base_image, package_only=False):
    """
    Return a PackageData built from Dockerfile `labels` (a mapping) and the
    `base_image` from the FROM instruction.
    """
    oci_labels = {
        key[len(OCI_LABEL_PREFIX):]: value
        for key, value in labels.items()
        if key.startswith(OCI_LABEL_PREFIX)
    }

    package_data = dict(
        datasource_id=DockerfileHandler.datasource_id,
        type=DockerfileHandler.default_package_type,
    )

    for oci_key, field in LABEL_FIELD_BY_OCI_KEY.items():
        value = oci_labels.get(oci_key)
        if value:
            package_data[field] = value

    extra_data = {}

    documentation = oci_labels.get('documentation')
    if documentation:
        # There is no `documentation_url` field on the Package model yet (see
        # https://github.com/aboutcode-org/scancode-toolkit/issues/4092): keep the
        # value in extra_data, following the Cargo and Java-manifest precedent.
        # Switch to the real field once that issue lands.
        extra_data['documentation_url'] = documentation

    revision = oci_labels.get('revision')
    if revision:
        extra_data['revision'] = revision

    ref_name = oci_labels.get('ref.name')
    if ref_name:
        extra_data['ref_name'] = ref_name

    base_digest = oci_labels.get('base.digest')
    if base_digest:
        extra_data['base_image_digest'] = base_digest

    base_name = oci_labels.get('base.name')
    if base_name:
        extra_data['base_image_name'] = base_name

    if base_image:
        extra_data['base_image'] = base_image

    if labels:
        # Keep the full label mapping, including non-OCI labels: the OCI spec
        # requires consumers to not error on unknown keys.
        extra_data['labels'] = labels

    if extra_data:
        package_data['extra_data'] = extra_data

    authors = oci_labels.get('authors')
    if authors:
        # `authors` is a freeform string. Parse it as a single "Name <email>"
        # person; a comma-separated list of several authors is kept as one
        # party rather than split on commas, which would mangle names such as
        # "Jitsi Team, Inc.".
        parties = list(cargo.get_parties([authors], party_role='author'))
        if parties:
            package_data['parties'] = parties

    vendor = oci_labels.get('vendor')
    if vendor:
        package_data.setdefault('parties', []).append(
            models.Party(
                type='organization',
                role='vendor',
                name=vendor,
            ).to_dict()
        )

    licenses = oci_labels.get('licenses')
    if licenses:
        # The value is already an SPDX license expression per the OCI spec.
        # `from_data` runs license detection on it below.
        package_data['extracted_license_statement'] = licenses

    created = oci_labels.get('created')
    if created:
        package_data['release_date'] = created

    package = models.PackageData.from_data(package_data, package_only)

    if not package.name:
        # If no name was detected for the Package, then we use the basename
        # of the parent directory as the Package name, following the
        # ReadmeHandler precedent.
        parent_dir = fileutils.parent_directory(location)
        package.name = fileutils.file_base_name(parent_dir)

    return package
