#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import json

from packageurl import PackageURL

from packagedcode import maven
from packagedcode import models


"""
Handle Gradle Module Metadata (.module) files.

Gradle Module Metadata is the JSON format Gradle publishes next to a POM
when it publishes a component to a Maven repository. The format is
documented at:
https://docs.gradle.org/current/userguide/supported_metadata_formats.html

The authoritative schema lives in the Gradle source tree in
GradleModuleMetadataParser (subprojects/dependency-management); the
human-readable design document the issue linked to has moved and its old URL
is dead. The field inventory implemented here was confirmed against that
parser (formatVersion "1.1") and against the two real-world examples in
https://github.com/aboutcode-org/scancode-toolkit/issues/3522:

- top level: "formatVersion", "component", "createdBy", "variants".
- "component": "group", "module", "version", "attributes".
- variant keys: "name", "attributes", "files", "dependencies",
  "dependencyConstraints", "capabilities", "available-at".
- dependency keys: "group", "module", "version", "excludes", "reason",
  "attributes", "requestedCapabilities", "endorseStrictVersions",
  "thirdPartyCompatibility".
- version object keys: "prefers", "requires", "strictly", "rejects".
- capabilities: {"group", "name", "version"} (version required at variant
  level); "available-at": {"url", "group", "module", "version"} (a variant
  with "available-at" cannot declare "dependencyConstraints" or "files").
- file entries: {"name", "url", "size", "sha512", "sha256", "sha1", "md5"}.
  The parser itself ignores size and hashes, but they are present in real
  files and ScanCode records them.
- formatVersion "1.0" vs "1.1": the observable difference is that 1.1
  files carry sha256/sha512 checksums; the top-level shape is otherwise
  identical. Both versions are accepted and the version is recorded in
  extra_data; no behaviour branches on it.

Known limitation (v1): when a .module file sits next to a .pom for the same
component (the usual Maven Central layout), the two datafiles produce two
top-level packages with the same purl, one from each handler. Merging them
into a single package is a follow-up: the pom's richer fields
(description, licenses, homepage) should win over the .module's empty ones,
while the .module's variant-aware dependency list should win over the
pom's. Until that merge lands, scan a directory containing both files with
that duplication in mind.
"""


class GradleModuleMetadataHandler(models.DatafileHandler):
    datasource_id = 'gradle_module_metadata'
    path_patterns = ('*.module',)
    default_package_type = 'maven'
    default_primary_language = 'Java'
    description = 'Gradle Module Metadata (.module)'
    documentation_url = (
        'https://docs.gradle.org/current/userguide/supported_metadata_formats.html'
    )

    @classmethod
    def is_datafile(cls, location, filetypes=tuple(), _bare_filename=False):
        """
        Return True if the file at location is highly likely to be Gradle
        Module Metadata. The `.module` extension is not exclusive to Gradle,
        so a pattern match alone is not enough: the content must also be a
        JSON object carrying "formatVersion" and a "component" object.
        """
        if not super().is_datafile(location, filetypes=filetypes, _bare_filename=_bare_filename):
            return False
        if _bare_filename:
            # No file to sniff: the pattern match is all we can check.
            return True
        try:
            with io.open(location, encoding='utf-8') as loc:
                module_data = json.load(loc)
        except Exception:
            return False
        return (
            isinstance(module_data, dict)
            and 'formatVersion' in module_data
            and isinstance(module_data.get('component'), dict)
        )

    @classmethod
    def parse(cls, location, package_only=False):
        try:
            with io.open(location, encoding='utf-8') as loc:
                module_data = json.load(loc)
        except Exception:
            # Unparseable content: yield nothing, do not raise.
            return
        package_data = cls._parse(module_data, package_only)
        if package_data:
            yield package_data

    @classmethod
    def _parse(cls, module_data, package_only=False):
        """
        Return a PackageData built from already-loaded `.module` JSON data,
        or None if the data is not usable Gradle Module Metadata.
        """
        if not isinstance(module_data, dict):
            return None

        format_version = module_data.get('formatVersion')
        if format_version not in ('1.0', '1.1'):
            # Unknown format version: do not guess the shape.
            return None

        component = module_data.get('component') or {}
        namespace = component.get('group')
        name = component.get('module')
        if not namespace or not name:
            return None
        version = component.get('version')

        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            namespace=namespace,
            name=name,
            version=version,
            primary_language=cls.default_primary_language,
        )

        extra_data = {'format_version': format_version}

        component_attributes = component.get('attributes')
        if component_attributes:
            extra_data['component_attributes'] = component_attributes

        created_by = module_data.get('createdBy') or {}
        gradle = created_by.get('gradle') or {}
        gradle_version = gradle.get('version')
        if gradle_version:
            extra_data['gradle_version'] = gradle_version

        dependency_constraints = module_data.get('dependencyConstraints')
        if dependency_constraints:
            extra_data['dependency_constraints'] = dependency_constraints

        variants = module_data.get('variants') or []
        variants_extra = {}
        for variant in variants:
            if not isinstance(variant, dict):
                continue
            variant_name = variant.get('name')
            if not variant_name:
                continue
            variant_extra = {}
            attributes = variant.get('attributes')
            if attributes:
                variant_extra['attributes'] = attributes
            capabilities = variant.get('capabilities')
            if capabilities:
                variant_extra['capabilities'] = capabilities
            available_at = variant.get('available-at')
            if available_at:
                # A variant that is available elsewhere: the dependencies
                # and files live at the other component. Record it; the
                # package is still built from `component` above.
                variant_extra['available-at'] = available_at
            files = variant.get('files')
            if files:
                variant_extra['files'] = files
            if variant_extra:
                variants_extra[variant_name] = variant_extra
        if variants_extra:
            extra_data['variants'] = variants_extra

        main_file = get_main_file(variants)
        if main_file and version:
            file_name = main_file.get('name')
            if file_name:
                package_data['download_url'] = maven.build_url(
                    group_id=namespace,
                    artifact_id=name,
                    version=version,
                    filename=file_name,
                )
            for key in ('size', 'sha1', 'md5', 'sha256', 'sha512'):
                value = main_file.get(key)
                if value:
                    package_data[key] = value

        source_packages = get_source_packages(variants, namespace, name, version)
        if source_packages:
            package_data['source_packages'] = source_packages

        dependencies = get_dependencies(variants)
        if dependencies:
            package_data['dependencies'] = dependencies

        urls = {}
        if version:
            urls = maven.get_urls(namespace, name, version, qualifiers={})
        package_data.update(urls)
        # The "API" URL for a .module component is the .module file itself,
        # not the .pom that get_urls() assumes.
        if version:
            package_data['api_data_url'] = maven.build_url(
                group_id=namespace,
                artifact_id=name,
                version=version,
                filename=maven.build_filename(
                    artifact_id=name,
                    version=version,
                    extension='module',
                ),
            )

        package_data['extra_data'] = extra_data
        return models.PackageData.from_data(package_data, package_only)


