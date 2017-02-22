#
# Copyright (c) 2016 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import, print_function

from functools import partial
from itertools import izip_longest
import logging
import os.path
from os.path import dirname
from os.path import join
import re

from commoncode import filetype
from commoncode import fileutils
from typecode import contenttype

from packagedcode import xmlutils
from packagedcode import models


logger = logging.getLogger(__name__)
# import sys
# logging.basicConfig(stream=sys.stdout)
# logger.setLevel(logging.DEBUG)


"""
Support Maven POMs including older versions.
Attempts to resolve some Maven properties when possible.
"""

# FIXME: use Maven Java code directly or pymaven instead. The parsing done here is rather weird.
# the only part that is somewheta interesting short of using the original Maven parser is the properties resolution

# FIXME: Maven 1 is an oddity and the code should cleaned to deal separately with each version
# or Maven1 support dropped entirely



class MavenJar(models.JavaJar):
    metafiles = ('META-INF/**/*.pom', 'pom.xml',)
    repo_types = (models.repo_maven,)

    type = models.StringType(default='Apache Maven')

    @classmethod
    def recognize(cls, location):
        return parse(location)


# Maven1 field name -> xpath
MAVEN1_FIELDS = [
    ('component_extend_1', '/project/extend'),
    ('component_current_version_1', '/project/currentVersion'),
    ('distribution_management_site_1', '/project/distributionSite'),
    ('distribution_management_directory_1', '/project/distributionDirectory'),
    ('project_short_description_1', '/project/shortDescription'),
    ('repository_url_1', '/project/repository/url'),
    ('repository_connection_1', '/project/repository/connection'),
    ('repository_developer_connection_1', '/project/repository/developerConnection'),
]


# Maven2 field name -> xpath
MAVEN2_FIELDS = [
    ('component_artifact_id', '/project/artifactId'),
    ('component_classifier', '/project/classifier'),
    ('component_group_id', '/project/groupId'),
    ('component_parent_group_id', '/project/parent/groupId'),
    ('component_parent_version', '/project/parent/version'),
    ('component_packaging', '/project/packaging'),
    ('component_version', '/project/version'),

    ('developer_email', '/project/developers/developer/email'),
    ('developer_name', '/project/developers/developer/name'),
    ('developer_organization', '/project/developers/developer/organization'),

    ('contributor_email', '/project/contributors/contributor/email'),
    ('contributor_name', '/project/contributors/contributor/name'),
    ('contributor_organization', '/project/contributors/contributor/organization'),

    ('distribution_management_site_url', '/project/distributionManagement/site/url'),
    ('distribution_management_repository_url','/project/distributionManagement/repository/url'),

    ('license', '/project/licenses/license/name'),
    ('license_comments', '/project/licenses/license/comments'),
    ('license_distribution', '/project/licenses/license/distribution'),
    ('license_name', '/project/licenses/license/name'),
    ('license_url', '/project/licenses/license/url'),

    ('organization_name', '/project/organization/name'),
    ('organization_url', '/project/organization/url'),

    ('issue_url', '/project/issueManagement/url'),

    ('project_name', '/project/name'),
    ('project_description', '/project/description'),
    ('project_inception_year', '/project/inceptionYear'),
    ('project_url', '/project/url'),

    ('repository_id', '/project/repositories/repository/id'),
    ('repository_layout', '/project/repositories/repository/layout'),
    ('repository_name', '/project/repositories/repository/name'),
    ('repository_url', '/project/repositories/repository/url'),

    ('scm_connection', '/project/scm/connection'),
    ('scm_developer_connection', '/project/scm/developerConnection'),
    ('scm_url', '/project/scm/url'),

    ('distribution_management_group_id', '/project/distributionManagement/relocation/groupId'),
    ('model_version', '/project/modelVersion'),

    ('dependency', '/project/dependencies/dependency/artifactId'),
    ('dependency_version', '/project/dependencies/dependency/version'),
    ('dependency_scope', '/project/dependencies/dependency/artifactId/scope'),
]


