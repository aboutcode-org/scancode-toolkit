#
# Copyright (c) 2015 nexB Inc. and others. All rights reserved.
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

from __future__ import absolute_import, print_function


from commoncode.testcase import FileBasedTesting

from textcode import pdf
import os

class TestPdf(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_get_text_lines(self):
        test_file = self.get_test_loc('pdf/pdf.pdf')
        result = pdf.get_text_lines(test_file)
        expected = u'''pdf

"""
Extracts text from a pdf file.
"""
import contextlib
from StringIO import StringIO

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter

def get_text(location):
    rs_mgr = PDFResourceManager()
    extracted_text = StringIO()
    with contextlib.closing(TextConverter(rs_mgr, extracted_text)) as extractor:
        with open(location, \'rb\') as pdf_file:
            interpreter = PDFPageInterpreter(rs_mgr, extractor)
            pages = PDFPage.get_pages(pdf_file, check_extractable=True)
            for page in pages:
                interpreter.process_page(page)
    return extracted_text

Page 1

\x0c'''.splitlines(True)

        assert expected == result

    def test_pdfminer_cant_parse_faulty_broadcom_doc(self):
        # test for https://github.com/euske/pdfminer/issues/118
        test_file = self.get_test_loc('pdf/pdfminer_bug_118/faulty.pdf')
        from pdfminer.pdfparser import PDFParser
        from pdfminer.pdfdocument import PDFDocument
        from pdfminer.pdfdocument import PDFEncryptionError
        with open(test_file, 'rb') as inputfile:
            parser = PDFParser(inputfile)
            try:
                PDFDocument(parser)
            except PDFEncryptionError:
                # this should not fail of course, and will when upstream is fixed
                pass

    def test_get_text_lines_skip_parse_faulty_broadcom_doc(self):
        test_file = self.get_test_loc('pdf/pdfminer_bug_118/faulty.pdf')
        try:
            pdf.get_text_lines(test_file)
            self.fail('Exception should be thrown on faulty PDF')
        except:
            pass