def is_documentation_variant(variant):
    """
    Return True if a variant only carries documentation (sources, javadoc):
    its dependencies and files do not describe the component itself.
    """
    attributes = variant.get('attributes') or {}
    return (
        attributes.get('org.gradle.category') == 'documentation'
        or 'org.gradle.docstype' in attributes
    )


def get_main_file(variants):
    """
    Return the file entry of the main artifact: the first .jar file of the
    `apiElements` variant, falling back to `runtimeElements`, then to the
    first variant (in file order) that ships a .jar file. In practice
    apiElements and runtimeElements carry the same jar with the same hashes;
    preferring `apiElements` is a deterministic convention.
    """
    by_name = {}
    for variant in variants:
        if isinstance(variant, dict) and variant.get('name'):
            by_name.setdefault(variant['name'], variant)
    candidates = []
    for variant_name in ('apiElements', 'runtimeElements'):
        variant = by_name.get(variant_name)
        if variant:
            candidates.append(variant)
    candidates.extend(
        variant for variant in variants
        if isinstance(variant, dict) and variant not in candidates
    )
    for variant in candidates:
        for file_entry in variant.get('files') or []:
            if isinstance(file_entry, dict) and (file_entry.get('name') or '').endswith('.jar'):
                return file_entry
    return None


def get_source_packages(variants, namespace, name, version):
    """
    Return a list of source-package purls for documentation variants that
    ship a sources jar, mirroring the Maven `classifier=sources` pattern.
    """
    source_packages = []
    for variant in variants:
        if not isinstance(variant, dict):
            continue
        attributes = variant.get('attributes') or {}
        if attributes.get('org.gradle.docstype') != 'sources':
            continue
        files = variant.get('files') or []
        if not files:
            continue
        source_purl = PackageURL(
            type='maven',
            namespace=namespace,
            name=name,
            version=version,
            qualifiers=dict(classifier='sources'),
        ).to_string()
        source_packages.append(source_purl)
    return source_packages


