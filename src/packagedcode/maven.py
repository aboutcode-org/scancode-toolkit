#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
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

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import codecs
from collections import OrderedDict
import logging
import os.path
from os.path import dirname
from os.path import join
import re

from lxml import etree
from pymaven import pom
from pymaven import artifact

from commoncode import filetype
from commoncode import fileutils
from packagedcode import models
from typecode import contenttype
from textcode import analysis


logger = logging.getLogger(__name__)
# import sys
# logging.basicConfig(stream=sys.stdout)
# logger.setLevel(logging.DEBUG)


"""
Support Maven2 POMs.
Attempts to resolve Maven properties when possible.
"""

class MavenPomPackage(models.Package):
    metafiles = ('.pom', 'pom.xml',)
    extensions = ('.pom', '.xml',)
    repo_types = (models.repo_maven,)
    type = models.StringType(default='Apache Maven POM')
    packaging = models.StringType(default=models.as_archive)
    primary_language = models.StringType(default='Java')

    @classmethod
    def recognize(cls, location):
        return parse(location)


class ParentPom(artifact.Artifact):
    """
    A minimal Artifact subclass used to store parent poms when no POM file is available for these.
    """

    def __init__(self, coordinate):
        super(ParentPom, self).__init__(coordinate)

        # add empty, pom.Pom-class-like empty attributes
        self.client = None
        self.dependencies = {}
        self.dependency_management = {}
        self.parent = None
        self.properties = {}
        # TODO: ????
        # self.pom_data/self._xml = None

    def to_dict(self):
        """
        Return a mapping representing this POM
        """
        return OrderedDict([
            ('group_id', self.group_id),
            ('artifact_id', self.artifact_id),
            ('version', str(self.version) if self.version else None),
            ('classifier', self.classifier),
            ('type', self.type),
        ])


STRIP_NAMESPACE_RE = re.compile(r"<project(.|\s)*?>", re.UNICODE)


