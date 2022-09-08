# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import json
import logging
import uuid
from collections import defaultdict
from datetime import datetime
from enum import Enum
from typing import List
import warnings

import attr
from lxml import etree

from commoncode.cliutils import OUTPUT_GROUP
from commoncode.cliutils import PluggableCommandLineOption
from formattedcode import FileOptionType
from licensedcode.cache import build_spdx_license_expression
from plugincode.output import OutputPlugin
from plugincode.output import output_impl


TRACE = os.environ.get('SCANCODE_DEBUG_OUTPUTS', False)


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    import sys

    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))


class ToDictMixin:

    def to_dict(self):
        return attr.asdict(self)


@attr.s
class CycloneDxLicenseExpression(ToDictMixin):
    """
    An SPDX license expression.
    """
    expression: str = attr.ib(default=None)

    @classmethod
    def from_package(cls, package):
        """
        Yield CycloneDxLicenseExpression built from a mapping of ``package``
        data.
        """
        license_expression = package.get('license_expression')
        if license_expression:
            spdx = build_spdx_license_expression(license_expression)
            yield CycloneDxLicenseExpression(expression=spdx)


@attr.s
class CycloneDxProperty(ToDictMixin):
    """
    A name/value pair property
    """
    name: str = attr.ib()
    value: str = attr.ib()


@attr.s
class CycloneDxHashObject(ToDictMixin):
    """
    A hash (aka. checksum) with an identifying alg algorithm and a hex-encoded
    content string.
    """
    cdx_hash_types_by_scancode_field = {
        'md5': 'MD5',
        'sha1': 'SHA-1',
        'sha256': 'SHA-256',
        'sha512': 'SHA-512',
    }

    alg: str = attr.ib()
    content: str = attr.ib()

    @classmethod
    def from_package(cls, package):
        """
        Yield CycloneDxHashObject built from a mapping of ScanCode ``package``
        data.
        """
        for sc_alg, cdx_alg in cls.cdx_hash_types_by_scancode_field.items():
            digest = package.get(sc_alg)
            if digest:
                yield CycloneDxHashObject(alg=cdx_alg, content=digest)

    def to_xml_element(self):
        """
        Return a new Element built from this hash
        """
        hash_el = etree.Element('hash', {'alg': self.alg})
        hash_el.text = self.content
        return hash_el


@attr.s
class CycloneDxExternalRef(ToDictMixin):
    """
    External URL reference.
    """
    known_types = frozenset([
        'advisories',
        'bom',
        'build-meta',
        'build-system',
        'chat',
        'distribution',
        'documentation',
        'issue-tracker',
        'license',
        'mailing-list',
        'other',
        'social',
        'support',
        'vcs',
        'website',
    ])

    # map of ScanCode Package field names for various URLs to CycloneDx external
    # reference types
    cdx_url_type_by_scancode_field = {
        'api_data_url': 'bom',
        'bug_tracking_url': 'issue-tracker',
        'code_view_url': 'other',
        'download_url': 'distribution',
        'homepage_url': 'website',
        'repository_download_url': 'distribution',
        'repository_homepage_url': 'website',
        'vcs_url': 'vcs',
    }

    url: str = attr.ib()
    type: str = attr.ib(validator=attr.validators.in_(known_types))
    comment: str = attr.ib(default=None)
    hashes: List[CycloneDxHashObject] = attr.ib(factory=list)

    @classmethod
    def from_package(cls, package: dict):
        """
        Yield CycloneDxExternalRef from a mapping of ``package`` data.
        """
        for sc_key, cdx_type in cls.cdx_url_type_by_scancode_field.items():
            ref_url = package.get(sc_key)
            # TODO: Download URL come with hashes
            if ref_url:
                yield CycloneDxExternalRef(url=ref_url, type=cdx_type)

    @classmethod
    def from_license_expression(cls, license_expression):
        """
        Yield CycloneDxExternalRef for each SPDX LicenseRefs found in a ScanCode
        ``license_expression`` string.
        """
        if not license_expression:
            return

        from licensedcode.cache import get_licensing
        from scancode.api import SCANCODE_LICENSEDB_URL

        licensing = get_licensing()
        symbols = licensing.license_symbols(license_expression)
        symbols = [s for s in symbols if s.wrapped.spdx_license_key.startswith('LicenseRef')]
        for lic in symbols:
            l = lic.wrapped
            spdx_license_key = l.spdx_license_key
            if not spdx_license_key.startswith('LicenseRef'):
                continue
            scancode_key = l.key
            url = SCANCODE_LICENSEDB_URL.format(scancode_key)
            comment = f'Information about ScanCode SPDX LicenseRef: {spdx_license_key}'
            yield CycloneDxExternalRef(url=url, type='license', comment=comment)

    def to_xml_element(self):
        """
        Return a new Element built from this external reference
        """
        ext_ref_el = etree.Element('reference', {'type': self.type})
        add_text_element(ext_ref_el, 'url', self.url)
        add_text_element(ext_ref_el, 'comment', self.comment)
        if self.hashes:
            hashes = etree.SubElement(ext_ref_el, 'hashes')
            for h in self.hashes:
                hashes.append(h.to_xml_element())
        return ext_ref_el


