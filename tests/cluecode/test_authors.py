#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
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
        expected = [
            u'John Doe',
        ]
        check_detection(expected, 'authors/author_addr_c-addr_c.c', what='authors')

    def test_author_avinash(self):
        expected = [
            u'Avinash Kak (kak@purdue.edu)',
            u'Avinash Kak (kak@purdue.edu)',
        ]
        check_detection(expected, 'authors/author_avinash-BitVector_py.py', what='authors')

    def test_author_avinash_kak(self):
        expected = [
            u'Avinash Kak (kak@purdue.edu)',
            u'Avinash Kak (kak@purdue.edu)',
        ]
        check_detection(expected, 'authors/author_avinash_kak-BitVector_py.py', what='authors')

    def test_author_complex_author(self):
        expected = [
            'the University of California, Berkeley and its contributors.',
        ]
        check_detection(expected, 'authors/author_complex_author-strtol_c.c', what='authors')

    def test_author_correct(self):
        expected = []
        check_detection(expected, 'authors/author_correct-detail_9_html.html', what='authors')

    def test_author_do_not_detect_authorize_as_author(self):
        expected = []
        check_detection(expected, 'authors/author_do_not_detect_authorize_as_author.csv', what='authors')

    def test_author_expat(self):
        expected = []
        check_detection(expected, 'authors/author_expat-expat_h.h', what='authors')

    def test_author_gary(self):
        expected = [
            "Gary O'Neall",
        ]
        check_detection(expected, 'authors/author_gary-ProjectInfo_java.java', what='authors')

    def test_author_gthomas_c(self):
        expected = [
            u'gthomas, sorin@netappi.com',
            u'gthomas, sorin@netappi.com, andrew.lunn@ascom.ch',
        ]
        check_detection(expected, 'authors/author_gthomas_c-c.c', what='authors')

    def test_author_in_java(self):
        expected = [
            u'Scott Violet',
        ]
        check_detection(expected, 'authors/author_in_java-MergeSort_java.java', what='authors')

    def test_author_in_java_tag(self):
        expected = [
            u'Apple Banana Car',
        ]
        check_detection(expected, 'authors/author_in_java_tag-java.java', what='authors')

    def test_author_in_postcript(self):
        expected = []
        check_detection(expected, 'authors/author_in_postcript-9__ps.ps', what='authors')

    def test_author_in_visio_doc(self):
        expected = []
        check_detection(expected, 'authors/author_in_visio_doc-Glitch_ERD_vsd.vsd', what='authors')

    def test_author_nathan(self):
        notes = '''name +email is not enough to create an author
            hence this is not detected correctly
            Nathan Mittler <nathan.mittler@gmail.com>'''
        expected = [
        ]
        check_detection(expected, 'authors/author_nathan-KEYS', what='authors', notes=notes)

    def test_author_no_author(self):
        expected = []
        check_detection(expected, 'authors/author_no_author-c.c', what='authors')

    def test_author_none(self):
        expected = []
        check_detection(expected, 'authors/author_none-wrong', what='authors')

    def test_author_none_c(self):
        expected = []
        check_detection(expected, 'authors/author_none_c-c.c', what='authors')

    def test_author_none_fp(self):
        expected = []
        check_detection(expected, 'authors/author_none_fp-false_positives_c.c', what='authors')

    def test_author_none_js(self):
        expected = []
        check_detection(expected, 'authors/author_none_js-editor_beta_de_js.js', what='authors')

    def test_author_none_license(self):
        expected = []
        check_detection(expected, 'authors/author_none_license-LICENSE', what='authors')

    def test_author_none_sample_java(self):
        expected = []
        check_detection(expected, 'authors/author_none_sample_java-java.java', what='authors')

    def test_author_russ_c(self):
        notes = '''these are detected as copyrights, not authors
        Russ Dill <Russ.Dill@asu.edu>
        Vladimir Oleynik <dzo@simtreas.ru>
        '''
        expected = []
        check_detection(expected, 'authors/author_russ_c-c.c', what='authors', notes=notes)

    def test_author_sample(self):
        expected = []
        check_detection(expected, 'authors/author_sample-c.c', what='authors')

    def test_author_samplepy(self):
        expected = []
        check_detection(expected, 'authors/author_samplepy-py.py', what='authors')

    def test_author_snippet(self):
        expected = []
        check_detection(expected, 'authors/author_snippet', what='authors')

    def test_author_stacktrace_cpp(self):
        expected = [
            u'faith@dict.org',
        ]
        check_detection(expected, 'authors/author_stacktrace_cpp-stacktrace_cpp.cpp', what='authors')

    def test_author_treetablemodeladapter_java(self):
        expected = [
            u'Philip Milne', u'Scott Violet',
        ]
        check_detection(expected, 'authors/author_treetablemodeladapter_java-TreeTableModelAdapter_java.java', what='authors')

    def test_author_uc(self):
        expected = [
            u'the University of California, Berkeley and its contributors.',
            u'UC Berkeley and its contributors.',
            u'the University of California, Berkeley and its contributors.',
        ]
        check_detection(expected, 'authors/author_uc-LICENSE', what='authors')

    def test_author_var_route_c(self):
        notes = '''these are detected as copyrights, not authors
            Erik Schoenfelder (schoenfr@ibr.cs.tu-bs.de)
            Simon Leinen (simon@switch.ch)'''
        expected = []
        check_detection(expected, 'authors/author_var_route_c-var_route_c.c', what='authors', notes=notes)

    def test_author_vs(self):
        expected = []
        check_detection(expected, 'authors/author_vs-visual_studio.txt', what='authors')

    def test_author_young_c(self):
        notes = 'a duplicated instance of Tim Hudson (tjh@mincom.oz.au). is not detected'
        expected = [
            u'Eric Young (eay@mincom.oz.au).',
            u'Eric Young (eay@mincom.oz.au)',
            u'Tim Hudson (tjh@mincom.oz.au)',
        ]
        check_detection(expected, 'authors/author_young_c-c.c', what='authors', notes=notes)

    def test_author_young_c2(self):
        expected = [
            u'Copyright (c) 1995-1997 Eric Young (eay@mincom.oz.au)'
        ]
        check_detection(expected, 'authors/author_young_c-c.c')

    def test_author_wcstok_c(self):
        expected = [
            u'Wes Peters <wes@softweyr.com>'
        ]
        check_detection(expected, 'authors/wcstok.c', what='authors')

    def test_author_iproute(self):
        expected = [u'Patrick McHardy <kaber@trash.net>']
        check_detection(expected, 'authors/iproute.c', what='authors')

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