class MavenPom(pom.Pom):
    def __init__(self, location):
        # NOTE: most of this is copied over from Pom.__init__
        try:
            with codecs.open(location, 'rb', encoding='UTF-8') as fh:
                xml = fh.read()
        except UnicodeDecodeError as _a:
            xml = analysis.unicode_text(location)

        xml = xml[xml.find('<project'):]
        xml = STRIP_NAMESPACE_RE.sub('<project>', xml, 1)

        parser = etree.XMLParser(
            recover=True,
            remove_comments=True,
            remove_pis=True,
            remove_blank_text=True, resolve_entities=False
        )

        self._xml = etree.fromstring(xml, parser=parser)

        # FXIME: we do not use a client for now. there are pending issues at pymaven to address this
        self._client = None

        self.model_version = self._get_attribute('modelVersion')
        self.group_id = self._get_attribute('groupId')
        self.artifact_id = self._get_attribute('artifactId')
        self.version = self._get_attribute('version')
        self.classifier = self._get_attribute('classifier')
        self.packaging = self._get_attribute('packaging') or 'jar'
        self.name = self._get_attribute('name')
        self.description = self._get_attribute('description')
        self.inception_year = self._get_attribute('inceptionYear')
        self.url = self._get_attribute('url')
        self.organization_name = self._get_attribute('organization/name')
        self.organization_url = self._get_attribute('organization/url')
        self.licenses = list(self._find_licenses())
        self.developers = list(self._find_parties('developers/developer'))
        self.contributors = list(self._find_parties('contributors/contributor'))
        self.mailing_lists = list(self._find_mailing_lists())
        self.scm = self._find_scm()
        self.issue_management = self._find_issue_management()
        self.ci_management = self._find_ci_management()
        self.distribution_management = self._find_distribution_management()
        self.repositories = list(self._find_repositories('repositories/repository'))
        self.plugin_repositories = list(self._find_repositories('pluginRepositories/pluginRepository'))
        self.modules = self._get_attributes_list('modules/module')

        # FIXME: this attribute should be collected with the parent but
        # is not retrieved yet by pymaven it points to the relative path
        # where to find the full parent POM
        self.parent_relative_path = self._get_attribute('relativePath')  # or '../pom.xml'

        # FIXME: Other types that are not collected for now (or
        # indirectly through dependencies management) include: build,
        # reporting, profiles, etc

        # dynamic attributes
        self._parent = None
        self._dep_mgmt = None
        self._dependencies = None
        self._properties = None

    def _extra_properties(self):
        """
        Return a mapping of extra properties
        """
        properties = {}
        properties['classifier'] = self.classifier
        properties['project.classifier'] = self.classifier
        properties['pom.classifier'] = self.classifier

        properties['packaging'] = self.packaging
        properties['project.packaging'] = self.packaging
        properties['pom.packaging'] = self.packaging

        properties['organization.name'] = self.organization_name
        properties['project.organization.name'] = self.organization_name
        properties['pom.organization.name'] = self.organization_name

        properties['organization.url'] = self.organization_url
        properties['project.organization.url'] = self.organization_url
        properties['pom.organization.url'] = self.organization_url

        # TODO: collect props defined in a properties file
        # see https://maven.apache.org/shared/maven-archiver/#class_archive
        # afaik this only applies for POMs stored inside a JAR

        return properties

    @classmethod
    def _replace_props(cls, text, properties):

        def subfunc(matchobj):
            """Return the replacement value for a matched property key."""
            key = matchobj.group(1)
            # does this key contain a substring?
            real_key, start_end = _get_substring_expression(key)
            if not start_end:
                value = properties.get(key)

                return value
            # apply the substring transform
            value = properties.get(real_key)
            if not value:
                return value
            start, end = start_end
            return substring(value, start, end)

        result = pom.PROPERTY_RE.sub(subfunc, text)
        while result and pom.PROPERTY_RE.match(result):
            result = pom.PROPERTY_RE.sub(subfunc, result)

        if not result:
            result = text
        return result.strip()

    def _replace_properties(self, text, properties=None):
        # copied from pymavem.pom.Pom
        if properties is None:
            properties = self.properties
        return MavenPom._replace_props(text, properties)

    def resolve(self):
        """
        Resolve POM Maven "properties" in attribute values and inherit
        from parent. Update the POM attributes in place.
        """
        # inherit first to get essential parent properties
        self._inherit_from_parent()

        # then collect properties + extra
        properties = dict(self.properties)
        properties.update(self._extra_properties())

        # these attributes are plain strings
        plain_attributes = [
            'group_id',
            'version',
            'classifier',
            'packaging',
            'name',
            'description',
            'inception_year',
            'url',
            'organization_name',
            'organization_url',
        ]
        for attr in plain_attributes:
            attr_val = getattr(self, attr, None)
            if not attr_val:
                continue
            resolved = self._replace_properties(attr_val, properties)
            setattr(self, attr, resolved)

        # these attributes are mappings
        mapping_attributes = [
            'scm',
            'issue_management',
            'ci_management',
        ]
        for map_attr in mapping_attributes:
            mapping = getattr(self, map_attr, {})
            if not mapping:
                continue
            for key, value in mapping.items():
                if not value:
                    continue
                mapping[key] = self._replace_properties(value, properties)

        # these attributes are lists of mappings
        mappings_list_attributes = [
            'repositories',
            'plugin_repositories',
        ]
        for lmap_attr in mappings_list_attributes:
            lmapping = getattr(self, lmap_attr, [])
            if not lmapping:
                continue
            for mapping in lmapping:
                for key, value in mapping.items():
                    if not value:
                        continue
                    mapping[key] = self._replace_properties(value, properties)

        # these attributes are complex nested and lists mappings

        # TODO: add:
        # nest dicts
        # 'distribution_management',
        # nest lists
        #    'mailing_lists',


    def _inherit_from_parent(self):
        """
        Update attributes using inheritance from parent attributes. For
        instance, the parent group_id is used if group_id is not defined.
        """
        # TODO: there are more attributes (all) that can be inherited
        if not self.parent:
            return
        if self.group_id is None and self.parent.group_id:
            self.group_id = self.parent.group_id
        if self.version is None and self.parent.version:
            self.version = str(self.parent.version)
        if not self.classifier is None and self.parent.classifier:
            self.classifier = self.parent.classifier

        # special handling for URLs: see
        # http://maven.apache.org/ref/3.5.0/maven-model-builder/index.html#Inheritance_Assembly
        # Notice that the 5 URLs from the model:
        # project.url,
        # project.scm.connection, project.scm.developerConnection, project.scm.url
        # project.distributionManagement.site.url)
        # ... have a special inheritance handling: if not configured in
        # current model, the inherited value is the parent's one with
        # current artifact id appended.
        if (self.url is None
            and hasattr(self.parent, 'url')
            and getattr(self.parent, 'url', None)
            and self.artifact_id):
            self.url = self.parent.url + self.artifact_id

        parent_scm = getattr(self.parent, 'scm', None)
        if self.scm and parent_scm and self.artifact_id:
            ps_url = parent_scm.get('url')
            if not self.scm.get('url') and ps_url:
                self.scm['url'] = ps_url + self.artifact_id

            ps_connection = parent_scm.get('connection')
            if not self.scm.get('connection') and ps_connection:
                self.scm['connection'] = ps_connection + self.artifact_id

            ps_devconnection = parent_scm.get('developer_connection')
            if not self.scm.get('developer_connection') and ps_devconnection:
                self.scm['developer_connection'] = ps_devconnection + self.artifact_id

        # TODO: distribution_management.site.url


    def _pom_factory(self, group_id, artifact_id, version):
        return ParentPom('%s:%s:pom:%s' % (group_id, artifact_id, version))

    def _get_attribute(self, xpath, xml=None):
        """Return a single value text attribute for a given xpath or None."""
        if xml is None:
            xml = self._xml
        attr = xml.findtext(xpath)
        return attr and attr.strip() or None

    def _get_attributes_list(self, xpath, xml=None):
        """Return a list of text attribute values for a given xpath or None."""
        if xml is None:
            xml = self._xml
        attrs = xml.findall(xpath)
        attrs = [attr.text for attr in attrs]
        return [attr.strip() for attr in attrs if attr and attr.strip()]

    def _find_licenses(self):
        """Return an iterable of license mappings."""
        for lic in self._xml.findall('licenses/license'):
            yield OrderedDict([
                ('name', self._get_attribute('name', lic)),
                ('url', self._get_attribute('url', lic)),
                ('comments', self._get_attribute('comments', lic)),
                # arcane and seldom used
                ('distribution', self._get_attribute('distribution', lic)),
            ])

    def _find_parties(self, key='developers/developer'):
        """Return an iterable of party mappings for a given xpath."""
        for party in self._xml.findall(key):
            yield OrderedDict([
                ('id', self._get_attribute('id', party)),
                ('name', self._get_attribute('name', party)),
                ('email', self._get_attribute('email', party)),
                ('url', self._get_attribute('url', party)),
                ('organization', self._get_attribute('organization', party)),
                ('organization_url', self._get_attribute('organizationUrl', party)),
                ('roles', [role.findtext('.') for role in party.findall('roles/role')]),
            ])

    def _find_mailing_lists(self):
        """Return an iterable of mailing lists mappings."""
        for ml in self._xml.findall('mailingLists/mailingList'):
            archive_url = self._get_attribute('archive', ml)
            # TODO: add 'otherArchives/otherArchive' as lists?
            yield OrderedDict([
                ('name', self._get_attribute('name', ml)),
                ('archive_url', archive_url),
            ])

    def _find_scm(self):
        """Return a version control/scm mapping."""
        scm = self._xml.find('scm')
        if scm is None:
            return {}
        return OrderedDict([
            ('connection', self._get_attribute('connection', scm)),
            ('developer_connection', self._get_attribute('developer_connection', scm)),
            ('url', self._get_attribute('url', scm)),
            ('tag', self._get_attribute('tag', scm)),
        ])

    def _find_issue_management(self):
        """Return an issue management mapping."""
        imgt = self._xml.find('issueManagement')
        if imgt is None:
            return {}
        return OrderedDict([
            ('system', self._get_attribute('system', imgt)),
            ('url', self._get_attribute('url', imgt)),
        ])

    def _find_ci_management(self):
        """Return a CI mapping."""
        cimgt = self._xml.find('ciManagement')
        if cimgt is None:
            return {}
        return OrderedDict([
            ('system', self._get_attribute('system', cimgt)),
            ('url', self._get_attribute('url', cimgt)),
        ])

    def _find_repository(self, xpath, xml=None):
        """Return a repository mapping for an xpath."""
        if xml is None:
            xml = self._xml
        repo = xml.find(xpath)
        if repo is None:
            return {}
        return OrderedDict([
            ('id', self._get_attribute('id', repo)),
            ('name', self._get_attribute('name', repo)),
            ('url', self._get_attribute('url', repo)),
        ])

    def _find_distribution_management(self):
        """Return a distribution management mapping."""
        dmgt = self._xml.find('distributionManagement')
        if dmgt is None:
            return {}
        return OrderedDict([
            ('download_url', self._get_attribute('distributionManagement/downloadUrl')),
            ('site', self._find_repository('distributionManagement/site')),
            ('repository', self._find_repository('distributionManagement/repository')),
            ('snapshot_repository', self._find_repository('distributionManagement/snapshotRepository'))
        ])

    def _find_repositories(self, key='repositories/repository'):
        """Return an iterable or repository mappings for an xpath."""
        for repo in self._xml.findall(key):
            rep = self._find_repository('.', repo)
            if rep:
                yield rep

    def to_dict(self):
        """
        Return a mapping representing this POM.
        """
        dependencies = OrderedDict()
        for scope, deps in self.dependencies.items():
            dependencies[scope] = [
                OrderedDict([
                    ('group_id', gid),
                    ('artifact_id', aid),
                    ('version', version),
                    ('required', required),
                ])
            for ((gid, aid, version), required) in deps]

        return OrderedDict([
            ('model_version', self.model_version),
            ('group_id', self.group_id),
            ('artifact_id', self.artifact_id),
            ('version', self.version),
            ('classifier', self.classifier),
            ('packaging ', self.packaging),

            ('parent', self.parent.to_dict() if self.parent else {}),

            ('name', self.name),
            ('description', self.description),
            ('inception_year', self.inception_year),
            ('url', self.url),
            ('organization_name', self.organization_name),
            ('organization_url', self.organization_url),

            ('licenses', self.licenses or []),

            ('developers', self.developers or []),
            ('contributors', self.contributors or []),

            ('modules', self.modules or []),
            ('mailing_lists', self.mailing_lists),
            ('scm', self.scm),
            ('issue_management', self.issue_management),
            ('ci_management', self.ci_management),
            ('distribution_management', self.distribution_management),
            ('repositories', self.repositories),
            ('plugin_repositories', self.plugin_repositories),
            # FIXME: move to proper place in sequeence of attributes
            ('dependencies', dependencies or {}),
        ])


