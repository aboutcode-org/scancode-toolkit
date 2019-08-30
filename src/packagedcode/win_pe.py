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

from collections import OrderedDict
from contextlib import closing

from ftfy import fix_text
import pefile
from six import string_types

from commoncode import text
from typecode import contenttype


TRACE = False

def logger_debug(*args):
    pass

if TRACE:
    import logging
    import sys
    logger = logging.getLogger(__name__)
    # logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(
            isinstance(a, string_types) and a or repr(a) for a in args))


"""
Extract data from windows PE DLLs and executable.
Note that the extraction may not be correct for all PE in particular
older legacy PEs. See tests and:
    http://msdn.microsoft.com/en-us/library/aa381058%28v=VS.85%29.aspx
PE stores data in a "VarInfo" structure for "variable information".
VarInfo are by definition variable key/value pairs:
    http://msdn.microsoft.com/en-us/library/ms646995%28v=vs.85%29.aspx

Therefore we use a list of the most common and useful key names with
an eye on origin and license related information and return a value
when there is one present.
"""

# List of common info keys found in PE.
PE_INFO_KEYS = (
    u'APIVersion',
    u'Assembly Version',
    # u'BinType',
    u'BuildDate',
    # u'BuildType',
    # u'BuildVariant',
    u'BuildVersion',
    u'Comments',
    u'Company',
    u'CompanyName',
    # u'Configuration',
    u'FileDescription',
    u'FileVersion',
    u'Full Version',
    u'InternalName',
    u'LegalCopyright',
    u'LegalTrademarks',
    u'LegalTrademarks1',
    u'LegalTrademarks2',
    # u'LibToolFileVersion',
    u'License',
    u'OriginalFilename',
    u'ProductName',
    u'ProductVersion',
    # u'PrivateBuild',
    # u'SharedMemoryVersion',
    # u'SpecialBuild',
    u'WWW',
)

PE_INFO_KEYSET = set(PE_INFO_KEYS)


def pe_info(location, include_extra_data=False):
    """
    Return a mapping of common data available for a Windows dll or exe PE
    (portable executable).
    Return None for non-Windows PE files.
    Return an empty mapping for PE from which we could not collect data.

    If `include_extra_data` is True, also collect extra data found if any,
    returned as a dictionary under the 'extra_data' key in the returned mapping.
    """
    if not location:
        return {}

    T = contenttype.get_type(location)

    if not T.is_winexe:
        return {}

    # FIXME: WTF: we initialize with empty values, as we must always
    # return something for all values
    result = OrderedDict([(k, None,) for k in PE_INFO_KEYS])
    result['extra_data'] = OrderedDict()

    try:
        with closing(pefile.PE(location)) as pe:
            if not hasattr(pe, 'FileInfo'):
                # No fileinfo section: we return just empties
                return result

            # >>> pe.FileInfo: this is a list of list of Structure objects:
            # [[<Structure: [VarFileInfo] >,  <Structure: [StringFileInfo]>]]
            pefi = pe.FileInfo
            if not pefi or not isinstance(pefi, list):
                if TRACE:
                    logger.debug('pe_info: not pefi')
                return result

            # here we have anon-empty list
            pefi = pefi[0]
            if TRACE:
                logger.debug('pe_info: pefi:', pefi)

            sfi = [x for x in pefi
                   if type(x) == pefile.Structure
                   and hasattr(x, 'name')
                   and x.name == 'StringFileInfo']

            if not sfi:
                # No stringfileinfo section: we return just empties
                if TRACE:
                    logger.debug('pe_info: not sfi')
                return result

            sfi = sfi[0]

            if not hasattr(sfi, 'StringTable'):
                # No fileinfo.StringTable section: we return just empties
                if TRACE:
                    logger.debug('pe_info: not StringTable')
                return result

            strtab = sfi.StringTable
            if not strtab or not isinstance(strtab, list):
                return result

            strtab = strtab[0]

            if TRACE:
                logger.debug('pe_info: Entries keys: ' + str(set(k for k in strtab.entries)))
                logger.debug('pe_info: Entry values:')
                for k, v in strtab.entries.items():
                    logger.debug('  ' + str(k) + ': ' + repr(type(v)) + repr(v))

            for k, v in strtab.entries.items():
                # convert unicode to a safe ASCII representation
                key = text.as_unicode(k).strip()
                value = text.as_unicode(v).strip()
                value = fix_text(value)
                if key in PE_INFO_KEYSET:
                    result[key] = value
                else:
                    # collect extra_data if any:
                    result['extra_data'][key] = value

    except Exception as e:
        raise
        if TRACE:
            logger.debug('pe_info: Failed to collect infos: ' + repr(e))
        # FIXME: return empty for now: this is wrong

    # the ordering of extra_data is not guaranteed on Python 2 because the dict is not ordered
    result['extra_data'] = OrderedDict(sorted(result['extra_data'].items()))
    return result
