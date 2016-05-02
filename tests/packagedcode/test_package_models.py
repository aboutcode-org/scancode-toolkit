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

from packagedcode.models import AssertedLicense
from packagedcode import models
from packagedcode.models import Package
from packagedcode.models import Party


class TestModels(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_model_creation_and_dump(self):
        aap = models.AndroidAppPackage(name='someAndroidPAcakge')
        result = aap.as_dict()
        expected = OrderedDict([
            ('asserted_licenses', []),
            ('authors', []),
            ('bug_tracking_url', None),
            ('code_view_url', None),
            ('contributors', []),
            ('copyright_top_level', None),
            ('copyrights', []),
            ('dependencies', {}),
            ('description', None),
            ('distributors', []),
            ('download_md5', None),
            ('download_sha1', None),
            ('download_sha256', None),
            ('download_urls', []),
            ('homepage_url', None),
            ('id', None),
            ('keywords', []),
            ('keywords_doc_url', None),
            ('legal_file_locations', []),
            ('license_expression', None),
            ('license_texts', []),
            ('maintainers', []),
            ('metafile_locations', []),
            ('metafile_urls', []),
            ('name', u'someAndroidPAcakge'),
            ('notes', None),
            ('notice_texts', []),
            ('owners', []),
            ('packagers', []),
            ('packaging', u'archive'),
            ('payload_type', None),
            ('primary_language', u'Java'),
            ('related_packages', []),
            ('summary', None),
            ('support_contacts', []),
            ('type', u'Android app'),
            ('vcs_repository', None),
            ('vcs_revision', None),
            ('vcs_tool', None),
            ('vendors', []),
            ('versioning', None)]
        )
        no_errors = True
        try:
            aap.validate()
        except:
            no_errors = False
        self.assertTrue(no_errors)
        assert expected == result

    def test_validate_package(self):
        package = Package(
            name='Sample',
            summary='Some package',
            payload_type='source',
            authors=[Party(
                    name='Some Author',
                    email='some@email.com'
                )
            ],
            keywords=['some', 'keyword'],
            vcs_tool='git',
            asserted_licenses=[
                AssertedLicense(
                    license='apache-2.0'
                    )
            ],
        )
        expected = OrderedDict([
            ('asserted_licenses',
             [{'license': u'apache-2.0', 'notice': None, 'text': None, 'url': None}]),
            ('authors',
             [{'email': u'some@email.com',
               'name': u'Some Author',
               'type': None,
               'url': None}]),
            ('bug_tracking_url', None),
            ('code_view_url', None),
            ('contributors', []),
            ('copyright_top_level', None),
            ('copyrights', []),
            ('dependencies', {}),
            ('description', None),
            ('distributors', []),
            ('download_md5', None),
            ('download_sha1', None),
            ('download_sha256', None),
            ('download_urls', []),
            ('homepage_url', None),
            ('id', None),
            ('keywords', [u'some', u'keyword']),
            ('keywords_doc_url', None),
            ('legal_file_locations', []),
            ('license_expression', None),
            ('license_texts', []),
            ('maintainers', []),
            ('metafile_locations', []),
            ('metafile_urls', []),
            ('name', u'Sample'),
            ('notes', None),
            ('notice_texts', []),
            ('owners', []),
            ('packagers', []),
            ('packaging', None),
            ('payload_type', u'source'),
            ('related_packages', []),
            ('summary', u'Some package'),
            ('support_contacts', []),
            ('type', None),
            ('vcs_repository', None),
            ('vcs_revision', None),
            ('vcs_tool', u'git'),
            ('vendors', []),
            ('versioning', None)]
        )
        no_errors = True
        try:
            package.validate()
        except:
            no_errors = False
        self.assertTrue(no_errors)
        assert expected == package.as_dict()
