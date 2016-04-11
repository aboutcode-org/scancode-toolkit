#
# Copyright (c) 2015 nexB Inc. and others. All rights reserved.
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

import re
import logging

from lxml import etree  # @UnresolvedImport

from textcode import analysis
from commoncode import filetype
from typecode import contenttype
from os.path import dirname
from commoncode import fileutils
import os.path
from os.path import join


logger = logging.getLogger(__name__)

DEBUG = False


def xpath_ns_expr(x):
    """
    Build a namespace-aware XPath expression using local-name, essentially
    ignoring namespaces.

    XPath expressions in XML documents with namespaces are eventually complex,
    as needed by lxml that supports namespaces. See
    http://jcooney.net/archive/2005/08/09/6517.aspx

    This function helps keeping these expression simple and transforms a
    simple path expression in a complex one. TODO: this is probably very
    inefficient.
    """
    ns_aware_expression_template = "*[local-name()='%s']"
    transformed_steps = []
    # we assume that the input expression is simple using only /
    xpath_steps = x.split('/')
    for step in xpath_steps:
        if step.strip():
            # apply expression template, searching * and then a local-name in
            # the returned elements
            transformed_steps.append(ns_aware_expression_template % step)
        else:
            transformed_steps.append(step)
    return '/'.join(transformed_steps)


def strip_namespace(tag_name):
    """
    Given a tag name, removes lxml-added namespace if present.

    For example, this lxml tag name:
        {http://maven.apache.org/POM/4.0.0}geronimo.osgi.export.pkg
    becomes:
        geronimo.osgi.export.pkg
    """
    if '}' in tag_name:
        return tag_name.split('}', 1)[1]
    else:
        return tag_name


# Maven1 tuples of (field name, xpath to get value for this field)
MAVEN1_FIELDS = [
    ('component_extend_1', '/project/extend'),
    ('component_current_version_1', '/project/currentVersion'),
    ('distribution_management_site_1', '/project/distributionSite'),
    ('distribution_management_directory_1', '/project/distributionDirectory'),
    ('project_short_description_1', '/project/shortDescription'),
    ('repository_url_1', '/project/repository/url'),
    ('repository_connection_1', '/project/repository/connection'),
    ('repository_developer_connection_1',
     '/project/repository/developerConnection'),
]


# maven2 tuples of (field name, xpath to get value for this field)
MAVEN2_FIELDS = [
    ('component_artifact_id', '/project/artifactId'),
    ('component_classifier', '/project/classifier'),
    ('component_group_id', '/project/groupId'),
    ('component_parent_group_id', '/project/parent/groupId'),
    ('component_packaging', '/project/packaging'),
    ('component_version', '/project/version'),

    ('developer_email', '/project/developers/developer/email'),
    ('developer_name', '/project/developers/developer/name'),

    ('distribution_management_site_url',
     '/project/distributionManagement/site/url'),
    ('distribution_management_repository_url',
     '/project/distributionManagement/repository/url'),

    ('license', '/project/licenses/license/name'),
    ('license_comments', '/project/licenses/license/comments'),
    ('license_distribution', '/project/licenses/license/distribution'),
    ('license_name', '/project/licenses/license/name'),
    ('license_url', '/project/licenses/license/url'),

    ('organization_name', '/project/organization/name'),
    ('organization_url', '/project/organization/url'),

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

    ('distribution_management_group_id',
     '/project/distributionManagement/relocation/groupId'),
    ('model_version', '/project/modelVersion')
]


MAVEN_FIELDS = [('maven_' + key, xpath_ns_expr(expression)) for
                key, expression in (MAVEN2_FIELDS + MAVEN1_FIELDS)]


def find(xdoc, xpath):
    """
    Given an XML etree `xdoc` and an `xpath` expression, return a list of
    values matching that expression in `xdoc`.
    """
    result = xdoc.xpath(xpath)
    if isinstance(result, list):
        # xpath can return a list (nodeset), or bool, float or string
        output = []
        for element in result:
            if element.text:
                output.append(element.text.strip())
        return output
    else:
        return [unicode(result).strip()]


# common Maven property keys and corresponding XPath to the value

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


STANDARD_MAVEN_PROPERTIES = [(p, xpath_ns_expr(xp),) for p, xp in MAVEN_PROPS]


# we hardcode some uncommon properties
HARDCODED_PROPERTIES = {
    'maven.javanet.project': 'maven2-repository'
}


def get_properties(xdoc):
    """
    Given an XML etree `xdoc`, build a dict mapping property keys to their
    values, using standard maven properties and pom-specific properties. This
    mapping is used later to resolve properties in the values of the document.
    """
    props = {}

    # collect core maven properties
    props.update(get_standard_properties(xdoc))

    # collect props defined in the POM proper
    props.update(get_pom_defined_properties(xdoc))

    props.update(HARDCODED_PROPERTIES)

    # property values values can reference other properties
    # so we repeat resolve a few times (3) to expand such nested properties
    for _ in range(3):
        for key in props:
            props[key] = resolve_properties(props[key], props)

    return props


