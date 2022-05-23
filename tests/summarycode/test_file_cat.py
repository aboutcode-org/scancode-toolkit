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


test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), "data")


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
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourceCsharp.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "source"

    def test_SourceGo(self):
        test_resource_01 = resource_class(
            name="foo.go",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourceGo.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "source"

    def test_SourceHaskell(self):
        test_resource_01 = resource_class(
            name="foo.hs",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourceHaskell.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "source"

        test_resource_02 = resource_class(
            name="foo.lhs",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourceHaskell.categorize(test_resource_02)

    def test_SourceJava(self):
        test_resource_01 = resource_class(
            name="foo.java",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourceJava.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "source"

    def test_SourceJavascript(self):
        test_resource_01 = resource_class(
            name="foo.js",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourceJavascript.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "source"

    def test_SourceJavaserverpage(self):
        test_resource_01 = resource_class(
            name="foo.jsp",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourceJavaserverpage.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "source"

    def test_SourceKotlin(self):
        test_resource_01 = resource_class(
            name="foo.kt",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourceKotlin.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "source"

    def test_SourceObjectivec(self):
        test_resource_01 = resource_class(
            name="foo.m",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourceObjectivec.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "source"

        test_resource_02 = resource_class(
            name="foo.mm",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourceObjectivec.categorize(test_resource_02)

        test_resource_03 = resource_class(
            name="foo.h",
            location="",
            path="",
            is_file=True,
            mime_type="text/x-objective-c",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourceObjectivec.categorize(test_resource_03)

    def test_SourcePerl(self):
        test_resource_01 = resource_class(
            name="foo.pl",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourcePerl.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "source"

        test_resource_02 = resource_class(
            name="foo.pm",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourcePerl.categorize(test_resource_02)

    def test_SourcePhp(self):
        test_resource_01 = resource_class(
            name="foo.php",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourcePhp.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "source"

        test_resource_02 = resource_class(
            name="foo.php3",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourcePhp.categorize(test_resource_02)

        test_resource_03 = resource_class(
            name="foo.php4",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourcePhp.categorize(test_resource_03)

        test_resource_04 = resource_class(
            name="foo.php5",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourcePhp.categorize(test_resource_04)

    def test_SourcePython(self):
        test_resource_01 = resource_class(
            name="foo.py",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourcePython.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "source"

    def test_SourceRuby(self):
        test_resource_01 = resource_class(
            name="foo.rb",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourceRuby.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "source"

        test_resource_02 = resource_class(
            name="foo.rake",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourceRuby.categorize(test_resource_02)

    def test_SourceRust(self):
        test_resource_01 = resource_class(
            name="foo.rs",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourceRust.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "source"

    def test_SourceScala(self):
        test_resource_01 = resource_class(
            name="foo.scala",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourceScala.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "source"

    def test_SourceSwift(self):
        test_resource_01 = resource_class(
            name="foo.swift",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.SourceSwift.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "source"

    def test_SourceTypescript(self):
        test_resource_01 = resource_class(
            name="foo.ts",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="TypeScript",
        )
        assert file_cat.SourceTypescript.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "source"

    def test_WebCss(self):
        test_resource_01 = resource_class(
            name="foo.css",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.WebCss.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "web"

        test_resource_02 = resource_class(
            name="foo.less",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.WebCss.categorize(test_resource_02)

        test_resource_03 = resource_class(
            name="foo.scss",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.WebCss.categorize(test_resource_03)

    def test_WebHtml(self):
        test_resource_01 = resource_class(
            name="foo.htm",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.WebHtml.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "web"

        test_resource_02 = resource_class(
            name="foo.html",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.WebHtml.categorize(test_resource_02)

    def test_WebRuby(self):
        test_resource_01 = resource_class(
            name="foo.erb",
            location="",
            path="",
            is_file=True,
            mime_type="",
            file_type="",
            programming_language="",
        )
        assert file_cat.WebRuby.categorize(test_resource_01)
        assert file_cat.categorize_resource(test_resource_01).file_category == "web"


def test_media01_info():
    test_dir = test_env.get_test_loc("file_cat/code/media01")
    result_file = test_env.get_temp_file("json")
    run_scan_click(["--info", "--file-cat", test_dir, "--json", result_file])
    expected = test_env.get_test_loc("file_cat/scans/media01/media01-info-scan.json")
    check_json_scan(
        expected, result_file, remove_file_date=True, regen=REGEN_TEST_FIXTURES
    )
