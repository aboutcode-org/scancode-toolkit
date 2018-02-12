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

import os

from commoncode.testcase import FileBasedTesting
from textcode import pdf



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

        assert expected == result

    def test_pdfminer_cant_parse_faulty_broadcom_doc(self):
        # test for https://github.com/euske/pdfminer/issues/118
        test_file = self.get_test_loc('pdf/pdfminer_bug_118/faulty.pdf')
        from pdfminer.pdfparser import PDFParser
        from pdfminer.pdfdocument import PDFDocument
        with open(test_file, 'rb') as inputfile:
            parser = PDFParser(inputfile)
            PDFDocument(parser)

    def test_get_text_lines_skip_parse_faulty_broadcom_doc(self):
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
        assert expected == result

    def test_pdfminer_cant_parse_apache_fop_test_pdf(self):
        test_file = self.get_test_loc('pdf/fop_test_pdf_1.5_test.pdf')
        from pdfminer.pdfparser import PDFParser
        from pdfminer.pdfdocument import PDFDocument
        with open(test_file, 'rb') as inputfile:
            parser = PDFParser(inputfile)
            PDFDocument(parser)

        result = pdf.get_text_lines(test_file)
        expected = apache_fop_expected
        assert expected == result


apache_fop_expected = [
    b'This is the page header\n',
    b'(There\xe2\x80\x99s another page se-\n',
    b'quence below.)\n',
    b'\n',
    b'About Apache FOP\n',
    b'It  is  a  print  formatter  driv-\n',
    b'en  by  XSL  formatting  ob-\n',
    b'jects (XSL-FO) and an out-\n',
    b'put \n',
    b'format-\n',
    b'\n',
    b'independent \n',
    b'\n',
    b'Page 1\n',
    b'ter1. FOP has a nice logo:\n',
    b'\n',
    b'Header 1.1 Header 1.2\n',
    b'Cell 1.1\n',
    b'\n',
    b'Cell 1.2\n',
    b'\n',
    b'See the FOP website for more information\n',
    b'\n',
    b'\x0cThis is the page header\n',
    b'\n',
    b'Header 1.1 Header 1.2\n',
    b'Cell 2.1\n',
    b'\n',
    b'Cell 2.2\n',
    b'\n',
    b'Page 2\n',
    b'(XSL-FO) and an output in-\n',
    b'dependent formatter. It is a\n',
    b'Java application that reads\n',
    b'a  formatting  object  (FO)\n',
    b'tree  and  renders  the  res-\n',
    b'ulting pages to a specified\n',
    b'output.\n',
    b'\n',
    b'Apache  FOP  (Formatting\n',
    b'Objects  Processor)  is  a\n',
    b'print  formatter  driven  by\n',
    b'XSL \n',
    b'formatting  objects\n',
    b'This fo:block element spans all the columns of the docu-\n',
    b'ment. This is intended to test the abilities of the text-to-\n',
    b'speech program.\n',
    b'And  now  we  are  back  to\n',
    b'normal  content  flowing  in\n',
    b'\n',
    b'\x0cPage 3\n',
    b'\n',
    b'This is the page header\n',
    b'two  columns.  Let\xe2\x80\x99s  start  a\n',
    b'numbered list:\n',
    b'1. Line 1 of item 1\n',
    b'Line 2 of item 1\n',
    b'Line 3 of item 1\n',
    b'2. Line 1 of item 2\n',
    b'Line 2 of item 2\n',
    b'Line 3 of item 2\n',
    b'\n',
    b'And  now  we  are  going  to\n',
    b'see  how  a  second  page\n',
    b'sequence is handled.\n',
    b'\n',
    b'\x0cThis is the page header\n',
    b'Apache  FOP  (Formatting\n',
    b'Objects  Processor)  is  a\n',
    b'print  formatter  driven  by\n',
    b'XSL \n',
    b'formatting  objects\n',
    b'(XSL-FO)  and  an  output\n',
    b'independent  formatter1.  It\n',
    b'is  a  Java  application  that\n',
    b'reads  a  formatting  object\n',
    b'(FO) tree and renders the\n',
    b'\n',
    b'See the FOP website for more information\n',
    b'\n',
    b'Page 4\n',
    b'resulting  pages  to  a  spe-\n',
    b'cified output.\n',
    b'\n',
    b'Header 1.1 Header 1.2\n',
    b'Cell 1.1\n',
    b'Cell 2.1\n',
    b'\n',
    b'Cell 1.2\n',
    b'Cell 2.2\n',
    b'\n',
    b'Apache  FOP  (Formatting\n',
    b'Objects  Processor)  est\n',
    b'une application de mise en\n',
    b'page  de  documents  res-\n',
    b'pectant  le  standard  XSL-\n',
    b'\n',
    b'\x0cThis is the page header\n',
    b'Page 5\n',
    b'FO. \xc3\x80 partir d\xe2\x80\x99un document\n',
    b'va  effectue  une  mise  en\n',
    b'au  format  XSL-FO,  cette\n',
    b'page  et  renvoie  un  docu-\n',
    b'application  \xc3\xa9crite  en  Ja-\n',
    b'ment pr\xc3\xaat pour impression.\n',
    b'This fo:block element spans all the columns of the docu-\n',
    b'ment. This is intended to test the abilities of the text-to-\n',
    b'speech program.\n',
    b'And  now  we  are  back  to\n',
    b'normal  content  flowing  in\n',
    b'two  columns.  Let\xe2\x80\x99s  start  a\n',
    b'numbered list:\n',
    b'1. Line 1 of item 1\n',
    b'Line 2 of item 1\n',
    b'\n',
    b'Line 3 of item 1\n',
    b'2. Line 1 of item 2\n',
    b'Line 2 of item 2\n',
    b'Line 3 of item 2\n',
    b'\n',
    b'The  end  of  the  document\n',
    b'has now been reached.\n',
    b'\n',
    b'\x0c'
]
