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

from collections import OrderedDict
import os.path
import json
import shutil

import bz2file

from commoncode import text
from commoncode import testcase
from commoncode import fileutils

from packagedcode import maven
from packagedcode import xmlutils


class BaseMavenCase(testcase.FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def bz_uncompress(self, location):
        """
        Uncompress the bzip2-compressed file at location and return the path to
        the uncompressed file.
        """
        file_name = fileutils.file_name(location)
        # remove the bz2 extension
        file_name, _ext = os.path.splitext(file_name)
        target_loc = self.get_temp_file(extension='', file_name=file_name)

        with bz2file.BZ2File(location, 'rb') as compressed:
            with open(target_loc, 'wb') as uncompressed:
                uncompressed.write(compressed.read())
        return target_loc

    def bz_compress(self, location):
        """
        Compress the file at location with bzip2 and return the path to the
        compressed file.
        """
        file_name = fileutils.file_name(location)
        if not location.endswith('.bz2'):
            file_name = file_name + '.bz2'

        target_loc = self.get_temp_file(extension='', file_name=file_name)

        with open(location, 'rb') as uncompressed:
            with bz2file.BZ2File(target_loc , 'wb') as compressed:
                compressed.write(uncompressed.read())
        return target_loc


    def check_pom(self, test_pom_loc, expected_json_loc, regen=False):
        if not os.path.isabs(test_pom_loc):
            test_pom_loc = self.get_test_loc(test_pom_loc)
        if not os.path.isabs(expected_json_loc):
            expected_json_loc = self.get_test_loc(expected_json_loc)

        # uncompress test if needed
        if test_pom_loc.endswith('.bz2'):
            test_pom_loc = self.bz_uncompress(test_pom_loc)
        # test proper
        results = maven.parse_pom(location=test_pom_loc)
        compressed_exp = expected_json_loc.endswith('.bz2')

        if regen:
            regened_exp_loc = self.get_temp_file(extension='.bz2')

            with open(regened_exp_loc, 'wb') as ex:
                json.dump(results, ex, ensure_ascii=True, indent=2)

            if compressed_exp:
                regened_exp_loc = self.bz_compress(regened_exp_loc)

            expected_dir = os.path.dirname(expected_json_loc)
            if not os.path.exists(expected_dir):
                os.makedirs(expected_dir)
            shutil.copy(regened_exp_loc, expected_json_loc)

        # uncompress expected if needed
        if compressed_exp:
            expected_json_loc = self.bz_uncompress(expected_json_loc)

        with open(expected_json_loc) as ex:
            expected = json.load(ex)

        assert expected == results


class TestMavenPom(BaseMavenCase):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_pom_version_maven2(self):
        non_poms = [
            'non-maven.pom',
        ]
        test_dir = self.get_test_loc('maven/maven2')
        for test_file in os.listdir(test_dir):
            loc = os.path.join(test_dir, test_file)
            if test_file in non_poms:
                assert None == maven.pom_version(loc)
            else:
                assert 2 == maven.pom_version(loc)

    def test_resolve_properties(self):
        properties = {'groupId': 'org.apache'}
        value = '${groupId}.mycomponent'
        expected = 'org.apache.mycomponent'
        test = maven.resolve_properties(value, properties)
        assert expected == test

    def test_resolve_properties_with_expression(self):
        properties = {'groupId': 'org.apache'}
        value = '${groupId.substring(4)}.mycomponent'
        expected = 'apache.mycomponent'
        test = maven.resolve_properties(value, properties)
        assert expected == test

    def test_resolve_properties_with_substring_expression(self):
        properties = {'groupId': 'org.apache'}
        value = '${groupId.substring(0,3)}.mycomponent'
        expected = 'org.mycomponent'
        test = maven.resolve_properties(value, properties)
        assert expected == test

    def test_properties_get_pom_defined_properties(self):
        test_loc = self.get_test_loc('maven/variable_replacement/properties-section.xml')
        handler = maven.get_pom_defined_properties
        test = xmlutils.parse(test_loc, handler)
        expected = {'pkgArtifactId': 'axis',
                    'pkgGroupId': 'org.apache.axis',
                    'pkgVersion': '1.4'}
        assert expected == test

    def test_properties_get_pom_defined_properties_single(self):
        test_loc = self.get_test_loc('maven/variable_replacement/properties-section-single.xml')
        handler = maven.get_pom_defined_properties
        test = xmlutils.parse(test_loc, handler)
        expected = {'pkgGroupId': 'org.apache.axis'}
        assert expected == test

    def test_properties_get_standard_properties(self):
        test_loc = self.get_test_loc('maven/variable_replacement/properties-section.xml')
        handler = maven.get_standard_properties
        test = xmlutils.parse(test_loc, handler)
        expected = {
            'artifactId': 'axis',
            'groupId': 'org.apache.geronimo.bundles',
            'packaging': 'bundle',
            'parent.artifactId': 'framework',
            'parent.groupId': 'org.apache.geronimo.framework',
            'parent.version': '3.0-SNAPSHOT',
            'pom.artifactId': 'axis',
            'pom.description':
        'This bundle simply wraps ${pkgArtifactId}-${pkgVersion}.jar.',
            'pom.groupId': 'org.apache.geronimo.bundles',
            'pom.packaging': 'bundle',
            'pom.parent.artifactId': 'framework',
            'pom.parent.groupId': 'org.apache.geronimo.framework',
            'pom.parent.version': '3.0-SNAPSHOT',
            'pom.version': '1.4_1-SNAPSHOT',
            'project.artifactId': 'axis',
            'project.description':
        'This bundle simply wraps ${pkgArtifactId}-${pkgVersion}.jar.',
            'project.groupId': 'org.apache.geronimo.bundles',
            'project.packaging': 'bundle',
            'project.parent.artifactId': 'framework',
            'project.parent.groupId': 'org.apache.geronimo.framework',
            'project.parent.version': '3.0-SNAPSHOT',
            'project.version': '1.4_1-SNAPSHOT',
            'version': '1.4_1-SNAPSHOT'}
        assert expected == test

    def test_properties_get_properties(self):
        test_loc = self.get_test_loc('maven/variable_replacement/properties-section.xml')
        handler = maven.get_properties
        test = xmlutils.parse(test_loc, handler)
        expected = {
            'artifactId': u'axis',
            'groupId': u'org.apache.geronimo.bundles',
            'maven.javanet.project': u'maven2-repository',
            'packaging': u'bundle',
            'parent.artifactId': u'framework',
            'parent.groupId': u'org.apache.geronimo.framework',
            'parent.version': u'3.0-SNAPSHOT',
            'pkgArtifactId': u'axis',
            'pkgGroupId': u'org.apache.axis',
            'pkgVersion': u'1.4',
            'pom.artifactId': u'axis',
            'pom.description': u'This bundle simply wraps axis-1.4.jar.',
            'pom.groupId': u'org.apache.geronimo.bundles',
            'pom.packaging': u'bundle',
            'pom.parent.artifactId': u'framework',
            'pom.parent.groupId': u'org.apache.geronimo.framework',
            'pom.parent.version': u'3.0-SNAPSHOT',
            'pom.version': u'1.4_1-SNAPSHOT',
            'project.artifactId': u'axis',
            'project.description': u'This bundle simply wraps axis-1.4.jar.',
            'project.groupId': u'org.apache.geronimo.bundles',
            'project.packaging': u'bundle',
            'project.parent.artifactId': u'framework',
            'project.parent.groupId': u'org.apache.geronimo.framework',
            'project.parent.version': u'3.0-SNAPSHOT',
            'project.version': u'1.4_1-SNAPSHOT',
            'version': u'1.4_1-SNAPSHOT'}
        assert expected == test

    def test_parse_pom_non_pom(self):
        test_pom_loc = self.get_test_loc('maven/maven2/non-maven.pom')
        results = maven.parse_pom(location=test_pom_loc)
        assert {} == results

    def test_parse_pom_partial_pom_mysql_connector(self):
        self.check_pom('maven/maven2/mysql-connector-java-5.0.4.pom',
                       'maven/expectations/mysql-connector-java-5.0.4.pom.json')

    def test_parse_pom_partial_pom_plexus(self):
        self.check_pom('maven/maven2/plexus-root-1.0.3.pom',
                       'maven/expectations/plexus-root-1.0.3.pom.json')

    def test_parse_pom_property_resolution_dbwebx_pom_xml(self):
        self.check_pom('maven/variable_replacement/dbwebx_pom.xml',
                       'maven/expectations/dbwebx_pom.xml.json')

    def test_parse_pom_property_resolution_fna2_pom_xml(self):
        self.check_pom('maven/variable_replacement/fna2_pom.xml',
                       'maven/expectations/fna2_pom.xml.json')

    def test_parse_pom_property_resolution_fna_pom_project_xml(self):
        self.check_pom('maven/variable_replacement/fna_pom_project.xml',
                       'maven/expectations/fna_pom_project.xml.json')

    def test_parse_pom_property_resolution_gero_pom_xml(self):
        self.check_pom('maven/variable_replacement/gero_pom.xml',
                       'maven/expectations/gero_pom.xml.json')

    def test_parse_pom_property_resolution_idega_pom_xml(self):
        self.check_pom('maven/variable_replacement/idega_pom.xml',
                       'maven/expectations/idega_pom.xml.json')

    def test_parse_pom_property_resolution_logback_access_pom(self):
        self.check_pom('maven/variable_replacement/logback-access.pom',
                       'maven/expectations/logback-access.pom.json')

    def test_parse_pom_property_resolution_palmed_project_xml(self):
        self.check_pom('maven/variable_replacement/palmed_project.xml',
                       'maven/expectations/palmed_project.xml.json')

    def test_parse_pom_property_resolution_proper_pom_xml(self):
        self.check_pom('maven/variable_replacement/proper_pom.xml',
                       'maven/expectations/proper_pom.xml.json')

    def test_parse_pom_property_resolution_rel_pom_xml(self):
        self.check_pom('maven/variable_replacement/rel_pom.xml',
                       'maven/expectations/rel_pom.xml.json')

    def test_parse_pom_property_resolution_sea_pom_xml(self):
        self.check_pom('maven/variable_replacement/sea_pom.xml',
                       'maven/expectations/sea_pom.xml.json')

    def test_parse_pom_property_resolution_specs_1_3_pom(self):
        self.check_pom('maven/variable_replacement/specs-1.3.pom',
                       'maven/expectations/specs-1.3.pom.json')

    def test_parse_pom_property_resolution_uni_pom_xml(self):
        self.check_pom('maven/variable_replacement/uni_pom.xml',
                       'maven/expectations/uni_pom.xml.json')

    def test_parse_pom_property_resolution_urwerk_pom_xml(self):
        self.check_pom('maven/variable_replacement/urwerk_pom.xml',
                       'maven/expectations/urwerk_pom.xml.json')

    def test_parse_pom_property_resolution_urwerky_pom_xml(self):
        self.check_pom('maven/variable_replacement/urwerky_pom.xml',
                       'maven/expectations/urwerky_pom.xml.json')

    def test_parse_pom_property_resolution_webre_pom_xml(self):
        self.check_pom('maven/variable_replacement/webre_pom.xml',
                       'maven/expectations/webre_pom.xml.json')

    def test_parse_pom_adarwin(self):
        self.check_pom('maven/maven2/adarwin-1.0.pom',
                       'maven/expectations/adarwin-1.0.pom.json')

    def test_parse_pom_ant(self):
        self.check_pom('maven/maven2/ant-1.6.5.pom',
                       'maven/expectations/ant-1.6.5.pom.json')

    def test_parse_pom_ant_jai(self):
        self.check_pom('maven/maven2/ant-jai-1.7.0.pom',
                       'maven/expectations/ant-jai-1.7.0.pom.json')

    def test_parse_pom_ant_jsch(self):
        self.check_pom('maven/maven2/ant-jsch-1.7.0.pom',
                       'maven/expectations/ant-jsch-1.7.0.pom.json')

    def test_parse_pom_aopalliance(self):
        self.check_pom('maven/maven2/aopalliance-1.0.pom',
                       'maven/expectations/aopalliance-1.0.pom.json')

    def test_parse_pom_classworlds(self):
        self.check_pom('maven/maven2/classworlds-1.1-alpha-2.pom',
                       'maven/expectations/classworlds-1.1-alpha-2.pom.json')

    def test_parse_pom_commons_fileupload(self):
        self.check_pom('maven/maven2/commons-fileupload-1.0.pom',
                       'maven/expectations/commons-fileupload-1.0.pom.json')

    def test_parse_pom_bcel(self):
        self.check_pom('maven/maven2/bcel-5.1.pom',
                       'maven/expectations/bcel-5.1.pom.json')

    def test_parse_pom_easyconf(self):
        self.check_pom('maven/maven2/easyconf-0.9.0.pom',
                       'maven/expectations/expected_eayconf.json')

    def test_parse_pom_startup_trigger_plugin(self):
        self.check_pom('maven/maven2/startup-trigger-plugin-0.1.pom',
                       'maven/expectations/startup-trigger-plugin-0.1.pom.json')

    def test_parse_pom_jrecordbind(self):
        self.check_pom('maven/maven2/jrecordbind-2.3.4.pom',
                       'maven/expectations/jrecordbind-2.3.4.pom.json')

    def test_parse_pom_findbugs(self):
        self.check_pom('maven/maven2/findbugs-maven-plugin-1.1.1.pom',
                       'maven/expectations/findbugs-maven-plugin-1.1.1.pom.json')

    def test_parse_pom_plexus_2(self):
        self.check_pom('maven/maven2/plexus-interactivity-api-1.0-alpha-4.pom',
                       'maven/expectations/plexus-interactivity-api-1.0-alpha-4.pom.json')

    def test_parse_pom_spring(self):
        self.check_pom('maven/maven2/spring-2.5.4.pom',
                       'maven/expectations/spring-2.5.4.pom.json')

    def test_parse_pom_springorm(self):
        self.check_pom('maven/maven2/spring-orm-2.5.3.pom',
                       'maven/expectations/spring-orm-2.5.3.pom.json')

    def test_parse_pom_springweb(self):
        self.check_pom('maven/maven2/spring-webmvc-2.5.3.pom',
                       'maven/expectations/spring-webmvc-2.5.3.pom.json')

    def test_parse_pom_commons_validator(self):
        self.check_pom('maven/maven2/commons-validator-1.2.0.pom',
                       'maven/expectations/commons-validator-1.2.0.pom.json')

    def test_parse_pom_simple_maven1_pom(self):
        self.check_pom('maven/maven1/project.xml',
                       'maven/expectations/project.xml.json')

    def test_parse_pom_maven1_codemodel(self):
        self.check_pom('maven/maven1/codemodel-2.0-SNAPSHOT.pom',
                       'maven/expectations/codemodel-2.0-SNAPSHOT.pom.json')

    def test_parse_pom_maven1_jen(self):
        self.check_pom('maven/maven1/jen-0.14.pom',
                       'maven/expectations/jen-0.14.pom.json')

    def test_parse_pom_activemq_camel(self):
        self.check_pom('maven/maven2/activemq-camel-pom.xml',
                       'maven/expectations/activemq-camel-pom.xml.json', regen=False)


class TestMavenPackage(BaseMavenCase):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_to_package(self):
        test_file = self.get_test_loc('maven/maven2/spring-beans-4.2.2.RELEASE.pom.xml')
        package = maven.parse(test_file)

        assert isinstance(package, maven.MavenJar)
        expected = [
            ('type', u'Apache Maven'),
            ('name', u'org.springframework:spring-beans'),
            ('version', u'4.2.2.RELEASE'),
            ('primary_language', u'Java'),
            ('packaging', u'archive'),
            ('summary', u'Spring Beans'),
            ('description', u'Spring Beans'),
            ('payload_type', None),
            ('authors', [OrderedDict([('type', u'person'), ('name', u'Juergen Hoeller'), ('email', u'jhoeller@pivotal.io'), ('url', None)])]),
            ('maintainers', []),
            ('contributors', []),
            ('owners', [OrderedDict([('type', u'organization'), ('name', u'Spring IO'), ('email', None), ('url', u'http://projects.spring.io/spring-framework')])]),
            ('packagers', []),
            ('distributors', []),
            ('vendors', []),
            ('keywords', []),
            ('keywords_doc_url', None),
            ('metafile_locations', []),
            ('metafile_urls', []),
            ('homepage_url', u'https://github.com/spring-projects/spring-framework'),
            ('notes', None),
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
            ('copyright_top_level', None),
            ('copyrights', []),
            ('asserted_licenses', [OrderedDict([('license', u'The Apache Software License, Version 2.0'), ('url', u'http://www.apache.org/licenses/LICENSE-2.0.txt'), ('text', None), ('notice', None)])]),
            ('legal_file_locations', []),
            ('license_expression', None),
            ('license_texts', []),
            ('notice_texts', []),
            ('dependencies', {}),
            ('related_packages', [])
        ]
        assert expected == package.as_dict().items()
        package.validate()


class TestMavenDataDriven(BaseMavenCase):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')


def relative_walk(dir_path, extension):
    """
    Walk path and yield files path matching an extension.
    Do not return the dir_path segments.
    """
    for base_dir, _dirs, files in os.walk(dir_path):
        for file_name in files:
            if not file_name.endswith(extension):
                continue
            file_path = os.path.join(base_dir, file_name)
            file_path = file_path.replace(dir_path, '', 1)
            file_path = file_path.strip(os.path.sep)
            yield file_path


def make_test_function(test_pom_loc, expected_json_loc, regen, test_name):
    # closure on the test params
    def test_pom(self):
        self.check_pom(test_pom_loc, expected_json_loc, regen)

    # set good function name to display in reports and use in discovery
    test_pom.__name__ = test_name
    test_pom.funcname = test_name
    return test_pom


def build_tests(root_dir, test_dir, expected_dir, clazz, regen=False):
    """
    Dynamically build an individual test method for each bzipped POMs and each
    bzipped JSON expectation file using a closure on a test method and attach
    the test method to the `clazz` class.
    """
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')
    root_loc = testcase.get_test_loc(root_dir, test_data_dir)
    test_loc = os.path.join(root_loc, test_dir)
    expected_loc = os.path.join(root_loc, expected_dir)
    # loop through all items and attach a test method to our test class
    for test_path in relative_walk(test_loc, extension='.pom.bz2'):
        no_ext, _ = os.path.splitext(test_path)
        test_name = 'test_maven_long_' + text.python_safe_name(no_ext)
        test_pom_loc = os.path.join(test_loc, test_path)
        expected_json_loc = os.path.join(expected_loc, test_path)
        test_method = make_test_function(test_pom_loc, expected_json_loc, regen, test_name)
        # attach that method to the class
        setattr(clazz, test_name, test_method)


# note: we use short dir names to deal with Windows long paths limitations
build_tests(root_dir='m2', test_dir='r', expected_dir='e', clazz=TestMavenDataDriven, regen=False)