def get_standard_properties(xdoc):
    """
    Given an XML etree `xdoc`, build a dict mapping property keys to their
    values, using standard maven properties and pom-specific properties. This
    mapping is used later to resolve properties in the values of the document.
    """
    props = {}
    # collect core maven properties
    for prop_name, xpath in STANDARD_MAVEN_PROPERTIES:
        prop_vals = list(find(xdoc, xpath))
        logger.debug('get_standard_properties: '
                  'with prop_name=%(prop_name)r, '
                  'xpath=%(xpath)r found: prop_vals=%(prop_vals)r' % locals())
        if not prop_vals:
            continue
        if prop_name not in props or not props[prop_name]:
            logger.debug('get_standard_properties: '
                      'adding prop_name=%(prop_name)r, '
                      'prop_vals=%(prop_vals)r' % locals())
            props[prop_name] = ' '.join(prop_vals)

    return props


# XPaths for properties
PROPS_XPATH = [
    "/*[local-name()='project']/*[local-name()='properties']/*",
    "/*[local-name()='project']/*[local-name()='profiles']"
    "/*[local-name()='profile']/*[local-name()='properties']/*"
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
        prop_vals = list(xdoc.xpath(xpath))
        props_for_path = dict([property_for_tag(el) for el in prop_vals])
        props.update(props_for_path)
    return props


def property_for_tag(elem):
    """
    Given an etree XML element `elem`, return a tuple (key, text value)  for
    each property. Remove lxml-added namespaces and namespace prefixes if
    present.

    For example with this NS-prefixd lxml XML snippet:
        {http://maven.apache.org/POM/4.0.0}geronimo.osgi.export.pkg
    becomes:
        geronimo.osgi.export.pkg
    The prop_key name is returned and is a property key:
        geronimo.osgi.export.pkg
    """
    prop_val = elem.text
    prop_key = elem.tag
    for prefix, ns in elem.nsmap.items():
        if prefix:
            prop_key = prop_key.replace('{%s}' % prefix, '')
        if ns:
            prop_key = prop_key.replace('{%s}' % ns, '')
    return prop_key , prop_val


property_start = u'${'
property_end = u'}'


# use non capturing groups for alternation
def property_splitter_re():
    return re.compile(
        r'(?:[^\$\{\}])+'
        r'|(?:\$\{)'
        r'|(?:\})',
        re.UNICODE).finditer


def value_splitter(value):
    """
    Given a string value, return a list of strings splitting `value` in a
    tuple of regular text, property start and property end.
    """
    if value:
        splitter = property_splitter_re()
        for word in splitter(value):
            yield word.group()
    else:
        yield


def resolve_properties(value, properties):
    """
    Return a string based on a `value` string with maven properties resolved.

    Resolve the properties (e.g. ${ } parts) against the `properties`
    dictionary of keys/values. Resolve possible maven expressions (e.g.
    substring) using an equivalent python_expression.
    """
    resolved_props = []
    next_is_prop = False

    # iterate the split value
    for val in value_splitter(value):
        if not val:
            continue

        # if we have a property marker start or end, just skip and setup a
        # flag telling that the next item will be a property or not
        if val == property_start:
            next_is_prop = True
            continue

        if val == property_end:
            # TODO: handle braces balancing issues
            next_is_prop = False
            continue

        # Here val != property_start and val != property_end: val is either a
        # regular value or a property based on the flag. If this is not a prop,
        # just accumulate the value and continue
        if not next_is_prop:
            resolved_props.append(val)
            continue

        # Here val is guaranteed to be a property name to be resolved. Does it
        # contain a maven expression? this is true if the property name ends
        # with a known maven expression. find it with string.partition
        for maven_expression, python_expression in MAVEN_EXPRESSIONS.items():
            prop_key, has_expression, _ = val.partition(maven_expression)
            if has_expression:
                break

        # Now has_expression and python_expression are known
        # resolve the property proper
        try:
            # resolve the property key to a value
            resolved_val = properties[prop_key]

            # eval expression on resolved value if needed
            if has_expression:
                resolved_val = eval_expression(resolved_val, python_expression)
            # and accumulate the value
            resolved_props.append(resolved_val)
            next_is_prop = False
        except Exception, e:
            msg = ('Failed to resolve property %(val)r. error:\n%(e)r'
                       % locals())
            logger.debug(msg)
            # raise
            # always accumulate the raw value if we failed to resolve
            original = u'${%(val)s}' % locals()
            resolved_props.append(original)

    return u''.join(resolved_props)


# A map of known maven expressions and the corresponding python expression.
# Only handles python functions that can be direct;y applied to a string.
# TODO: We should try to abstract numbers rather than hardcoding expressions
MAVEN_EXPRESSIONS = {
                     '.substring(1)': '[1:]',
                     '.substring(2)': '[2:]',
                     '.substring(3)': '[3:]',
                     '.substring(4)': '[4:]',
                     '.substring(5)': '[5:]',
                     '.substring(6)': '[6:]',
                     '.substring(7)': '[7:]',
                     '.substring(8)': '[8:]',
                     '.substring(9)': '[9:]',
                     '.substring(0,1)': '[:1]',
                     '.substring(0,2)': '[:2]',
                     '.substring(0,3)': '[:3]',
                     '.substring(0,4)': '[:4]',
                     '.substring(0,5)': '[:5]',
                     '.substring(0,6)': '[:6]',
                     '.substring(0,7)': '[:7]',
                     '.substring(0,8)': '[:8]',
                     '.substring(0,8)': '[:9]',
                    }


def eval_expression(value, python_expression):
    """
    Given a value string representing a resolved property and a found
    python_expression to apply to this property value, eval the expression on
    the value and return the transformed value.
    """
    evaled = value
    try:
        # build an eval of the string value, padding the 'function' at the end
        # such as in 'some text' becomes 'some text'[8:]
        evaluable = repr(value) + python_expression
        evaled = eval(evaluable)
    except Exception, e:
        msg = ('Failed to evaluate expression: %(python_expression)r '
               'on value %(value)r: error:\n%(e)r' % locals)
        logger.debug(msg)
        raise
    return evaled


def get_xml_parser():
    return etree.XMLParser(# @UndefinedVariable
                           recover=True,
                           remove_blank_text=True,
                           resolve_entities=False)


def xdoc_parser(location):
    """
    Return an etree doc from the file at `location` using lxml directly first.
    """
    return etree.parse(location, get_xml_parser())  # @UndefinedVariable


def xdoc_parser_fallback(location):
    """
    Return an etree doc from file at `location`, trying hard to get Unicode
    before invoking lxml. Use text pre-processing to get Unicode.

    NB: we could use BS4 instead.
    """
    text = analysis.unicode_text(location)
    return etree.fromstring(text, get_xml_parser())  # @UndefinedVariable


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
    Parse the Maven POM object for the file at location and return a
    dictionary of Maven fields/values where each value is a list.

    Try first using lxml directly then try using alternate parsing.
    """
    if not pom_version(location):
        return

    # try with two different parsing approaches
    try:
        return try_parse_pom(location, fields, parser=xdoc_parser)
    except:
        return try_parse_pom(location, fields, parser=xdoc_parser_fallback)


def try_parse_pom(location, fields, parser):
    """
    Parse the Maven POM file at `location` and return a dictionary of Maven
    fields/values where each value is a list.
    """
    if not pom_version(location):
        return {}

    pom = parser(location)

    if pom is None:
        return {}

    pom_data = {}
    properties = get_properties(pom)
    for field_name, xpath_expression in fields:
        found = find(pom, xpath_expression)
        if found:
            found = [resolve_properties(value , properties)
                     for value in found]

        pom_data[field_name] = found or []

    pom_data = inherit_from_parent(pom_data)
    return pom_data


def inherit_from_parent(pom_data):
    """
    Add defaults to a pom `pom_data` mapping using inheritance from parent data
    when needed. For instance, if no groupid is defined, the parent groupid
    should be used.
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


def transposed(lists):
    """
    Transpose a list of lists.

    Equivalent to these examples:
    >>> a=[[1,2,3],[4,5,6]]
    >>> transposed(a)
    [[1, 4], [2, 5], [3, 6]]
    >>> zip(*a)
    [(1, 4), (2, 5), (3, 6)]
    >>> map(None,a)
    [[1, 2, 3], [4, 5, 6]]
    >>> map(None,*a)
    [(1, 4), (2, 5), (3, 6)]
    """
    if not lists:
        return []
    return map(lambda *row: list(row), *lists)


def parse(location):
    """
    Parse a pom file at location and return a package object.
    """
    from packagedcode.models import Package, AssertedLicense
    if not location.endswith('pom.xml') or location.endswith('.pom'):
        return None
    pom_metadata = parse_pom(location)
    asserted_license = AssertedLicense(license=pom_metadata['maven_license'], url=pom_metadata['maven_license_url'])
    package = Package(
            version=''.join(pom_metadata['maven_component_version']),
            id=''.join(pom_metadata['maven_component_group_id']),
            authors='\n'.join(pom_metadata['maven_developer_name']),
            homepage_url=''.join(pom_metadata['maven_project_url']),
            description=''.join(pom_metadata['maven_project_description']),
            name=''.join(pom_metadata['maven_component_artifact_id']),
            asserted_licenses=[asserted_license],
            location=location
            )
    return package


class MavenRecognizer(object):
    """
    A package recognizer for Maven-based packages.
    """
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
                        # META-INF, return that, with a type and the POM metafile to parse.
                        pass
                except:
                    pass
                
                # second case: a maven pom.xml at the root of component development tree
                # we should find a few extra clues in the conventional directory structure below
                # for now we take this as being the component root.
                # return that, with a type and the POM metafile to parse.

                pass
            elif f.endswith('.pom'):
                # first case: a maven repo layout
                # the jars are side-by-side with the pom
                #check if there are side-by-side artifacts
                jar = loc.replace('.pom', '.jar')
                if os.path.exists(jar):
                # return that, with a type and the POM metafile to parse.
                    pass
