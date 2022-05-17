#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

import pytest

from commoncode.testcase import FileBasedTesting
from textcode import pdf
from textcode.analysis import numbered_text_lines


class TestPdf(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_get_text_lines(self):
        test_file = self.get_test_loc('pdf/pdf.pdf')
        result = pdf.get_text_lines(test_file)
        expected = b'''pdf

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

        assert result == expected

    def test_pdfminer_can_parse_faulty_broadcom_doc(self):
        # test for https://github.com/euske/pdfminer/issues/118
        test_file = self.get_test_loc('pdf/pdfminer_bug_118/faulty.pdf')
        from pdfminer.pdfparser import PDFParser
        from pdfminer.pdfdocument import PDFDocument
        with open(test_file, 'rb') as inputfile:
            parser = PDFParser(inputfile)
            PDFDocument(parser)

    def test_get_text_lines_can_parse_faulty_broadcom_doc(self):
        test_file = self.get_test_loc('pdf/pdfminer_bug_118/faulty.pdf')
        result = list(pdf.get_text_lines(test_file))
        expected = [
            b'Programmer\xe2\x80\x99s Guide\n',
            b'BCM5756M\n', b'\n',
            b'Host Programmer Interface Specification for the \n',
            b'NetXtreme\xc2\xae and NetLink\xe2\x84\xa2 Family of Highly \n',
            b'Integrated Media Access Controllers\n',
            b'\n',
            b'5300 California Avenue  \xe2\x80\xa2  Irvine, CA 92617  (cid:129)  Phone: 949-926-5000  (cid:129)  Fax: 949-926-5203\n',
            b'\n',
            b'5756M-PG101-R\n',
            b'\n',
            b'10/15/07\n',
            b'\n',
            b'\x0c']
        assert result == expected

    def test_pdfminer_can_parse_apache_fop_test_pdf(self):
        test_file = self.get_test_loc('pdf/fop_test_pdf_1.5_test.pdf')
        result = pdf.get_text_lines(test_file)
        for expected in apache_fop_expected:
            assert expected in result

    @pytest.mark.xfail(reason='Latest pdfminer.six from 2022 has a regression')
    def test_numbered_text_lines_does_not_fail_on_autocad_test_pdf(self):
        test_file = self.get_test_loc('pdf/AutoCad_Diagram.pdf')
        result = list(numbered_text_lines(test_file))
        assert result == []


apache_fop_expected = [
    b'This is the page header\n',
    b'About Apache FOP\n',
    b'It  is  a  print  formatter  driv-\n',
    b'en  by  XSL  formatting  ob-\n',
    b'jects (XSL-FO) and an out-\n',
    b'(XSL-FO) and an output in-\n',
    b'dependent formatter. It is a\n',
    b'Java application that reads\n',
    b'Line 2 of item 1\n',
    b'Apache  FOP  (Formatting\n',
    b'Objects  Processor)  est\n',
    b'une application de mise en\n',
    b'The  end  of  the  document\n',
    b'has now been reached.\n',
]
