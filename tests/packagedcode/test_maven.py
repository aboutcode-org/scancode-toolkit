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
import json
import os.path

from commoncode import fileutils
from commoncode import text
from commoncode import testcase
from packagedcode import maven


def parse_pom(location=None, text=None, check_is_pom=False):
    """
    Return a POM mapping from the Maven POM file at location.
    """
    from packagedcode.maven import _get_mavenpom
    pom = _get_mavenpom(location, text, check_is_pom)
    if not pom:
        return {}
    return pom.to_dict()


class TestIsPom(testcase.FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_is_pom_non_pom(self):
        test_file = self.get_test_loc('maven_misc/non-maven.pom')
        assert not maven.is_pom(test_file)

    def test_is_pom_maven2(self):
        test_dir = self.get_test_loc('maven2')
        for test_file in fileutils.resource_iter(test_dir, with_dirs=False):
            if test_file.endswith('.json'):
                continue

            loc = os.path.join(test_dir, test_file)
            assert maven.is_pom(loc), loc + ' should be a POM'

    def test_is_pom_not_misc2(self):
        test_file = self.get_test_loc('maven_misc/parse/properties-section-single.xml')
        assert not maven.is_pom(test_file)

    def test_is_pom_m2(self):
        test_dir = self.get_test_loc('m2')
        for test_file in fileutils.resource_iter(test_dir, with_dirs=False):
            if test_file.endswith('.json'):
                continue

            loc = os.path.join(test_dir, test_file)
            assert maven.is_pom(loc), 'file://' + loc + ' should be a POM'

    def test_is_pom_not_misc(self):
        test_file = self.get_test_loc('maven_misc/parse/properties-section.xml')
        assert not maven.is_pom(test_file)


class TestMavenMisc(testcase.FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_pom_non_pom(self):
        test_pom_loc = self.get_test_loc('maven_misc/non-maven.pom')
        results = parse_pom(location=test_pom_loc, check_is_pom=True)
        assert {} == results
        results = parse_pom(location=test_pom_loc, check_is_pom=False)
        expected = OrderedDict([
            (u'model_version', None),
            (u'group_id', None),
            (u'artifact_id', None),
            (u'version', None),
            (u'classifier', None),
            (u'packaging ', 'jar'),
            (u'parent', {}),
            (u'name', 'Maven Abbot plugin'),
            (u'description', None),
            (u'inception_year', None),
            (u'url', None),
            (u'organization_name', None),
            (u'organization_url', None),
            (u'licenses', []),
            (u'developers', []),
            (u'contributors', []),
            (u'modules', []),
            (u'mailing_lists', []),
            (u'scm', {}),
            (u'issue_management', {}),
            (u'ci_management', {}),
            (u'distribution_management', {}),
            (u'repositories', []),
            (u'plugin_repositories', []),
            (u'dependencies', {})
        ])
        assert expected == results

    def test_pom_dependencies(self):
        test_loc = self.get_test_loc('maven2/activemq-camel-pom.xml')
        pom = maven.MavenPom(test_loc)
        expected = [
            ('compile', [
                (('commons-logging', 'commons-logging-api', 'latest.release'), True),
                (('org.apache.camel', 'camel-jms', 'latest.release'), True),
                (('${project.groupId}', 'activemq-core', 'latest.release'), True),
                (('${project.groupId}', 'activemq-pool', 'latest.release'), True),
                (('org.apache.geronimo.specs', 'geronimo-annotation_1.0_spec', 'latest.release'), False)
            ]),
            ('test', [
                (('${project.groupId}', 'activemq-core', 'latest.release'), True),
                (('org.apache.camel', 'camel-core', 'latest.release'), True),
                (('org.apache.camel', 'camel-spring', 'latest.release'), True),
                (('org.springframework', 'spring-test', 'latest.release'), True),
                (('junit', 'junit', 'latest.release'), True),
                (('org.hamcrest', 'hamcrest-all', 'latest.release'), True),
            ]),
        ]

        expected = [(s, sorted(v)) for s, v in expected]

        results = [(s, sorted(v)) for s, v in pom.dependencies.items()]
        assert expected == results

    def test_pom_dependencies_are_resolved(self):
        test_loc = self.get_test_loc('maven2/activemq-camel-pom.xml')
        pom = maven.MavenPom(test_loc)
        pom.resolve()
        expected = [
            (u'compile', [
                ((u'commons-logging', u'commons-logging-api', u'latest.release'), True),
                ((u'org.apache.camel', u'camel-jms', u'latest.release'), True),
                ((u'org.apache.activemq', u'activemq-core', u'latest.release'), True),
                ((u'org.apache.activemq', u'activemq-pool', u'latest.release'), True),
                ((u'org.apache.geronimo.specs', u'geronimo-annotation_1.0_spec', u'latest.release'), False)
            ]),
            (u'test', [
                ((u'org.apache.activemq', u'activemq-core', u'latest.release'), True),
                ((u'org.apache.camel', u'camel-core', u'latest.release'), True),
                ((u'org.apache.camel', u'camel-spring', u'latest.release'), True),
                ((u'org.springframework', u'spring-test', u'latest.release'), True),
                ((u'junit', u'junit', u'latest.release'), True),
                ((u'org.hamcrest', u'hamcrest-all', u'latest.release'), True),
            ]),
        ]
        expected = [(s, sorted(v)) for s, v in expected]

        results = [(s, sorted(v)) for s, v in pom.dependencies.items()]
        assert expected == results

    def test_parse_to_package(self):
        test_file = self.get_test_loc('maven_misc/spring-beans-4.2.2.RELEASE.pom.xml')
        package = maven.parse(test_file)

        assert isinstance(package, maven.MavenPomPackage)
        expected = [
            ('type', u'Apache Maven POM'),
            ('name', u'org.springframework:spring-beans'),
            ('version', u'4.2.2.RELEASE'),
            ('primary_language', u'Java'),
            ('packaging', u'archive'),
            ('description', u'Spring Beans'),
            ('payload_type', None),
            ('size', None),
            ('release_date', None),
            ('authors', [OrderedDict([
                ('type', u'person'),
                ('name', u'Juergen Hoeller'),
                ('email', u'jhoeller@pivotal.io'),
                ('url', None)
            ])]),
            ('maintainers', []),
            ('contributors', []),
            ('owners', [OrderedDict([
                ('type', u'organization'),
                ('name', u'Spring IO'),
                ('email', None),
                ('url', u'http://projects.spring.io/spring-framework')
            ])]),
            ('packagers', []),
            ('distributors', []),
            ('vendors', []),
            ('keywords', []),
            ('keywords_doc_url', None),
            ('homepage_url', u'https://github.com/spring-projects/spring-framework'),
            ('download_urls', []),
            ('download_sha1', None),
            ('download_sha256', None),
            ('download_md5', None),
            ('bug_tracking_url', None),
            ('support_contacts', []),
            ('code_view_url', None),
            ('vcs_tool', None),
            ('vcs_repository', None),
            ('vcs_revision', None),
            ('copyright', None),
            ('asserted_license', 
                u'The Apache Software License, Version 2.0'
                u'\n'
                u'http://www.apache.org/licenses/LICENSE-2.0.txt',
            ),
            ('license_expression', None),
            ('license_texts', []),
            ('notice_text', None),
            ('dependencies',
             {u'compile': [
                OrderedDict([('type', u'Apache Maven POM'), ('name', u'javax.el:javax.el-api'), ('version', u'2.2.5')]),
                OrderedDict([('type', u'Apache Maven POM'), ('name', u'javax.inject:javax.inject'), ('version', u'1')]),
                OrderedDict([('type', u'Apache Maven POM'), ('name', u'org.codehaus.groovy:groovy-all'), ('version',u'2.4.5')]),
                OrderedDict([('type', u'Apache Maven POM'), ('name', u'org.springframework:spring-core'), ('version', u'4.2.2.RELEASE')]),
                OrderedDict([('type', u'Apache Maven POM'), ('name', u'org.yaml:snakeyaml'), ('version',  u'1.16')]),
            ]}),
            ('related_packages', [])
        ]
        assert expected == package.to_dict().items()
        package.validate()

    def test_parse_to_package_then_back(self):
        test_file = self.get_test_loc('maven_misc/spring-beans-4.2.2.RELEASE.pom.xml')
        package = maven.parse(test_file)
        package2 = maven.MavenPomPackage(**package.to_dict())
        assert package.to_dict().items() == package2.to_dict().items()


class TestPomProperties(testcase.FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_resolve_properties(self):
        properties = {'groupId': 'org.apache'}
        value = '${groupId}.mycomponent'
        expected = 'org.apache.mycomponent'
        test = maven.MavenPom._replace_props(value, properties)
        assert expected == test

    def test_resolve_properties_with_expression(self):
        properties = {'groupId': 'org.apache'}
        value = '${groupId.substring(4)}.mycomponent'
        expected = 'apache.mycomponent'
        test = maven.MavenPom._replace_props(value, properties)
        assert expected == test

    def test_resolve_properties_with_substring_expression(self):
        properties = {'groupId': 'org.apache'}
        value = '${groupId.substring(0,3)}.mycomponent'
        expected = 'org.mycomponent'
        test = maven.MavenPom._replace_props(value, properties)
        assert expected == test

    def test_get_properties(self):
        test_loc = self.get_test_loc('maven2_props/multiple/pom.xml')
        pom = maven.MavenPom(test_loc)
        test = pom.properties
        expected = {
            'groupId': 'org.apache.geronimo.bundles',
            'project.groupId': 'org.apache.geronimo.bundles',
            'pom.groupId': 'org.apache.geronimo.bundles',

            'artifactId': 'axis',
            'project.artifactId': 'axis',
            'pom.artifactId': 'axis',

            'version': '1.4_1-SNAPSHOT',
            'project.version': '1.4_1-SNAPSHOT',
            'pom.version': '1.4_1-SNAPSHOT',

            'parent.groupId': 'org.apache.geronimo.framework',
            'project.parent.groupId': 'org.apache.geronimo.framework',
            'pom.parent.groupId': 'org.apache.geronimo.framework',

            'parent.artifactId': 'framework',
            'project.parent.artifactId': 'framework',
            'pom.parent.artifactId': 'framework',

            'parent.version': '3.0-SNAPSHOT',
            'project.parent.version': '3.0-SNAPSHOT',
            'pom.parent.version': '3.0-SNAPSHOT',

            'pkgArtifactId': 'axis',
            'pkgGroupId': 'org.apache.axis',
            'pkgVersion': '1.4',
        }

        assert expected == test

    def test_get_properties_single(self):
        test_loc = self.get_test_loc('maven2_props/single/pom.xml')
        pom = maven.MavenPom(test_loc)
        test = pom.properties
        expected = {
            'artifactId': None,
            'groupId': None,
            'pkgGroupId': 'org.apache.axis',
            'pom.artifactId': None,
            'pom.groupId': None,
            'pom.version': None,
            'project.artifactId': None,
            'project.groupId': None,
            'project.version': None,
            'version': None
        }

        assert expected == test

    def test_parse_can_run_without_pom_check(self):
        test_loc = self.get_test_loc('maven_misc/ant-1.6.5.maven')
        pom = maven.parse(test_loc, check_is_pom=False)
        assert pom
        pom = maven.parse(test_loc, check_is_pom=True)
        assert not pom


class BaseMavenCase(testcase.FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def check_parse_pom(self, test_pom, regen=False):
        """
        Test the parsing of POM at test_pom against an expected JSON
        from the same name with a .json extension.
        """
        test_pom_loc = self.get_test_loc(test_pom)
        expected_json_loc = test_pom_loc + '.json'
        parsed_pom = parse_pom(location=test_pom_loc)

        if regen:
            with codecs.open(expected_json_loc, 'wb', encoding='utf-8') as ex:
                json.dump(parsed_pom, ex, indent=2)  # , separators=(',', ': '))

        with codecs.open(expected_json_loc, encoding='utf-8') as ex:
            expected = json.load(ex, object_pairs_hook=OrderedDict)

        assert expected.items() == parsed_pom.items()

    def check_parse_to_package(self, test_pom, regen=False):
        """
        Test the creation of a Package from a POM at test_pom against an
        expected JSON from the same name with a .package.json extension.
        """
        test_pom_loc = self.get_test_loc(test_pom)
        expected_json_loc = test_pom_loc + '.package.json'
        package = maven.parse(location=test_pom_loc)
        if not package:
            package = {}
        else:
            package = package.to_dict()

        if regen:
            with codecs.open(expected_json_loc, 'wb', encoding='utf-8') as ex:
                json.dump(package, ex, indent=2)  # , separators=(',', ': '))

        with codecs.open(expected_json_loc, encoding='utf-8') as ex:
            expected = json.load(ex, object_pairs_hook=OrderedDict)

        assert expected.items() == package.items()


def relative_walk(dir_path):
    """
    Walk path and yield POM files paths relative to dir_path.
    """
    for base_dir, _dirs, files in os.walk(dir_path):
        for file_name in files:
            if file_name.endswith('.json'):
                continue
            file_path = os.path.join(base_dir, file_name)
            file_path = file_path.replace(dir_path, '', 1)
            file_path = file_path.strip(os.path.sep)
            yield file_path


def create_test_function(test_pom_loc, test_name, check_pom=True, regen=False):
    """
    Return a test function closed on test arguments.
    If check_parse_pom is True, test the POM parsing; otherwise, test Package creation
    """
    # closure on the test params
    if check_pom:

        def test_pom(self):
            self.check_parse_pom(test_pom_loc, regen)

    else:

        def test_pom(self):
            self.check_parse_to_package(test_pom_loc, regen)

    # set a proper function name to display in reports and use in discovery
    # function names are best as bytes
    if isinstance(test_name, unicode):
        test_name = test_name.encode('utf-8')
    test_pom.__name__ = test_name
    test_pom.funcname = test_name
    return test_pom


def build_tests(test_dir, clazz, prefix='test_maven2_parse_', check_pom=True, regen=False):
    """
    Dynamically build test methods for each POMs in `test_dir`  and
    attach the test method to the `clazz` class.
    If check_parse_pom is True, test the POM parsing; otherwise, test Package creation
    """
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')
    test_dir = os.path.join(test_data_dir, test_dir)
    # loop through all items and attach a test method to our test class
    for test_file in relative_walk(test_dir):
        test_name = prefix + text.python_safe_name(test_file)
        test_pom_loc = os.path.join(test_dir, test_file)
        test_method = create_test_function(test_pom_loc, test_name, check_pom=check_pom, regen=regen)
        # attach that method to the class
        setattr(clazz, test_name, test_method)


class TestMavenDataDrivenParsePom(BaseMavenCase): 
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


build_tests(test_dir='maven_misc/parse', clazz=TestMavenDataDrivenParsePom, prefix='test_maven2_parse_', check_pom=True, regen=False)


class TestMavenDataDrivenParsePomBasic(BaseMavenCase):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


build_tests(test_dir='maven2', clazz=TestMavenDataDrivenParsePomBasic, prefix='test_maven2_basic_parse_', check_pom=True, regen=False)


class TestMavenDataDrivenCreatePackageBasic(BaseMavenCase):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


build_tests(test_dir='maven2', clazz=TestMavenDataDrivenCreatePackageBasic, prefix='test_maven2_basic_package_', check_pom=False, regen=False)


class TestMavenDataDrivenParsePomComprehensive(BaseMavenCase):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


# note: we use short dir names to deal with Windows long paths limitations
build_tests(test_dir='m2', clazz=TestMavenDataDrivenParsePomComprehensive, prefix='test_maven2_parse', check_pom=True, regen=False)


class TestMavenDataDrivenCreatePackageComprehensive(BaseMavenCase):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


# note: we use short dir names to deal with Windows long paths limitations
build_tests(test_dir='m2', clazz=TestMavenDataDrivenCreatePackageComprehensive, prefix='test_maven2_package', check_pom=False, regen=False)