MAVEN_FIELDS = [('maven_' + key, xmlutils.namespace_unaware(xpath)) for key, xpath in (MAVEN2_FIELDS + MAVEN1_FIELDS)]


# Common Maven property keys and corresponding XPath to the value

MAVEN_PROPS = [
    ('pom.groupId', '/project/groupId'),
    ('project.groupId', '/project/groupId'),
    ('groupId', '/project/groupId'),
    # fall back to parent
    ('groupId', '/project/parent/groupId'),
    ('pom.groupId', '/project/parent/groupId'),
    ('project.groupId', '/project/parent/groupId'),

    ('artifactId', '/project/artifactId'),
    ('pom.artifactId', '/project/artifactId'),
    ('project.artifactId', '/project/artifactId'),
    # fall back to parent
    ('artifactId', '/project/parent/artifactId'),
    ('pom.artifactId', '/project/parent/artifactId'),
    ('project.artifactId', '/project/parent/artifactId'),

    ('version', '/project/version'),
    ('pom.version', '/project/version'),
    ('project.version', '/project/version'),
    # fall back to parent
    ('version', '/project/parent/version'),
    ('pom.version', '/project/parent/version'),
    ('project.version', '/project/parent/version'),

    ('classifier', '/project/classifier'),
    ('pom.classifier', '/project/classifier'),
    ('project.classifier', '/project/classifier'),
    # fall back to parent
    ('classifier', '/project/parent/classifier'),
    ('pom.classifier', '/project/parent/classifier'),
    ('project.classifier', '/project/parent/classifier'),

    ('packaging', '/project/packaging'),
    ('pom.packaging', '/project/packaging'),
    ('project.packaging', '/project/packaging'),

    # fall back to parent
    ('packaging', '/project/parent/packaging'),
    ('pom.packaging', '/project/parent/packaging'),
    ('project.packaging', '/project/parent/packaging'),

    ('pom.organization.name', '/project/organization/name'),
    ('project.organization.name', '/project/organization/name'),

    ('pom.description', '/project/description'),
    ('project.description', '/project/description'),

    ('scm.url', '/project/scm/url'),

    # parent
    ('parent.groupId', '/project/parent/groupId'),
    ('pom.parent.groupId', '/project/parent/groupId'),
    ('project.parent.groupId', '/project/parent/groupId'),

    ('parent.artifactId', '/project/parent/artifactId'),
    ('pom.parent.artifactId', '/project/parent/artifactId'),
    ('project.parent.artifactId', '/project/parent/artifactId'),

    ('parent.version', '/project/parent/version'),
    ('pom.parent.version', '/project/parent/version'),
    ('project.parent.version', '/project/parent/version'),

    ('parent.classifier', '/project/parent/classifier'),
    ('pom.parent.classifier', '/project/parent/classifier'),
    ('project.parent.classifier', '/project/parent/classifier'),

    ('parent.packaging', '/project/parent/packaging'),
    ('pom.parent.packaging', '/project/parent/packaging'),
    ('project.parent.packaging', '/project/parent/packaging'),
]


STANDARD_MAVEN_PROPERTIES = [(p, xmlutils.namespace_unaware(xp)) for p, xp in MAVEN_PROPS]


# We hardcode some uncommon properties
HARDCODED_PROPERTIES = {
    'maven.javanet.project': 'maven2-repository'
}


def get_properties(xdoc):
    """
    Given an etree `xdoc` return a mapping of property key -> value using
    standard maven properties and pom-specific properties. This mapping is used
    later to resolve properties to values in a POM.
    """
    props = {}

    # collect core maven properties
    props.update(get_standard_properties(xdoc))

    # collect props defined in the POM proper
    props.update(get_pom_defined_properties(xdoc))

    props.update(HARDCODED_PROPERTIES)

    # property values values can reference other properties
    # so we repeat resolve a few times to expand such nested properties
    for _step in range(3):
        for key in props:
            props[key] = resolve_properties(props[key], props)

    return props


