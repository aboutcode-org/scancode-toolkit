# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import attr
import click
import json
import re
import uuid
from datetime import datetime
from enum import Enum
from lxml import etree


from commoncode.cliutils import OUTPUT_GROUP
from commoncode.cliutils import PluggableCommandLineOption
from formattedcode import FileOptionType
from plugincode.output import OutputPlugin
from plugincode.output import output_impl
from typing import FrozenSet, List, Optional, Tuple


def _get_set_of_known_licenses_and_spdx_license_ids() -> Tuple[List, FrozenSet[str]]:
    """load all licenses and all SPDX Ids known to ScanCode
    this will also load scancode licenserefs, so we filter those
    """
    from licensedcode.cache import get_licenses_db

    licenses = get_licenses_db()
    spdx_keys = filter(lambda id: id is not None,
                        map(
                           lambda license: license.spdx_license_key,
                           licenses.values()
                       )
                    )
    return (licenses, frozenset(spdx_keys))


known_licenses, spdx_ids = _get_set_of_known_licenses_and_spdx_license_ids()
spdx_licenseref_prefix = "LicenseRef-scancode-"

@attr.s
class CycloneDxLicense:
    id: str = attr.ib(default=None)
    name: str = attr.ib(default=None)
    url: str = attr.ib(default=None)


@attr.s
class CycloneDxLicenseEntry:
    @classmethod
    def from_declared_license(cls, declared_license) -> 'CycloneDxLicenseEntry':
        lic = CycloneDxLicense()
        if isinstance(declared_license, str):
            # if license key is in list of known spdx ids, set as id
            if declared_license in spdx_ids:
                lic.id = declared_license
            # if we match this regex assume we are dealing with a URL
            elif declared_license is not None and url_pattern.match(declared_license):
                lic.url = declared_license
            else:
                lic.name = declared_license
        # some declared_license entries are also expressed as dicts
        elif isinstance(declared_license, dict):
            lic_type = declared_license.get('type')
            if lic_type in spdx_ids:
                lic.id = lic_type
            else:
                lic.name = lic_type
            lic.url = declared_license.get('url')
        return CycloneDxLicenseEntry(license=lic, expression=None)


    @classmethod
    def from_license_expression(
            cls, license_expression: str,
    ) -> Optional['CycloneDxLicenseEntry']:
        """
        Return Optional[CycloneDxLicenseEntry] built from a license_expression
        Attempt to resolve `license_expression` to a CycloneDxLicense
        if that fails, set it as `expression`
        if `license_expression`is None, return None
        """

        # exit early if we don't have a valid license_expression
        if license_expression is None:
            return None

        from scancode.api import SCANCODE_LICENSEDB_URL

        license = known_licenses.get(license_expression)
        if license is not None:
            # set ScanCode license DB URL as fallback
            url = SCANCODE_LICENSEDB_URL.format(license.key)
            if license.text_urls:
                url = license.text_urls[0]
            lic = CycloneDxLicense(id=license.spdx_license_key, name=license.name, url=url)
            return CycloneDxLicenseEntry(license=lic, expression=None)
        else:
            return CycloneDxLicenseEntry(license=None, expression=license_expression)

    @classmethod
    def from_package(cls, package: dict) -> List['CycloneDxLicenseEntry']:
        """
        Return a list of CycloneDxLicenseEntry instances built from package data
        Attempt to map `license_expression` and `declared_license` data to CycloneDx format
        """
        # store previously encountered IDs to identify duplicates
        seen_ids = set()

        lic_expr = package.get("license_expression")
        entry = CycloneDxLicenseEntry.from_license_expression(lic_expr)
        if entry is not None:
            licenses = [entry]
            if entry.license is not None:
                seen_ids.add(entry.license.id)
        else:
            licenses = []

        declared_license = package["declared_license"]
        if isinstance(declared_license, list):
            for entry in declared_license:
                lic_entry = CycloneDxLicenseEntry.from_declared_license(entry)
                if lic_entry is None:
                    continue
                id = lic_entry.license.id if lic_entry.license is not None else None
                if id in seen_ids or id is None:
                    continue
                else:
                    seen_ids.add(id)
                    if lic_entry is not None:
                        licenses.append(lic_entry)
        else:
            lic_entry = CycloneDxLicenseEntry.from_declared_license(declared_license)
            if lic_entry is not None:
                id = lic_entry.license.id if lic_entry.license is not None else None
                if id not in seen_ids and id is not None:
                    seen_ids.add(id)
                    licenses.append(lic_entry)

        return licenses

    license: CycloneDxLicense = attr.ib(default=None)
    expression: str = attr.ib(default=None)


