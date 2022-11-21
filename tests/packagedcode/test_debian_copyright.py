#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from os import path
from os import walk

import saneyaml
from commoncode.testcase import FileBasedTesting
from commoncode import text
from debian_inspector.copyright import DebianCopyright
from debian_inspector.copyright import CatchAllParagraph
from debian_inspector.copyright import CopyrightLicenseParagraph
from debian_inspector.copyright import CopyrightHeaderParagraph
from debian_inspector.copyright import CopyrightFilesParagraph

from packagedcode import debian_copyright
from scancode_config import REGEN_TEST_FIXTURES


def check_expected_parse_copyright_file(
    test_loc,
    expected_loc,
    regen=REGEN_TEST_FIXTURES,
    simplified=False,
):
    '''
    Check copyright parsing of `test_loc` location against an expected JSON file
    at `expected_loc` location. Regen the expected file if `regen` is True.
    '''
    if simplified:
        filter_duplicates = True
        skip_debian_packaging = True
        simplify_licenses = True
        unique_copyrights = True
    else:
        filter_duplicates = False
        skip_debian_packaging = False
        simplify_licenses = False
        unique_copyrights = False

    try:
        dc = debian_copyright.parse_copyright_file(
            location=test_loc,
            check_consistency=False,
        )

        declared_license = dc.get_declared_license(
            filter_duplicates=filter_duplicates,
            skip_debian_packaging=skip_debian_packaging,
        )

        copyrght = dc.get_copyright(
            skip_debian_packaging=skip_debian_packaging,
            unique_copyrights=unique_copyrights,
        ).strip()

        license_fields = debian_copyright.DebianLicenseFields.get_license_fields(
            debian_copyright=dc,
            simplify_licenses=simplify_licenses,
            skip_debian_packaging=skip_debian_packaging,
            filter_duplicates=filter_duplicates,
        )

        results = {
            'declared_license': declared_license,
            'declared_license_expression': license_fields.declared_license_expression,
            'declared_license_expression_spdx': license_fields.declared_license_expression_spdx,
            'other_license_expression': license_fields.other_license_expression,
            'other_license_expression_spdx': license_fields.other_license_expression_spdx,
            'license_detections': license_fields.license_detections,
            'other_license_detections': license_fields.other_license_detections,
            'copyright': copyrght,
        }

        if regen:
            expected = results
            with open(expected_loc, 'w') as res:
                res.write(saneyaml.dump(results))
        else:
            with open(expected_loc) as ex:
                expected = saneyaml.load(ex.read())
    except Exception as e:
        import traceback
        files = [
            'file://' + test_loc,
            'file://' + expected_loc,
        ]
        raise Exception(repr(e), traceback.format_exc(), files) from e

    if (
        not regen
        and (saneyaml.dump(results) != saneyaml.dump(expected)
        or 'unknown-license-reference' in license_fields.license_expression_keys)
    ) :
        res = {
            'test_loc': f'file://{test_loc}',
            'expected_loc': f'file://{expected_loc}',
        }
        res.update(results)
        results = saneyaml.dump(res)
        results = results.replace(
            'unknown-license-reference',
            'unknown-license-reference should not be detected',
        )
        assert results == saneyaml.dump(expected)


def relative_walk(dir_path):
    '''
    Walk path and yield files paths relative to dir_path.
    '''
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
    simplified=False,
    regen=REGEN_TEST_FIXTURES,
):
    '''
    Return a test function closed on test arguments.
    '''

    # closure on the test params
    def test_func(self):
        check_expected_parse_copyright_file(
            test_loc,
            expected_loc,
            simplified=simplified,
            regen=regen,
        )

    # set a proper function name to display in reports and use in discovery
    if isinstance(test_name, bytes):
        test_name = test_name.decode('utf-8')

    test_func.__name__ = test_name
    return test_func


def build_tests(test_dir, clazz, prefix='test_', regen=REGEN_TEST_FIXTURES):
    '''
    Dynamically build test methods for each copyright file in `test_dir` and
    attach the test method to the `clazz` class.
    '''
    test_data_dir = path.join(path.dirname(__file__), 'data')
    test_dir_loc = path.join(test_data_dir, test_dir)
    # loop through all items and attach a test method to our test class
    for test_file in relative_walk(test_dir_loc):
        test_loc = path.join(test_dir_loc, test_file)

        test_name2 = prefix + 'detailed_' + text.python_safe_name(test_file)
        test_method = create_test_function(
            test_loc=test_loc,
            expected_loc=test_loc + '-detailed.expected.yml',
            test_name=test_name2,
            regen=regen,
            simplified=False,
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
    regen=REGEN_TEST_FIXTURES,
)


