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

from commoncode.testcase import FileBasedTesting

from packagedcode.models import AssertedLicense
from packagedcode import models
from packagedcode.models import Package
from packagedcode.models import Party


class TestModels(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_model_creation_and_dump(self):
        aap = models.AndroidAppPackage()
        result = aap.as_dict()
        expected = {
            'as_archive': u'archive',
            'as_dir': u'directory',
            'as_file': u'file',
            'asserted_licenses': [],
            'authors': None,
            'bug_tracking_url': None,
            'code_view_url': None,
            'contributors': None,
            'copyright_top_level': None,
            'copyrights': None,
            'dependencies': {},
            'description': None,
            'distributors': None,
            'download_md5': None,
            'download_sha1': None,
            'download_sha256': None,
            'download_urls': [],
            'homepage_url': None,
            'id': None,
            'keywords': None,
            'keywords_doc_url': None,
            'legal_file_locations': None,
            'license_expression': None,
            'license_texts': None,
            'location': None,
            'maintainers': None,
            'metafile_locations': None,
            'metafile_urls': [],
            'name': None,
            'notes': None,
            'notice_texts': None,
            'owners': None,
            'packagers': None,
            'packaging': u'archive',
            'payload_bin': u'binary',
            'payload_doc': u'doc',
            'payload_src': u'source',
            'payload_type': None,
            'primary_language': u'Java',
            'related_packages': [],
            'summary': None,
            'support_contacts': None,
            'type': u'Android app',
            'vcs_repository': None,
            'vcs_revision': None,
            'vcs_tool': None,
            'vendors': None,
            'versioning': None
        }
        assert expected == result

    def test_validate_package(self):
        package = Package(dict(
            name='Sample',
            summary='Some package',
            payload_type='source',
            authors=[Party(
                dict(
                    name='Some Author',
                    email='some@email.com'
                    )
                )
            ],
            keywords=['some', 'keyword'],
            vcs_tool='git',
            asserted_licenses=[
                AssertedLicense(dict(
                    license='apache-2.0'
                    )
                )
            ],
            )
        )
        expected = {
            'as_archive': u'archive',
            'as_dir': u'directory',
            'as_file': u'file',
            'asserted_licenses': [{
                'license': u'apache-2.0',
                'notice': None,
                'text': None,
                'url': None}
            ],
            'authors': [{
                'email': u'some@email.com',
                'name': u'Some Author',
                'type': None,
                'url': None}
            ],
            'bug_tracking_url': None,
            'code_view_url': None,
            'contributors': None,
            'copyright_top_level': None,
            'copyrights': None,
            'dependencies': {},
            'description': None,
            'distributors': None,
            'download_md5': None,
            'download_sha1': None,
            'download_sha256': None,
            'download_urls': [],
            'homepage_url': None,
            'id': None,
            'keywords': [u'some', u'keyword'],
            'keywords_doc_url': None,
            'legal_file_locations': None,
            'license_expression': None,
            'license_texts': None,
            'location': None,
            'maintainers': None,
            'metafile_locations': None,
            'metafile_urls': [],
            'name': u'Sample',
            'notes': None,
            'notice_texts': None,
            'owners': None,
            'packagers': None,
            'packaging': None,
            'payload_bin': u'binary',
            'payload_doc': u'doc',
            'payload_src': u'source',
            'payload_type': u'source',
            'related_packages': [],
            'summary': u'Some package',
            'support_contacts': None,
            'type': None,
            'vcs_repository': None,
            'vcs_revision': None,
            'vcs_tool': u'git',
            'vendors': None,
            'versioning': None
    }
        assert expected == package.as_dict()