def _get_substring_expression(text):
    """
    Return a tuple of (text, start/end) such that:

    - if there is a substring() expression in text, the returned text
    has been stripped from it and start/end is a tuple representing
    slice indexes for the substring expression.

    - if there is no substring() expression in text, text is returned
    as-is and start/end is None.

    For example:
    >>> assert ('pom.artifactId', (8, None)) == _get_substring_expression('pom.artifactId.substring(8)')
    >>> assert ('pom.artifactId', None) == _get_substring_expression('pom.artifactId')
    """
    key, _, start_end = text.partition('.substring(')
    if not start_end:
        return text, None

    start_end = start_end.rstrip(')')
    start_end = [se.strip() for se in start_end.split(',')]

    # we cannot parse less than 1 and more than 2 slice indexes
    if len(start_end) not in (1, 2):
        return text, None

    # we cannot parse slice indexes that are not numbers
    if not all(se.isdigit() for se in start_end):
        return text, None
    start_end = [int(se) for se in start_end]

    if len(start_end) == 1:
        start = start_end[0]
        end = None
    else:
        start, end = start_end

    return key, (start, end)


def substring(s, start, end):
    """
    Return a slice of s based on start and end indexes (that can be None).
    """
    startless = start is None
    endless = end is None
    if startless and endless:
        return s
    if endless:
        return s[start:]
    if startless:
        return s[:end]
    return s[start:end]


