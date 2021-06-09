#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
from os import path
from os import walk

from debian_inspector.copyright import DebianCopyright

from commoncode.testcase import FileBasedTesting
from commoncode import text
import saneyaml

from packagedcode import debian_copyright


def check_expected_parse_copyright_file(
    test_loc,
    expected_loc,
    regen=False,
    with_details=True,
):
    """
    Check copyright parsing of `test_loc` location against an expected JSON file
    at `expected_loc` location. Regen the expected file if `regen` is True.
    """
    if with_details:
        filter_licenses=False
        skip_debian_packaging=False
        simplify_licenses=False
        unique_copyrights=False
    else:
        filter_licenses=True
        skip_debian_packaging=True
        simplify_licenses=False
        unique_copyrights=True

    dc = debian_copyright.parse_copyright_file(location=test_loc, check_consistency=False)
    declared_license = dc.get_declared_license(
        filter_licenses=filter_licenses,
        skip_debian_packaging=skip_debian_packaging,
        simplify_licenses=simplify_licenses,
    )
    license_expression = dc.get_license_expression(
        filter_licenses=filter_licenses,
        skip_debian_packaging=skip_debian_packaging,
        simplify_licenses=simplify_licenses,
    )
    copyright = dc.get_copyright(
        skip_debian_packaging=skip_debian_packaging,
        unique_copyrights=unique_copyrights,
    )

    parsed = declared_license, license_expression, copyright
    
    result = saneyaml.dump(list(parsed))
    if regen:
        with io.open(expected_loc, 'w', encoding='utf-8') as reg:
            reg.write(result)

    with io.open(expected_loc, encoding='utf-8') as ex:
        expected = ex.read()

    if result != expected:

        expected = '\n'.join([
            'file://' + test_loc,
            'file://' + expected_loc,
            expected
        ])

        assert result == expected


def relative_walk(dir_path):
    """
    Walk path and yield files paths relative to dir_path.
    """
    for base_dir, _dirs, files in walk(dir_path):
        for file_name in files:
            if file_name.endswith('.yml'):
                continue
            file_path = path.join(base_dir, file_name)
            file_path = file_path.replace(dir_path, '', 1)
            file_path = file_path.strip(path.sep)
            yield file_path


def create_test_function(
    test_loc,
    expected_loc,
    test_name,
    with_details=True,
    regen=False,
):
    """
    Return a test function closed on test arguments.
    """

    # closure on the test params
    def test_func(self):
        check_expected_parse_copyright_file(
            test_loc, expected_loc, with_details=with_details, regen=regen)

    # set a proper function name to display in reports and use in discovery
    if isinstance(test_name, bytes):
        test_name = test_name.decode('utf-8')

    test_func.__name__ = test_name
    return test_func


def build_tests(test_dir, clazz, prefix='test_', regen=False):
    """
    Dynamically build test methods for each copyright file in `test_dir` and
    attach the test method to the `clazz` class.
    """
    test_data_dir = path.join(path.dirname(__file__), 'data')
    test_dir_loc = path.join(test_data_dir, test_dir)
    # loop through all items and attach a test method to our test class
    for test_file in relative_walk(test_dir_loc):
        test_loc = path.join(test_dir_loc, test_file)

        # create two test methods: one with and one without details
        test_name1 = prefix + text.python_safe_name(test_file)
        test_method = create_test_function(
            test_loc=test_loc,
            expected_loc=test_loc + '.expected.yml',
            test_name=test_name1,
            regen=regen,
            with_details=False,
        )
        # attach that method to the class
        setattr(clazz, test_name1, test_method)

        test_name2 = prefix + 'detailed_' + text.python_safe_name(test_file)
        test_method = create_test_function(
            test_loc=test_loc,
            expected_loc=test_loc + '-detailed.expected.yml',
            test_name=test_name2,
            regen=regen,
            with_details=True,
        )
        # attach that method to the class
        setattr(clazz, test_name2, test_method)


class TestDebianCopyrightLicenseDetection(FileBasedTesting):
    # pytestmark = pytest.mark.scanslow
    test_data_dir = path.join(path.dirname(__file__), 'data')


build_tests(
    test_dir='debian/copyright/debian-2019-11-15',
    prefix='test_debian_parse_copyright_file_',
    clazz=TestDebianCopyrightLicenseDetection,
    regen=False,
)


