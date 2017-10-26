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

from collections import OrderedDict
import os

from commoncode.testcase import FileBasedTesting
from packagedcode import pypi


class TestPyPi(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse(self):
        test_file = self.get_test_loc('pypi/setup1/setup.py')
        package = pypi.parse(test_file)
        assert 'scancode-toolkit' == package.name
        assert '1.5.0' == package.version
        assert 'ScanCode' == package.parties[0].name
        assert ('ScanCode is a tool to scan code for license, '
                'copyright and other interesting facts.') == package.description
        assert 'https://github.com/nexB/scancode-toolkit' == package.homepage_url

    def test_get_setup_attribute(self):
        test_file = self.get_test_loc('pypi/setup2/setup.py')
        assert 'scancode-toolkit' == pypi.get_setup_attribute(test_file, 'name')
        assert '1.5.0' == pypi.get_setup_attribute(test_file, 'version')
        assert 'ScanCode' == pypi.get_setup_attribute(test_file, 'author')

    def test_parse_metadata(self):
        test_folder = self.get_test_loc('pypi')
        test_file = os.path.join(test_folder, 'metadata.json')
        package = pypi.parse_metadata(test_file)
        assert 'six' == package.name
        assert '1.10.0' == package.version
        assert 'Python 2 and 3 compatibility utilities' == package.description
        assert 'MIT' in package.asserted_license
        expected = [
            OrderedDict([
                ('type', u'person'), ('role', u'contact'), 
                ('name', u'Benjamin Peterson'), ('email', None), ('url', None)])
        ]
        assert expected == [p.to_dict() for p in package.parties]
        assert 'http://pypi.python.org/pypi/six/' == package.homepage_url

    def test_parse_pkg_info(self):
        test_file = self.get_test_loc('pypi/PKG-INFO')
        package = pypi.parse_pkg_info(test_file)
        assert 'TicketImport' == package.name
        assert '0.7a' == package.version
        assert 'Import CSV and Excel files' == package.description
        assert 'BSD' in package.asserted_license
        assert 'http://nexb.com' == package.homepage_url
        expected = [OrderedDict([('type', u'person'), ('role', u''), ('name', u'Francois Granade'), ('email', None), ('url', None)])]
        assert expected == [p.to_dict() for p in package.parties]