def is_pom(location):
    """
    Return True if the file at location is highly likely to be a POM.
    """
    if (not filetype.is_file(location)
    or not location.endswith(('.pom', 'pom.xml', 'project.xml',))):
        return

    T = contenttype.get_type(location)
    # logger.debug('location: %(location)r, T: %(T)r)' % locals())
    if T.is_text and ('xml' in T.filetype_file.lower()
                      or 'sgml' in T.filetype_file.lower()
                      or 'xml' in T.filetype_pygment.lower()
                      or 'genshi' in T.filetype_pygment.lower()):

        # check the POM version in the first 100 lines
        with codecs.open(location, encoding='utf-8') as pom:
            for n, line in enumerate(pom):
                if n > 100:
                    break
                if any(x in line for x in
                       ('http://maven.apache.org/POM/4.0.0', '<modelVersion>',)):
                    return True


def parse_pom(location, check_is_pom=False):
    """
    Return a MavenPom object from the Maven POM file at location.
    """
    pom = _get_mavenpom(location, check_is_pom)
    if not pom:
        return {}
    return pom.to_dict()


def _get_mavenpom(location, check_is_pom=False):
    if check_is_pom and not is_pom(location):
        return
    pom = MavenPom(location)
    pom.resolve()
    if check_is_pom and not (pom.model_version and pom.group_id and pom.artifact_id):
        return
    return pom