class CycloneDxComponentType:
    APPLICATION = 'application'
    FRAMEWORK = 'framework'
    LIBRARY = 'library'
    CONTAINER = 'container'
    OPERATING_SYSTEM = 'operating-system'
    DEVICE = 'device'
    FIRMWARE = 'firmware'
    FILE = 'file'


class CycloneDxComponentScope:
    REQUIRED = 'required'
    OPTIONAL = 'optional'
    EXCLUDED = 'excluded'


@attr.s
class CycloneDxComponent:
    """
    A software component. This is mapped to a ScanCode Package.
    """
    name: str = attr.ib()
    version: str = attr.ib()
    bom_ref: str = attr.ib(default=None)
    group: str = attr.ib(default=None)
    purl: str = attr.ib(default=None)

    # FIXME: this mapping is not clear
    type: str = attr.ib(default=CycloneDxComponentType.LIBRARY, repr=False)

    # FIXME: this mapping is not clear
    scope: str = attr.ib(default=CycloneDxComponentScope.REQUIRED, repr=False)

    copyright: str = attr.ib(default=None, repr=False)
    author: str = attr.ib(default=None, repr=False)
    description: str = attr.ib(default=None, repr=False)

    hashes: List[CycloneDxHashObject] = attr.ib(factory=list, repr=False)
    licenses: List[CycloneDxLicenseExpression] = attr.ib(factory=list, repr=False)
    externalReferences: List[CycloneDxExternalRef] = attr.ib(factory=list, repr=False)
    properties: List[CycloneDxProperty] = attr.ib(factory=list, repr=False)

    def to_dict(self):
        """
        Return a mapping representing this component.
        """
        return {
            'name': self.name,
            'version': self.version,
            # note the kebab case
            'bom-ref': self.bom_ref,
            'group': self.group,
            'type': self.type,
            'scope': self.scope,
            'copyright': self.copyright,
            'author': self.author,
            'description': self.description,
            'purl': self.purl,
            'hashes': [h.to_dict() for h in self.hashes],
            'licenses': [l.to_dict() for l in self.licenses],
            'externalReferences': [e.to_dict() for e in self.externalReferences],
            'properties': [p.to_dict() for p in self.properties],
        }

    @classmethod
    def from_package(cls, package):
        """
        Return a CycloneDxComponent built from a ``package`` mapping of ScanCode
        package data.
        """
        name = package.get('name')
        version = package.get('version')

        # FIXME: if we don't have at least the required name and version we skip
        # the component
        properties = []
        if not (name and version):
            properties.append(
                CycloneDxProperty(
                    name='WARNING',
                    value=f'WARNING: component skipped in CycloneDX output: {package!r}'
                )
            )

        purl = package.get('purl')

        return cls(
            bom_ref=purl,
            purl=purl,
            name=name,
            version=version,
            group=package.get('namespace'),
            author=get_author_from_parties(package.get('parties')),
            copyright=package.get('copyright'),
            description=package.get('description'),
            hashes=list(CycloneDxHashObject.from_package(package)),
            licenses=list(CycloneDxLicenseExpression.from_package(package)),
            externalReferences=list(CycloneDxExternalRef.from_package(package)),
            properties=properties,
        )

    @classmethod
    def from_packages(cls, packages):
        """
        Yield CycloneDxComponent built from a ``packages`` list of mapping of
        ScanCode ``package`` data. CycloneDxComponent are unique based on their
        ``purl``. CycloneDxComponent with the same pul are "merged" together.

        Note: since purl is used as a bom-ref here, the purl has to be unique in
        a given BOM.
        """
        components_by_purl = defaultdict(list)
        for package in packages:
            comp = cls.from_package(package)
            if not comp:
                continue
            components_by_purl[comp.purl].append(comp)

        for components in components_by_purl.values():
            base_component = components[0]
            if len(components) == 1 :
                yield base_component
                continue

            other_components = components[1:]
            for other_component in other_components:
                base_component.merge(other_component)

            yield base_component

    def merge(self, other):
        """
        Merge an ``other`` CycloneDxComponent in this component.

        Raise a ValueError if components do not have the same purl.
        Merging does either:
        - append ``other`` values avoiding duplicates for list fields
        - if field is empty, set value to ``other `` value for other field types.
        """
        if self.purl != other.purl:
            raise ValueError(
                f'Merging is only allowed for components with identical purls: '
                f'self: {self!r}, other: {other!r}'
            )

        if not self.author:
            self.author = other.author

        if not self.copyright:
            self.copyright = other.author

        if not self.description:
            self.description = other.description

        if not self.licenses:
            self.licenses = other.licenses
        elif other.licenses:
            merge_lists(self.licenses, other.licenses)

        if not self.externalReferences:
            self.externalReferences = other.externalReferences
        elif other.externalReferences:
            merge_lists(self.externalReferences, other.externalReferences)

        if not self.hashes:
            self.hashes = other.hashes
        elif other.hashes:
            merge_lists(self.hashes, other.hashes)

        if not self.properties:
            self.properties = other.properties
        elif not other.properties:
            merge_lists(self.properties, other.properties)

    def to_xml_element(self):
        """
        Return a new Element built from this component
        """
        comp = etree.Element(
            'component',
            {'type': self.type, 'bom-ref': self.bom_ref}
        )
        etree.SubElement(comp, 'name').text = self.name
        etree.SubElement(comp, 'version').text = self.version

        add_text_element(comp, 'description', self.description)
        add_text_element(comp, 'copyright', self.copyright)
        add_text_element(comp, 'group', self.group)
        add_text_element(comp, 'author', self.author)
        add_text_element(comp, 'scope', self.scope)
        add_text_element(comp, 'purl', self.purl)

        if self.hashes:
            hashes = etree.SubElement(comp, 'hashes')
            for h in self.hashes:
                hashes.append(h.to_xml_element())

        if self.licenses:
            licenses = etree.SubElement(comp, 'licenses')
            for license_entry in self.licenses:
                if license_entry.expression:
                    expr_el = etree.Element('expression')
                    expr_el.text = license_entry.expression
                    licenses.append(expr_el)

        if self.externalReferences:
            ext_refs = etree.SubElement(comp, 'externalReferences')
            for external_ref in self.externalReferences:
                ext_refs.append(external_ref.to_xml_element())

        return comp


