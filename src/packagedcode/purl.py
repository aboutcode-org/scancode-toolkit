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

from collections import namedtuple
from urllib import quote
from urlparse import unquote


# Python 2 and 3 support
try:
    # Python 2
    unicode
    str = unicode
    basestring = basestring
except NameError:
    # Python 3
    unicode = str
    basestring = (bytes, str,)


"""
A purl (aka. Package URL) implementation as specified at:
https://github.com/package-url/purl-spec
"""


class PackageURL(namedtuple('PackageURL',
    ['type', 'namespace', 'name', 'version', 'qualifiers', 'subpath'])):
    """
    A purl is a package URL as defined at
    https://github.com/package-url/purl-spec.
    """
    def __new__(self, type=None, namespace=None, name=None,
                version=None, qualifiers=None, subpath=None):

        for key, value in (
            ('type', type),
            ('namespace', namespace),
            ('name', name),
            ('version', version),
            ('qualifiers', qualifiers),
            ('subpath', subpath)):

            if key == 'qualifiers':
                if qualifiers and not isinstance(qualifiers, dict):
                    raise ValueError(
                        "Invalid purl: 'qualifiers' "
                        "must be a mapping: {}".format(repr(qualifiers)))
                continue

            if value and not isinstance(value, basestring):
                raise ValueError(
                    'Invalid purl: '
                    '{} must be a string: {}'.format(repr(name), repr(value)))

            if key == 'name' and not name:
                raise ValueError("Invalid purl: a 'name' is required.")

        return super(PackageURL, self).__new__(PackageURL,
            type or None, namespace or None, name,
            version or None, qualifiers or None, subpath or None)

    def __str__(self, *args, **kwargs):
        return self.to_string()

    def to_string(self):
        """
        Return a purl string.
        """
        purl = []
        if self.type:
            purl.append(self.type.strip().lower())
            purl.append(':')

        if self.namespace:
            namespace = self.namespace.strip().strip('/')
            if self.type and type in ('bitbucket', 'github',):
                namespace = namespace.lower()
            segments = namespace.split('/')
            segments = [
                seg for seg in segments if seg and seg.strip()]
            if segments:
                subpaths = map(quote, segments)
                purl.append('/'.join(segments))
                purl.append('/')

        name = self.name.strip().strip('/')
        if self.type and type in ('bitbucket', 'github', 'pypi',):
            name = name.lower()
        if self.type and type in ('pypi',):
            name = name.replace('_', '-')
        name = quote(name)
        purl.append(name)

        if self.version:
            purl.append('@')
            purl.append(quote(self.version.strip()))

        if self.qualifiers:
            quals = {
                k.strip().lower(): quote(v)
                for k, v in self.qualifiers.items()
                if k and k.strip() and v and v.strip()
            }
            quals = sorted(quals.items())
            quals = ['{}={}'.format(k, v) for k, v in quals]
            quals = '&'.join(quals)
            if quals:
                purl.append('?')
                purl.append(quals)

        if self.subpath:
            purl.append('#')
            subpaths = self.subpath.split('/')
            subpaths = [
                sp for sp in subpaths
                if sp and sp.strip() and sp not in ('.', '..')
            ]
            if subpaths:
                subpaths = map(quote, subpaths)
                purl.append('/'.join(subpaths))
        return ''.join(purl)

    @classmethod
    def from_string(cls, purl, require_type=True, require_namespace=True,
                    require_version=True):
        """
        Return a PackageURL object parsed from a string.
        Raise ValueError on errors.
        Optionally raise ValuError for empty parts based on require_* flags.
        - `name` is always a required part.
        - `qualifiers` and `subpath` are always optional parts.
        """
        if (not purl or not isinstance(purl, basestring)
            or not purl.strip()):
            raise ValueError('A purl string is required as argument.')

        purl = purl.strip().strip('/')

        head, _sep, subpath = purl.rpartition('#')
        if subpath:
            subpaths = subpath.split('/')
            subpaths = [
                sp for sp in subpaths
                if sp and sp.strip() and sp not in ('.', '..')
            ]
            if subpaths:
                subpaths = map(unquote, subpaths)
                subpath = '/'.join(subpaths)
        subpath = subpath or None

        head, _sep, qualifiers = head.rpartition('?')
        if qualifiers:
            qualifiers = qualifiers.split('&')
            qualifiers = [kv.partition('=') for kv in qualifiers]
            qualifiers = {
                k.strip().lower(): unquote(v)
                for k, _, v in qualifiers
                if k and k.strip() and v and v.strip()
            }
        qualifiers = qualifiers or None

        head, _sep, version = head.rpartition('@')
        if version and version.strip():
            version = unquote(version).strip()
        version = version or None
        if require_version and not version:
            raise ValueError(
                'purl is missing the required '
                'version part: {}'.format(repr(purl)))

        type, _sep, ns_name = head.rpartition(':')
        if type:
            type = type.strip().lower()
        type = type or None
        if require_type and not type:
            raise ValueError(
                'purl is missing the required '
                'type part: {}'.format(repr(purl)))

        ns_name = ns_name.strip().strip('/')
        ns_name = ns_name.split('/')
        ns_name = [unquote(seg).strip() for seg in ns_name
                   if seg and seg.strip()]
        namespace = ''
        if len(ns_name) > 1:
            name = ns_name[-1]
            ns = ns_name[0:-1]
            namespace = '/'.join(ns)
        elif len(ns_name) == 1:
            name = ns_name[0]

        namespace = namespace or None

        if require_namespace and not namespace:
            raise ValueError(
                'purl is missing the required '
                'namespace part: {}'.format(repr(purl)))

        if not name:
            raise ValueError(
                'purl is missing the required '
                'name part: {}'.format(repr(purl)))

        return PackageURL(type, namespace, name, version, qualifiers, subpath)
