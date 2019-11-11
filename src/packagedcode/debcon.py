
# Copyright (c) nexB Inc. and others. All rights reserved.
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
import email
import io

from packagedcode import desig

"""
Utilities to parse Debian-style control files aka. deb822 format.
See https://salsa.debian.org/dpkg-team/dpkg/blob/0c9dc4493715ff3b37262528055943c52fdfb99c/man/deb822.man
"""


def get_paragraphs(location):
    """
    Yield paragraphs from a Debian control file at `location`.
    Each paragraph is a list of (name, value) tuples.
    """
    with io.open(location, encoding='utf-8') as df:
        paragraphs = [p for p in df.read().split('\n\n') if p]

    for para in paragraphs:
        parsed = get_paragraph(para)
        if parsed:
            yield parsed


def get_paragraph(text, remove_pgp_signature=False):
    """
    Return a parsed paragraph from `text` as a list of (name, value) tuples.
    Optionally remove a wrapping PGP signature if `remove_pgp_signature` is True.
    """
    if not text:
        return []
    if remove_pgp_signature:
        text = desig.unsign(text)
    mls = email.message_from_string(text)
    #assert not mls.get_payload()
    return list(mls.items())


def to_dict(paragraph, duplicates_as_list=False, lower=True):
    """
    Return an ordered mapping built from a Debian `paragraph` list of name/value
    pairs.

    If `duplicates_as_list` is True, the values of a field name that occurs
    multiple times are converted to a list. Otherwise, raise an Exception when a
    field appears more than once in a paragraph.

    If `lower` is True, field names are normalized to lower-case. Note that
    Debian 822 field names are case-insensitive.
    """
    mapping = OrderedDict()
    for name, value in paragraph:
        lowered = name.lower()
        if lower:
            name = lowered
        name = name.strip()
        value = value.strip()
        name_exists = name in mapping
        if name_exists:
            if duplicates_as_list:
                existing_value = mapping(name)
                if not isinstance(existing_value, (list, tuple)):
                    existing_value = [existing_value, value]
                else:
                    existing_value.append(value)
            else:
                raise Exception('Invalid duplicate name: {}, with value: {}'.format(name, value,))
        else:
            mapping[name] = value
    return mapping


def fold(value):
    """
    Return a folded `value` string.
    """
    if not value:
        return value
    return ''.join(value.split())


def line_separated(value):
    """
    Return a list of values from a `value` string using line delimiters.
    """
    if not value:
        return []
    return [v.strip() for v in value.splitlines(False) if v]