class TestDebianSlimCopyrightLicenseDetection(FileBasedTesting):
    # pytestmark = pytest.mark.scanslow
    test_data_dir = path.join(path.dirname(__file__), 'data')


build_tests(
    test_dir='debian/copyright/debian-slim-2021-04-07',
    prefix='test_debian_slim_parse_copyright_file_',
    clazz=TestDebianSlimCopyrightLicenseDetection,
    regen=REGEN_TEST_FIXTURES,
)


class TestDebianMiscCopyrightLicenseDetection(FileBasedTesting):
    # pytestmark = pytest.mark.scanslow
    test_data_dir = path.join(path.dirname(__file__), 'data')


build_tests(
    test_dir='debian/copyright/debian-misc',
    prefix='test_debian_misc_parse_copyright_file_',
    clazz=TestDebianMiscCopyrightLicenseDetection,
    regen=REGEN_TEST_FIXTURES,
)


class TestDebianDetector(FileBasedTesting):
    test_data_dir = path.join(path.dirname(__file__), 'data/debian/copyright/')

    def test_add_unknown_matches(self):
        matches = debian_copyright.add_undetected_debian_matches(name='foo', text='bar')
        assert len(matches) == 1
        match = matches[0]
        assert match.matched_text() == 'license foo\nbar'