def get_standard_properties(xdoc):
    """
    Given an XML etree `xdoc`, build a dict mapping property keys to their
    values for "standard" maven properties and pom-specific properties. This
    mapping is used later to resolve properties in the values of the document.
    """
    properties = {}
    for name, xpath in STANDARD_MAVEN_PROPERTIES:
        values = xmlutils.find_text(xdoc, xpath)
#         logger.debug('get_standard_properties: with name=%(name)r,  xpath=%(xpath)r found: values=%(values)r' % locals())
        if not values:
            continue
        if name not in properties or not properties[name]:
#             logger.debug('get_standard_properties:  adding name=%(name)r, values=%(values)r' % locals())
            # FIXME: what if we have several times the same property defined?
            properties[name] = ' '.join(values)

    return properties


# XPaths for properties
PROPS_XPATH = [
    "/*[local-name()='project']/*[local-name()='properties']/*",
    "/*[local-name()='project']/*[local-name()='profiles']/*[local-name()='profile']/*[local-name()='properties']/*"
]


def get_pom_defined_properties(xdoc):
    """
    Resolve the maven properties section:

      <properties>
        <maven.compile.source>1.2</maven.compile.source>
        <maven.compile.target>1.1</maven.compile.target>
      </properties>
    """
    props = {}

    for xpath in PROPS_XPATH:
        xpath
        prop_vals = list(xdoc.xpath(xpath))
        logger.debug('get_pom_defined_properties: ###: {xpath} :'.format(**locals()) + repr(prop_vals))
        # FIXME: what if we have several times the same property defined?
        if prop_vals:
            props.update(map(xmlutils.name_value, prop_vals))
    return props


property_start = u'${'
property_end = u'}'


# use non capturing groups for alternation
_split_prop = re.compile(
    r'(?:[^\$\{\}])+'
    r'|'
    '(?:\$\{)'
    r'|'
    '(?:\})',
    re.UNICODE).finditer


def value_splitter(value):
    """
    Given a string value, return a list of strings splitting `value` in a
    tuple of regular text, property start and property end.
    """
    if not value:
        return
    for word in _split_prop(value):
        yield word.group()


def resolve_properties(value, properties):
    """
    Return a string based on a `value` string with maven properties resolved.

    Resolve the properties (e.g. ${ } parts) against the `properties`
    dictionary of keys/values. Resolve possible maven expressions (e.g.
    substring) using an equivalent substring_slice.
    """
    resolved_props = []
    next_is_prop = False

    # iterate the split value
    for val in value_splitter(value):
        logger.debug('  resolve_properties: %(val)r' % locals())

        if not val:
            logger.debug('   resolve_properties: if not val')
            continue

        # if we have a property marker start or end, just skip and setup a
        # flag telling that the next item will be a property or not
        if val == property_start:
            next_is_prop = True
            logger.debug('   resolve_properties: val == property_start')
            continue

        if val == property_end:
            # TODO: handle braces balancing issues
            next_is_prop = False
            logger.debug('   resolve_properties: val == property_end')
            continue

        # Here val != property_start and val != property_end: val is either a
        # regular value or a property based on the flag. If this is not a prop,
        # just accumulate the value and continue
        if not next_is_prop:
            resolved_props.append(val)
            logger.debug('   resolve_properties: not next_is_prop: resolved_props.append(%(val)r)' % locals())
            continue

        # Here val is guaranteed to be a property name to be resolved. Does it
        # contain a maven expression? this is true if the property name ends
        # with a known maven expression. find it with string.partition
        for maven_expression, substring_slice in MAVEN_SUBSTRINGS.items():
            prop_key, has_expression, _ = val.partition(maven_expression)
            if has_expression:
                break

        # Now has_expression and substring_slice are known
        # resolve the property proper
        try:
            # resolve the property key to a value
            resolved_val = properties[prop_key]

            # get the slice if needed
            if has_expression:
                resolved_val = substring(resolved_val, substring_slice)

            resolved_props.append(resolved_val)
            logger.debug('   resolve_properties: resolved_props.append(%(resolved_val)r)' % locals())

            next_is_prop = False
        except KeyError, e:
            logger.debug('   resolve_properties: KeyError')

            msg = ('Failed to resolve property %(val)r. error:\n%(e)r' % locals())
            logger.debug('   resolve_properties: ' + msg)
            # always accumulate the raw value if we failed to resolve
            original = u'${%(val)s}' % locals()
            logger.debug('   resolve_properties: IndexError: resolved_props.append(%(original)r)' % locals())
            resolved_props.append(original)

    logger.debug('### resolve_properties: %(resolved_props)r' % locals())
    return u''.join(resolved_props)


