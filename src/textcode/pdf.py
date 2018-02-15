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
from __future__ import unicode_literals

import contextlib
from io import BytesIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfdocument import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser


def get_text_lines(location, max_pages=5):
    """
    Return a list of unicode text lines extracted from a pdf file at
    `location`. May raise exceptions. Extract up to `max_pages` pages.
    """
    extracted_text = BytesIO()
    laparams = LAParams()
    with open(location, 'rb') as pdf_file:
        with contextlib.closing(PDFParser(pdf_file)) as parser:
            document = PDFDocument(parser)
            if not document.is_extractable:
                raise PDFTextExtractionNotAllowed(
                    'Encrypted PDF document: text extraction is not allowed')

            manager = PDFResourceManager()
            with contextlib.closing(
                TextConverter(manager, extracted_text, laparams=laparams)) as extractor:
                interpreter = PDFPageInterpreter(manager, extractor)
                pages = PDFPage.create_pages(document)
                for page_num, page in enumerate(pages, 1):
                    interpreter.process_page(page)
                    if max_pages and page_num == max_pages:
                        break
                extracted_text.seek(0)
                return extracted_text.readlines()
