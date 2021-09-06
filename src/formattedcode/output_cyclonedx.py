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
from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import OUTPUT_GROUP
from datetime import datetime
from enum import Enum
from formattedcode import FileOptionType
import json
import re
from typing import FrozenSet, List, Tuple
from plugincode.output import output_impl
from plugincode.output import OutputPlugin
import uuid


def _get_set_of_known_licenses_and_spdx_license_ids() -> Tuple[List, FrozenSet[str]]:
    """load all licenses and all SPDX Ids known to ScanCode
       this will also load scancode licenserefs, so we filter those
    """
    from licensedcode.models import get_all_spdx_keys, load_licenses
    licenses = load_licenses(with_deprecated=True)
    spdx_keys = filter(lambda x: "LicenseRef" not in x,
                       get_all_spdx_keys(licenses))
    return (licenses, frozenset(spdx_keys))

known_licenses, spdx_ids = _get_set_of_known_licenses_and_spdx_license_ids()

hash_type_mapping = {
    'md5': 'MD5',
    'sha1': 'SHA-1',
    'sha256': 'SHA-256',
    'sha512': 'SHA-512',
}

@attr.s
class CycloneDxLicense:
    id: str = attr.ib(default=None)
    name: str = attr.ib(default=None)
    url: str = attr.ib(default=None)

@attr.s
class CycloneDxLicenseEntry:
    license: CycloneDxLicense = attr.ib(default=None)
    expression: str = attr.ib(default=None)

@attr.s
class CycloneDxAttribute:
    name: str = attr.ib()
    value: str = attr.ib()