def merge_lists(x, y):
    """
    Merge ``y`` list items in list ``x`` avoiding duplicate entries.
    Return the updated ``x``.
    """
    seen = set(x)
    new = (i for i in y if i not in seen)
    x.extend(new)
    return x


def get_author_from_parties(parties):
    """
    Return an author string built from a ``parties`` list of party mappings, or
    None.
    """
    if not parties:
        return

    # get all entries with role author and join their names
    authors = [a['name']  for a in parties if a['role'] == 'author']
    authors = '\n'.join(a for a in authors if a)
    return authors or None


@attr.s
class CycloneDxDependency(ToDictMixin):
    """
    A dependency characterized by a ``ref`` purl that ``dependsOn`` a list
    of purls.
    """
    ref: str = attr.ib()
    dependsOn: str = attr.ib(factory=list)
    warnings: List[str] = attr.ib(factory=list, repr=False)

    def to_dict(self):
        return dict(ref=self.ref, dependsOn=self.dependsOn)

    @classmethod
    def from_packages(cls, packages, components):
        """
        Yield unique CycloneDxDependency built from a ``packages`` list of
        ScanCode package data mapping and a ``components_by_purl`` mapping of
        existing CycloneDxComponent by purl.
        """
        componenty_by_purl = {c.purl: c for c in components}
        seen = set()
        for package in packages:
            for dep in cls.from_package(package, componenty_by_purl):
                if dep.ref not in seen:
                    yield dep
                    seen.add(dep.ref)

    @classmethod
    def from_package(cls, package, components_by_purl):
        """
        Yield CycloneDxDependency built from a ``package`` ScanCode
        package data mapping and a ``components_by_purl`` mapping of existing
        CycloneDxComponent by purl.
        ATTENTION: unresolved dependencies ARE SKIPPED.
        """
        purl = package['purl']

        # FIXME: also handle dependency scopes: CycloneDX track scopes at the
        # component level which is problematic. For instance, it is possible to
        # a multiple instances of the same Package (and purl) where some are
        # optional and some not optional in some contexts or some used in dev
        # and some runtime. The scope is therefore a dependency-level attribute
        # and not a Package/component attribute

        # holds a mapping of purl -> list(purl)
        dependencies_by_dependent = defaultdict(set)

        # ist of error messages for a given "ref"
        warnings_by_dependent = defaultdict(list)

        for dependency in package.get('dependencies', []):
            dpurl = dependency['purl']

            if dependency['is_resolved']:
                dependencies_by_dependent[purl].add(dpurl)
            else:
                existing = components_by_purl.get(dpurl)
                if existing:
                    dependencies_by_dependent[purl].add(dpurl)
                else:
                    # FIXME: the format cannot cope with unresolved deps since
                    # version is a mandatory for Component AND resolving is not
                    # an easy task
                    msg = (
                        f'WARNING: unresolved dependency: {dpurl} of {purl} '
                        'is skipped in CycloneDX output!'
                    )
                    warnings_by_dependent[purl].append(msg)

        for ref, dependsOn in dependencies_by_dependent.items():
            yield cls(
                ref=ref,
                dependsOn=dependsOn,
                warnings=warnings_by_dependent.get(purl, [])
            )

    def to_xml_element(self):
        """
        Return a new Element built from this dependency or None
        """
        dep_el = etree.Element('dependency', {'ref': self.ref})
        for entry in self.dependsOn:
            etree.SubElement(dep_el, 'dependency', {'ref': entry})
        return dep_el


