#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

"""
Helper functions to write scan results in a compact manner as JSON, preserving
only non-duplicated key detection information, and skipping attributes with
large values or more details.
"""

# Tracing flags
TRACE = False


def logger_debug(*args):
    pass


if TRACE:
    import sys
    import logging

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str)
                                     and a or repr(a) for a in args))


COMPACT_CONFLICTING_OPTIONS = [
    'summary', 'classify', 'consolidate', 'todo', 'mark_source', 'tallies',
    'tallies_by_facet', 'tallies_with_details', 'tallies_key_files',
    'license_references', 'license_text', 'license_diagnostics', 'license_text_diagnostics',
    'go_symbol', 'rust_symbol'
]

PACKAGE_DETECTION_FIELDS = [
    # Detection fields have a lot of inlined duplicated data which needs to be skipped,
    # just identifiers are enough, and this will be kept in the data mapping seperately
    "license_detections",
    "other_license_detections"
]

COMPACT_PACKAGES_SKIP_ATTRIBUTES = [
    # These are PackageURL fields and are coontained in `package_uid` which is a purl + identifier
    "type",
    "namespace",
    "name",
    "version",
    "qualifiers",
    "subpath",
    "purl",
    # This usually has text which is too large and not useful for a compact output 
    "description",
    # Just `declared_license_expression_spdx` is enough
    "declared_license_expression",
    # Just `other_license_expression_spdx` is enough
    "other_license_expression_spdx",
    # Already captured by license detection fields if present
    "extracted_license_statement",
    # This usually has text which is too large and not useful for a compact output 
    "notice_text",
    "extra_data",  
    # This can be deduced from datafile_paths
    "datasource_ids"
] + PACKAGE_DETECTION_FIELDS


COMPACT_DEPENDENCIES_SKIP_ATTRIBUTES = [
    "resolved_package",
    # Not essential information
    "extra_data",
    # This can be deduced from `datafile_path`
    "datasource_id"
]

COMPACT_LICENSES_SKIP_ATTRIBUTES = [
    # Just keeping `license_expression_spdx` is enough
    "license_expression",
    # This needs to be compact further, so we can't have as-is 
    "reference_matches"
]

COMPACT_LICENSE_MATCHES_SKIP_ATTRIBUTES = [
    # Just keeping `license_expression_spdx` is enough
    "license_expression",
    # We have the `rule_identifier` and this is derivative
    "rule_url",
    # We have the `rule_identifier` and this info can be fetched 
    "rule_relevance"
]

COMPACT_RESOURCES_SKIP_ATTRIBUTES = [
    # Just keeping `detected_license_expression_spdx` is enough
    "detected_license_expression",
    # Detection fields have a lot of inlined duplicated data which needs to be skipped,
    # just identifiers are enough, and this will be kept in the data mapping seperately
    "license_detections",
    "package_data",
    # license clues are matches not aggregated in the top-level license detections, but
    # these mappings need to be processed to make them more compact
    "license_clues",
    # `name`, `base_name` and `extension` info is also present in the full-path
    "name",
    "base_name",
    "extension"
]

def get_compact_packages(package_mapping):
    compact_package_mapping = get_compact_mapping(
        mapping=package_mapping,
        keys_to_skip=COMPACT_PACKAGES_SKIP_ATTRIBUTES,
    )

    # Only keep the license detection identifiers from the detection mappings
    for detection_attribute in PACKAGE_DETECTION_FIELDS:
        detection_mapping = [
            {"identifier": detection.get("identifier")}
            for detection in package_mapping.get(detection_attribute, [])
            if detection
        ]
        if detection_mapping:
            compact_package_mapping[detection_attribute] = detection_mapping

    return compact_package_mapping


def get_compact_dependencies(dependency_mapping):
    return get_compact_mapping(
        mapping=dependency_mapping,
        keys_to_skip=COMPACT_DEPENDENCIES_SKIP_ATTRIBUTES,
    )


def get_compact_license_detections(license_mapping):
    compact_license_mapping = get_compact_mapping(
        mapping=license_mapping,
        keys_to_skip=COMPACT_LICENSES_SKIP_ATTRIBUTES,
    )
    compact_license_mapping["reference_matches"] = [
        get_compact_mapping(
            mapping=match,
            keys_to_skip=COMPACT_LICENSE_MATCHES_SKIP_ATTRIBUTES,
        )
        for match in license_mapping.get("reference_matches", [])
    ]
    return compact_license_mapping


def get_compact_mapping(mapping, keys_to_skip=[]):
    """
    Get a more compact version of `mapping` which doesn't have
    empty key/value pairs or attributes which are explicitly skipped
    with the `keys_to_skip` list.

    Also removes empty key/value pairs recursively.
    """
    if type(mapping) is not dict:
        return mapping

    return {
        key: get_compact_mapping(value)
        for key, value in mapping.items()
        if value and key not in keys_to_skip
    }


get_compact_func_by_key = {
    "packages": get_compact_packages,
    "dependencies": get_compact_dependencies,
    "license_detections": get_compact_license_detections,
}

def write_compact_codebase_attributes(stream, key, value):
    if not key in get_compact_func_by_key:
        return

    func = get_compact_func_by_key.get(key)
    if func:
        compact_output = [
            func(instance)
            for instance in value
        ]
        if compact_output:
            return stream.write(key, compact_output)


def get_compact_resource(resource_mapping):
    compact_resource_mapping = get_compact_mapping(
        mapping=resource_mapping,
        keys_to_skip=COMPACT_RESOURCES_SKIP_ATTRIBUTES,
    )

    # Only keep detection identifiers for resource level package/license
    # detections as these are assembled into top-level summaries and so
    # these inlined data is duplicate information
    package_data = [
        {"purl": detection.get("purl")}
        for detection in resource_mapping.get("package_data", [])
        if detection and detection.get("purl")
    ]
    if package_data:
        compact_resource_mapping["package_data"] = package_data

    license_detections = [
        {"identifier": detection.get("identifier")}
        for detection in resource_mapping.get("license_detections", [])
        if detection
    ]
    if license_detections:
        compact_resource_mapping["license_detections"] = license_detections

    # license clues are matches not aggregated in the top-level license detections, but
    # these mappings need to be processed to make them more compact
    license_clues = [
        get_compact_mapping(
            mapping=clue_mapping,
            keys_to_skip=COMPACT_LICENSE_MATCHES_SKIP_ATTRIBUTES,
        )
        for clue_mapping in resource_mapping.get("license_clues", [])
        if clue_mapping
    ]
    if license_clues:
        compact_resource_mapping["license_clues"] = license_clues

    return compact_resource_mapping