# A map of known maven substring expressions and the corresponding string slice

MAVEN_SUBSTRINGS = {
    '.substring(1)': (1, None),
    '.substring(2)': (2, None),
    '.substring(3)': (3, None),
    '.substring(4)': (4, None),
    '.substring(5)': (5, None),
    '.substring(6)': (6, None),
    '.substring(7)': (7, None),
    '.substring(8)': (8, None),
    '.substring(9)': (9, None),
    '.substring(0,1)': (None, 1),
    '.substring(0,2)': (None, 2),
    '.substring(0,3)': (None, 3),
    '.substring(0,4)': (None, 4),
    '.substring(0,5)': (None, 5),
    '.substring(0,6)': (None, 6),
    '.substring(0,7)': (None, 7),
    '.substring(0,8)': (None, 8),
    '.substring(0,9)': (None, 9),
}


def substring(s, start_end):
    """
    Return a slice of s where start_end is the start and end of a slice.
    """
    start, end = start_end
    startless = start is None
    endless = end is None
    if startless and endless:
        return s
    if startless:
        return s[:end]
    if endless:
        return s[start:]

    return s[start:end]


pom_extensions = ('.pom', 'pom.xml', 'project.xml', '.xml')


def pom_version(location):
    """
    Return 1 or 2 corresponding to the maven major
    version of POM style, not the POM version) if the file at location is
    highly likely to be a POM, otherwise None.
    """
    if (not filetype.is_file(location)
        or not location.endswith(pom_extensions)):
        return

    T = contenttype.get_type(location)
    # logger.debug('location: %(location)r, T: %(T)r)' % locals())
    if T.is_text and ('xml' in T.filetype_file.lower()
                      or 'sgml' in T.filetype_file.lower()
                      or 'xml' in T.filetype_pygment.lower()
                      or 'genshi' in T.filetype_pygment.lower()):

        # check the POM version in the first 100 lines
        with open(location, 'rb') as pom:
            for n, l in enumerate(pom):
                if n > 100:
                    break
                if ('http://maven.apache.org/POM/4.0.0' in l
                    or '<modelVersion>' in l):
                    return 2
                elif '<pomVersion>' in l:
                    return 1


def parse_pom(location, fields=MAVEN_FIELDS):
    """
    Parse the Maven POM object for the file at location using a `fields` mapping
    of field name -> xpath.
    Return a mapping of field name -> [values].
    """
    if not pom_version(location):
        return {}

    pom_handler = partial(extract_pom_data, fields=fields)

    pom = xmlutils.parse(location, handler=pom_handler)
    logger.debug('###parse_pom: {pom}'.format(**locals()))
    if not pom:
        return {}
    return pom


def extract_pom_data(xdoc, fields=MAVEN_FIELDS):
    """
    Extract POM data from an etree document using a `fields` mapping of field
    name -> xpath.
    Return a mapping of field name -> [values].
    """
    pom_data = {}
    props = get_properties(xdoc)

    for name, xpath in fields:
        values = xmlutils.find_text(xdoc, xpath)
        if values:
            pass
            # logger.debug('processing name: {name}, xpath: {xpath}'.format(**locals()))
            # logger.debug(' found: {values}'.format(**locals()))
        resolved = [resolve_properties(val , props)for val in values]

        if resolved:
            logger.debug(' extract_pom_data: found: {resolved}'.format(**locals()))
        # FIXME: this is grossly incorrect!
        pom_data[name] = resolved or []

    # logger.debug(' found: {pom_data}'.format(**locals()))
    pom_data = inherit_from_parent(pom_data)
    # logger.debug(' inherited: {pom_data}'.format(**locals()))
    return pom_data


