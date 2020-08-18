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

import io
from collections import OrderedDict
import json
import os.path

import pytest

from commoncode import compat
from commoncode import fileutils
from commoncode import text
from commoncode import testcase
from packagedcode import maven
from scancode.resource import Codebase


mode = 'w'


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
        test_file = self.get_test_loc('maven_misc/properties-section-single.xml')
        assert not maven.is_pom(test_file)

    def test_is_pom_m2(self):
        test_dir = self.get_test_loc('m2')
        for test_file in fileutils.resource_iter(test_dir, with_dirs=False):
            if test_file.endswith('.json'):
                continue

            loc = os.path.join(test_dir, test_file)
            assert maven.is_pom(loc), 'file://' + loc + ' should be a POM'

    def test_is_pom_not_misc(self):
        test_file = self.get_test_loc('maven_misc/properties-section.xml')
        assert not maven.is_pom(test_file)


def compare_results(results, test_pom_loc, expected_json_loc, regen=False):
    if regen:
        with open(expected_json_loc, mode) as ex:
            json.dump(results, ex, indent=2)

    with io.open(expected_json_loc, encoding='utf-8') as ex:
        expected = json.load(ex, object_pairs_hook=OrderedDict)

    results_dump = json.dumps(results, indent=2)
    expected_dump = json.dumps(expected, indent=2)
    try:
        assert expected_dump == results_dump
    except AssertionError:
        test_pom_loc = 'file://' + test_pom_loc
        expected_json_loc = 'file://' + expected_json_loc
        expected = [test_pom_loc, expected_json_loc, expected_dump]
        assert '\n'.join(expected) == results_dump


def parse_pom(location=None, text=None, check_is_pom=False):
    """
    Return a POM mapping from the Maven POM file at location.
    """
    pom = maven.get_maven_pom(location, text, check_is_pom)
    if not pom:
        return {}
    return pom.to_dict()


