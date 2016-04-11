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

import os.path

from commoncode.testcase import FileBasedTesting

from packagedcode import nuget


class TestNuget(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_bootstrap_nuspec(self):
        test_file = self.get_test_loc('nuget/bootstrap.nuspec')
        output_obtained = nuget.get_nuspec_tags(test_file)
        expected_output = {
            'authors': u'Twitter, Inc.',
            'copyright': u'Copyright 2015',
            'description': u'The most popular front-end framework for developing responsive, mobile first projects on the web.',
            'id': u'bootstrap',
            'licenseUrl': u'https://github.com/twbs/bootstrap/blob/master/LICENSE',
            'owners': u'bootstrap',
            'projectUrl': u'http://getbootstrap.com',
            'releaseNotes': u'http://blog.getbootstrap.com',
            'requireLicenseAcceptance': u'false',
            'summary': u'Bootstrap framework in CSS. Includes fonts and JavaScript',
            'title': u'Bootstrap CSS',
            'version': u'4.0.0-alpha'
        }
        assert expected_output == output_obtained

    def test_parse_entity_nuspec(self):
        test_file = self.get_test_loc('nuget/EntityFramework.nuspec')
        result = nuget.get_nuspec_tags(test_file)
        expected = {
            'authors': u'Microsoft',
            'copyright': None,
            'description': u"Entity Framework is Microsoft's recommended data access technology for new applications.",
            'id': u'EntityFramework',
            'licenseUrl': u'http://go.microsoft.com/fwlink/?LinkID=320539',
            'owners': u'Microsoft',
            'projectUrl': u'http://go.microsoft.com/fwlink/?LinkID=320540',
            'releaseNotes': None,
            'requireLicenseAcceptance': u'true',
            'summary': u"Entity Framework is Microsoft's recommended data access technology for new applications.",
            'title': u'EntityFramework',
            'version': u'6.1.3'
        }
        assert expected == result

    def test_parse_jquery_nuspec(self):
        test_file = self.get_test_loc('nuget/jQuery.UI.Combined.nuspec')
        result = nuget.get_nuspec_tags(test_file)
        expected = {
            'authors': u'jQuery UI Team',
            'copyright': None,
            'description': u"jQuery UI is an open source library of interface components \u2014 interactions, full-featured widgets, and animation effects \u2014 based on the stellar jQuery javascript library . Each component is built according to jQuery's event-driven architecture (find something, manipulate it) and is themeable, making it easy for developers of any skill level to integrate and extend into their own code.\n    NOTE: This package is maintained on behalf of the library owners by the NuGet Community Packages project at http://nugetpackages.codeplex.com/",
            'id': u'jQuery.UI.Combined',
            'licenseUrl': u'http://jquery.org/license',
            'owners': u'jQuery UI Team',
            'projectUrl': u'http://jqueryui.com/',
            'releaseNotes': None,
            'requireLicenseAcceptance': u'false',
            'summary': u'The full jQuery UI library as a single combined file. Includes the base theme.',
            'title': u'jQuery UI (Combined Library)',
            'version': u'1.11.4'
        }
        assert expected == result

    def test_parse_microsoft_asp_nuspec(self):
        test_file = self.get_test_loc('nuget/Microsoft.AspNet.Mvc.nuspec')
        result = nuget.get_nuspec_tags(test_file)
        expected = {
            'authors': u'Microsoft',
            'copyright': u'Copyright \xa9 Microsoft Corporation',
            'description': u'ASP.NET MVC is a web framework that gives you a powerful, patterns-based way to build dynamic websites and Web APIs. ASP.NET MVC enables a clean separation of concerns and gives you full control over markup.',
            'id': u'Microsoft.AspNet.Mvc',
            'licenseUrl': u'http://www.microsoft.com/web/webpi/eula/net_library_eula_enu.htm',
            'owners': u'Microsoft',
            'projectUrl': u'http://www.asp.net/',
            'releaseNotes': None,
            'requireLicenseAcceptance': u'true',
            'summary': None,
            'title': None,
            'version': u'6.0.0-beta7'
        }
        assert expected == result

    def test_parse(self):
        test_file = self.get_test_loc('nuget/Microsoft.Net.Http.nuspec')
        result = nuget.parse(test_file)
        assert 'Microsoft.Net.Http' == result.name
        assert 'Microsoft.Net.Http' == result.id
        assert [u'Copyright \xa9 Microsoft Corporation'] == result.copyrights
        assert '2.2.29' == result.version
        assert 'http://go.microsoft.com/fwlink/?LinkID=280055' == result.homepage_url
        assert 'Microsoft HTTP Client Libraries' == result.summary
        assert 'Microsoft' == result.authors
        assert 'Microsoft' == result.owners

