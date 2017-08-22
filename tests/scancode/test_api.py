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

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from collections import OrderedDict
import os

from commoncode.testcase import FileBasedTesting

from scancode import api


class TestAPI(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_get_package_infos_can_pickle(self):
        test_file = self.get_test_loc('api/package/package.json')
        package = api.get_package_infos(test_file)

        import pickle
        import cPickle
        try:
            _pickled = pickle.dumps(package, pickle.HIGHEST_PROTOCOL)
            _cpickled = cPickle.dumps(package, pickle.HIGHEST_PROTOCOL)
            self.fail('pickle.HIGHEST_PROTOCOL used to fail to pickle this data')
        except:
            _pickled = pickle.dumps(package)
            _cpickled = cPickle.dumps(package)

    def test_get_file_infos_flag_are_not_null(self):
        # note the test file is EMPTY on purpose to generate all False is_* flags
        test_dir = self.get_test_loc('api/info')
        info = api.get_file_infos(test_dir)
        is_key_values = [v for k, v in info.items() if k.startswith('is_')]
        assert all(v is not None for v in is_key_values)

    def test_get_package_infos_works_for_maven_dot_pom(self):
        test_file = self.get_test_loc('api/package/p6spy-1.3.pom')
        packages = api.get_package_infos(test_file)
        assert len(packages) == 1
        package = packages[0]
        assert package['version'] == '1.3'

    def test_get_package_infos_works_for_maven_pom_dot_xml(self):
        test_file = self.get_test_loc('api/package/pom.xml')
        packages = api.get_package_infos(test_file)
        assert len(packages) == 1
        package = packages[0]
        assert package['version'] == '1.3'

    def test_get_file_infos_include_base_name(self):
        test_dir = self.get_test_loc('api/info/test.txt')
        info = api.get_file_infos(test_dir)
        assert 'test' == info['base_name']

    def test_get_copyrights_include_copyrights_and_authors(self):
        test_file = self.get_test_loc('api/copyright/iproute.c')
        cops = list(api.get_copyrights(test_file))
        expected = [
            OrderedDict([
                (u'statements', [u'Copyright (c) 2010 Patrick McHardy']),
                (u'holders', [u'Patrick McHardy']),
                (u'authors', []),
                (u'start_line', 2), (u'end_line', 2)]),
            OrderedDict([
                (u'statements', []),
                (u'holders', []),
                (u'authors', [u'Patrick McHardy <kaber@trash.net>']),
                (u'start_line', 11), (u'end_line', 11)])
        ]
        assert expected == cops
