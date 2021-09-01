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
from typing import List,FrozenSet
from plugincode.output import output_impl
from plugincode.output import OutputPlugin
import uuid


def _get_list_of_known_spdx_license_ids() -> FrozenSet[str]:
    """load all SPDX Ids known to ScanCode
       this will also load scancode licenserefs, so we filter those
    """
    from licensedcode.models import get_all_spdx_keys, load_licenses
    spdx_keys = filter(lambda x: "LicenseRef" not in x,
                       get_all_spdx_keys(load_licenses(with_deprecated=True)))
    return frozenset(spdx_keys)

spdx_ids = _get_list_of_known_spdx_license_ids()

hash_type_mapping = {
    'md5': 'MD5',
    'sha1': 'SHA-1',
    'sha256': 'SHA-256',
    'sha512': 'SHA-512',
}


class CycloneDxFlavor(Enum):
    XML = 0
    JSON = 1

@attr.s
class CycloneDxLicense:
    id: str = attr.ib(default=None)
    name: str = attr.ib(default=None)
    url: str = attr.ib(default=None)

@attr.s
class CycloneDxLicenseEntry:
    license: CycloneDxLicense = attr.ib()
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
    group: str = attr.ib()
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

def get_external_ref_from_key(package: dict, key: str) -> CycloneDxExternalRef:
    url = package.get(key)
    type = url_type_mapping[key]
    if url is not None and type is not None:
        return CycloneDxExternalRef(url=url, type=type)
    return None

url_pattern = re.compile(r"^(https?://)?[^\s/$.?#].[^\s]*$")

def get_licenses(package: dict)->List[CycloneDxLicenseEntry]:
    licenses = [CycloneDxLicenseEntry(None, package.get("license_expression"))]
    declared_license = package["declared_license"]
    if isinstance(declared_license, list):
        for entry in declared_license:
            click.echo(entry)
            if isinstance(entry, str):
                lic = CycloneDxLicense()
                # if our license key is in our list of known spdx ids, set as id
                if entry in spdx_ids:
                    lic.id = entry
                # if we match this regex it is safe to assume we are dealing with a URL
                elif entry is not None and url_pattern.match(entry):
                    lic.url = entry
                else:
                    lic.name = entry
                licenses.append(CycloneDxLicenseEntry(license=lic))
    return licenses


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


"""
Output plugin to write scan results in CycloneDX format.
For additional information on the format,
please see https://cyclonedx.org/specification/overview/
"""
@ output_impl
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
        return super().process_codebase(codebase, output_cyclonedx, **kwargs)


@ output_impl
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
        write_results(bom, output_file=output_cyclonedx_json,
                      cyclonedx_flavor=CycloneDxFlavor.JSON, **kwargs)


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

def write_results(bom, output_file, cyclonedx_flavor: CycloneDxFlavor, **kwargs):

    close_fd = False
    if isinstance(output_file, str):
        output_file = open(output_file, 'w')
        close_fd = True

    json.dump(bom, output_file, default=truncate_none_or_empty_values)


def generate_component_list(codebase, **kwargs) -> List[CycloneDxComponent]:
    files = OutputPlugin.get_files(codebase, **kwargs)
    components = []
    for file in files:
        for package in file.get("packages", []):
            hashes = get_hashes_list(package)
            refs = get_external_refs(package)
            licenses = get_licenses(package)

            components.append(CycloneDxComponent(
                name=package.get("name"), version=package.get("version"),
                group=package.get("namespace"), purl=package.get("purl"),
                description=package.get("description"),
                hashes=hashes, licenses=licenses, externalReferences=refs))
    return components