def get_dependencies(variants):
    """
    Return a deduped list of DependentPackage objects collected from all
    non-documentation variants. A dependency shared by several variants
    (apiElements and runtimeElements list the same entries in practice)
    yields a single entry: `runtimeElements` wins for scope, and every
    variant it appears in is recorded in the dependency's extra_data.
    """
    collected = {}
    order = []
    for variant in variants:
        if not isinstance(variant, dict):
            continue
        if is_documentation_variant(variant):
            continue
        variant_name = variant.get('name')
        attributes = variant.get('attributes') or {}
        usage = attributes.get('org.gradle.usage')
        is_runtime_variant = usage == 'java-runtime' or variant_name == 'runtimeElements'
        for dependency in variant.get('dependencies') or []:
            if not isinstance(dependency, dict):
                continue
            group = dependency.get('group')
            module = dependency.get('module')
            if not group or not module:
                continue
            version = dependency.get('version')
            requirement, purl_version, is_pinned, version_extra = parse_version(version)
            dependency_extra = get_dependency_extra(dependency)
            dep_extra = merge_version_extra(version_extra, dependency_extra)
            key = (group, module, requirement)
            entry = collected.get(key)
            if entry is None:
                entry = dict(
                    group=group,
                    module=module,
                    requirement=requirement,
                    purl_version=purl_version,
                    is_pinned=is_pinned,
                    version_extra=dep_extra,
                    variants=[],
                    is_runtime=False,
                )
                collected[key] = entry
                order.append(key)
            entry['variants'].append(variant_name)
            if is_runtime_variant:
                entry['is_runtime'] = True
            # A later variant may carry richer version info (e.g. rejects):
            # keep the first-seen requirement, but do not lose extras.
            if dep_extra:
                entry['version_extra'] = merge_version_extra(
                    entry['version_extra'], dep_extra
                )

    dependencies = []
    for key in order:
        entry = collected[key]
        variants = [name for name in entry['variants'] if name]
        # runtimeElements wins for scope; otherwise the first variant seen.
        if 'runtimeElements' in variants:
            scope = 'runtimeElements'
        elif 'apiElements' in variants:
            scope = 'apiElements'
        else:
            scope = variants[0] if variants else None
        purl = PackageURL(
            type='maven',
            namespace=entry['group'],
            name=entry['module'],
            version=entry['purl_version'],
        ).to_string()
        extra_data = dict(entry['version_extra'] or {})
        if len(variants) > 1:
            extra_data['variants'] = variants
        dependent = models.DependentPackage(
            purl=purl,
            extracted_requirement=entry['requirement'],
            scope=scope,
            is_runtime=entry['is_runtime'],
            is_optional=False,
            is_pinned=entry['is_pinned'],
            extra_data=extra_data or None,
        )
        dependencies.append(dependent)
    return dependencies


def get_dependency_extra(dependency):
    """
    Return the extra_data mapping for a dependency entry: its `reason`,
    `excludes`, `attributes`, requested capabilities and other
    dependency-level fields that have no dedicated DependentPackage field.
    Exclusions are recorded, not modelled as negative dependencies:
    ScanCode has no such concept.
    """
    extra_data = {}
    reason = dependency.get('reason')
    if reason:
        extra_data['reason'] = reason
    excludes = dependency.get('excludes')
    if excludes:
        extra_data['excludes'] = excludes
    attributes = dependency.get('attributes')
    if attributes:
        extra_data['attributes'] = attributes
    capabilities = dependency.get('requestedCapabilities')
    if capabilities:
        extra_data['capabilities'] = capabilities
    if dependency.get('endorseStrictVersions'):
        extra_data['endorse_strict_versions'] = True
    if dependency.get('thirdPartyCompatibility'):
        extra_data['third_party_compatibility'] = True
    return extra_data


def parse_version(version):
    """
    Return a (requirement, purl_version, is_pinned, extra_data) tuple for a
    dependency `version` value from a .module file.

    - {"requires": "1.2.3"}: exact version, pinned.
    - {"strictly": "1.2.3"}: exact version, pinned.
    - {"prefers": "1.2.3"}: a preferred version, not pinned: no version in
      the purl (as Maven does for unpinned requirements) and the preference
      kept in extra_data.
    - a plain string "1.2.3": exact version, pinned.
    - missing/empty: no requirement, not pinned.
    - "rejects" entries are kept in extra_data in every case.
    """
    extra_data = {}
    if isinstance(version, str):
        return version, version, True, extra_data
    if not isinstance(version, dict):
        return None, None, False, extra_data
    rejects = version.get('rejects')
    if rejects:
        extra_data['rejects'] = rejects
    if version.get('requires'):
        return version['requires'], version['requires'], True, extra_data
    if version.get('strictly'):
        return version['strictly'], version['strictly'], True, extra_data
    if version.get('prefers'):
        extra_data['version'] = {'prefers': version['prefers']}
        return version['prefers'], None, False, extra_data
    return None, None, False, extra_data


def merge_version_extra(existing, new):
    """
    Merge two version extra_data mappings, keeping the first-seen value on
    conflict and combining `rejects` lists.
    """
    merged = dict(existing or {})
    for key, value in (new or {}).items():
        if key == 'rejects' and key in merged:
            merged[key] = list(dict.fromkeys(merged[key] + value))
        else:
            merged.setdefault(key, value)
    return merged
