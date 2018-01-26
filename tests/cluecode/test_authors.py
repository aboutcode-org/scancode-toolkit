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

import os.path

from commoncode.testcase import FileBasedTesting
from cluecode_assert_utils import check_detection


class TestAuthors(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_author_addr_c(self):
        test_file = self.get_test_loc('authors/author_addr_c-addr_c.c')
        expected = [
            u'John Doe',
        ]
        check_detection(expected, test_file, what='authors')

    def test_author_avinash(self):
        test_file = self.get_test_loc('authors/author_avinash-BitVector_py.py')
        expected = [
            u'Avinash Kak (kak@purdue.edu)',
            u'Avinash Kak (kak@purdue.edu)',
        ]
        check_detection(expected, test_file, what='authors')

    def test_author_avinash_kak(self):
        test_file = self.get_test_loc('authors/author_avinash_kak-BitVector_py.py')
        expected = [
            u'Avinash Kak (kak@purdue.edu)',
            u'Avinash Kak (kak@purdue.edu)',
        ]
        check_detection(expected, test_file, what='authors')

    def test_author_complex_author(self):
        test_file = self.get_test_loc('authors/author_complex_author-strtol_c.c')
        expected = [
            'the University of California, Berkeley and its contributors.',
        ]
        check_detection(expected, test_file, what='authors')

    def test_author_correct(self):
        test_file = self.get_test_loc('authors/author_correct-detail_9_html.html')
        expected = []
        check_detection(expected, test_file, what='authors')

    def test_author_do_not_detect_authorize_as_author(self):
        test_file = self.get_test_loc('authors/author_do_not_detect_authorize_as_author.csv')
        expected = []
        check_detection(expected, test_file, what='authors')

    def test_author_expat(self):
        test_file = self.get_test_loc('authors/author_expat-expat_h.h')
        expected = []
        check_detection(expected, test_file, what='authors')

    def test_author_gary(self):
        test_file = self.get_test_loc('authors/author_gary-ProjectInfo_java.java')
        expected = [
            "Gary O'Neall",
        ]
        check_detection(expected, test_file, what='authors')

    def test_author_gthomas_c(self):
        test_file = self.get_test_loc('authors/author_gthomas_c-c.c')
        expected = [
            u'gthomas, sorin@netappi.com',
            u'gthomas, sorin@netappi.com, andrew.lunn@ascom.ch',
        ]
        check_detection(expected, test_file, what='authors')

    def test_author_in_java(self):
        test_file = self.get_test_loc('authors/author_in_java-MergeSort_java.java')
        expected = [
            u'Scott Violet',
        ]
        check_detection(expected, test_file, what='authors')

    def test_author_in_java_tag(self):
        test_file = self.get_test_loc('authors/author_in_java_tag-java.java')
        expected = [
            u'Apple Banana Car',
        ]
        check_detection(expected, test_file, what='authors')

    def test_author_in_postcript(self):
        test_file = self.get_test_loc('authors/author_in_postcript-9__ps.ps')
        expected = []
        check_detection(expected, test_file, what='authors')

    def test_author_in_visio_doc(self):
        test_file = self.get_test_loc('authors/author_in_visio_doc-Glitch_ERD_vsd.vsd')
        expected = []
        check_detection(expected, test_file, what='authors')

    def test_author_nathan(self):
        test_file = self.get_test_loc('authors/author_nathan-KEYS')
        # name +email is not enough to create an author
        expected = [
            # 'Nathan Mittler <nathan.mittler@gmail.com>',
        ]
        check_detection(expected, test_file, what='authors')

    def test_author_no_author(self):
        test_file = self.get_test_loc('authors/author_no_author-c.c')
        expected = []
        check_detection(expected, test_file, what='authors')

    def test_author_none(self):
        test_file = self.get_test_loc('authors/author_none-wrong')
        expected = []
        check_detection(expected, test_file, what='authors')

    def test_author_none_c(self):
        test_file = self.get_test_loc('authors/author_none_c-c.c')
        expected = []
        check_detection(expected, test_file, what='authors')

    def test_author_none_fp(self):
        test_file = self.get_test_loc('authors/author_none_fp-false_positives_c.c')
        expected = []
        check_detection(expected, test_file, what='authors')

    def test_author_none_js(self):
        test_file = self.get_test_loc('authors/author_none_js-editor_beta_de_js.js')
        expected = []
        check_detection(expected, test_file, what='authors')

    def test_author_none_license(self):
        test_file = self.get_test_loc('authors/author_none_license-LICENSE')
        expected = []
        check_detection(expected, test_file, what='authors')

    def test_author_none_sample_java(self):
        test_file = self.get_test_loc('authors/author_none_sample_java-java.java')
        expected = []
        check_detection(expected, test_file, what='authors')

    def test_author_russ_c(self):
        test_file = self.get_test_loc('authors/author_russ_c-c.c')
        # these are detected as copyrights, not authors
        # u'Russ Dill <Russ.Dill@asu.edu>',
        # u'Vladimir Oleynik <dzo@simtreas.ru>',
        expected = []
        check_detection(expected, test_file, what='authors')

    def test_author_sample(self):
        test_file = self.get_test_loc('authors/author_sample-c.c')
        expected = []
        check_detection(expected, test_file, what='authors')

    def test_author_samplepy(self):
        test_file = self.get_test_loc('authors/author_samplepy-py.py')
        expected = []
        check_detection(expected, test_file, what='authors')

    def test_author_snippet(self):
        test_file = self.get_test_loc('authors/author_snippet')
        expected = []
        check_detection(expected, test_file, what='authors')

    def test_author_stacktrace_cpp(self):
        test_file = self.get_test_loc('authors/author_stacktrace_cpp-stacktrace_cpp.cpp')
        expected = [
            u'faith@dict.org',
        ]
        check_detection(expected, test_file, what='authors')

    def test_author_treetablemodeladapter_java(self):
        test_file = self.get_test_loc('authors/author_treetablemodeladapter_java-TreeTableModelAdapter_java.java')
        expected = [
            u'Philip Milne', u'Scott Violet',
        ]
        check_detection(expected, test_file, what='authors')

    def test_author_uc(self):
        test_file = self.get_test_loc('authors/author_uc-LICENSE')
        expected = [
            u'the University of California, Berkeley and its contributors.',
            u'UC Berkeley and its contributors.',
            u'the University of California, Berkeley and its contributors.',
        ]
        check_detection(expected, test_file, what='authors')

    def test_author_var_route_c(self):
        test_file = self.get_test_loc('authors/author_var_route_c-var_route_c.c')
        # these are detected as copyrights, not authors
        # u'Erik Schoenfelder (schoenfr@ibr.cs.tu-bs.de)',
        # u'Simon Leinen (simon@switch.ch)',
        expected = []
        check_detection(expected, test_file, what='authors')

    def test_author_vs(self):
        test_file = self.get_test_loc('authors/author_vs-visual_studio.txt')
        expected = []
        check_detection(expected, test_file, what='authors')

    def test_author_young_c(self):
        test_file = self.get_test_loc('authors/author_young_c-c.c')
        expected = [
            u'Eric Young (eay@mincom.oz.au).',
#            u'Tim Hudson (tjh@mincom.oz.au).',
            u'Eric Young (eay@mincom.oz.au)',
            u'Tim Hudson (tjh@mincom.oz.au)',
        ]
        check_detection(expected, test_file, what='authors')

        expected = [
            u'Copyright (c) 1995-1997 Eric Young (eay@mincom.oz.au)'
        ]
        check_detection(expected, test_file, what='copyrights')

    def test_author_wcstok_c(self):
        test_file = self.get_test_loc('authors/wcstok.c')
        expected = [u'Wes Peters <wes@softweyr.com>']
        check_detection(expected, test_file, what='authors')

    def test_author_iproute(self):
        test_file = self.get_test_loc('authors/iproute.c')
        expected = [u'Patrick McHardy <kaber@trash.net>']
        check_detection(expected, test_file, what='authors')

    def test_author_with_cvs_keywords(self):
        test_lines = '''
            Author|Date|Header|Id|Name|Locker|Log|RCSfile|Revision|Source|State
        '''.splitlines(False)
        expected = [
        ]
        check_detection(expected, test_lines, what='authors')

    def test_author_with_trailing_date(self):
        test_lines = '''
         As of:   commit 006b89d4464ae1bb6d545ea5716998654124df45   Author: Nikos Mavrogiannopoulos <nmav@redhat.com>   Date:   Fri Apr 1 10:46:12 2016 +0200     priorities:

       * : commit 3debe362faa62e5b381b880e3ba23aee07c85f6e Author:
        Alexander Kanavin <alex.kanavin@gmail.com> Date:   Wed Dec 14
        17:42:45 2016 +0200

        '''.splitlines(False)
        expected = [
            u'Nikos Mavrogiannopoulos <nmav@redhat.com>',
            u'Alexander Kanavin <alex.kanavin@gmail.com>',
        ]
        check_detection(expected, test_lines, what='authors')

