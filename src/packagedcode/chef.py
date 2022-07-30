# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import json
import logging

from commoncode import fileutils
from packageurl import PackageURL
from pygments import highlight
from pygments.formatter import Formatter
from pygments.lexers.ruby import RubyLexer
from pygments.token import Token

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


def chef_download_url(name, version):
    """
    Return an Chef cookbook download url given a name, version, and base registry URL.

    For example:
    >>> c = chef_download_url('seven_zip', '1.0.4')
    >>> assert c == u'https://supermarket.chef.io/cookbooks/seven_zip/versions/1.0.4/download'
    """
    return name and version and f'https://supermarket.chef.io/cookbooks/{name}/versions/{version}/download'


def chef_api_url(name, version):
    """
    Return a package API data URL given a name, version and a base registry URL.

    For example:
    >>> c = chef_api_url('seven_zip', '1.0.4')
    >>> assert c == u'https://supermarket.chef.io/api/v1/cookbooks/seven_zip/versions/1.0.4'
    """
    return name and version and f'https://supermarket.chef.io/api/v1/cookbooks/{name}/versions/{version}'


def get_urls(name, version):
    """
    Return a mapping of URLs given a name and version.
    """
    dnl = chef_download_url(name, version)
    rhu = name and version and f'https://supermarket.chef.io/cookbooks/{name}/versions/{version}/'
    return dict(
        download_url=dnl,
        repository_download_url=dnl,
        repository_homepage_url=rhu,
        api_data_url=chef_api_url(name, version),
    )


class ChefMetadataFormatter(Formatter):

    def format(self, tokens, outfile):
        """
        Parse lines from a Chef `metadata.rb` file.

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
        and its values are those variable's values. This dictionary is then dumped
        to `outfile` as JSON.
        """
        metadata = dict(depends={})
        line = []
        identifiers_and_literals = (
            Token.Name,
            Token.Name.Builtin,  # NOQA
            Token.Punctuation,
            Token.Literal.String.Single,  # NOQA
            Token.Literal.String.Double  # NOQA
        )
        quotes = '"', "'"
        quoted = lambda x: (x.startswith('"') and x.endswith('"')) or (x.startswith("'") and value.endswith("'"))

        for ttype, value in tokens:
            # We don't allow tokens that are just '\"' or '\''
            if (ttype in identifiers_and_literals and value not in quotes):
                # Some tokens are strings with leading and trailing quotes, so
                # we remove them
                if quoted(value):
                    value = value[1:-1]
                line.append(value)

            if ttype in (Token.Text,) and value.endswith('\n') and line:
                # The field name should be the first element in the list
                key = line.pop(0)
                # Join all tokens as a single string
                joined_line = ''.join(line)

                # Store dependencies as dependency_name:dependency_requirement
                # in an Object instead of a single string
                if key == 'depends':
                    # Dependencies are listed in the form of dependency,requirement
                    dep_requirement = joined_line.rsplit(',')
                    if len(dep_requirement) == 2:
                        dep_name = dep_requirement[0]
                        requirement = dep_requirement[1]
                    else:
                        dep_name = joined_line
                        requirement = None
                    metadata[key][dep_name] = requirement
                else:
                    metadata[key] = joined_line

                line = []
        json.dump(metadata, outfile)


class BaseChefMetadataHandler(models.DatafileHandler):

    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder):
        """
        Assemble Package from Chef metadata.rb, then from metadata.json files.
        """
        yield from cls.assemble_from_many_datafiles(
            datafile_name_patterns=('metadata.rb', 'metadata.json',),
            directory=resource.parent(codebase),
            codebase=codebase,
            package_adder=package_adder,
        )


# TODO: implemet me: extract and parse and register
class ChefCookbookHandler(BaseChefMetadataHandler):
    datasource_id = 'chef_cookbook_tarball'
    path_patterns = ('*.tgz',)
    default_package_type = 'chef'
    default_primary_language = 'Ruby'
    description = 'Chef cookbook tarball'


