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
from __future__ import unicode_literals

from collections import OrderedDict

import attr

"""
Utilities and helpers for data classes.
"""

# Python 2 and 3 support
try:
    # Python 2
    unicode
    str_orig = str
    bytes = str  # NOQA
    str = unicode  # NOQA
except NameError:
    # Python 3
    unicode = str  # NOQA

HELP_METADATA = '__field_help'


def attribute(default=attr.NOTHING, validator=None, repr=False, cmp=True,  # NOQA
              init=True, metadata=None, type=None, converter=None, help=None):  # NOQA
    """
    A generic attribute with help metadata and that is not included in the
    representation by default.
    """
    metadata = metadata or dict()
    if help:
        metadata[HELP_METADATA] = help

    return attr.attrib(
        default=default, validator=validator, repr=repr, cmp=cmp, init=init,
        metadata=metadata, type=type, converter=converter
    )


def Boolean(default=False, validator=None, repr=False, cmp=True,  # NOQA
            init=True, metadata=None, converter=None, help=None):  # NOQA
    """
    A boolean attribute.
    """
    return attribute(
        default=default, validator=validator, repr=repr, cmp=cmp, init=init,
        metadata=metadata, type=bool, converter=converter, help=help
    )


def String(default='', validator=None, repr=False, cmp=True,  # NOQA
           init=True, metadata=None, converter=None, help=None):  # NOQA
    """
    A string attribute.
    """
    return attribute(
        default=default, validator=validator, repr=repr, cmp=cmp, init=init,
        metadata=metadata, type=str, converter=converter, help=help
    )


def Int(default=0, validator=None, repr=False, cmp=True,  # NOQA
        init=True, metadata=None, converter=None, help=None):  # NOQA
    """
    An integer attribute.
    """
    return attribute(
        default=default, validator=validator, repr=repr, cmp=cmp, init=init,
        metadata=metadata, type=int, converter=converter, help=help
    )


def Float(default=0.0, validator=None, repr=False, cmp=True,  # NOQA
          init=True, metadata=None, converter=None, help=None):  # NOQA
    """
    A float attribute.
    """
    return attribute(
        default=default, validator=validator, repr=repr, cmp=cmp, init=init,
        metadata=metadata, type=float, converter=converter, help=help
    )


def List(validator=None, repr=False, cmp=True,  # NOQA
         init=True, metadata=None, converter=None, help=None):  # NOQA
    """
    A list attribute.
    """
    return attribute(
        default=attr.Factory(list), validator=validator, repr=repr, cmp=cmp,
        init=init, metadata=metadata, type=list, converter=converter, help=help
    )


def Mapping(validator=None, repr=False, cmp=True,  # NOQA
            init=True, metadata=None, converter=None, help=None):  # NOQA
    """
    A mapping attribute.
    """
    return attribute(
        default=attr.Factory(OrderedDict), validator=validator, repr=repr,
        cmp=cmp, init=init, metadata=metadata, type=OrderedDict,
        converter=converter, help=help
    )