def parse(location):
    """
    Parse a pom file at location and return a Package or None.
    """
    mavenpom = _get_mavenpom(location, check_is_pom=True)
    if not mavenpom:
        return

    pom = mavenpom.to_dict()

    licenses = []
    for lic in pom['licenses']:
        licenses.append(models.AssertedLicense(
            license=lic['name'],
            url=lic['url'],
            notice=lic['comments']
        ))

    # FIXME: we are skipping all the organization related fields, roles and the id
    authors = []
    for dev in pom['developers']:
        authors.append(models.Party(
                type=models.party_person,
                name=dev['name'],
                email=dev['email'],
                url=dev['url'],
        ))

    # FIXME: we are skipping all the organization related fields and roles
    contributors = []
    for cont in pom['contributors']:
        contributors.append(models.Party(
                type=models.party_person,
                name=cont['name'],
                email=cont['email'],
                url=cont['url'],
        ))


    name = pom['organization_name']
    url = pom['organization_url']
    if name or url:
        owners = [models.Party(type=models.party_org, name=name, url=url)]
    else:
        owners = []

    dependencies = OrderedDict()
    for scope, deps in pom['dependencies'].items():
        scoped_deps = dependencies[scope] = []
        for dep in deps:
            scoped_deps.append(models.Dependency(
                name='{group_id}:{artifact_id}'.format(**dep),
                version_constraint=dep['version'],
            ))

    # FIXME: there are still a lot of other data to map in a Package
    package = MavenPomPackage(
        location=location,
        name='{group_id}:{artifact_id}'.format(**pom),
        version=pom['version'],
        summary=pom['name'],
        description=pom['description'],
        homepage_url=pom['url'],
        asserted_licenses=licenses,
        authors=authors,
        owners=owners,
        contributors=contributors,
        dependencies=dependencies,
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
            if not is_pom(location):
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

                # second case: a maven .pom nested in META-INF
