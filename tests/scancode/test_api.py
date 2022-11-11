#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

from commoncode.testcase import FileBasedTesting
from scancode import api


class TestPackageAPI(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_get_package_info_works_for_maven_dot_pom(self):
        test_file = self.get_test_loc('api/package/p6spy-1.3.pom')
        packages = api.get_package_data(test_file)
        assert packages['package_data'][0]['version'] == '1.3'

    def test_get_package_info_works_for_maven_pom_dot_xml(self):
        test_file = self.get_test_loc('api/package/pom.xml')
        packages = api.get_package_data(test_file)
        assert packages['package_data'][0]['version'] == '1.3'


class TestAPI(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_get_package_info_can_pickle(self):
        test_file = self.get_test_loc('api/package/package.json')
        package = api.get_package_data(test_file)

        import pickle
        try:
            import cPickle
        except ImportError:
            import pickle as cPickle
        try:
            _pickled = pickle.dumps(package, pickle.HIGHEST_PROTOCOL)
            _cpickled = cPickle.dumps(package, pickle.HIGHEST_PROTOCOL)
            self.fail('pickle.HIGHEST_PROTOCOL used to fail to pickle this data')
        except:
            _pickled = pickle.dumps(package)
            _cpickled = cPickle.dumps(package)

    def test_get_file_info_include_size(self):
        # note the test file is EMPTY on purpose to generate all False is_* flags
        test_dir = self.get_test_loc('api/info/test.txt')
        info = api.get_file_info(test_dir)
        expected = [
            ('size', 0),
            ('sha1', None),
            ('md5', None),
            ('sha256', None),
            ('mime_type', 'inode/x-empty'),
            ('file_type', 'empty'),
            ('programming_language', None),
            ('is_binary', False),
            ('is_text', True),
            ('is_archive', False),
            ('is_media', False),
            ('is_source', False),
            ('is_script', False)
        ]
        assert [(k, v) for k, v in info.items() if k != 'date'] == expected

    def test_get_copyrights_include_copyrights_and_authors(self):
        test_file = self.get_test_loc('api/copyright/iproute.c')
        cops = api.get_copyrights(test_file)
        expected = dict([
            ('copyrights', [
                dict([('copyright', 'Copyright (c) 2010 Patrick McHardy'), ('start_line', 2), ('end_line', 2)])
            ]),
            ('holders', [
                dict([('holder', 'Patrick McHardy'), ('start_line', 2), ('end_line', 2)])
            ]),
            ('authors', [
                dict([('author', 'Patrick McHardy <kaber@trash.net>'), ('start_line', 11), ('end_line', 11)])
            ]),
        ])

        assert cops == expected

    def test_get_emails(self):
        test_file = self.get_test_loc('api/email/3w-xxxx.c')
        results = api.get_emails(test_file)
        expected = dict(emails=[
            dict([(u'email', u'linux@3ware.com'), (u'start_line', 1), (u'end_line', 1)]),
            dict([(u'email', u'acme@conectiva.com.br'), (u'start_line', 3), (u'end_line', 3)]),
            dict([(u'email', u'andre@suse.com'), (u'start_line', 5), (u'end_line', 5)])
        ])
        assert results == expected
        results = api.get_emails(test_file, threshold=0)
        assert results == expected

    def test_get_emails_with_threshold(self):
        test_file = self.get_test_loc('api/email/3w-xxxx.c')
        results = api.get_emails(test_file, threshold=1)
        expected = dict(emails=[
            dict([(u'email', u'linux@3ware.com'), (u'start_line', 1), (u'end_line', 1)]),
        ])
        assert results == expected

    def test_get_urls(self):
        test_file = self.get_test_loc('api/url/IMarkerActionFilter.java')
        results = api.get_urls(test_file)
        expected = dict(urls=[
            dict([(u'url', u'http://www.eclipse.org/legal/epl-v10.html'), (u'start_line', 2), (u'end_line', 2)]),
            dict([(u'url', u'https://github.com/rpm-software-management'), (u'start_line', 4), (u'end_line', 4)]),
            dict([(u'url', u'https://gitlab.com/Conan_Kudo'), (u'start_line', 6), (u'end_line', 6)]),
        ])
        assert results == expected
        results = api.get_urls(test_file, threshold=0)
        assert results == expected

    def test_get_urls_with_threshold(self):
        test_file = self.get_test_loc('api/url/IMarkerActionFilter.java')
        expected = dict(urls=[
            dict([(u'url', u'http://www.eclipse.org/legal/epl-v10.html'), (u'start_line', 2), (u'end_line', 2)])
        ])
        results = api.get_urls(test_file, threshold=1)
        assert results == expected

    def test_get_license_with_expression(self):
        test_file = self.get_test_loc('api/license/apache-1.0.txt')
        results = api.get_licenses(test_file)
        expected = 'apache-1.0 AND (gpl-2.0 WITH linux-syscall-exception-gpl OR linux-openib)'
        assert results['detected_license_expression'] == expected

    def test_get_license_with_expression2(self):
        test_file = self.get_test_loc('api/license/expression.RULE')
        results = api.get_licenses(test_file)
        expected = 'gpl-2.0 WITH linux-syscall-exception-gpl OR linux-openib'
        assert results['detected_license_expression'] == expected

    def test_get_license_returns_correct_lines(self):
        test_file = self.get_test_loc('api/license/correct_lines2')
        results = api.get_licenses(test_file)
        assert results['detected_license_expression'] == 'mit'
        assert results['license_detections'][0]['matches'][0]['start_line'] == 2
        assert results['license_detections'][0]['matches'][0]['end_line'] == 4
