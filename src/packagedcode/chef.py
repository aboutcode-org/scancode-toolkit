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
import io
import json
import logging

import attr
from packageurl import PackageURL
from pygments import highlight
from pygments.formatter import Formatter
from pygments.lexers import RubyLexer
from pygments.token import Token

from commoncode import filetype
from commoncode import fileutils
from packagedcode import models


"""
Handle Chef cookbooks
"""


TRACE = False

logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


@attr.s()
class ChefPackage(models.Package):
    metafiles = ('metadata.json', 'metadata.rb')
    filetypes = ('.tgz',)
    mimetypes = ('application/x-tar',)
    default_type = 'chef'
    default_primary_language = 'Ruby'
    default_web_baseurl = 'https://supermarket.chef.io/cookbooks'
    default_download_baseurl = 'https://supermarket.chef.io/cookbooks'
    default_api_baseurl = 'https://supermarket.chef.io/api/v1'

    @classmethod
    def recognize(cls, location):
        return parse(location)

    @classmethod
    def get_package_root(cls, manifest_resource, codebase):
        return manifest_resource.parent(codebase)

    def repository_download_url(self, baseurl=default_download_baseurl):
        return chef_download_url(self.name, self.version, registry=baseurl)

    def api_data_url(self, baseurl=default_api_baseurl):
        return chef_api_url(self.name, self.version, registry=baseurl)

    def compute_normalized_license(self):
        return models.compute_normalized_license(self.declared_license)


def chef_download_url(name, version, registry='https://supermarket.chef.io/cookbooks'):
    """
    Return an Chef cookbook download url given a name, version, and base registry URL.

    For example:
    >>> chef_download_url('seven_zip', '1.0.4')
    u'https://supermarket.chef.io/cookbooks/seven_zip/versions/1.0.4/download'
    """
    registry = registry.rstrip('/')
    return '{registry}/{name}/versions/{version}/download'.format(**locals())


def chef_api_url(name, version, registry='https://supermarket.chef.io/api/v1'):
    """
    Return a package API data URL given a name, version and a base registry URL.

    For example:
    >>> chef_api_url('seven_zip', '1.0.4')
    u'https://supermarket.chef.io/api/v1/cookbooks/seven_zip/versions/1.0.4'
    """
    registry = registry.rstrip('/')
    return '{registry}/cookbooks/{name}/versions/{version}'.format(**locals())


def is_metadata_json(location):
    return (filetype.is_file(location)
            and fileutils.file_name(location).lower() == 'metadata.json')


def is_metadata_rb(location):
    return (filetype.is_file(location)
            and fileutils.file_name(location).lower() == 'metadata.rb')


def ChefMetadataFormatter(Formatter):
    def format(self, tokens, outfile):
        """
        Parse lines from a `metadata.rb` file.

        For example, a field in `metadata.rb` can look like this:

        name               "python"

        `RubyLexer()` interprets the line as so:

        ['Token.Name.Builtin', "u'name'"],
        ['Token.Text', "u'              '"],
        ['Token.Literal.String.Double', 'u\'"\''],
        ['Token.Literal.String.Double', "u'python'"],
        ['Token.Literal.String.Double', 'u\'"\''],
        ['Token.Text', "u'\\n'"]

        With this pattern of tokens, we iterate through the token stream to
        create a dictionary whose keys are the variable names from `metadata.rb`
        and its values are those variable's values.
        """
        metadata = {}
        line = []
        for ttype, value in tokens:
            if ttype in (Token.Name, Token.Name.Builtin, Token.Punctuation, Token.Literal.String.Double,)
                    and value not in ('\"', '\'',):
                line.append(value)
            if ttype in (Token.Text,) and value.endswith('\n'):
                # The field name should be the first element in the list
                key = line.pop(0)
                if key == 'depends':
                    depends = metadata.get(key)
                    if not depends:
                        metadata[key] = [''.join(line)]
                    else:
                        metadata[key].append(''.join(line))
                else:
                    metadata[key] = ''.join(line)
                line = []
        json.dump(metadata, outfile)


