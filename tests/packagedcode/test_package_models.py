#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

from packagedcode import misc
from packagedcode import models
from packagedcode import ALL_DATAFILE_HANDLERS
from packagedcode.models import PackageData
from packagedcode.models import Party
from packages_test_utils import PackageTester
from scancode_config import REGEN_TEST_FIXTURES


class TestModels(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_Package_creation_and_dump(self):
        pd = misc.AndroidAppArchiveHandler.create_default_package_data(
            name='someAndroidPAcakge',
        )
        expected = [
            ('type', 'android'),
            ('namespace', None),
            ('name', 'someAndroidPAcakge'),
            ('version', None),
            ('qualifiers', {}),
            ('subpath', None),
            ('primary_language', 'Java'),
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
            ('declared_license_expression', None),
            ('declared_license_expression_spdx', None),
            ('license_detections', []),
            ('extracted_license_statement', None),
            ('notice_text', None),
            ('source_packages', []),
            ('file_references', []),
            ('extra_data', {}),
            ('dependencies', []),
            ('repository_homepage_url', None),
            ('repository_download_url', None),
            ('api_data_url', None),
            ('datasource_id', 'android_apk'),
            ('purl', 'pkg:android/someAndroidPAcakge'),
        ]
        assert list(pd.to_dict().items()) == expected

    def test_Package_simple(self):
        package = PackageData(
            datasource_id = 'rpm_archive',
            type='rpm',
            name='Sample',
            description='Some package',
            parties=[Party(name='Some Author', role='author', email='some@email.com')],
            keywords=['some', 'keyword'],
            vcs_url='git+https://somerepo.com/that.git',
            extracted_license_statement='apache-2.0',
        )
        expected_loc = 'models/simple-expected.json'
        self.check_package_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_Package_model_qualifiers_are_serialized_as_mappings(self):
        package = models.PackageData(
            type='maven', name='this', version='23', qualifiers=dict(this='that')
        )
        assert package.to_dict()['qualifiers'] == dict(this='that')

    def test_Package_model_qualifiers_are_kept_as_mappings(self):
        package = models.PackageData(
            type='maven', name='this', version='23', qualifiers=dict(this='that')
        )
        assert package.qualifiers == dict(this='that')

    def test_Package_model_qualifiers_are_converted_to_mappings(self):
        package = models.PackageData(
            type='maven', name='this', version='23', qualifiers='this=that'
        )
        assert package.qualifiers == dict(this='that')

    def test_Package_full(self):
        package = PackageData(
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
            parties=[Party(name='Some Author', role='author', email='some@email.com')],
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
            extracted_license_statement=u'apache-2.0',
            notice_text='licensed under the apacche 2.0 \nlicense',
            source_packages=["pkg:maven/aspectj/aspectjtools@1.5.4?classifier=sources"],
        )
        expected_loc = 'models/full-expected.json'
        self.check_package_data(package, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_package_data_datasource_id_are_unique(self):
        """
        Check that we do not have two DataFileHandlers with the same
        datasource_id and that all have one.
        """
        seen = {}
        for pdh in ALL_DATAFILE_HANDLERS:
            pdhid = pdh.datasource_id
            assert pdhid
            assert (
                pdh.datasource_id not in seen
            ), f'Duplicated datasource_id: {pdh!r} with {seen[pdhid]!r}'
            seen[pdh.datasource_id] = pdh
    
    def test_package_data_file_patterns_are_tuples(self):
        """
        Check that all file patterns are tuples, as if they are
        strings the matching will happen per character and will be
        True for most of the cases.
        """
        for pdh in ALL_DATAFILE_HANDLERS:
            if pdh.path_patterns:
                assert type(pdh.path_patterns) == tuple, pdh
            if pdh.filetypes:
                assert type(pdh.filetypes) == tuple, pdh
