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

import os.path

from lxml import etree

from commoncode import testcase

from packagedcode import xmlutils


class TestXmlutils(testcase.FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_xpath_with_bare_lxml(self):
        test_file = self.get_test_loc('xmlutils/ant-jai-1.7.0.pom')
        doc = etree.parse(test_file)
        assert None == doc.findtext('//version')
        assert None == doc.findtext('version')
        assert None == doc.findtext('.//version')
        assert '1.7.0' == doc.findtext('//{http://maven.apache.org/POM/4.0.0}version')
        assert '1.7.0' == doc.findtext('{http://maven.apache.org/POM/4.0.0}version')
        assert '1.7.0' == doc.findtext('.//{http://maven.apache.org/POM/4.0.0}version')
        assert ['1.7.0'] == [e.text  for e in doc.xpath(xmlutils.namespace_unaware('/project/version'))]

    def test_find_text_handler(self):
        test_doc = self.get_test_loc('xmlutils/project.xml')
        handler = lambda xdoc: xmlutils.find_text(xdoc, '/project/shortDescription')
        test = xmlutils.parse(test_doc, handler)
        assert ['Abbot Tests'] == test

    def test_find_text_ignoring_namespaces(self):
        test_doc = self.get_test_loc('xmlutils/ant-jai-1.7.0.pom')
        expr = "/*[local-name()='project']/*[local-name()='modelVersion']"
        handler = lambda xdoc: xmlutils.find_text(xdoc, expr)
        test = xmlutils.parse(test_doc, handler)
        assert ['4.0.0'] == test

        expr2 = xmlutils.namespace_unaware("/project/modelVersion")
        handler2 = lambda xdoc: xmlutils.find_text(xdoc, expr2)
        test = xmlutils.parse(test_doc, handler2)
        assert ['4.0.0'] == test

    def test_namespace_unaware(self):
        # (tag name, expected stripped name)
        test_xp = [
        ('/project/artifactId', "/*[local-name()='project']/*[local-name()='artifactId']"),
        ('/project/properties/projectName', "/*[local-name()='project']/*[local-name()='properties']/*[local-name()='projectName']")]
        ('/project/developers/developer/email', "/*[local-name()='project']/*[local-name()='developers']/*[local-name()='developer']/*[local-name()='email']"),
        for simple_xpath, expected in test_xp:
            assert expected == xmlutils.namespace_unaware(simple_xpath)