class TestEnhancedDebianCopyright(FileBasedTesting):
    test_data_dir = path.join(path.dirname(__file__), 'data/debian/copyright/')

    def test_simplification(self):
        test_loc = self.get_test_loc('simplified-license/stable_copyright')
        expected_loc = self.get_test_loc('simplified-license/stable_copyright.expected.yml')

        check_expected_parse_copyright_file(
            test_loc=test_loc,
            expected_loc=expected_loc,
            simplified=True,
            regen=REGEN_TEST_FIXTURES,
        )

    def test_is_paragraph_debian_packaging(self):
        test_file = self.get_test_loc('debian-slim-2021-04-07/usr/share/doc/libhogweed6/copyright')
        edebian_copyright = debian_copyright.EnhancedDebianCopyright(debian_copyright=DebianCopyright.from_file(test_file))
        file_paras = edebian_copyright.file_paragraphs
        assert debian_copyright.is_paragraph_debian_packaging(file_paras[-3])

    def test_is_paragraph_primary_license(self):
        test_file = self.get_test_loc('debian-slim-2021-04-07/usr/share/doc/libhogweed6/copyright')
        edebian_copyright = debian_copyright.EnhancedDebianCopyright(debian_copyright=DebianCopyright.from_file(test_file))
        file_paras = edebian_copyright.file_paragraphs
        assert debian_copyright.is_paragraph_primary_license(file_paras[0])

    def test_get_header_para(self):
        test_file = self.get_test_loc('debian-slim-2021-04-07/usr/share/doc/libhogweed6/copyright')
        edebian_copyright = debian_copyright.EnhancedDebianCopyright(debian_copyright=DebianCopyright.from_file(test_file))
        header_para = edebian_copyright.header_paragraph
        assert header_para.license.name == 'LGPL-3+ or GPL-2+'
        assert header_para.upstream_name.value == 'Nettle'
        assert header_para.source.text == 'http://www.lysator.liu.se/~nisse/nettle/'

    def test_get_files_paras(self):
        test_file = self.get_test_loc('debian-2019-11-15/main/c/cryptsetup/stable_copyright')
        edebian_copyright = debian_copyright.EnhancedDebianCopyright(debian_copyright=DebianCopyright.from_file(test_file))
        files_paras = edebian_copyright.file_paragraphs
        assert len(files_paras) == 15
        assert files_paras[1].license.name == 'GPL-2+'

    def test_get_license_paras(self):
        test_file = self.get_test_loc('debian-2019-11-15/main/c/cryptsetup/stable_copyright')
        edebian_copyright = debian_copyright.EnhancedDebianCopyright(debian_copyright=DebianCopyright.from_file(test_file))
        license_paras = edebian_copyright.license_paragraphs
        assert len(license_paras) == 6
        assert license_paras[0].license.name == 'GPL-2+'

    def test_get_paras_with_license_text(self):
        test_file = self.get_test_loc('debian-slim-2021-04-07/usr/share/doc/liblzma5/copyright')
        edebian_copyright = debian_copyright.EnhancedDebianCopyright(debian_copyright=DebianCopyright.from_file(test_file))
        paras_with_license = edebian_copyright.paragraphs_with_license_text
        assert isinstance(paras_with_license[0], debian_copyright.CopyrightHeaderParagraph)
        assert isinstance(paras_with_license[1], debian_copyright.CopyrightFilesParagraph)

    def test_get_other_paras(self):
        test_file = self.get_test_loc('crafted_for_tests/test_other_paras')
        edebian_copyright = debian_copyright.EnhancedDebianCopyright(debian_copyright=DebianCopyright.from_file(test_file))
        other_paras = edebian_copyright.other_paragraphs
        assert len(other_paras) == 1
        assert other_paras[0].extra_data['unknown'] == 'Example of other paras.'

    def test_get_duplicate_license_paras(self):
        test_file = self.get_test_loc('crafted_for_tests/test_duplicate_license_para_name')
        edebian_copyright = debian_copyright.EnhancedDebianCopyright(debian_copyright=DebianCopyright.from_file(test_file))
        duplicate_paras = edebian_copyright.duplicate_license_paragraphs
        assert len(duplicate_paras) == 1
        assert duplicate_paras[0].license.name == 'GPL-2+'

    def test_if_structured_copyright_file(self):
        test_file = self.get_test_loc('debian-slim-2021-04-07/usr/share/doc/libhogweed6/copyright')
        content = debian_copyright.unicode_text(test_file)
        assert debian_copyright.EnhancedDebianCopyright.is_machine_readable_copyright(content)

    def test_if_not_structured_copyright_file(self):
        test_file = self.get_test_loc('debian-2019-11-15/main/p/pulseaudio/stable_copyright')
        content = debian_copyright.unicode_text(test_file)
        assert not debian_copyright.EnhancedDebianCopyright.is_machine_readable_copyright(content)

    def test_multiple_blank_lines_is_valid_paragraph(self):
        test_file = self.get_test_loc('multiple-blank-lines.copyright')
        edebian_copyright = debian_copyright.EnhancedDebianCopyright(debian_copyright=DebianCopyright.from_file(test_file))
        other_paras = edebian_copyright.other_paragraphs
        assert len(other_paras) == 1
        assert other_paras[0].extra_data['unknown'] == 'This is a catchall para.'

    def test_is_really_structured(self):

        def build_dc(paragraphs):
            d = DebianCopyright()
            d.paragraphs.extend(paragraphs)
            return d

        assert debian_copyright.is_really_structured(
            build_dc([CopyrightHeaderParagraph()])
        )
        assert debian_copyright.is_really_structured(
            build_dc([CopyrightLicenseParagraph()])
        )
        assert debian_copyright.is_really_structured(
            build_dc([CopyrightFilesParagraph()])
        )
        assert not debian_copyright.is_really_structured(
            build_dc([CatchAllParagraph()])
        )

        assert  debian_copyright.is_really_structured(
            build_dc([
                CopyrightHeaderParagraph(),
                CopyrightFilesParagraph(),
                CopyrightFilesParagraph(),
                CopyrightLicenseParagraph(),
                CopyrightLicenseParagraph(),
            ])
        )

        assert not debian_copyright.is_really_structured(
            build_dc([CatchAllParagraph(), CatchAllParagraph()])
        )

        assert not debian_copyright.is_really_structured(
            build_dc([
                CopyrightLicenseParagraph(),
                CatchAllParagraph(),
                CatchAllParagraph(),
                CatchAllParagraph(),
                CatchAllParagraph(),
                CatchAllParagraph(),
            ])
        )

        assert debian_copyright.is_really_structured(
            build_dc([
                CopyrightLicenseParagraph(),
                CatchAllParagraph(),
            ])
        )
        assert debian_copyright.is_really_structured(
            build_dc([
                CopyrightHeaderParagraph(),
                CatchAllParagraph(),
            ])
        )
        assert debian_copyright.is_really_structured(
            build_dc([
                CopyrightFilesParagraph(),
                CatchAllParagraph(),
            ])
        )
        assert debian_copyright.is_really_structured(
            build_dc([
                CopyrightLicenseParagraph(),
                CatchAllParagraph(),
            ])
        )

    def test_is_really_structured_from_file(self):

        assert not debian_copyright.is_really_structured(DebianCopyright.from_file(self.get_test_loc('dep5-pretend.copyright')))
        assert not debian_copyright.is_really_structured(DebianCopyright.from_file(self.get_test_loc('dep5-not-dep5.copyright')))

        # catchall are merged
        assert debian_copyright.is_really_structured(DebianCopyright.from_file(self.get_test_loc('dep5-pretend-5-catchall.copyright')))

        assert debian_copyright.is_really_structured(DebianCopyright.from_file(self.get_test_loc('dep5-ok.copyright')))
        assert debian_copyright.is_really_structured(DebianCopyright.from_file(self.get_test_loc('dep5-ok-header-only.copyright')))
        assert debian_copyright.is_really_structured(DebianCopyright.from_file(self.get_test_loc('dep5-ok-mini.copyright')))
        assert debian_copyright.is_really_structured(DebianCopyright.from_file(self.get_test_loc('dep5-ok.copyright')))