def parse(location):
    """
    Return a Package object from a metadata.json file or None.
    """
    if is_metadata_json(location):
        with io.open(location, encoding='utf-8') as loc:
            package_data = json.load(loc, object_pairs_hook=OrderedDict)
        return build_package_from_json(package_data)

    if is_metadata_rb(location):
        with io.open(location, encoding='utf-8') as loc:
            file_contents = loc.read()
        formatted_file_contents = highlight(file_contents, RubyLexer(), ChefMetadataFormatter())
        package_data = json.loads(formatted_file_contents)
        return build_package_from_rb(package_data)


def build_package_from_json(package_data):
    """
    Return a Package object from a package_data mapping (from a metadata.json or
    similar) or None.
    """
    name = package_data.get('name')
    version = package_data.get('version')
    if not name or not version:
        # a metadata.json without name and version is not a usable chef package
        # FIXME: raise error?
        return

    maintainer_name = package_data.get('maintainer', '')
    maintainer_email = package_data.get('maintainer_email', '')
    parties = []
    if maintainer_name or maintainer_email:
        parties.append(
            models.Party(
                name=maintainer_name or None,
                role='maintainer',
                email=maintainer_email or None,
            )
        )

    description = package_data.get('description', '')
    if not description:
        description = package_data.get('long_description', '')

    license = package_data.get('license', '')
    code_view_url = package_data.get('source_url', '')
    bug_tracking_url = package_data.get('issues_url', '')

    dependencies = package_data.get('dependencies') or None
    package_dependencies = []
    if dependencies:
        for dependency_name, requirement in dependencies.items():
            if not dependency_name:
                continue
            dep = models.DependentPackage(
                purl=PackageURL(type='chef', name=dependency_name).to_string(),
                scope='dependencies',
                requirement=requirement,
                is_runtime=True,
                is_optional=False,
            )
            package_dependencies.append(dep)

    return ChefPackage(
        name=name,
        version=version,
        parties=parties,
        description= description.strip() or None,
        declared_license=license.strip() or None,
        code_view_url=code_view_url.strip() or None,
        bug_tracking_url=bug_tracking_url.strip() or None,
        download_url=chef_download_url(name, version).strip(),
        dependencies=package_dependencies,
    )


def build_package_from_rb(package_data):
    """
    Return a Package object from a package_data mapping (from a metadata.json or
    similar) or None.
    """
    name = package_data.get('name')
    version = package_data.get('version')
    if not name or not version:
        # a metadata.json without name and version is not a usable chef package
        # FIXME: raise error?
        return

    maintainer_name = package_data.get('maintainer', '')
    maintainer_email = package_data.get('maintainer_email', '')
    parties = []
    if maintainer_name or maintainer_email:
        parties.append(
            models.Party(
                name=maintainer_name or None,
                role='maintainer',
                email=maintainer_email or None,
            )
        )

    description = package_data.get('description', '')
    if not description:
        description = package_data.get('long_description', '')

    license = package_data.get('license', '')
    code_view_url = package_data.get('source_url', '')
    bug_tracking_url = package_data.get('issues_url', '')

    dependencies = package_data.get('depends', [])
    package_dependencies = []
    for dependency in dependencies.items():
        dep_requirement = dependency.rsplit(',')
        if len(deps) == 2:
            dep_name = dep_requirement[0]
            requirement = dep_requirement[1]
        else:
            dep_name = dependency
            requirement = None
        package_dependencies.append(
            models.DependentPackage(
                purl=PackageURL(type='chef', name=dep_name).to_string(),
                scope='dependencies',
                requirement=requirement,
                is_runtime=True,
                is_optional=False,
            )
        )

    return ChefPackage(
        name=name,
        version=version,
        parties=parties,
        description= description.strip() or None,
        declared_license=license.strip() or None,
        code_view_url=code_view_url.strip() or None,
        bug_tracking_url=bug_tracking_url.strip() or None,
        download_url=chef_download_url(name, version).strip(),
        dependencies=package_dependencies,
    )