def get_uuid_urn():
    """
    Return a new UUID URN
    """
    return f'urn:uuid:{uuid.uuid4()}'


def get_ts():
    """
    Return a non-timezone aware UTC timestamp string.
    """
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')


@attr.s
class CycloneDxMetadata:
    """
    BOM metadata.
    """
    timestamp = attr.ib(factory=get_ts)
    tools: List[dict] = attr.ib(factory=list)
    properties: List[CycloneDxProperty] = attr.ib(factory=list)

    def to_dict(self):
        properties = (p.to_dict() for p in self.properties)
        properties = [p for p in properties if p]
        return dict(
            timestamp=self.timestamp,
            tools=self.tools,
            properties=properties,
        )

    @classmethod
    def from_headers(cls, headers):
        """
        Return a CycloneDxMetadata built from a ``headers`` list of
        ScanCode codebase header mappings.
        """
        # FIXME: is this correct? we only retain the scancode-toolkit header in
        # the CycloneDx output
        headers = [h for h in headers if h.get('tool_name') == 'scancode-toolkit']
        scancode_header = headers[0] if headers else {}

        if TRACE:
            logger_debug('CycloneDxMetadata: headers')
            from pprint import pformat
            logger_debug(pformat(headers))

        try:
            tool_header = {
                'vendor': 'AboutCode.org',
                'name': 'scancode-toolkit',
                'version': scancode_header['tool_version'],
            }
        except KeyError:
            raise Exception(scancode_header)

        props = dict(
            notice=scancode_header.get('notice'),
            errors=scancode_header.get('errors', []),
            warnings=scancode_header.get('warnings', []),
            message=scancode_header.get('message'),
        )
        props.update(scancode_header.get('extra_data', {}))
        properties = [CycloneDxProperty(k, v) for k, v in props.items()]

        if TRACE:
            logger_debug('CycloneDxMetadata: properties')
            from pprint import pformat
            logger_debug(pformat(properties))

        return CycloneDxMetadata(
            tools=[tool_header],
            properties=properties,
        )

    def to_xml_element(self):
        """
        Return an Element for this metadata.
        """
        xmetadata = etree.Element('metadata')
        etree.SubElement(xmetadata, 'timestamp').text = self.timestamp

        tool = etree.Element('tool')
        bom_tool = self.tools[0]
        etree.SubElement(tool, 'vendor').text = bom_tool['vendor']
        etree.SubElement(tool, 'name').text = bom_tool['name']
        etree.SubElement(tool, 'version').text = bom_tool['version']

        tools = etree.SubElement(xmetadata, 'tools')
        tools.append(tool)
        return xmetadata


class CycloneDxPluginNoPackagesWarning(DeprecationWarning):
    pass


