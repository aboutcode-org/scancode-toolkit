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
import os.path

from packagedcode import models
from packagedcode.models import Package
from packagedcode.models import Party
from packagedcode.models import DependentPackage
from packages_test_utils import PackageTester


class TestModels(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_Package_creation_and_dump(self):
        package = models.AndroidApp(name='someAndroidPAcakge')
        expected = [
            ('type', u'android'),
            ('namespace', None),
            ('name', u'someAndroidPAcakge'),
            ('version', None),
            ('qualifiers', None),
            ('subpath', None),
            ('primary_language', u'Java'),
            ('description', None),
            ('release_date', None),
            ('parties', []),
            ('keywords', []),
            ('homepage_url', None),
            ('download_url', None),
            ('size', None),
            ('sha1', None),
            ('md5', None),
            ('sha256', None),
            ('sha512', None),
            ('bug_tracking_url', None),
            ('code_view_url', None),
            ('vcs_url', None),
            ('copyright', None),
            ('license_expression', None),
            ('declared_license', None),
            ('notice_text', None),
            ('manifest_path', None),
            ('dependencies', []),
            ('contains_source_code', None),
            ('source_packages', []),
            ('purl', u'pkg:android/someAndroidPAcakge'),
            ('repository_homepage_url', None),
            ('repository_download_url', None),
            ('api_data_url', None),
        ]
        assert expected == package.to_dict().items()

    def test_Package_simple(self):
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
            vcs_url='git+https://somerepo.com/that.git',
            declared_license='apache-2.0'
        )
        expected_loc = 'models/simple-expected.json'
        self.check_package(package, expected_loc, regen=False)

    def test_Package_model_qualifiers_are_serialized_as_strings(self):
        package = models.Package(
            type='maven',
            name='this',
            version='23',
            qualifiers=OrderedDict(this='that')
        )
        assert 'this=that' == package.to_dict()['qualifiers']

    def test_Package_full(self):
        package = Package(
            type='rpm',
            namespace='fedora',
            name='Sample',
            version='12.2.3',
            qualifiers={'this': 'that', 'abc': '12'},
            subpath='asdasd/asdasd/asdasd/',
            primary_language='C/C++',
            description='Some package',
            size=12312312312,
            release_date='2012-10-21',
            parties=[
                Party(
                    name='Some Author',
                    role='author',
                    email='some@email.com'
                )
            ],
            keywords=['some', 'other', 'keyword'],
            homepage_url='http://homepage.com',
            download_url='http://homepage.com/dnl',
            sha1='ac978f7fd045f5f5503772f525e0ffdb533ba0f8',
            md5='12ed302c4b4c2aa10638db389082d07d',
            sha256='0b07d5ee2326cf76445b12a32456914120241d2b78c5b55273e9ffcbe6ffbc9f',
            sha512='c9a92789e94d68029629b9a8380afddecc147ba48f0ae887b89b88492d02aec96a92cf3c7eeb200111a6d94d1b7419eecd66e79de32c826e694f05d2eda644ae',
            bug_tracking_url='http://homepage.com/issues',
            code_view_url='http://homepage.com/code',
            vcs_url='git+http://homepage.com/code.git@12ed302c4b4c2aa10638db3890',
            copyright='copyright (c) nexB Inc.',
            license_expression='apache-2.0',
            declared_license=u'apache-2.0',
            notice_text='licensed under the apacche 2.0 \nlicense',
            manifest_path='package.json',
            dependencies=[
                DependentPackage(
                  purl='pkg:maven/org.aspectj/aspectjtools',
                  requirement='1.5.4',
                  scope='relocation',
                  is_runtime=True,
                  is_optional=False,
                  is_resolved=False
                ),
                DependentPackage(
                  purl='pkg:maven/org.aspectj/aspectjruntime',
                  requirement='1.5.4-release',
                  scope='runtime',
                  is_runtime=True,
                  is_optional=False,
                  is_resolved=True
                )
            ],
            contains_source_code=True,
            source_packages=[
                "pkg:maven/aspectj/aspectjtools@1.5.4?classifier=sources"
            ],
        )
        expected_loc = 'models/full-expected.json'
        self.check_package(package, expected_loc, regen=False)
