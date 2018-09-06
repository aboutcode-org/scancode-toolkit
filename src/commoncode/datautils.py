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
import typing


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
LABEL_METADATA = '__field_label'


def attribute(default=attr.NOTHING, validator=None,
              repr=False, cmp=True,  # NOQA
              init=True, type=None, converter=None,  # NOQA
              help=None, label=None, metadata=None,):  # NOQA
    """
    A generic attribute with help metadata and that is not included in the
    representation by default.
    """
    metadata = metadata or dict()
    if help:
        metadata[HELP_METADATA] = help

    if label:
        metadata[LABEL_METADATA] = label

    return attr.attrib(
        default=default, validator=validator, repr=repr, cmp=cmp, init=init,
        metadata=metadata, type=type, converter=converter
    )


def Boolean(default=False, validator=None, repr=False, cmp=True,  # NOQA
            converter=None, label=None, help=None,):  # NOQA
    """
    A boolean attribute.
    """
    return attribute(
        default=default,
        validator=validator,
        repr=repr,
        cmp=cmp,
        init=True,
        type=bool,
        converter=converter,
        help=help,
        label=label,
    )


def String(default=None, validator=None, repr=False, cmp=True,  # NOQA
           converter=None, label=None, help=None,):  # NOQA
    """
    A string attribute.
    """
    return attribute(
        default=default,
        validator=validator,
        repr=repr, cmp=cmp,
        init=True,
        type=str,
        converter=converter,
        help=help,
        label=label,
    )


def Integer(default=0, validator=None, repr=False, cmp=True,  # NOQA
            converter=None, label=None, help=None,):  # NOQA
    """
    An integer attribute.
    """
    converter = converter or attr.converters.optional(int)
    return attribute(
        default=default,
        validator=validator,
        repr=repr,
        cmp=cmp,
        init=True,
        type=int,
        converter=converter,
        help=help,
        label=label,
    )


def Float(default=0.0, validator=None, repr=False, cmp=True,  # NOQA
          converter=None, label=None, help=None,):  # NOQA
    """
    A float attribute.
    """
    return attribute(
        default=default,
        validator=validator,
        repr=repr,
        cmp=cmp,
        init=True,
        type=float,
        converter=converter,
        help=help,
        label=label,
    )


def List(item_type=typing.Any, default=attr.NOTHING, validator=None, repr=False, cmp=True,  # NOQA
         converter=None, label=None, help=None,):  # NOQA
    """
    A list attribute: the optional item_type defines the type of items it stores.
    """
    if default is attr.NOTHING:
        default = attr.Factory(list)

    return attribute(
        default=default,
        validator=validator,
        repr=repr,
        cmp=cmp,
        init=True,
        type=typing.List[item_type],
        converter=converter,
        help=help,
        label=label,
    )


def Mapping(value_type=typing.Any, default=attr.NOTHING, validator=None, repr=False, cmp=True,  # NOQA
            converter=None, help=None, label=None):  # NOQA
    """
    A mapping attribute: the optional value_type defines the type of values it
    stores. The key is always a string.

    Notes: in Python 2 the type is Dict as there is no typing available for
    OrderedDict for now.
    """
    if default is attr.NOTHING:
        default = attr.Factory(OrderedDict)

    return attribute(
        default=default,
        validator=validator,
        repr=repr,
        cmp=cmp,
        init=True,
        type=typing.Dict[str, value_type],
        converter=converter,
        help=help,
        label=label,
    )


##################################################
# FIXME: add proper support for dates!!!
##################################################

def Date(default=None, validator=None, repr=False, cmp=True,  # NOQA
           converter=None, label=None, help=None,):  # NOQA
    """
    A date attribute. It always serializes to an ISO date string.
    Behavior is TBD and for now this is exactly a string.
    """
    return String(default, validator, repr, cmp, converter, label, help)
