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

from __future__ import print_function, absolute_import

import os
import logging

from zipfile import ZipFile
from extractcode import ExtractError
from extractcode import ExtractErrorPasswordProtected

logger = logging.getLogger('extractcode')
# logging.basicConfig(level=logging.DEBUG)


"""
Low level support for tar-based archive extraction using Python built-in tar
support.
"""

def list_entries(location):
    raise NotImplementedError()



def extract(location, target_dir):
    with ZipFile(location) as zipped:
        try:
            for zinfo in zipped.infolist():
                newfilename = zinfo.filename
                d = os.path.join(target_dir, os.path.dirname(newfilename))
                if not os.path.exists(d):
                    os.makedirs(d)
                if os.path.basename(newfilename) != '':
                    with open(os.path.join(d, os.path.basename(newfilename)), 'wb') as f:
                        f.write(zipped.read(zinfo.filename))
        except Exception, e:
            if str(e).find('Bad CRC-32') != -1:
                raise ExtractErrorPasswordProtected(file + ' needs password to unzip,the details of the exception is:' + str(e))
            else:
                raise ExtractError(str(e))