def inherit_from_parent(pom_data):
    """
    Add defaults to a pom `pom_data` mapping using inheritance from parent data
    when needed. For instance, the parent groupid is used if no groupid is
    defined.
    """
    gid = pom_data.get('maven_component_group_id')
    pgid = pom_data.get('maven_component_parent_group_id')
    if not gid and pgid:
        pom_data['maven_component_group_id'] = pgid

    gvers = pom_data.get('maven_component_version')
    pvers = pom_data.get('maven_component_parent_version')
    if not gvers and pvers:
        pom_data['maven_component_version'] = pvers
    return pom_data


def parse(location):
    """
    Parse a pom file at location and return a Package or None.
    """
    if not location.endswith('pom.xml') or location.endswith('.pom'):
        return

    pom = parse_pom(location)

    def get_val(key):
        val = pom.get(key)
        if not val:
            return
        if isinstance(val, list) and len(val) == 1:
            return val[0]
        else:
            return u'\n'.join(val)

    group_artifact = ':'.join([get_val('maven_component_group_id'), get_val('maven_component_artifact_id')])

    # FIXME: the way we collect nested tags is entirely WRONG, especially for licenses
    # attempt to align licenses for now
    licenses = izip_longest(
        pom['maven_license'],
        pom['maven_license_url'],
        pom['maven_license_comments'],
    )
    licenses = [models.AssertedLicense(license=lic, url=url, notice=comments)
                for lic, url, comments in licenses]

    authors = izip_longest(
        pom['maven_developer_name'],
        pom['maven_developer_email'],
    )
    authors = [models.Party(type=models.party_person, name=name, email=email) for name, email in authors]

    orgs = izip_longest(
        pom['maven_organization_name'],
        pom['maven_organization_url'],
    )
    orgs = [models.Party(type=models.party_org, name=name, url=url) for name, url in orgs]

    package = MavenJar(
        location=location,
        name=group_artifact,
        # FIXME: this is not right: name and identifier should be storable
        summary=get_val('maven_project_name'),
        version=get_val('maven_component_version'),
        homepage_url=get_val('maven_project_url'),
        description=get_val('maven_project_description'),
        asserted_licenses=licenses,
        authors=authors,
        owners=orgs,
    )
    return package


class MavenRecognizer(object):
    """
    A package recognizer for Maven-based packages.
    """
    def __init__(self):
        return NotImplementedError()

    def recon(self, location):
        for f in  os.listdir(location):
            loc = join(location, f)
            if not filetype.is_file(loc):
                continue
            # a pom is an xml doc
            pom_ver = pom_version(location)
            if not pom_ver:
                continue

            if f == 'pom.xml':
                # first case: a maven pom.xml inside a META-INF directory
                # such as in META-INF/maven/log4j/log4j/pom.xml
                # the directory tree has a fixed depth
                # as is: META-INF/maven/groupid/artifactid/pom.xml
                # this will typically be inside a binary jar, so we should find
                # a typical structure above
                try:
                    gggp = dirname(dirname(dirname(dirname(loc))))
                    if fileutils.file_name(gggp) == 'META-INF':
                        # recon here: the root of the component is the parent of
                        # META-INF, return that, with a type and the POM
                        # metafile to parse.
                        pass
                except:
                    pass

                # second case: a maven pom.xml at the root of component
                # development tree we should find a few extra clues in the
                # conventional directory structure below for now we take this as
                # being the component root. return that, with a type and the POM
                # metafile to parse.

                pass
            elif f.endswith('.pom'):
                # first case: a maven repo layout
                # the jars are side-by-side with the pom
                # check if there are side-by-side artifacts
                jar = loc.replace('.pom', '.jar')
                if os.path.exists(jar):
                # return that, with a type and the POM metafile to parse.
                    pass

                # second case: a maven .pom nested in MANIFEST.MF
