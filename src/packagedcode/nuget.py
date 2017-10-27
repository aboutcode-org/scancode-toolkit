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

from packagedcode import models
from packagedcode.utils import join_texts
from packagedcode import xmlutils

"""
Handle nuget.org Nuget packages.
"""


class NugetPackage(models.Package):
    metafiles = ('[Content_Types].xml', '*.nuspec',)
    filetypes = ('zip archive', 'microsoft ooxml',)
    mimetypes = ('application/zip', 'application/octet-stream',)
    extensions = ('.nupkg',)

    type = models.StringType(default='Nuget')

    @classmethod
    def recognize(cls, location):
        return parse(location)


nuspec_tags = [
    'id',
    'version',
    'title',
    'authors',
    'owners',
    'licenseUrl',
    'projectUrl',
    'requireLicenseAcceptance',
    'description',
    'summary',
    'releaseNotes',
    'copyright'
]


def parse_nuspec(location):
    """
    Return a dictionary of Nuget metadata from a .nuspec file at location.
    Return None if this is not a parsable nuspec.
    """
    if not location.endswith('.nuspec'):
        return
    return xmlutils.parse(location, _nuget_handler)


def _nuget_handler(xdoc):
    tags = {}
    for tag in nuspec_tags:
        xpath = xmlutils.namespace_unaware('/package/metadata/{}'.format(tag))
        values = xmlutils.find_text(xdoc, xpath)
        if values:
            value = u''.join(values)
            tags[tag] = value and value or None
    return tags


def parse(location):
    """
    Return a Nuget package from a nuspec file at location.
    Return None if this is not a parsable nuspec.
    """
    nuspec = parse_nuspec(location)
    if not nuspec:
        return

    parties = []
    authors = nuspec.get('authors')
    if authors:
        parties.append(models.Party(name=authors, role='author'))

    owners = nuspec.get('owners')
    if owners:
        parties.append(models.Party(name=owners, role='owner'))

    description = join_texts(nuspec.get('title') , nuspec.get('description'))

    package = NugetPackage(
        location=location,
        name=nuspec.get('id'),
        version=nuspec.get('version'),
        description=description or None,
        homepage_url=nuspec.get('projectUrl') or None,
        parties=parties,
        asserted_license=nuspec.get('licenseUrl') or None,
        copyright=nuspec.get('copyright') or None,
    )
    return package
