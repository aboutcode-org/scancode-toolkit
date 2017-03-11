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


import chardet
from lxml import etree

from textcode import analysis


"""
Utility functions for dealing with XML.
"""


def parse(location, handler):
    """
    Given the location of an XML file and a handler function accepting a
    etree document, parse the file at location and invoke the handler on
    the etree doc. If parsing fails while calling handler, another
    approach to parsing is used.

    This is a workaround some lxml bug/weirdness wrt unicode in the 2.3
    version in use.

    The `handler` function must have no side effects and can be called
    again on failures without risk.

    Try first to call lxml from a location then try from a string to
    deal with weird encodings
    """
    try:
        parser = etree.XMLParser(recover=True, remove_blank_text=True, resolve_entities=False)
        xdoc = etree.parse(location, parser)
        return handler(xdoc)
    except:
        parser = etree.XMLParser(recover=True, remove_blank_text=True, resolve_entities=False)
        text = analysis.unicode_text(location)
        xdoc= etree.fromstring(_as_unicode_bytes(text), parser)
        return handler(xdoc)


# FIXME: encoding should be processed/detected elsewhere
def _as_unicode_bytes(text):
    """
    Given a unicode text, return a unicode encoded byte string.
    """
    try:
        return text.encode('utf-8')
    except UnicodeEncodeError:
        encoding = chardet.detect(text[:4096])

    if encoding:
        encoding = encoding.get('encoding')
        return text.encode(encoding)

    else:
        raise


def find_text(xdoc, xpath):
    """
    Return a list of text values from an `xpath` expression found in an
    etree `xdoc`.
    """
    result = xdoc.xpath(xpath)
    # xpath can return a list (nodeset), bool, float or string
    texts = []
    if isinstance(result, list):
        for element in result:
            if element.text:
                texts.append(element.text.strip())
    else:
        # FIXME: this could fail
        texts.append(unicode(result).strip())
    return texts


def namespace_unaware(xpath):
    """
    Return a new namespace-unaware xpath expression accepting any namespace
    given a simple xpath expression using only single slashes.

    This is achieved by wrapping each step of an expression with the local-
    name() XPath function. XPath expressions with namespaced XML can be complex
    and hard to read and write: this helps keep expression simple when
    namespaces do not matter.

    Use with caution: this works only for simple expression using only single /.

    For example:
    >>> simple_xpath = '/project/organization/url'
    >>> expected = "/*[local-name()='project']/*[local-name()='organization']/*[local-name()='url']"
    >>> assert expected == namespace_unaware(simple_xpath)
    """
    # Search * and then a local-name in the returned elements
    ignore_namespace = "*[local-name()='%s']"
    new_steps = []
    # we assume that the input expression is simple using only /
    for step in xpath.split('/'):
        if step:
            new_steps.append(ignore_namespace % step)
        else:
            new_steps.append(step)
    return '/'.join(new_steps)


def strip_namespace(tag_name):
    """
    Strip all namespaces or namespace prefixes if present in an XML tag name .

    For example:
    >>> tag_name = '{http://maven.apache.org/POM/4.0.0}geronimo.osgi.export.pkg'
    >>> expected = 'geronimo.osgi.export.pkg'
    >>> assert expected == strip_namespace(tag_name)
    """
    head, brace, tail = tag_name.rpartition('}')
    return tail if brace else head


def name_value(elem):
    """
    Return the name, value of an etree element `elem` stripping all namespaces
    and prefixes from the tag name.
    """
    name = strip_namespace(elem.tag).strip()

    value = elem.text and elem.text.strip() or ''
    return name, value