class TestDebianSlimCopyrightLicenseDetection(FileBasedTesting):
    # pytestmark = pytest.mark.scanslow
    test_data_dir = path.join(path.dirname(__file__), 'data')


build_tests(
    test_dir='debian/copyright/debian-slim-2021-04-07',
    prefix='test_debian_slim_parse_copyright_file_',
    clazz=TestDebianSlimCopyrightLicenseDetection,
    regen=False,
)


class TestDebianDetector(FileBasedTesting):
    test_data_dir = path.join(path.dirname(__file__), 'data/debian/copyright/')

    def test_add_unknown_matches(self):
        
        matches = debian_copyright.add_unknown_matches(name='foo',text='bar')
        assert len(matches) == 1
        

class TestEnhancedDebianCopyright(FileBasedTesting):
    test_data_dir = path.join(path.dirname(__file__), 'data/debian/copyright/')
    
    def test_is_paragraph_debian_packaging(self):
        test_file = self.get_test_loc("debian-slim-2021-04-07/usr/share/doc/libhogweed6/copyright")
        edebian_copyright = debian_copyright.EnhancedDebianCopyright(debian_copyright=DebianCopyright.from_file(test_file))
        file_paras = edebian_copyright.file_paragraphs
        assert debian_copyright.is_paragraph_debian_packaging(file_paras[-3])

    def test_is_paragraph_primary_license(self):
        test_file = self.get_test_loc("debian-slim-2021-04-07/usr/share/doc/libhogweed6/copyright")
        edebian_copyright = debian_copyright.EnhancedDebianCopyright(debian_copyright=DebianCopyright.from_file(test_file))
        file_paras = edebian_copyright.file_paragraphs
        assert debian_copyright.is_paragraph_primary_license(file_paras[0])

    def test_get_header_para(self):
        test_file = self.get_test_loc("debian-slim-2021-04-07/usr/share/doc/libhogweed6/copyright")
        edebian_copyright = debian_copyright.EnhancedDebianCopyright(debian_copyright=DebianCopyright.from_file(test_file))
        header_para = edebian_copyright.header_paragraph
        assert header_para.license.name == "LGPL-3+ or GPL-2+"
        assert header_para.upstream_name.value == "Nettle"
        assert header_para.source.text == "http://www.lysator.liu.se/~nisse/nettle/"
    
    def test_get_files_paras(self):
        test_file = self.get_test_loc("debian-2019-11-15/main/c/cryptsetup/stable_copyright")
        edebian_copyright = debian_copyright.EnhancedDebianCopyright(debian_copyright=DebianCopyright.from_file(test_file))
        files_paras = edebian_copyright.file_paragraphs
        assert len(files_paras) == 15
        assert files_paras[1].license.name == "GPL-2+"
        
    def test_get_license_paras(self):
        test_file = self.get_test_loc("debian-2019-11-15/main/c/cryptsetup/stable_copyright")
        edebian_copyright = debian_copyright.EnhancedDebianCopyright(debian_copyright=DebianCopyright.from_file(test_file))
        license_paras = edebian_copyright.license_paragraphs
        assert len(license_paras) == 6
        assert license_paras[0].license.name == "GPL-2+"

    def test_get_paras_with_license_text(self):
        test_file = self.get_test_loc("debian-slim-2021-04-07/usr/share/doc/liblzma5/copyright")
        edebian_copyright = debian_copyright.EnhancedDebianCopyright(debian_copyright=DebianCopyright.from_file(test_file))
        paras_with_license = edebian_copyright.paragraphs_with_license_text
        assert isinstance(paras_with_license[0], debian_copyright.CopyrightHeaderParagraph)
        assert isinstance(paras_with_license[1], debian_copyright.CopyrightFilesParagraph)
        

    def test_get_other_paras(self):
        test_file = self.get_test_loc("crafted_for_tests/test_other_paras")
        edebian_copyright = debian_copyright.EnhancedDebianCopyright(debian_copyright=DebianCopyright.from_file(test_file))
        other_paras = edebian_copyright.other_paragraphs
        assert len(other_paras) == 1
        assert other_paras[0].extra_data["unknown"].text == "Example of other paras."
        
    def test_get_duplicate_license_paras(self):
        test_file = self.get_test_loc("crafted_for_tests/test_duplicate_license_para_name")
        edebian_copyright = debian_copyright.EnhancedDebianCopyright(debian_copyright=DebianCopyright.from_file(test_file))
        duplicate_paras = edebian_copyright.duplicate_license_paragraphs
        assert len(duplicate_paras) == 1
        duplicate_paras[0].license.name == "GPL-2+"

    def test_get_license_nameless_paras_with_name(self):
        test_file = self.get_test_loc("crafted_for_tests/test_license_with_names")
        edebian_copyright = debian_copyright.EnhancedDebianCopyright(debian_copyright=DebianCopyright.from_file(test_file))
        nameless_paras = edebian_copyright.license_nameless_paragraphs
        assert len(nameless_paras) == 0

    def test_get_license_nameless_paras_without_name(self):
        test_file = self.get_test_loc("crafted_for_tests/test_license_nameless")
        edebian_copyright = debian_copyright.EnhancedDebianCopyright(debian_copyright=DebianCopyright.from_file(test_file))
        nameless_paras = edebian_copyright.license_nameless_paragraphs
        assert len(nameless_paras) == 1
        
    def test_is_all_licenses_used_all_used(self):
        test_file = self.get_test_loc("crafted_for_tests/test_license_with_names")
        edebian_copyright = debian_copyright.EnhancedDebianCopyright(debian_copyright=DebianCopyright.from_file(test_file))
        assert edebian_copyright.is_all_licenses_used

    def test_is_all_licenses_used_all_not_used(self):
        test_file = self.get_test_loc("crafted_for_tests/test_all_licenses_not_used")
        edebian_copyright = debian_copyright.EnhancedDebianCopyright(debian_copyright=DebianCopyright.from_file(test_file))
        assert not edebian_copyright.is_all_licenses_used
        
    def test_is_all_licenses_expressions_parsable_case_parsable(self):
        test_file = self.get_test_loc("crafted_for_tests/test_license_with_names")
        edebian_copyright = debian_copyright.EnhancedDebianCopyright(debian_copyright=DebianCopyright.from_file(test_file))
        assert edebian_copyright.is_all_licenses_expressions_parsable

    def test_is_all_licenses_expressions_parsable_case_unparsable(self):
        test_file = self.get_test_loc("crafted_for_tests/test_licenses_unparsable")
        edebian_copyright = debian_copyright.EnhancedDebianCopyright(debian_copyright=DebianCopyright.from_file(test_file))
        assert not edebian_copyright.is_all_licenses_expressions_parsable
        
    def test_consistency_structured_copyright_file_inconsistent(self):
        test_file = self.get_test_loc("debian-slim-2021-04-07/usr/share/doc/perl-base/copyright")
        try:
            debian_copyright.parse_copyright_file(location=test_file, check_consistency=True)
            self.fail(msg="Exception not raised")
        except debian_copyright.DebianCopyrightStructureError:
            pass

    def test_consistency_unstructured_copyright_file(self):
        test_file = self.get_test_loc("debian-2019-11-15/main/p/pulseaudio/stable_copyright")
        try:
            debian_copyright.parse_copyright_file(location=test_file, check_consistency=True)
            self.fail(msg="Exception not raised")
        except debian_copyright.DebianCopyrightStructureError:
            pass

    def test_if_structured_copyright_file(self):
        test_file = self.get_test_loc("debian-slim-2021-04-07/usr/share/doc/libhogweed6/copyright")
        content = debian_copyright.unicode_text(test_file)
        assert debian_copyright.is_machine_readable_copyright(content)

    def test_if_not_structured_copyright_file(self):
        test_file = self.get_test_loc("debian-2019-11-15/main/p/pulseaudio/stable_copyright")
        content = debian_copyright.unicode_text(test_file)
        assert not debian_copyright.is_machine_readable_copyright(content)

    def test_multiple_blank_lines_is_valid_paragraph(self):
        test_file = self.get_test_loc("debian-slim-gpgv.copyright")
        edebian_copyright = debian_copyright.EnhancedDebianCopyright(debian_copyright=DebianCopyright.from_file(test_file))
        other_paras = edebian_copyright.other_paragraphs
        print(other_paras)
        assert len(other_paras) == 1
        assert other_paras[0].extra_data["unknown"].text == "This is a catchall para."