class BaseMavenCase(testcase.FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def check_parse_pom(self, test_pom, regen=False):
        """
        Test the parsing of POM at test_pom against an expected JSON
        from the same name with a .json extension.
        """
        test_pom_loc = self.get_test_loc(test_pom)
        expected_json_loc = test_pom_loc + '.json'
        results = parse_pom(location=test_pom_loc)
        compare_results(results, test_pom_loc, expected_json_loc, regen)

    def check_parse_to_package(self, test_pom, regen=False):
        """
        Test the creation of a Package from a POM at test_pom against an
        expected JSON from the same name with a .package.json extension.
        """
        test_pom_loc = self.get_test_loc(test_pom)
        expected_json_loc = test_pom_loc + '.package.json'
        package = maven.parse(location=test_pom_loc)
        if not package:
            results = {}
        else:
            package.license_expression = package.compute_normalized_license()
            results = package.to_dict()
        compare_results(results, test_pom_loc, expected_json_loc, regen)


class TestMavenMisc(BaseMavenCase):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_pom_non_pom(self):
        test_pom_loc = self.get_test_loc('maven_misc/non-maven.pom')
        results = parse_pom(location=test_pom_loc, check_is_pom=True)
        assert {} == results
        self.check_parse_pom(test_pom_loc, regen=False)

    def test_MavenPom_simple_creation(self):
        test_loc = self.get_test_loc('maven_misc/mini-pom.xml')
        pom = maven.MavenPom(test_loc)
        assert 'activemq-camel' == pom.artifact_id
        # note: there has been no parent resolving yet
        assert None == pom.group_id

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

    def test_pom_issue_management_properties_are_resolved(self):
        test_loc = self.get_test_loc('maven2/xml-format-maven-plugin-3.0.6.pom')
        pom = maven.MavenPom(test_loc)
        pom.resolve()
        expected = OrderedDict([
            (u'system', 'GitHub Issues'),
            (u'url', 'https://github.com/acegi/xml-format-maven-plugin/issues')]
        )
        result = pom.issue_management
        assert expected == result

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

    def test_parse_to_package_base(self):
        test_file = self.get_test_loc('maven_misc/spring-beans-4.2.2.RELEASE.pom.xml')
        self.check_parse_pom(test_file, regen=False)

    def test_parse_to_package_and_validate(self):
        test_file = self.get_test_loc('maven_misc/spring-beans-4.2.2.RELEASE.pom.xml')
        package = maven.parse(test_file)
        assert isinstance(package, maven.MavenPomPackage)

    def test_parse_to_package_then_back(self):
        test_file = self.get_test_loc('maven_misc/spring-beans-4.2.2.RELEASE.pom.xml')
        package = maven.parse(test_file)
        package2 = maven.MavenPomPackage(**package.to_dict(exclude_properties=True))
        assert package.to_dict().items() == package2.to_dict().items()

    def test_package_root_is_properly_returned_for_metainf_poms(self):
        from packagedcode.plugin_package import PackageScanner
        test_dir = self.get_test_loc('maven_misc/package_root')
        codebase = Codebase(test_dir, resource_attributes=PackageScanner.resource_attributes)
        manifest_resource = [r for r in codebase.walk() if r.name == 'pom.xml'][0]
        packages = list(maven.MavenPomPackage.recognize(manifest_resource.location))
        assert packages
        manifest_resource.packages.append(packages[0].to_dict())
        manifest_resource.save(codebase)
        proot = maven.MavenPomPackage.get_package_root(manifest_resource, codebase)
        assert 'activiti-image-generator-7-201802-EA-sources.jar-extract' == proot.name

    def test_package_dependency_not_missing(self):
        test_file = self.get_test_loc('maven2/log4j-pom.xml')
        self.check_parse_to_package(test_file, regen=False)


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

    def test_get_properties_advanced(self):
        test_loc = self.get_test_loc('maven2_props/xml-format-maven-plugin-3.0.6.pom')
        pom = maven.MavenPom(test_loc)
        test = pom.properties
        expected = {
            'artifactId': 'xml-format-maven-plugin',
            'github.org': 'acegi',
            'github.repo': 'xml-format-maven-plugin',
            'groupId': 'au.com.acegi',
            'license.excludes': '**/test*.xml,**/invalid.xml',
            'license.licenseName': 'apache_v2',
            'maven.compiler.source': '1.7',
            'maven.compiler.target': '1.7',
            'maven.enforcer.java': '1.7',
            'parent.artifactId': u'acegi-standard-project',
            'parent.groupId': u'au.com.acegi',
            'parent.version': '0.1.4',
            'pom.artifactId': 'xml-format-maven-plugin',
            'pom.groupId': 'au.com.acegi',
            'pom.parent.artifactId': u'acegi-standard-project',
            'pom.parent.groupId': u'au.com.acegi',
            'pom.parent.version': '0.1.4',
            'pom.version': '3.0.6',
            'project.artifactId': 'xml-format-maven-plugin',
            'project.groupId': 'au.com.acegi',
            'project.parent.artifactId': u'acegi-standard-project',
            'project.parent.groupId': u'au.com.acegi',
            'project.parent.version': '0.1.4',
            'project.version': '3.0.6',
            'version': '3.0.6'
        }
        assert expected == test

    def test_parse_can_run_without_pom_check(self):
        test_loc = self.get_test_loc('maven_misc/ant-1.6.5.maven')
        pom = maven.parse(test_loc, check_is_pom=False)
        assert pom
        pom = maven.parse(test_loc, check_is_pom=True)
        assert not pom

    def test_parse_will_load_extra_pom_properties_if_file_present(self):
        # there is a file at maven2_props/props_file/activiti-image-generator/pom.properties
        test_loc = self.get_test_loc('maven2_props/props_file/activiti-image-generator/pom.xml')
        pom = maven.parse(test_loc, check_is_pom=False)
        assert 'org.activiti' == pom.namespace


class TestMavenComputeNormalizedLicense(testcase.FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_compute_normalized_license_two_names_only(self):
        declared_license = [
            {'name': 'apache-2.0'},
            {'name': 'mit'}
        ]
        result = maven.compute_normalized_license(declared_license)
        expected = 'apache-2.0 AND mit'
        assert expected == result

    def test_compute_normalized_license_tree_nodes(self):
        declared_license = [
            {'name': 'apache-2.0'},
            {'name': 'mit'}
        ]
        result = maven.compute_normalized_license(declared_license)
        expected = 'apache-2.0 AND mit'
        assert expected == result

    def test_compute_normalized_license_with_unknown_url(self):
        declared_license = [
            {'name': 'apache-2.0', 'url': 'unknown'},
            {'name': 'mit'}
        ]
        result = maven.compute_normalized_license(declared_license)
        expected = 'apache-2.0 AND mit'
        assert expected == result

    def test_compute_normalized_license_with_unknown_url_known_comments(self):
        declared_license = [
            {'name': 'apache-2.0', 'url': 'unknown', 'comments': 'apache-2.0'},
            {'name': 'mit'}
        ]
        result = maven.compute_normalized_license(declared_license)
        expected = 'apache-2.0 AND mit'
        assert expected == result

    def test_compute_normalized_license_with_unknown_url_unknown_comments(self):
        declared_license = [
            {'name': 'apache-2.0', 'url': 'unknown', 'comments': 'unknown'},
            {'name': 'mit'}
        ]
        result = maven.compute_normalized_license(declared_license)
        expected = 'apache-2.0 AND mit'
        assert expected == result

    def test_compute_normalized_license_unknown_name(self):
        declared_license = [
            {'name': 'unknown', 'url': 'apache-2.0'},
            {'name': 'mit'}
        ]
        result = maven.compute_normalized_license(declared_license)
        expected = '(unknown AND apache-2.0) AND mit'
        assert expected == result

    def test_compute_normalized_license_same_name_and_url(self):
        declared_license = [
            {'name': 'apache-2.0', 'url': 'apache-2.0'},
            {'name': 'mit'}
        ]
        result = maven.compute_normalized_license(declared_license)
        expected = 'apache-2.0 AND mit'
        assert expected == result

    def test_compute_normalized_license_same_name_url_comments(self):
        declared_license = [
            {'name': 'apache-2.0', 'url': 'apache-2.0', 'comments': 'apache-2.0'},
            {'name': 'mit'}
        ]
        result = maven.compute_normalized_license(declared_license)
        expected = 'apache-2.0 AND mit'
        assert expected == result

    def test_compute_normalized_license_with_url_invalid(self):
        declared_license = [
            {'name': 'MIT', 'url': 'LICENSE.txt'},
        ]
        result = maven.compute_normalized_license(declared_license)
        expected = 'mit'
        assert expected == result

    def test_compute_normalized_license_with_duplicated_license(self):
        declared_license = [
            {'name': 'LGPL'},
            {'name': 'GNU Lesser General Public License', 'url': 'http://www.gnu.org/licenses/lgpl.html'},
        ]
        result = maven.compute_normalized_license(declared_license)
        expected = 'lgpl-2.0-plus'
        assert expected == result


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
    if isinstance(test_name, bytes):
        test_name = test_name.decode('utf-8')

    test_pom.__name__ = test_name
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


class TestMavenDataDrivenPomMisc(BaseMavenCase):
    pytestmark = pytest.mark.scanslow
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

build_tests(test_dir='maven_misc/parse', clazz=TestMavenDataDrivenPomMisc,
            prefix='test_maven2_parse_misc_', check_pom=True, regen=False)

build_tests(test_dir='maven_misc/parse', clazz=TestMavenDataDrivenPomMisc,
            prefix='test_maven2_package_misc_', check_pom=False, regen=False)


class TestMavenDataDrivenPomBasic(BaseMavenCase):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

build_tests(test_dir='maven2', clazz=TestMavenDataDrivenPomBasic,
            prefix='test_maven2_basic_parse_', check_pom=True, regen=False)
build_tests(test_dir='maven2', clazz=TestMavenDataDrivenPomBasic,
            prefix='test_maven2_basic_package_', check_pom=False, regen=False)


class TestMavenDataDrivenPomComprehensive(BaseMavenCase):
    pytestmark = pytest.mark.scanslow
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

# note: we use short dir names to deal with Windows long paths limitations
build_tests(test_dir='m2', clazz=TestMavenDataDrivenPomComprehensive,
            prefix='test_maven2_parse', check_pom=True, regen=False)
build_tests(test_dir='m2', clazz=TestMavenDataDrivenPomComprehensive,
            prefix='test_maven2_package', check_pom=False, regen=False)