class ChefMetadataJsonHandler(BaseChefMetadataHandler):
    datasource_id = 'chef_cookbook_metadata_json'
    path_patterns = ('*/metadata.json',)
    default_package_type = 'chef'
    default_primary_language = 'Ruby'
    description = 'Chef cookbook metadata.json'
    documentation_url = 'https://docs.chef.io/config_rb_metadata/'

    @classmethod
    def is_datafile(cls, location, filetypes=tuple()):
        """
        Return True if `location` path is for a Chef metadata.json file. The
        metadata.json is/was also used in Python legacy wheels in a 'dist-info'
        directory.
        """
        if super().is_datafile(location, filetypes=filetypes):
            parent = fileutils.file_name(fileutils.parent_directory(location))
            return not parent.endswith('dist-info')

    @classmethod
    def parse(cls, location):
        """
        Yield one or more Package manifest objects given a file ``location``
        pointing to a package archive, manifest or similar.
        """
        with io.open(location, encoding='utf-8') as loc:
            package_data = json.load(loc)
        return build_package(package_data, datasource_id=cls.datasource_id)


class ChefMetadataRbHandler(BaseChefMetadataHandler):
    datasource_id = 'chef_cookbook_metadata_rb'
    path_patterns = ('*/metadata.rb',)
    default_package_type = 'chef'
    default_primary_language = 'Ruby'
    description = 'Chef cookbook metadata.rb'
    documentation_url = 'https://docs.chef.io/config_rb_metadata/'

    @classmethod
    def parse(cls, location):
        with io.open(location, encoding='utf-8') as loc:
            file_contents = loc.read()

        # we use a Pygments formatter for parsing lexed Ruby code
        formatted_file_contents = highlight(
            file_contents,
            RubyLexer(),
            ChefMetadataFormatter()
        )
        package_data = json.loads(formatted_file_contents)
        return build_package(package_data, datasource_id=cls.datasource_id)


def build_package(package_data, datasource_id):
    """
    Return a PackageData object from a package_data mapping from a metadata.json
    or similar or None.
    """
    name = package_data.get('name')
    version = package_data.get('version')

    maintainer_name = package_data.get('maintainer', '')
    maintainer_email = package_data.get('maintainer_email', '')
    parties = []
    if maintainer_name or maintainer_email:
        parties.append(
            models.Party(
                name=maintainer_name.strip() or None,
                role='maintainer',
                email=maintainer_email.strip() or None,
            )
        )

    # TODO: combine descriptions as done elsewhere
    description = package_data.get('description', '') or package_data.get('long_description', '')
    lic = package_data.get('license', '')
    declared_license = None
    license_expression = None
    if lic:
        declared_license=lic.strip()
        if declared_license:
            license_expression = models.compute_normalized_license(declared_license)
    code_view_url = package_data.get('source_url', '')
    bug_tracking_url = package_data.get('issues_url', '')

    deps = dict(package_data.get('dependencies', {}) or {})
    deps.update(package_data.get('depends', {}) or {})

    dependencies = []
    for dependency_name, requirement in deps.items():
        dependencies.append(
            models.DependentPackage(
                purl=PackageURL(type='chef', name=dependency_name).to_string(),
                scope='dependencies',
                extracted_requirement=requirement,
                is_runtime=True,
                is_optional=False,
            )
        )

    yield models.PackageData(
        datasource_id=datasource_id,
        type=ChefMetadataJsonHandler.default_package_type,
        name=name,
        version=version,
        parties=parties,
        description=description.strip() or None,
        declared_license=declared_license,
        license_expression=license_expression,
        code_view_url=code_view_url.strip() or None,
        bug_tracking_url=bug_tracking_url.strip() or None,
        dependencies=dependencies,
        primary_language='Ruby',
        **get_urls(name, version),
    )