@attr.s
class CycloneDxMetadata():
    timestamp = attr.ib(
        default=datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
    tools: List[dict] = attr.ib(factory=list)
    properties: List[CycloneDxAttribute] = attr.ib(factory=list)

@attr.s
class CycloneDxHashObject():
    alg: str = attr.ib()
    content: str = attr.ib()

@attr.s
class CycloneDxExternalRef:
    url: str = attr.ib()
    type: str = attr.ib(validator=attr.validators.in_(["vcs", "issue-tracker","website",
                                                       "advisories", "bom", "mailing-list", "social", "chat",
                                                       "documentation", "support", "distribution", "license",
                                                       "build-meta", "build-system", "other"]))
    comment: str = attr.ib(default=None)
    hashes: List[CycloneDxHashObject] = attr.ib(factory=list)


class CycloneDxComponentType(str, Enum):
    APPLICATION = "application"
    FRAMEWORK = "framework"
    LIBRARY = "library"
    CONTAINER = "container"
    OPERATING_SYSTEM = "operating-system"
    DEVICE = "device"
    FIRMWARE = "firmware"
    FILE = "file"

@attr.s
class CycloneDxComponent():
    name: str = attr.ib()
    version: str = attr.ib()
    bom_ref: str = attr.ib(default=None)
    group: str = attr.ib(default=None)
    copyright: str = attr.ib(default=None)
    author: str = attr.ib(default=None)
    description: str = attr.ib(default=None)
    purl: str = attr.ib(default=None)
    hashes: List[CycloneDxHashObject] = attr.ib(factory=list)
    licenses: List[CycloneDxLicenseEntry] = attr.ib(factory=list)
    externalReferences: List[CycloneDxExternalRef] = attr.ib(factory=list)
    type: CycloneDxComponentType = attr.ib(
        default=CycloneDxComponentType.LIBRARY)
    properties: List[CycloneDxAttribute] = attr.ib(factory=list)

@attr.s
class CycloneDxBom():
    bomFormat: str = attr.ib(init=False, default="CycloneDX")
    specVersion: str = attr.ib(init=False, default="1.3")
    serialNumber: str = attr.ib(
        init=False, default="urn:uuid:" + str(uuid.uuid4()))
    version: int = attr.ib(init=False, default=1)
    metadata: CycloneDxMetadata = attr.ib(default=CycloneDxMetadata())
    components: List[CycloneDxComponent] = attr.ib(factory=list)

def get_tool_header(version: str) -> dict:
    return {
        "vendor": "nexB Inc.",
        "name": "scancode-toolkit",
        "version": version
    }

def get_external_ref_from_key(package: dict, key: str) -> CycloneDxExternalRef:
    url = package.get(key)
    type = url_type_mapping[key]
    if url is not None and type is not None:
        return CycloneDxExternalRef(url=url, type=type)
    return None

def get_license_entry_from_license_expression(license_expression: str) \
        -> CycloneDxLicenseEntry:
    """query our list of known licenses to see if we can resolve
    the license_expression to a single entry"""
    license = known_licenses.get(license_expression)
    if license is not None:
        #attempt to set either official OSI URL or any license text URL
        url = license.osi_url
        if license.text_urls:
            url = license.text_urls[0]
        lic = CycloneDxLicense(id=license.spdx_license_key,
                               name=license.name,
                               url = url)
        return CycloneDxLicenseEntry(license=lic, expression=None)
    else:
        return CycloneDxLicenseEntry(license=None, expression=license_expression)

url_pattern = re.compile(r"^(https?://)?[^\s/$.?#].[^\s]*$")


def get_license_entry_from_declared_license(declared_license) \
    -> CycloneDxLicenseEntry:
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
        lic_type = declared_license.get("type")
        if lic_type in spdx_ids:
            lic.id = lic_type
        else:
            lic.name = lic_type
        lic.url = declared_license.get("url")
    return CycloneDxLicenseEntry(license=lic, expression=None)

def get_licenses(package: dict)->List[CycloneDxLicenseEntry]:
    """map all license data for a package entry to
    a list of CycloneDX Licenses"""
    #store previously encountered IDs to identify duplicates
    seen_ids = set()

    lic_expr = package.get("license_expression")
    entry = get_license_entry_from_license_expression(lic_expr)
    if entry.license is not None:
        seen_ids.add(entry.license.id)
    licenses = [entry]

    declared_license = package["declared_license"]
    if isinstance(declared_license, list):
        for entry in declared_license:
            lic_entry = get_license_entry_from_declared_license(entry)
            id = lic_entry.license.id if lic_entry.license is not None else None
            if id in seen_ids:
                continue
            else:
                seen_ids.add(id)
                licenses.append(lic_entry)
    else:
        lic_entry = get_license_entry_from_declared_license(declared_license)
        id = lic_entry.license.id if lic_entry.license is not None else None
        if id not in seen_ids:
            seen_ids.add(id)
            licenses.append(lic_entry)

    return licenses

#maps ScanCode URL attributes to CycloneDx external reference types
url_type_mapping = {
    "homepage_url": "website",
    "download_url": "distribution",
    "bug_tracking_url": "issue-tracker",
    "code_view_url": "other",
    "vcs_url": "vcs",
    "repository_homepage_url": "website",
    "repository_download_url": "distribution",
    "api_data_url": "bom"
}


def get_external_refs(package: dict)->List[CycloneDxExternalRef]:
    ext_refs = []

    for key in url_type_mapping:
        ref = get_external_ref_from_key(package, key)
        if ref is not None:
            ext_refs.append(ref)
    return ext_refs


def get_hashes_list(package: dict) -> List[CycloneDxHashObject]:
    hashes = []
    for alg in hash_type_mapping:
        if alg in package:
            digest = package[alg]
            if alg is not None and digest is not None:
                hashes.append(CycloneDxHashObject(
                    hash_type_mapping[alg], digest))
    return hashes


def get_author_from_parties(parties: List[dict]) -> str:
    if parties is not None:
        try:
            # assume there can only ever be one author and get that with next()
            author = next(filter(lambda p: p.get("role")=="author" ,parties))
            return ' '.join(filter(None, (author.get("name"),
                                          author.get("email"),
                                          author.get("url"))))
        except StopIteration:
            return None


"""
Output plugin to write scan results in CycloneDX format.
For additional information on the format,
please see https://cyclonedx.org/specification/overview/
"""
@output_impl
class CycloneDxOutput(OutputPlugin):
    options = [
        PluggableCommandLineOption(('--cyclonedx', 'output_cyclonedx',),
                                   type=FileOptionType(
                                       mode='w', encoding='utf-8', lazy=True),
                                   metavar='FILE',
                                   help='Write scan output in CycloneDX format to FILE.',
                                   help_group=OUTPUT_GROUP,
                                   sort_order=70),
    ]

    def is_enabled(self, output_cyclonedx, **kwargs):
        return output_cyclonedx

    def process_codebase(self, codebase, output_cyclonedx, **kwargs):
        bom = build_bom(codebase)
        write_results(bom, output_cyclonedx, output_json=False)


@output_impl
class CycloneDxJsonOutput(OutputPlugin):
    options = [
        PluggableCommandLineOption(('--cyclonedx-json', 'output_cyclonedx_json',),
                                   type=FileOptionType(
                                       mode='w', encoding='utf-8', lazy=True),
                                   metavar='FILE',
                                   help='Write scan output in CycloneDX JSON format to FILE.',
                                   help_group=OUTPUT_GROUP,
                                   sort_order=70),
    ]

    def is_enabled(self, output_cyclonedx_json, **kwargs):
        return output_cyclonedx_json

    def process_codebase(self, codebase, output_cyclonedx_json, **kwargs):
        bom = build_bom(codebase)
        write_results(bom, output_file=output_cyclonedx_json)


def build_bom(codebase) -> CycloneDxBom:
    # TODO: find out if we can always expect that header to be present
    scancode_header = codebase.get_headers()[0]

    scancode_version = scancode_header.get("tool_version")

    tool_header = get_tool_header(scancode_version)
    bom_metadata = CycloneDxMetadata(tools=[tool_header])
    bom = CycloneDxBom(components=generate_component_list(
        codebase), metadata=bom_metadata)

    return bom


def truncate_none_or_empty_values(obj) -> dict:
    """gets a dict from an object and drops all items
     that have keys which are either None or an empty list """
    predicate = lambda el: not (el is None or isinstance(el, list) and len(el)==0)
    obj_dict = { k : v for k,v in vars(obj).items() if predicate(v) }
    return obj_dict


class CycloneDxEncoder(json.JSONEncoder):
    """Custom encoder that removes fields which are either empty or None.
       Additionally renames the `bom_ref` field to `bom-ref` for output"""
    def default(self, o) -> str:
        dict_repr = truncate_none_or_empty_values(o)
        if "bom_ref" in dict_repr:
            dict_repr["bom-ref"] = dict_repr["bom_ref"]
            del dict_repr["bom_ref"]
        return dict_repr


def write_results_json(bom, output_file):
    json.dump(bom, output_file, sort_keys=False, cls=CycloneDxEncoder)


def write_results_xml(bom, output_file):
    """TODO: map to xml"""
    pass


def write_results(bom, output_file, output_json: bool = True):
    close_fd = False
    if isinstance(output_file, str):
        output_file = open(output_file, 'w')
        close_fd = True
    if output_json:
        write_results_json(bom, output_file)
    else:
        write_results_xml(bom, output_file)

def generate_component_list(codebase, **kwargs) -> List[CycloneDxComponent]:
    files = OutputPlugin.get_files(codebase, **kwargs)
    components = []
    for file in files:
        for package in file.get("packages", []):
            hashes = get_hashes_list(package)
            refs = get_external_refs(package)
            licenses = get_licenses(package)
            author = get_author_from_parties(package.get("parties"))
            purl = package.get("purl")
            components.append(CycloneDxComponent(
                name=package.get("name"), version=package.get("version"),
                group=package.get("namespace"), purl=purl,
                author=author, copyright=package.get("copyright"),
                description=package.get("description"),
                hashes=hashes, licenses=licenses, externalReferences=refs,
                bom_ref= purl))
    return components
