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

import os.path

from commoncode.testcase import FileBasedTesting
from packagedcode.utils import parse_repo_url


class TestUtilsPi(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_url(self):
        inputs = ['npm/npm',
                  'gist:11081aaa281',
                  'bitbucket:example/repo',
                  'gitlab:another/repo',
                  'expressjs/serve-static',
                  'git://github.com/angular/di.js.git',
                  'git://github.com/hapijs/boom',
                  'git@github.com:balderdashy/waterline-criteria.git',
                  'http://github.com/ariya/esprima.git',
                  'http://github.com/isaacs/nopt',
                  'https://github.com/chaijs/chai',
                  'https://github.com/christkv/kerberos.git',
                  'https://gitlab.com/foo/private.git',
                  'git@gitlab.com:foo/private.git'
        ]
        results = []
        for input in inputs:
            results.append(parse_repo_url(input))
        expected = ['https://github.com/npm/npm',
                    'https://gist.github.com/11081aaa281',
                    'https://bitbucket.org/example/repo',
                    'https://gitlab.com/another/repo',
                    'https://github.com/expressjs/serve-static',
                    'git://github.com/angular/di.js.git',
                    'git://github.com/hapijs/boom',
                    'https://github.com/balderdashy/waterline-criteria.git',
                    'http://github.com/ariya/esprima.git',
                    'http://github.com/isaacs/nopt',
                    'https://github.com/chaijs/chai',
                    'https://github.com/christkv/kerberos.git',
                    'https://gitlab.com/foo/private.git',
                    'https://gitlab.com/foo/private.git'
        ]
        self.assertEquals(expected, results)

