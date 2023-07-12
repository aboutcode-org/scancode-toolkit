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
import os.path

import pytest

from commoncode import fileutils
from commoncode import text
from commoncode import testcase

from packagedcode import maven
from packagedcode import models
from packagedcode.licensing import get_license_detections_and_expression
from scancode.cli import run_scan
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES


class TestIsPom(testcase.FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_is_pom_maven2(self):
        test_dir = self.get_test_loc('maven2')
        for test_file in fileutils.resource_iter(test_dir, with_dirs=False):
            if test_file.endswith('.json'):
                continue

            loc = os.path.join(test_dir, test_file)
            assert maven.MavenPomXmlHandler.is_datafile(loc), loc + ' should be a POM'

    def test_is_pom_m2(self):
        test_dir = self.get_test_loc('m2')
        for test_file in fileutils.resource_iter(test_dir, with_dirs=False):
            if test_file.endswith('.json'):
                continue

            loc = os.path.join(test_dir, test_file)
            assert maven.MavenPomXmlHandler.is_datafile(loc), 'file://' + loc + ' should be a POM'

    def test_is_pom_is_detected_based_content(self):
        test_file = self.get_test_loc('maven_misc/properties-section.xml')
        assert maven.MavenPomXmlHandler.is_datafile(test_file)

    def test_is_pom_is_detected_based_content2(self):
        test_file = self.get_test_loc('maven_misc/properties-section-single.xml')
        assert maven.MavenPomXmlHandler.is_datafile(test_file)


def compare_results(results, test_pom_loc, expected_json_loc, regen=REGEN_TEST_FIXTURES):
    if regen:
        with open(expected_json_loc, 'w') as ex:
            json.dump(results, ex, indent=2)

    with io.open(expected_json_loc, encoding='utf-8') as ex:
        expected = json.load(ex)

    results_dump = json.dumps(results, indent=2)
    expected_dump = json.dumps(expected, indent=2)
    try:
        assert results == expected
    except AssertionError:
        test_pom_loc = 'file://' + test_pom_loc
        expected_json_loc = 'file://' + expected_json_loc
        expected = [test_pom_loc, expected_json_loc, expected_dump]
        assert results_dump == '\n'.join(expected)


def parse_pom(location=None):
    """
    Return a POM mapping from the Maven POM file at location.
    """
    pom = maven.get_maven_pom(location=location)
    if pom:
        return pom.to_dict()

    return {}


class BaseMavenCase(testcase.FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def check_parse_pom(self, test_pom, regen=REGEN_TEST_FIXTURES):
        """
        Test the parsing of POM at test_pom against an expected JSON
        from the same name with a .json extension.
        """
        test_pom_loc = self.get_test_loc(test_pom)
        expected_json_loc = f'{test_pom_loc}.json'
        results = parse_pom(location=test_pom_loc)
        compare_results(results, test_pom_loc, expected_json_loc, regen)

    def check_parse_to_package(self, test_pom, regen=REGEN_TEST_FIXTURES):
        """
        Test the creation of a Package from a POM at test_pom against an
        expected JSON from the same name with a .package.json extension.
        """
        test_pom_loc = self.get_test_loc(test_pom)
        expected_json_loc = f'{test_pom_loc}.package.json'
        packages_data = list(maven.MavenPomXmlHandler.parse(location=test_pom_loc))
        if not packages_data:
            results = {}
        else:
            package_data = packages_data.pop()
            package_data.populate_license_fields()
            results = package_data.to_dict()
        compare_results(results, test_pom_loc, expected_json_loc, regen)


class TestMavenMisc(BaseMavenCase):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_pom_non_pom_raise_expection(self):
        test_pom_loc = self.get_test_loc('maven_misc/non-maven.pom')
        try:
            parse_pom(location=test_pom_loc)
            raise Exception('Exception not raised')
        except Exception:
            pass

    def test_MavenPom_simple_creation(self):
        test_loc = self.get_test_loc('maven_misc/mini-pom.xml')
        pom = maven.MavenPom(test_loc)
        assert pom.artifact_id == 'activemq-camel'
        # note: there has been no parent resolving yet
        assert pom.group_id == None

    def test_pom_dependencies(self):
        test_loc = self.get_test_loc('maven2/activemq-camel/activemq-camel-pom.xml')
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
        assert results == expected

    def test_pom_issue_management_properties_are_resolved(self):
        test_loc = self.get_test_loc('maven2/xml-format-maven-plugin-3.0.6/xml-format-maven-plugin-3.0.6.pom')
        pom = maven.MavenPom(test_loc)
        pom.resolve()
        expected = dict([
            (u'system', 'GitHub Issues'),
            (u'url', 'https://github.com/acegi/xml-format-maven-plugin/issues')]
        )
        result = pom.issue_management
        assert result == expected

    def test_pom_dependencies_are_resolved(self):
        test_loc = self.get_test_loc('maven2/activemq-camel/activemq-camel-pom.xml')
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
        assert results == expected

    def test_parse_to_package_base(self):
        test_file = self.get_test_loc('maven_misc/spring-beans-4.2.2.RELEASE.pom.xml')
        self.check_parse_pom(test_file, regen=REGEN_TEST_FIXTURES)

    def test_parse_to_package_then_back(self):
        test_file = self.get_test_loc('maven_misc/spring-beans-4.2.2.RELEASE.pom.xml')
        packages = maven.MavenPomXmlHandler.parse(location=test_file)
        package = list(packages).pop()
        package2 = models.PackageData.from_dict(package.to_dict())
        assert package2.to_dict().items() == package.to_dict().items()

    def test_package_with_extracted_jars_and_metainf_poms_is_detected_correctly(self):
        test_dir = self.get_test_loc('maven_misc/extracted-jar/activiti-image-generator-7-201802-EA-sources.jar-extract/')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('maven_misc/extracted-jar/activiti-image-generator-expected.json')
        run_scan_click(['--package', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_package_with_extracted_jars_and_metainf_manifest_is_detected_correctly(self):
        test_dir = self.get_test_loc('maven_misc/extracted-jar/hsqldb-2.4.0.jar-extract/')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('maven_misc/extracted-jar/hsqldb-2.4.0-expected.json')
        run_scan_click(['--package', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_uberjars_is_detected_and_resource_assigned_correctly(self):
        test_dir = self.get_test_loc('maven_misc/uberjars/htrace-core-4.0.0-incubating')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('maven_misc/uberjars/htrace-core-4.0.0-incubating-expected.json')
        run_scan_click(['--package', '--license', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_maven_assembly_with_pom_and_manifest(self):
        test_dir = self.get_test_loc('maven_misc/assemble/johnzon-jsonb-1.2.11')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('maven_misc/assemble/johnzon-jsonb-1.2.11-expected.json')
        run_scan_click(['--package', '--license', '--license-diagnostics', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)

    def test_maven_assembly_with_pom_and_jar_manifest(self):
        test_dir = self.get_test_loc('maven_misc/assemble/numbers-1.7.4')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('maven_misc/assemble/numbers-1.7.4-expected.json')
        run_scan_click(['--package', '--license', '--license-diagnostics', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)
    
    def test_maven_unknown_reference_to_license_in_manifest(self):
        test_dir = self.get_test_loc('maven_misc/assemble/jackson-dataformat-xml-2.13.5')
        result_file = self.get_temp_file('json')
        expected_file = self.get_test_loc('maven_misc/assemble/jackson-dataformat-xml-2.13.5-expected.json')
        run_scan_click(['--package', '--license', '--license-diagnostics', '--processes', '-1', test_dir, '--json', result_file])
        check_json_scan(expected_file, result_file, remove_uuid=True, regen=REGEN_TEST_FIXTURES)


    def test_package_dependency_not_missing(self):
        test_file = self.get_test_loc('maven2/log4j/log4j-pom.xml')
        self.check_parse_to_package(test_file, regen=REGEN_TEST_FIXTURES)

    def test_package_dependency_populate_is_resolved_field(self):
        test_file = self.get_test_loc('maven_misc/parse/swagger-java-sample-app_2.10-1.3.1.pom')
        self.check_parse_to_package(test_file, regen=REGEN_TEST_FIXTURES)

    def test_get_top_level_resources(self):
        processes = 2
        test_dir = self.get_test_loc('maven_misc/extracted-jar/activiti-image-generator-7-201802-EA-sources.jar-extract')
        _, codebase = run_scan(
            input=test_dir,
            processes=processes,
            quiet=True,
            verbose=False,
            max_in_memory=0,
            return_results=False,
            return_codebase=True,
            system_package=True,
        )
        pom_resource = codebase.get_resource(
            'activiti-image-generator-7-201802-EA-sources.jar-extract/META-INF/maven/org.activiti/activiti-image-generator/pom.xml'
        )
        self.assertTrue(pom_resource)
        top_level_resources_paths = [
            r.path for r in maven.MavenPomXmlHandler.get_top_level_resources(pom_resource, codebase)
        ]
        expected_resource_paths = [
            'activiti-image-generator-7-201802-EA-sources.jar-extract/META-INF',
            'activiti-image-generator-7-201802-EA-sources.jar-extract/META-INF/MANIFEST.MF',
            'activiti-image-generator-7-201802-EA-sources.jar-extract/META-INF/maven',
            'activiti-image-generator-7-201802-EA-sources.jar-extract/META-INF/maven/org.activiti',
            'activiti-image-generator-7-201802-EA-sources.jar-extract/META-INF/maven/org.activiti/activiti-image-generator',
            'activiti-image-generator-7-201802-EA-sources.jar-extract/META-INF/maven/org.activiti/activiti-image-generator/pom.properties',
            'activiti-image-generator-7-201802-EA-sources.jar-extract/META-INF/maven/org.activiti/activiti-image-generator/pom.xml',
        ]
        self.assertEquals(expected_resource_paths, top_level_resources_paths)


class TestPomProperties(testcase.FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_resolve_properties(self):
        properties = {'groupId': 'org.apache'}
        value = '${groupId}.mycomponent'
        expected = 'org.apache.mycomponent'
        test = maven.MavenPom._replace_props(value, properties)
        assert test == expected

    def test_resolve_properties_with_expression(self):
        properties = {'groupId': 'org.apache'}
        value = '${groupId.substring(4)}.mycomponent'
        expected = 'apache.mycomponent'
        test = maven.MavenPom._replace_props(value, properties)
        assert test == expected

    def test_resolve_properties_with_substring_expression(self):
        properties = {'groupId': 'org.apache'}
        value = '${groupId.substring(0,3)}.mycomponent'
        expected = 'org.mycomponent'
        test = maven.MavenPom._replace_props(value, properties)
        assert test == expected

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

        assert test == expected

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
        assert test == expected

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
        assert test == expected

    def test_parse_can_run_without_pom_check(self):
        test_loc = self.get_test_loc('maven_misc/ant-1.6.5.maven')
        poms = maven.MavenPomXmlHandler.parse(test_loc)
        pom = list(poms)
        assert not pom

    def test_parse_will_load_extra_pom_properties_if_file_present(self):
        # there is a file at maven2_props/props_file/activiti-image-generator/pom.properties
        test_loc = self.get_test_loc('maven2_props/props_file/activiti-image-generator/pom.xml')
        poms = maven.MavenPomXmlHandler.parse(test_loc)
        pom = list(poms).pop()
        assert pom.namespace == 'org.activiti'


class TestMavenComputeNormalizedLicense(testcase.FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_get_license_detections_two_names_only(self):
        declared_license = [
            {'name': 'apache-2.0'},
            {'name': 'mit'}
        ]
        _detections, result = get_license_detections_and_expression(declared_license)
        expected = 'apache-2.0 AND mit'
        assert result == expected

    def test_get_license_detections_tree_nodes(self):
        declared_license = [
            {'name': 'apache-2.0'},
            {'name': 'mit'}
        ]
        _detections, result = get_license_detections_and_expression(declared_license)
        expected = 'apache-2.0 AND mit'
        assert result == expected

    def test_get_license_detections_with_unknown_url(self):
        declared_license = [
            {'name': 'apache-2.0', 'url': 'unknown'},
            {'name': 'mit'}
        ]
        _detections, result = get_license_detections_and_expression(declared_license)
        expected = 'apache-2.0 AND mit'
        assert result == expected

    def test_get_license_detections_with_unknown_url_known_comments(self):
        declared_license = [
            {'name': 'apache-2.0', 'url': 'unknown', 'comments': 'apache-2.0'},
            {'name': 'mit'}
        ]
        _detections, result = get_license_detections_and_expression(declared_license)
        expected = 'apache-2.0 AND mit'
        assert result == expected

    def test_get_license_detections_with_unknown_url_unknown_comments(self):
        declared_license = [
            {'name': 'apache-2.0', 'url': 'unknown', 'comments': 'unknown'},
            {'name': 'mit'}
        ]
        _detections, result = get_license_detections_and_expression(declared_license)
        expected = 'apache-2.0 AND mit'
        assert result == expected

    def test_get_license_detections_unknown_name(self):
        declared_license = [
            {'name': 'unknown', 'url': 'apache-2.0'},
            {'name': 'mit'}
        ]
        _detections, result = get_license_detections_and_expression(declared_license)
        expected = 'apache-2.0 AND mit'
        assert result == expected

    def test_get_license_detections_same_name_and_url(self):
        declared_license = [
            {'name': 'apache-2.0', 'url': 'apache-2.0'},
            {'name': 'mit'}
        ]
        _detections, result = get_license_detections_and_expression(declared_license)
        expected = 'apache-2.0 AND mit'
        assert result == expected

    def test_get_license_detections_same_name_url_comments(self):
        declared_license = [
            {'name': 'apache-2.0', 'url': 'apache-2.0', 'comments': 'apache-2.0'},
            {'name': 'mit'}
        ]
        _detections, result = get_license_detections_and_expression(declared_license)
        expected = 'apache-2.0 AND mit'
        assert result == expected

    def test_get_license_detections_with_url_invalid(self):
        declared_license = [
            {'name': 'MIT', 'url': 'LICENSE.txt'},
        ]
        _detections, result = get_license_detections_and_expression(declared_license)
        expected = 'mit'
        assert result == expected

    def test_get_license_detections_with_duplicated_license(self):
        declared_license = [
            {'name': 'LGPL'},
            {'name': 'GNU Lesser General Public License', 'url': 'http://www.gnu.org/licenses/lgpl.html'},
        ]
        _detections, result = get_license_detections_and_expression(declared_license)
        expected = 'lgpl-2.0-plus'
        assert result == expected


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


def create_test_function(test_pom_loc, test_name, check_pom=True, regen=REGEN_TEST_FIXTURES):
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


def build_tests(test_dir, clazz, prefix='test_maven2_parse_', check_pom=True, regen=REGEN_TEST_FIXTURES):
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
            prefix='test_maven2_parse_misc_', check_pom=True, regen=REGEN_TEST_FIXTURES)

build_tests(test_dir='maven_misc/parse', clazz=TestMavenDataDrivenPomMisc,
            prefix='test_maven2_package_misc_', check_pom=False, regen=REGEN_TEST_FIXTURES)


class TestMavenDataDrivenPomBasic(BaseMavenCase):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


build_tests(test_dir='maven2', clazz=TestMavenDataDrivenPomBasic,
            prefix='test_maven2_basic_parse_', check_pom=True, regen=REGEN_TEST_FIXTURES)
build_tests(test_dir='maven2', clazz=TestMavenDataDrivenPomBasic,
            prefix='test_maven2_basic_package_', check_pom=False, regen=REGEN_TEST_FIXTURES)


class TestMavenDataDrivenPomComprehensive(BaseMavenCase):
    pytestmark = pytest.mark.scanslow
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


# note: we use short dir names to deal with Windows long paths limitations
build_tests(test_dir='m2', clazz=TestMavenDataDrivenPomComprehensive,
            prefix='test_maven2_parse', check_pom=True, regen=REGEN_TEST_FIXTURES)
build_tests(test_dir='m2', clazz=TestMavenDataDrivenPomComprehensive,
            prefix='test_maven2_package', check_pom=False, regen=REGEN_TEST_FIXTURES)
