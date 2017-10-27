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

from __future__ import absolute_import
from __future__ import print_function

import os.path
from collections import OrderedDict

from commoncode.testcase import FileBasedTesting

from packagedcode import models
from packagedcode.models import Package
from packagedcode.models import Party


class TestModels(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_model_creation_and_dump(self):
        package = models.AndroidApp(name='someAndroidPAcakge')
        expected = [
            ('type', u'android'),
            ('name', u'someAndroidPAcakge'),
            ('version', None),
            ('primary_language', u'Java'),
            ('description', None),
            ('size', None),
            ('release_date', None),
            ('parties', []),
            ('keywords', []),
            ('homepage_url', None),
            ('download_url', None),
            ('download_checksums', []),
            ('bug_tracking_url', None),
            ('code_view_url', None),
            ('vcs_tool', None),
            ('vcs_repository', None),
            ('vcs_revision', None),
            ('copyright', None),
            ('asserted_license', None),
            ('license_expression', None),
            ('notice_text', None),
            ('dependencies', {}),
            ('related_packages', [])
        ]
        assert expected == package.to_dict().items()
        package.validate()

    def test_validate_package(self):
        package = Package(
            type='rpm',
            name='Sample',
            description='Some package',
            parties=[Party(
                    name='Some Author',
                    role='author',
                    email='some@email.com'
                )
            ],
            keywords=['some', 'keyword'],
            vcs_tool='git',
            asserted_license='apache-2.0'
        )
        expected = [
            ('type', 'rpm'),
            ('name', u'Sample'),
            ('version', None),
            ('primary_language', None),
            ('description', u'Some package'),
            ('size', None),
            ('release_date', None),
            ('parties', [
                OrderedDict([
                    ('type', None),
                    ('role', 'author'),
                    ('name', u'Some Author'),
                    ('email', u'some@email.com'),
                    ('url', None)
                ])
            ]),
            ('keywords', [u'some', u'keyword']),
            ('homepage_url', None),
            ('download_url', None),
            ('download_checksums', []),
            ('bug_tracking_url', None),
            ('code_view_url', None),
            ('vcs_tool', u'git'),
            ('vcs_repository', None),
            ('vcs_revision', None),
            ('copyright', None),
            ('asserted_license', u'apache-2.0'),
            ('license_expression', None),
            ('notice_text', None),
            ('dependencies', {}),
            ('related_packages', [])
        ]
        assert expected == package.to_dict().items()
        package.validate()
