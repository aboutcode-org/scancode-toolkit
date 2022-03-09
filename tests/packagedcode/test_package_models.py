#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os.path

from packagedcode import models
from packagedcode import PACKAGE_INSTANCE_CLASSES
from packagedcode import PACKAGE_DATA_CLASSES
from packagedcode import PACKAGE_DATA_BY_TYPE
from packagedcode import PACKAGE_INSTANCES_BY_TYPE
from packagedcode.models import PackageData
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
            ('qualifiers', {}),
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
            ('contains_source_code', None),
            ('source_packages', []),
            ('extra_data', {}),
            ('dependencies', []),
            ('purl', u'pkg:android/someAndroidPAcakge'),
            ('repository_homepage_url', None),
            ('repository_download_url', None),
            ('api_data_url', None),
        ]
        assert list(package.to_dict().items()) == expected

    def test_Package_simple(self):
        package = PackageData(
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

    def test_Package_model_qualifiers_are_serialized_as_mappings(self):
        package = models.PackageData(
            type='maven',
            name='this',
            version='23',
            qualifiers=dict(this='that')
        )
        assert package.to_dict()['qualifiers'] == dict(this='that')

    def test_Package_model_qualifiers_are_kept_as_mappings(self):
        package = models.PackageData(
            type='maven',
            name='this',
            version='23',
            qualifiers=dict(this='that')
        )
        assert package.qualifiers == dict(this='that')

    def test_Package_model_qualifiers_are_converted_to_mappings(self):
        package = models.PackageData(
            type='maven',
            name='this',
            version='23',
            qualifiers='this=that'
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
            contains_source_code=True,
            source_packages=[
                "pkg:maven/aspectj/aspectjtools@1.5.4?classifier=sources"
            ],
        )
        expected_loc = 'models/full-expected.json'
        self.check_package(package, expected_loc, regen=False)

    def test_Package_get_package_resource_works_with_nested_packages_and_ignores(self):
        from packagedcode import get_package_instance
        from packagedcode import npm
        from commoncode.resource import VirtualCodebase
        scan_loc = self.get_test_loc('models/nested-npm-packages.json')
        codebase = VirtualCodebase(scan_loc)
        for resource in codebase.walk():
            for package_data in resource.packages:
                package = get_package_instance(package_data)
                assert isinstance(package, npm.NpmPackageData)
                package_resources = list(package.get_package_resources(resource, codebase))
                assert any(r.name == 'package.json' for r in package_resources), resource.path


class TestManifestInstanceModels(PackageTester):

    def test_package_data_types(self):
        check_package_data_classes()

    def test_package_instance_types(self):
        check_package_instance_classes()


def check_package_instance_classes():
    """
    Check that we don't have two package instance classes with the same
    default_type.
    """
    package_instances_by_type = {
        cls.default_type: cls
        for cls in PACKAGE_INSTANCE_CLASSES
    }

    if len(package_instances_by_type) != len(PACKAGE_INSTANCE_CLASSES):
        seen_types = {}
        for pt in PACKAGE_INSTANCE_CLASSES:
            pk_instance = pt()
            assert pk_instance.default_type
            seen = seen_types.get(pk_instance.default_type)
            if seen:
                msg = ('Invalid duplicated packagedcode.Package types: '
                    '"{}:{}" and "{}:{}" have the same type.'
                    .format(pk_instance.default_type, pk_instance.__name__, seen.default_type, seen.__name__,))
                raise Exception(msg)
            else:
                seen_types[pk_instance.default_type] = pk_instance


def check_package_data_classes():
    """
    Check that we don't have two package manifest classes with the same
    package_data_type.
    """
    package_data_by_type = {
        cls.default_type: cls
        for cls in PACKAGE_DATA_CLASSES
    }

    if len(package_data_by_type) != len(PACKAGE_DATA_CLASSES):
        seen_types = {}
        for pmt in PACKAGE_DATA_CLASSES:
            manifest = pmt()
            assert manifest.package_data_type
            seen = seen_types.get(manifest.package_data_type)
            if seen:
                msg = ('Invalid duplicated packagedcode.Package types: '
                    '"{}:{}" and "{}:{}" have the same type.'
                    .format(manifest.package_data_type, manifest.__name__, seen.package_data_type, seen.__name__,))
                raise Exception(msg)
            else:
                seen_types[manifest.package_data_type] = manifest