@attr.s
class CycloneDxAttribute:
    name: str = attr.ib()
    value: str = attr.ib()


@attr.s
class CycloneDxMetadata:
    timestamp = attr.ib(default=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
    tools: List[dict] = attr.ib(factory=list)
    properties: List[CycloneDxAttribute] = attr.ib(factory=list)


@attr.s
class CycloneDxHashObject:
    __cdx_hash_types_by_scancode_hash = {
        'md5': 'MD5',
        'sha1': 'SHA-1',
        'sha256': 'SHA-256',
        'sha512': 'SHA-512',
    }
    @classmethod
    def from_package(cls, package: dict) -> List['CycloneDxHashObject']:
        hashes = []
        for scancode_alg, cyclonedx_alg in cls.__cdx_hash_types_by_scancode_hash.items():
            digest = package.get(scancode_alg)
            if digest:
                hashes.append(CycloneDxHashObject(alg=cyclonedx_alg, content=digest))
        return hashes
    alg: str = attr.ib()
    content: str = attr.ib()


@attr.s
class CycloneDxExternalRef:
    @classmethod
    def _get_external_ref_from_key(cls, package: dict, key: str) -> 'CycloneDxExternalRef':
        url = package.get(key)
        type = url_type_mapping[key]
        if url is not None and type is not None:
            return CycloneDxExternalRef(url=url, type=type)
        return None

    @classmethod
    def from_licenseref_id(cls, id: str) -> Optional['CycloneDxExternalRef']:
        """
        Returns an external reference to a license URL for LicenseRef-scancode-* license
        or none if the input is not a LicenseRef
        Expect a scancode SPDX LicenseRef as input
        and build a CycloneDxExternalRef from it
        """

        if id is None or not id.startswith(spdx_licenseref_prefix):
            return None

        from scancode.api import SCANCODE_LICENSEDB_URL

        scancode_id = id[len(spdx_licenseref_prefix):]
        url = SCANCODE_LICENSEDB_URL.format(scancode_id)
        comment = f"Information about scancode spdx license {id}"

        return CycloneDxExternalRef(url=url, type="license", comment=comment)

    @classmethod
    def from_package(cls, package: dict) -> List['CycloneDxExternalRef']:
        ext_refs = []
        for key in url_type_mapping:
            ref = cls._get_external_ref_from_key(package, key)
            if ref is not None:
                ext_refs.append(ref)
        return ext_refs

    url: str = attr.ib()
    reference_types = frozenset(
        [
            'vcs',
            'issue-tracker',
            'website',
            'advisories',
            'bom',
            'mailing-list',
            'social',
            'chat',
            'documentation',
            'support',
            'distribution',
            'license',
            'build-meta',
            'build-system',
            'other',
        ]
    )
    type: str = attr.ib(validator=attr.validators.in_(reference_types))
    comment: str = attr.ib(default=None)
    hashes: List[CycloneDxHashObject] = attr.ib(factory=list)


class CycloneDxComponentType(str, Enum):
    APPLICATION = 'application'
    FRAMEWORK = 'framework'
    LIBRARY = 'library'
    CONTAINER = 'container'
    OPERATING_SYSTEM = 'operating-system'
    DEVICE = 'device'
    FIRMWARE = 'firmware'
    FILE = 'file'


class CycloneDxComponentScope(str, Enum):
    REQUIRED = 'required'
    OPTIONAL = 'optional'
    EXCLUDED = 'excluded'


@attr.s
class CycloneDxComponent:
    @classmethod
    def from_packages(cls, packages) -> List['CycloneDxComponent']:
        components_by_purl = {}
        components = []
        for package in packages:
            hashes = CycloneDxHashObject.from_package(package)
            refs = CycloneDxExternalRef.from_package(package)
            licenses = CycloneDxLicenseEntry.from_package(package)
            author = get_author_from_parties(package.get('parties'))
            purl = package.get('purl')

            name = package.get('name')
            version = package.get('version')
            # if we don't have at least the required name and version we skip the component
            if name is not None and version is not None:
                component = CycloneDxComponent(
                    name=package.get('name'),
                    version=package.get('version'),
                    group=package.get('namespace'),
                    purl=purl,
                    author=author,
                    copyright=package.get('copyright'),
                    description=package.get('description'),
                    hashes=hashes,
                    licenses=licenses,
                    externalReferences=refs,
                    bom_ref=purl,
                )

                # since it is used as a bom-ref the purl has to be unique, merge duplicates
                if purl not in components_by_purl.keys():
                    components.append(component)
                    components_by_purl[purl] = component
                else:
                    merge_components(components_by_purl[purl], component)

        return components


    def _add_license_refs(self):
        """
        Build CycloneDxExternalRef entries for scancode SPDX LicenseRefs
        Modify the component in-place
        """
        licenses = filter(None, map(lambda lic: lic.license, self.licenses))
        license_ids = map(lambda lic: lic.id, licenses)
        licenseref_ids = filter(
            lambda lic_id: lic_id is not None and lic_id.startswith("LicenseRef-scancode-"),
            license_ids
        )

        for licenseref_id in licenseref_ids:
            ref = CycloneDxExternalRef.from_licenseref_id(licenseref_id)
            if ref:
                self.externalReferences.append(ref)


    name: str = attr.ib()
    version: str = attr.ib()
    bom_ref: str = attr.ib(default=None)
    group: str = attr.ib(default=None)
    type: CycloneDxComponentType = attr.ib(default=CycloneDxComponentType.LIBRARY)
    scope: CycloneDxComponentScope = attr.ib(default=CycloneDxComponentScope.REQUIRED)
    copyright: str = attr.ib(default=None)
    author: str = attr.ib(default=None)
    description: str = attr.ib(default=None)
    purl: str = attr.ib(default=None)
    hashes: List[CycloneDxHashObject] = attr.ib(factory=list)
    licenses: List[CycloneDxLicenseEntry] = attr.ib(factory=list)
    externalReferences: List[CycloneDxExternalRef] = attr.ib(factory=list)
    properties: List[CycloneDxAttribute] = attr.ib(factory=list)


@attr.s
class CycloneDxDependency:
    ref: str = attr.ib()
    dependsOn: str = attr.ib(factory=list)


@attr.s
class CycloneDxBom:
    @classmethod
    def from_codebase(cls, codebase) -> 'CycloneDxBom':
        # we only retain the scancode-toolkit header in the CycloneDx output
        scancode_header = next(
            (h for h in codebase.get_headers() if h.get('tool_name') == 'scancode-toolkit')
        )

        scancode_version = scancode_header.get('tool_version')

        tool_header = get_tool_header(scancode_version)
        bom_metadata = CycloneDxMetadata(tools=[tool_header])

        files = OutputPlugin.get_files(codebase)

        # get all packages that are not None
        packages = [package for file in files for package in file.get('packages')]
        # associate dependency relationship by purl of dependent package
        dep_map = dict(
            [(package.get('purl'), package.get('dependencies')) for package in packages]
        )

        components = CycloneDxComponent.from_packages(packages)
        # associate components by purl
        componenty_by_purl = dict(map(lambda c: (c.purl, c), components))

        dependencies = generate_dependencies_list(dep_map, componenty_by_purl)

        bom = CycloneDxBom(
            components=components, metadata=bom_metadata, dependencies=dependencies
        )
        return bom

    bomFormat: str = attr.ib(init=False, default='CycloneDX')
    specVersion: str = attr.ib(init=False, default='1.3')
    serialNumber: str = attr.ib(init=False, default='urn:uuid:' + str(uuid.uuid4()))
    version: int = attr.ib(init=False, default=1)
    metadata: CycloneDxMetadata = attr.ib(default=CycloneDxMetadata())
    components: List[CycloneDxComponent] = attr.ib(factory=list)
    dependencies: List[CycloneDxDependency] = attr.ib(factory=list)


def get_tool_header(version: str) -> dict:
    return {'vendor': 'nexB Inc.', 'name': 'scancode-toolkit', 'version': version}


url_pattern = re.compile(r"^(https?://)?[^\s/$.?#].[^\s]*$")


# maps ScanCode URL attributes to CycloneDx external reference types
url_type_mapping = {
    'homepage_url': 'website',
    'download_url': 'distribution',
    'bug_tracking_url': 'issue-tracker',
    'code_view_url': 'other',
    'vcs_url': 'vcs',
    'repository_homepage_url': 'website',
    'repository_download_url': 'distribution',
    'api_data_url': 'bom',
}


def get_author_from_parties(parties: List[dict]) -> str:
    if parties is not None:
        # get all entries with role author and join their names
        authors = list(
            filter(
                lambda p: p.get('role') == 'author' and p.get('name') is not None, parties
            )
        )
        # only return joined string if there is at least one author
        if authors:
            return '\n'.join(
                map(lambda author: author.get("name"), authors)
            )
    return None



@output_impl
class CycloneDxOutput(OutputPlugin):
    """
    Output plugin to write scan results in CycloneDX JSOn format.
    For additional information on the format,
    please see https://cyclonedx.org/specification/overview/
    """

    options = [
        PluggableCommandLineOption(
            (
                '--cyclonedx',
                'output_cyclonedx_json',
            ),
            type=FileOptionType(mode='w', encoding='utf-8', lazy=True),
            metavar='FILE',
            help='Write scan output in CycloneDX JSON format to FILE.',
            help_group=OUTPUT_GROUP,
            sort_order=70,
        ),
    ]

    def is_enabled(self, output_cyclonedx_json, **kwargs):
        return output_cyclonedx_json

    def process_codebase(self, codebase, output_cyclonedx_json, **kwargs):
        bom = CycloneDxBom.from_codebase(codebase)
        write_results(bom, output_cyclonedx_json)


@output_impl
class CycloneDxXmlOutput(OutputPlugin):
    """
    Output plugin to write scan results in CycloneDX XML format.
    """

    options = [
        PluggableCommandLineOption(
            (
                '--cyclonedx-xml',
                'output_cyclonedx_xml',
            ),
            type=FileOptionType(mode='w', encoding='utf-8', lazy=True),
            metavar='FILE',
            help='Write scan output in CycloneDX XML format to FILE.',
            help_group=OUTPUT_GROUP,
            sort_order=70,
        ),
    ]

    def is_enabled(self, output_cyclonedx_xml, **kwargs):
        return output_cyclonedx_xml

    def process_codebase(self, codebase, output_cyclonedx_xml, **kwargs):
        bom = CycloneDxBom.from_codebase(codebase)
        write_results(bom, output_file=output_cyclonedx_xml, output_json=False)


def _get_dependency_candidate(dependency, candidates):
    if len(candidates) == 1:
        return list(candidates.values())[0]
    else:
        return None


def _set_key_or_append(dictionary: dict, key, value):
    if key in dictionary:
        dictionary[key].append(value)
    else:
        dictionary[key] = [value]


def generate_dependencies_list(dep_map, comp_map) -> List[CycloneDxDependency]:
    # return early if we have no components to operate on
    if len(comp_map) == 0:
        return None

    # holds a mapping of type purl -> list(purl)
    dependencies_by_dependant = {}

    resolved_scopes = {}

    for purl in dep_map:
        for dependency in dep_map[purl]:
            if dependency.get('is_resolved'):
                _set_key_or_append(
                    dependencies_by_dependant, purl, dependency.get('purl')
                )
            else:
                candidates = dict(
                    filter(
                        lambda item: item[0] and item[0].startswith(dependency['purl']),
                        comp_map.items(),
                    )
                )
                resolved_dependency = _get_dependency_candidate(dependency, candidates)
                if resolved_dependency is not None:
                    _set_key_or_append(
                        dependencies_by_dependant, purl, resolved_dependency.bom_ref
                    )
                    _set_key_or_append(
                        resolved_scopes, purl, dependency.get('is_optional')
                    )

    for purl in resolved_scopes:
        if all(resolved_scopes[purl]):
            comp_map[purl].scope = CycloneDxComponentScope.OPTIONAL

    return list(
        map(
            lambda entry: CycloneDxDependency(ref=entry[0], dependsOn=entry[1]),
            dependencies_by_dependant.items(),
        )
    )


def merge_components(existing: CycloneDxComponent, new: CycloneDxComponent):
    """
    Merges a new component with an existing component in-place
    First verify that both components have the same purl,
    raise an exception of type ValueError if they don't
    """

    if existing.purl != new.purl:
        raise ValueError("Merging is only allowed for components with identical purls!")

    # helper that merges lists avoiding duplicate entries
    merge_lists = lambda x, y: x.extend([item for item in y if item not in x])

    if existing.author is None:
        existing.author = new.author

    if existing.copyright is None:
        existing.copyright = new.author

    if existing.description is None:
        existing.description = new.description

    if existing.licenses is None:
        existing.licenses = new.licenses
    elif new.licenses is not None:
        merge_lists(existing.licenses, new.licenses)

    if existing.externalReferences is None:
        existing.externalReferences = new.externalReferences
    elif new.externalReferences is not None:
        merge_lists(existing.externalReferences, new.externalReferences)

    if existing.hashes is None:
        existing.hashes = new.hashes
    elif new.hashes is not None:
        merge_lists(existing.hashes, new.hashes)

    if existing.properties is None:
        existing.properties = new.properties
    elif new.properties is not None:
        merge_lists(existing.properties, new.properties)


def truncate_none_or_empty_values(obj) -> dict:
    """
    Return a new dict that no longer contains any keys which have values
    that are either None, empty list or empty dict associated with them
    """
    predicate = lambda el: not (
        el is None or (isinstance(el, list) or isinstance(el, dict)) and len(el) == 0
    )
    if hasattr(obj, '__dict__'):
        obj = vars(obj)
    obj_dict = {k: v for k, v in obj.items() if predicate(v)}
    return obj_dict


class CycloneDxEncoder(json.JSONEncoder):
    """
    Custom encoder that removes fields which are either empty or None.
    Additionally renames the `bom_ref` field to `bom-ref` for output
    """

    def default(self, o) -> str:
        dict_repr = truncate_none_or_empty_values(o)
        if "bom_ref" in dict_repr:
            dict_repr = {
                "bom-ref" if k == "bom_ref" else k: v for k, v in dict_repr.items()
            }
        return dict_repr


def write_results_json(bom, output_file):
    json.dump(bom, output_file, indent=2, sort_keys=False, cls=CycloneDxEncoder)


class XmlSerializer:
    def __init__(self, bom: CycloneDxBom):
        self.bom = bom

    def _add_text_element_if_not_none(
        self, parent: etree.Element, name: str, value: str
    ):
        # serialize enums by referencing their value
        if isinstance(value, Enum):
            value = value.value
        if value is not None:
            etree.SubElement(parent, name).text = value

    def _get_root_element(self) -> etree.Element:
        bom_element = etree.Element(
            'bom',
            {
                'xmlns': 'http://cyclonedx.org/schema/bom/1.3',
                'version': '1',
                'serialNumber': self.bom.serialNumber,
            },
        )
        return bom_element

    def _get_tool_element(self) -> etree.Element:
        tool = etree.Element('tool')
        bom_tool = self.bom.metadata.tools[0]
        etree.SubElement(tool, 'vendor').text = bom_tool['vendor']
        etree.SubElement(tool, 'name').text = bom_tool['name']
        etree.SubElement(tool, 'version').text = bom_tool['version']
        return tool

    def _get_hash_element(self, hash: CycloneDxHashObject):
        hash_el = etree.Element('hash', {'alg': hash.alg})
        hash_el.text = hash.content
        return hash_el

    def _get_external_ref(self, ref: CycloneDxExternalRef):
        ext_ref_el = etree.Element('reference', {'type': ref.type})
        self._add_text_element_if_not_none(ext_ref_el, 'url', ref.url)
        self._add_text_element_if_not_none(ext_ref_el, 'comment', ref.comment)
        if ref.hashes:
            hashes = etree.SubElement(ext_ref_el, 'hashes')
            for hash in component.hashes:
                hashes.append(self._get_hash_element(hash))
        return ext_ref_el

    def _get_component_element(self, component: CycloneDxComponent) -> etree.Element:
        # exit early if we don't at least have name, version and bom-ref
        if (
            component.bom_ref is None
            or component.name is None
            or component.version is None
        ):
            return None

        el = etree.Element(
            'component', {'type': component.type.value, 'bom-ref': component.bom_ref}
        )
        etree.SubElement(el, 'name').text = component.name
        etree.SubElement(el, 'version').text = component.version

        self._add_text_element_if_not_none(el, 'description', component.description)
        self._add_text_element_if_not_none(el, 'copyright', component.copyright)
        self._add_text_element_if_not_none(el, 'group', component.group)
        self._add_text_element_if_not_none(el, 'author', component.author)
        self._add_text_element_if_not_none(el, 'scope', component.scope)
        self._add_text_element_if_not_none(el, 'purl', component.purl)

        hashes = etree.SubElement(el, 'hashes')
        for hash in component.hashes:
            hashes.append(self._get_hash_element(hash))

        licenses = etree.SubElement(el, 'licenses')
        for license_entry in component.licenses:
            if license_entry.license is not None:
                lic = license_entry.license
                lic_el = etree.Element('license')
                if lic.id is not None:
                    self._add_text_element_if_not_none(lic_el, 'id', lic.id)
                else:
                    self._add_text_element_if_not_none(lic_el, 'name', lic.name)
                self._add_text_element_if_not_none(lic_el, 'url', lic.url)
                licenses.append(lic_el)
            elif license_entry.expression is not None:
                expr_el = etree.Element('expression')
                expr_el.text = license_entry.expression
                licenses.append(expr_el)

        ext_refs = etree.SubElement(el, 'externalReferences')
        for external_ref in iter(filter(None, component.externalReferences)):
            ext_refs.append(self._get_external_ref(external_ref))
        return el

    def _build_metadata_element(self, bom: etree.Element) -> etree.Element:
        metadata = etree.SubElement(bom, 'metadata')
        bom_metadata = self.bom.metadata
        etree.SubElement(metadata, 'timestamp').text = bom_metadata.timestamp
        tools = etree.SubElement(metadata, 'tools')
        tools.append(self._get_tool_element())
        return bom

    def _build_components_element(self, bom: etree.Element) -> etree.Element:
        components = etree.SubElement(bom, 'components')
        for component in self.bom.components:
            comp_el = self._get_component_element(component)
            if comp_el is not None:
                components.append(comp_el)
        return bom

    def _build_dependencies_element(self, bom: etree.Element) -> etree.Element:
        dependencies = self.bom.dependencies
        # exit early
        if dependencies is None:
            return bom

        deps = etree.SubElement(bom, 'dependencies')

        for dependency in self.bom.dependencies:
            if dependency.ref is None:
                continue
            dep_el = etree.Element('dependency', {'ref': dependency.ref})
            for entry in dependency.dependsOn:
                etree.SubElement(dep_el, 'dependency', {'ref': entry})
            deps.append(dep_el)
        return bom

    def get_serialized_output(self):
        root_element = self._get_root_element()
        root_element = self._build_metadata_element(root_element)
        root_element = self._build_components_element(root_element)
        root_element = self._build_dependencies_element(root_element)
        xml_metatag = '<?xml version="1.0" encoding="UTF-8"?>\n'
        return xml_metatag + etree.tostring(
            root_element, encoding='unicode', pretty_print=True
        )


def write_results_xml(bom, output_file):
    serializer = XmlSerializer(bom)
    output = serializer.get_serialized_output()
    output_file.write(output)


def write_results(bom, output_file, output_json: bool = True):
    close_fd = False
    if isinstance(output_file, str):
        output_file = open(output_file, 'w')
        close_fd = True
    if output_json:
        write_results_json(bom, output_file)
    else:
        write_results_xml(bom, output_file)
    if close_fd:
        output_file.close()