@attr.s
class CycloneDxBom:
    """
    Represent a CycloneDX BOM
    """
    bomFormat = 'CycloneDX'
    specVersion = '1.3'

    serialNumber: str = attr.ib(factory=get_uuid_urn)
    version: int = attr.ib(default=1)
    metadata: CycloneDxMetadata = attr.ib(factory=CycloneDxMetadata)
    components: List[CycloneDxComponent] = attr.ib(factory=list)
    dependencies: List[CycloneDxDependency] = attr.ib(factory=list)

    def to_dict(self):
        """
        Return a mapping representing this object.
        """
        return dict(
            bomFormat=self.bomFormat,
            specVersion=self.specVersion,
            serialNumber=self.serialNumber,
            version=self.version,
            metadata=self.metadata.to_dict(),
            components=[c.to_dict() for c in self.components],
            dependencies=[d.to_dict() for d in self.dependencies],
        )

    @classmethod
    def from_codebase(cls, codebase):
        """
        Return a CycloneDxBom built from a ScanCode ``codebase``.
        """
        components = []
        dependencies = []

        packages_not_found_message = (
            "The --cyclonedx-xml option will not output any component/dependency data "
            "as there are no package data in the present scan. To get package data "
            "please rerun the scan with --package or --system-package CLI options enabled."
        )
        codebase.get_or_create_current_header()

        if hasattr(codebase.attributes, 'packages'):
            packages = codebase.attributes.packages
            components = list(CycloneDxComponent.from_packages(packages))
            dependencies = list(CycloneDxDependency.from_packages(packages, components))
        else:
            warnings.simplefilter('always', CycloneDxPluginNoPackagesWarning)
            warnings.warn(
                packages_not_found_message,
                CycloneDxPluginNoPackagesWarning,
                stacklevel=2,
            )
            headers = codebase.get_or_create_current_header()
            headers.warnings.append(packages_not_found_message)

        codebase_headers = codebase.get_headers()
        metadata = CycloneDxMetadata.from_headers(codebase_headers)

        return CycloneDxBom(
            metadata=metadata,
            components=components,
            dependencies=dependencies,
        )

    def to_json(self):
        """
        Return a JSON string for this bom
        """
        return json.dumps(self.to_dict(), indent=2, sort_keys=False)

    def to_xml(self):
        """
        Return an XML string for this bom
        """
        xbom = etree.Element(
            'bom',
            {
                'xmlns': 'http://cyclonedx.org/schema/bom/1.3',
                'version': '1',
                'serialNumber': self.serialNumber,
            },
        )

        xbom.append(self.metadata.to_xml_element())

        xcomponents = etree.SubElement(xbom, 'components')
        for component in self.components:
            # FIXME: skip if we don't at least have name, version and bom-ref
            # these are required by CycloeDX
            if not any([component.bom_ref, component.name, component.version]):
                print(f'WARNING: component skipped in CycloneDX output: {self!r}')
            else:
                xcomponents.append(component.to_xml_element())

        if self.dependencies:
            xdeps = etree.SubElement(xbom, 'dependencies')
            for dependency in self.dependencies:
                xdeps.append(dependency.to_xml_element())

        et = etree.tostring(xbom, encoding='unicode', pretty_print=True)
        return f'<?xml version="1.0" encoding="UTF-8"?>\n{et}'

    def write_json(self, output_file):
        """
        Write this bom as JSON to the ``output_file`` file-like object or path string.
        """
        return self._write(self.to_json(), output_file)

    def write_xml(self, output_file):
        """
        Write this bom as XML to the ``output_file`` file-like object or path string.
        """
        return self._write(self.to_xml(), output_file)

    def _write(self, content, output_file):
        """
        Write the ``content`` string to to the ``output_file`` file-like object
        or path string.
        """
        close_fd = False
        try:
            if isinstance(output_file, str):
                output_file = open(output_file, 'w')
                close_fd = True
            output_file.write(content)
        finally:
            if close_fd:
                output_file.close()


@output_impl
class CycloneDxJsonOutput(OutputPlugin):
    """
    Output plugin to write scan results in CycloneDX JSON format.
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
        bom.write_json(output_file=output_cyclonedx_json)


@output_impl
class CycloneDxXmlOutput(OutputPlugin):
    """
    Output plugin to write scan results in CycloneDX XML format.
    For additional information on the format,
    please see https://cyclonedx.org/specification/overview/
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
        bom.write_xml(output_file=output_cyclonedx_xml)


def add_text_element(parent: etree.Element, name: str, value: str):
    """
    Add a new text sub element to the ``parent`` Element using ``name`` with
    ``value`` as text. Return parent. Do nothing if the ``value`` is empty.
    """
    if isinstance(value, Enum):
        # serialize enums by referencing their value
        value = value.value

    if value:
        etree.SubElement(parent, name).text = value

    return parent
