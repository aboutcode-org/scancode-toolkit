#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import os

import attr

from commoncode.testcase import FileBasedTesting
from commoncode.testcase import FileDrivenTesting
from commoncode.resource import Resource

from scancode.cli_test_utils import run_scan_click
from scancode.cli_test_utils import check_json_scan
from scancode_config import REGEN_TEST_FIXTURES
from scancode.plugin_info import InfoScanner
from summarycode import file_cat


resource_class = attr.make_class(
    name="TestResource",
    attrs=InfoScanner.resource_attributes,
    slots=True,
    bases=(Resource,),
)


class TestFileCat(FileBasedTesting):

    test_data_dir = os.path.join(os.path.dirname(__file__), "data")

    def test_ArchiveAndroid(self):
        test_resource_01 = resource_class(
            name="foo.apk",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ArchiveAndroid.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "archive"

        test_resource_02 = resource_class(
            name="foo.aar",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ArchiveAndroid.categorize(test_resource_02)
        assert file_cat.categorize_resource(test_resource_02).file_category == "archive"

    def test_ArchiveDebian(self):
        test_resource_01 = resource_class(
            name="foo.deb",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ArchiveDebian.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "archive"

        test_resource_02 = resource_class(
            name="foo.2",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert not file_cat.ArchiveDebian.categorize(test_resource_02)

    def test_ArchiveGeneral(self):
        test_resource_01 = resource_class(
            name="foo.7zip",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ArchiveGeneral.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "archive"

        test_resource_02 = resource_class(
            name="foo.bz",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ArchiveGeneral.categorize(test_resource_02)

        test_resource_03 = resource_class(
            name="foo.bz2",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ArchiveGeneral.categorize(test_resource_03)

        test_resource_04 = resource_class(
            name="foo.bzip",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ArchiveGeneral.categorize(test_resource_04)

        test_resource_05 = resource_class(
            name="foo.gz",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ArchiveGeneral.categorize(test_resource_05)

        test_resource_06 = resource_class(
            name="foo.gzi",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ArchiveGeneral.categorize(test_resource_06)

        test_resource_07 = resource_class(
            name="foo.tar",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ArchiveGeneral.categorize(test_resource_07)

        test_resource_08 = resource_class(
            name="foo.tgz",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ArchiveGeneral.categorize(test_resource_08)

        test_resource_09 = resource_class(
            name="foo.xz",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ArchiveGeneral.categorize(test_resource_09)

        test_resource_10 = resource_class(
            name="foo.zip",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ArchiveGeneral.categorize(test_resource_10)

    def test_ArchiveIos(self):
        test_resource_01 = resource_class(
            name="foo.ipa",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ArchiveIos.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "archive"

    def test_ArchiveRpm(self):
        test_resource_01 = resource_class(
            name="foo.rpm",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ArchiveRpm.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "archive"

    def test_BinaryAr(self):
        test_resource_01 = resource_class(
            name="",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="application/x-archive",
            file_type="",
            programming_language="",
        )
        assert file_cat.BinaryAr.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "binary"

    def test_BinaryElfExec(self):
        test_resource_01 = resource_class(
            name="",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="application/x-executable",
            file_type="",
            programming_language="",
        )
        assert file_cat.BinaryElfExec.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "binary"

    def test_BinaryElfKo(self):
        test_resource_01 = resource_class(
            name="foo.ko",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="application/x-object",
            file_type="",
            programming_language="",
        )
        assert file_cat.BinaryElfKo.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "binary"

    def test_BinaryElfO(self):
        test_resource_01 = resource_class(
            name="",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="application/x-object",
            file_type="",
            programming_language="",
        )
        assert file_cat.BinaryElfO.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "binary"

    def test_BinaryElfSo(self):
        test_resource_01 = resource_class(
            name="",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="application/x-sharedlib",
            file_type="",
            programming_language="",
        )
        assert file_cat.BinaryElfSo.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "binary"

    def test_BinaryJava(self):
        test_resource_01 = resource_class(
            name="foo.class",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.BinaryJava.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "binary"

        test_resource_02 = resource_class(
            name="foo.jar",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.BinaryJava.categorize(test_resource_02)

        test_resource_03 = resource_class(
            name="foo.ear",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.BinaryJava.categorize(test_resource_03)

        test_resource_04 = resource_class(
            name="foo.sar",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.BinaryJava.categorize(test_resource_04)

        test_resource_05 = resource_class(
            name="foo.war",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.BinaryJava.categorize(test_resource_05)

    def test_BinaryPython(self):
        test_resource_01 = resource_class(
            name="foo.pyc",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.BinaryPython.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "binary"

        test_resource_02 = resource_class(
            name="foo.pyo",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.BinaryPython.categorize(test_resource_02)

    def test_BinaryWindows(self):
        test_resource_01 = resource_class(
            name="",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="application/x-dosexec",
            file_type="",
            programming_language="",
        )
        assert file_cat.BinaryWindows.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "binary"
        assert (
            file_cat.categorize_resource(test_resource_01).category_notes
            == "For DLL and EXE binaries in Windows"
        )

    def test_BuildBazel(self):
        test_resource_01 = resource_class(
            name="foo.bzl",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.BuildBazel.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "build"

        test_resource_02 = resource_class(
            name="build.bazel",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.BuildBazel.categorize(test_resource_02)

        test_resource_03 = resource_class(
            name="foo.bazel",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert not file_cat.BuildBazel.categorize(test_resource_03)

    def test_BuildBuck(self):
        test_resource_01 = resource_class(
            name="buck",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.BuildBuck.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "build"

        test_resource_02 = resource_class(
            name="Buck",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.BuildBuck.categorize(test_resource_02)

        test_resource_03 = resource_class(
            name="Buck.c",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert not file_cat.BuildBuck.categorize(test_resource_03)

    def test_BuildDocker(self):
        test_resource_01 = resource_class(
            name="dockerfile",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.BuildDocker.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "build"

        test_resource_02 = resource_class(
            name="dockerfile.c",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.BuildDocker.categorize(test_resource_02)

    def test_BuildMake(self):
        test_resource_01 = resource_class(
            name="makefile",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.BuildMake.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "build"

        test_resource_02 = resource_class(
            name="makefile.c",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.BuildMake.categorize(test_resource_02)

        test_resource_03 = resource_class(
            name="foo.mk",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.BuildMake.categorize(test_resource_03)

        test_resource_04 = resource_class(
            name="foo.make",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.BuildMake.categorize(test_resource_04)

    def test_BuildQt(self):
        test_resource_01 = resource_class(
            name="foo.pri",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.BuildQt.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "build"

        test_resource_02 = resource_class(
            name="foo.pro",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.BuildQt.categorize(test_resource_02)

    def test_Certificate(self):
        test_resource_01 = resource_class(
            name="foo.crt",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.Certificate.categorize(test_resource_01)
        assert (
            file_cat.categorize_resource(test_resource_01).file_category
            == "certificate"
        )

        test_resource_02 = resource_class(
            name="foo.der",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.Certificate.categorize(test_resource_02)

        test_resource_03 = resource_class(
            name="foo.pem",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.Certificate.categorize(test_resource_03)

    def test_ConfigGeneral(self):
        test_resource_01 = resource_class(
            name="foo.cfg",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ConfigGeneral.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "config"

        test_resource_02 = resource_class(
            name="foo.conf",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ConfigGeneral.categorize(test_resource_02)

        test_resource_03 = resource_class(
            name="foo.config",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ConfigGeneral.categorize(test_resource_03)

        test_resource_04 = resource_class(
            name="foo.jxs",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ConfigGeneral.categorize(test_resource_04)

        test_resource_05 = resource_class(
            name="foo.properties",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ConfigGeneral.categorize(test_resource_05)

        test_resource_06 = resource_class(
            name="foo.yaml",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ConfigGeneral.categorize(test_resource_06)

        test_resource_07 = resource_class(
            name="foo.yml",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ConfigGeneral.categorize(test_resource_07)

    def test_ConfigInitialPeriod(self):
        test_resource_01 = resource_class(
            name=".c",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ConfigInitialPeriod.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "config"

    def test_ConfigMacro(self):
        test_resource_01 = resource_class(
            name="foo.m4",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ConfigMacro.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "config"

    def test_ConfigPython(self):
        test_resource_01 = resource_class(
            name="__init__.py",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ConfigPython.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "config"

    def test_ConfigTemplate(self):
        test_resource_01 = resource_class(
            name="foo.tmpl",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ConfigTemplate.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "config"

    def test_ConfigVisualCpp(self):
        test_resource_01 = resource_class(
            name="foo.vcxproj",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ConfigVisualCpp.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "config"

        test_resource_02 = resource_class(
            name="foo.vcproj",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ConfigVisualCpp.categorize(test_resource_02)

    def test_ConfigXcode(self):
        test_resource_01 = resource_class(
            name="info.plist",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ConfigXcode.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "config"

    def test_ConfigXml(self):
        test_resource_01 = resource_class(
            name="foo.dtd",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ConfigXml.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "config"

        test_resource_02 = resource_class(
            name="foo.xml",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ConfigXml.categorize(test_resource_02)

        test_resource_03 = resource_class(
            name="foo.xsd",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ConfigXml.categorize(test_resource_03)

        test_resource_04 = resource_class(
            name="foo.xsl",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ConfigXml.categorize(test_resource_04)

        test_resource_05 = resource_class(
            name="foo.xslt",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ConfigXml.categorize(test_resource_05)

    def test_DataJson(self):
        test_resource_01 = resource_class(
            name="foo.json",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DataJson.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "data"

    def test_DataProtoBuf(self):
        test_resource_01 = resource_class(
            name="foo.proto",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DataProtoBuf.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "data"

    def test_Directory(self):
        test_resource_01 = resource_class(
            name="foo",
            location="",
            path="",
            rid="",
            pid="",
            is_file=False,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.Directory.categorize(test_resource_01)
        assert (
            file_cat.categorize_resource(test_resource_01).file_category == "directory"
        )
        assert file_cat.categorize_resource(test_resource_01).analysis_priority == "4"

        test_resource_02 = resource_class(
            name=".foo",
            location="",
            path="",
            rid="",
            pid="",
            is_file=False,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.Directory.categorize(test_resource_02)

        test_resource_03 = resource_class(
            name="foo",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert not file_cat.Directory.categorize(test_resource_03)

    def test_DocGeneral(self):
        test_resource_01 = resource_class(
            name="foo.csv",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DocGeneral.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "doc"

        test_resource_02 = resource_class(
            name="foo.doc",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DocGeneral.categorize(test_resource_02)

        test_resource_03 = resource_class(
            name="foo.docx",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DocGeneral.categorize(test_resource_03)

        test_resource_04 = resource_class(
            name="foo.man",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DocGeneral.categorize(test_resource_04)

        test_resource_05 = resource_class(
            name="foo.md",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DocGeneral.categorize(test_resource_05)

        test_resource_06 = resource_class(
            name="foo.odp",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DocGeneral.categorize(test_resource_06)

        test_resource_07 = resource_class(
            name="foo.ods",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DocGeneral.categorize(test_resource_07)

        test_resource_08 = resource_class(
            name="foo.odt",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DocGeneral.categorize(test_resource_08)

        test_resource_09 = resource_class(
            name="foo.pdf",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DocGeneral.categorize(test_resource_09)

        test_resource_10 = resource_class(
            name="foo.ppt",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DocGeneral.categorize(test_resource_10)

        test_resource_11 = resource_class(
            name="foo.pptx",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DocGeneral.categorize(test_resource_11)

        test_resource_12 = resource_class(
            name="foo.rtf",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DocGeneral.categorize(test_resource_12)

        test_resource_13 = resource_class(
            name="foo.tex",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DocGeneral.categorize(test_resource_13)

        test_resource_14 = resource_class(
            name="foo.txt",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DocGeneral.categorize(test_resource_14)

        test_resource_15 = resource_class(
            name="foo.xls",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DocGeneral.categorize(test_resource_15)

        test_resource_16 = resource_class(
            name="foo.xlsm",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DocGeneral.categorize(test_resource_16)

        test_resource_17 = resource_class(
            name="foo.xlsx",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DocGeneral.categorize(test_resource_17)

        test_resource_18 = resource_class(
            name="changelog",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DocGeneral.categorize(test_resource_18)

        test_resource_19 = resource_class(
            name="changes",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DocGeneral.categorize(test_resource_19)

    def test_DocLicense(self):
        test_resource_01 = resource_class(
            name="copying",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DocLicense.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "doc"

        test_resource_02 = resource_class(
            name="copyright",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DocLicense.categorize(test_resource_02)

        test_resource_03 = resource_class(
            name="license",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DocLicense.categorize(test_resource_03)

        test_resource_04 = resource_class(
            name="notice",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DocLicense.categorize(test_resource_04)

        test_resource_05 = resource_class(
            name="LICENSE.c",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DocLicense.categorize(test_resource_05)

    def test_DocReadme(self):
        test_resource_01 = resource_class(
            name="READmeplease",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DocReadme.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "doc"

        test_resource_02 = resource_class(
            name="READme.foo",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.DocReadme.categorize(test_resource_02)

    def test_Font(self):
        test_resource_01 = resource_class(
            name="foo.fnt",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.Font.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "font"

        test_resource_02 = resource_class(
            name="foo.otf",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.Font.categorize(test_resource_02)

        test_resource_03 = resource_class(
            name="foo.ttf",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.Font.categorize(test_resource_03)

        test_resource_04 = resource_class(
            name="foo.woff",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.Font.categorize(test_resource_04)

        test_resource_05 = resource_class(
            name="foo.woff2",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.Font.categorize(test_resource_05)

        test_resource_06 = resource_class(
            name="foo.eot",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.Font.categorize(test_resource_06)

    def test_ManifestBower(self):
        test_resource_01 = resource_class(
            name="bower.json",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ManifestBower.categorize(test_resource_01)
        assert (
            file_cat.categorize_resource(test_resource_01).file_category == "manifest"
        )

    def test_ManifestCargo(self):
        test_resource_01 = resource_class(
            name="cargo.toml",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ManifestCargo.categorize(test_resource_01)
        assert (
            file_cat.categorize_resource(test_resource_01).file_category == "manifest"
        )

        test_resource_02 = resource_class(
            name="cargo.lock",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ManifestCargo.categorize(test_resource_02)

    def test_ManifestCocoaPod(self):
        test_resource_01 = resource_class(
            name="foo.podspec",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ManifestCocoaPod.categorize(test_resource_01)
        assert (
            file_cat.categorize_resource(test_resource_01).file_category == "manifest"
        )

    def test_ManifestComposer(self):
        test_resource_01 = resource_class(
            name="composer.json",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ManifestComposer.categorize(test_resource_01)
        assert (
            file_cat.categorize_resource(test_resource_01).file_category == "manifest"
        )

        test_resource_02 = resource_class(
            name="composer.lock",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ManifestComposer.categorize(test_resource_02)

    def test_ManifestGolang(self):
        test_resource_01 = resource_class(
            name="go.mod",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ManifestGolang.categorize(test_resource_01)
        assert (
            file_cat.categorize_resource(test_resource_01).file_category == "manifest"
        )

        test_resource_02 = resource_class(
            name="go.sum",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ManifestGolang.categorize(test_resource_02)

    def test_ManifestGradle(self):
        test_resource_01 = resource_class(
            name="build.gradle",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ManifestGradle.categorize(test_resource_01)
        assert (
            file_cat.categorize_resource(test_resource_01).file_category == "manifest"
        )

    def test_ManifestHaxe(self):
        test_resource_01 = resource_class(
            name="haxelib.json",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ManifestHaxe.categorize(test_resource_01)
        assert (
            file_cat.categorize_resource(test_resource_01).file_category == "manifest"
        )

    def test_ManifestIvy(self):
        test_resource_01 = resource_class(
            name="ivy.xml",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ManifestIvy.categorize(test_resource_01)
        assert (
            file_cat.categorize_resource(test_resource_01).file_category == "manifest"
        )

    def test_ManifestMaven(self):
        test_resource_01 = resource_class(
            name="pom.xml",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ManifestMaven.categorize(test_resource_01)
        assert (
            file_cat.categorize_resource(test_resource_01).file_category == "manifest"
        )

    def test_ManifestNpm(self):
        test_resource_01 = resource_class(
            name="package.json",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ManifestNpm.categorize(test_resource_01)
        assert (
            file_cat.categorize_resource(test_resource_01).file_category == "manifest"
        )

        test_resource_02 = resource_class(
            name="package-lock.json",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ManifestNpm.categorize(test_resource_02)

        test_resource_03 = resource_class(
            name="yarn.lock",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ManifestNpm.categorize(test_resource_03)

    def test_ManifestNuGet(self):
        test_resource_01 = resource_class(
            name="foo.nuspec",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ManifestNuGet.categorize(test_resource_01)
        assert (
            file_cat.categorize_resource(test_resource_01).file_category == "manifest"
        )

    def test_ManifestPyPi(self):
        test_resource_01 = resource_class(
            name="requirements.txt",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ManifestPyPi.categorize(test_resource_01)
        assert (
            file_cat.categorize_resource(test_resource_01).file_category == "manifest"
        )

    def test_ManifestRubyGem(self):
        test_resource_01 = resource_class(
            name="gemfile",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ManifestRubyGem.categorize(test_resource_01)
        assert (
            file_cat.categorize_resource(test_resource_01).file_category == "manifest"
        )

        test_resource_02 = resource_class(
            name="gemfile.lock",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ManifestRubyGem.categorize(test_resource_02)

    def test_MediaAudio(self):
        test_resource_01 = resource_class(
            name="foo.3pg",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.MediaAudio.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "media"

        test_resource_02 = resource_class(
            name="foo.aac",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.MediaAudio.categorize(test_resource_02)

        test_resource_03 = resource_class(
            name="foo.amr",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.MediaAudio.categorize(test_resource_03)

        test_resource_04 = resource_class(
            name="foo.awb",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.MediaAudio.categorize(test_resource_04)

        test_resource_05 = resource_class(
            name="foo.m4a",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.MediaAudio.categorize(test_resource_05)

        test_resource_06 = resource_class(
            name="foo.mp3",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.MediaAudio.categorize(test_resource_06)

        test_resource_07 = resource_class(
            name="foo.mpa",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.MediaAudio.categorize(test_resource_07)

        test_resource_08 = resource_class(
            name="foo.ogg",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.MediaAudio.categorize(test_resource_08)

        test_resource_09 = resource_class(
            name="foo.opus",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.MediaAudio.categorize(test_resource_09)

        test_resource_10 = resource_class(
            name="foo.wav",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.MediaAudio.categorize(test_resource_10)

        test_resource_11 = resource_class(
            name="foo.wma",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.MediaAudio.categorize(test_resource_11)

    def test_MediaImage(self):
        test_resource_01 = resource_class(
            name="foo.bmp",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.MediaImage.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "media"

        test_resource_02 = resource_class(
            name="foo.gif",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.MediaImage.categorize(test_resource_02)

        test_resource_03 = resource_class(
            name="foo.ico",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.MediaImage.categorize(test_resource_03)

        test_resource_04 = resource_class(
            name="foo.jpg",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.MediaImage.categorize(test_resource_04)

        test_resource_05 = resource_class(
            name="foo.jpeg",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.MediaImage.categorize(test_resource_05)

        test_resource_06 = resource_class(
            name="foo.png",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.MediaImage.categorize(test_resource_06)

        test_resource_07 = resource_class(
            name="foo.svg",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.MediaImage.categorize(test_resource_07)

        test_resource_08 = resource_class(
            name="foo.webp",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.MediaImage.categorize(test_resource_08)

    def test_MediaVideo(self):
        test_resource_01 = resource_class(
            name="foo.avi",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.MediaVideo.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "media"

        test_resource_02 = resource_class(
            name="foo.h264",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.MediaVideo.categorize(test_resource_02)

        test_resource_03 = resource_class(
            name="foo.mp4",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.MediaVideo.categorize(test_resource_03)

        test_resource_04 = resource_class(
            name="foo.mpg",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.MediaVideo.categorize(test_resource_04)

        test_resource_05 = resource_class(
            name="foo.mpeg",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.MediaVideo.categorize(test_resource_05)

        test_resource_06 = resource_class(
            name="foo.swf",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.MediaVideo.categorize(test_resource_06)

        test_resource_07 = resource_class(
            name="foo.wmv",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.MediaVideo.categorize(test_resource_07)

    def test_ScriptBash(self):
        test_resource_01 = resource_class(
            name="foo.bash",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ScriptBash.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "script"

    def test_ScriptBatSh(self):
        test_resource_01 = resource_class(
            name="foo.bat",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ScriptBatSh.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "script"

        test_resource_02 = resource_class(
            name="foo.sh",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ScriptBatSh.categorize(test_resource_02)

    def test_ScriptBuild(self):
        test_resource_01 = resource_class(
            name="foo.cmake",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ScriptBuild.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "script"

        test_resource_02 = resource_class(
            name="foo.cmakelist",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ScriptBuild.categorize(test_resource_02)

        test_resource_03 = resource_class(
            name="foo.bar",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="text/x-makefile",
            file_type="",
            programming_language="",
        )
        assert file_cat.ScriptBuild.categorize(test_resource_03)

    def test_ScriptData(self):
        test_resource_01 = resource_class(
            name="foo.sql",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ScriptData.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "script"

        test_resource_02 = resource_class(
            name="foo.psql",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.ScriptData.categorize(test_resource_02)

    def test_SourceAssembler(self):
        test_resource_01 = resource_class(
            name="foo.S",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourceAssembler.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "source"

        test_resource_02 = resource_class(
            name="foo.s",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert not file_cat.SourceAssembler.categorize(test_resource_02)

    def test_SourceC(self):
        test_resource_01 = resource_class(
            name="foo.c",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourceC.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "source"

        test_resource_02 = resource_class(
            name="foo.h",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="text/x-c",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourceC.categorize(test_resource_02)

    def test_SourceCoffeeScript(self):
        test_resource_01 = resource_class(
            name="foo.coffee",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourceCoffeeScript.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "source"

    def test_SourceCpp(self):
        test_resource_01 = resource_class(
            name="foo.cpp",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourceCpp.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "source"

        test_resource_02 = resource_class(
            name="foo.hpp",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourceCpp.categorize(test_resource_02)

        test_resource_03 = resource_class(
            name="foo.cc",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourceCpp.categorize(test_resource_03)

        test_resource_04 = resource_class(
            name="foo.h",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="text/x-c++",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourceCpp.categorize(test_resource_04)

    def test_SourceCsharp(self):
        test_resource_01 = resource_class(
            name="foo.cs",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourceCsharp.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "source"

    # ==================================

    def test_WebRuby(self):
        test_resource_01 = resource_class(
            name="foo.erb",
            location="",
            path="",
            rid="",
            pid="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.WebRuby.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "web"
