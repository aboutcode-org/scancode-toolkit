#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
from os.path import abspath
from os.path import expanduser

import saneyaml
from commoncode import archive
from commoncode import fileutils
from packageurl import PackageURL

from packagedcode import models
from packagedcode import spec
from packagedcode.gemfile_lock import GemfileLockParser
from packagedcode.utils import combine_expressions
from packagedcode.utils import build_description
from packagedcode.utils import get_ancestor

# TODO: also support https://github.com/byrneg7/MWL_api/blob/master/.ruby-version

# TODO: support installed rails/bundler apps with vendor directory
# see https://github.com/brotandgames/ciao and logstash (jRuby) are good examples


class BaseGemHandler(models.DatafileHandler):

    @classmethod
    def compute_normalized_license(cls, package):
        return compute_normalized_license(package.declared_license)


class GemArchiveHandler(BaseGemHandler):
    path_patterns = ('*.gem',)
    filetypes = ('posix tar archive',)
    datasource_id = 'gem_archive'
    default_package_type = 'gem'
    default_primary_language = 'Ruby'
    description = 'RubyGems gem package archive'
    documentation_url = (
        'https://web.archive.org/web/20220326093616/'
        'https://piotrmurach.com/articles/looking-inside-a-ruby-gem/'
    )

    @classmethod
    def parse(cls, location):
        metadata = extract_gem_metadata(location)
        metadata = saneyaml.load(metadata)
        yield build_rubygem_package_data(
            gem_data=metadata,
            datasource_id=cls.datasource_id,
        )


def assemble_extracted_gem(cls, package_data, resource, codebase, package_adder):
    """
    An assemble implementation shared by handlers for manifests found in an
    extracted gem using extractcode.
    """
    datafile_name_patterns = (
        'metadata.gz-extract/metadata.gz-extract',
        'data.gz-extract/*.gemspec',
        'data.gz-extract/Gemfile',
        'data.gz-extract/Gemfile.lock',
    )

    gemroot = get_ancestor(levels_up=2, resource=resource, codebase=codebase)

    yield from cls.assemble_from_many_datafiles(
        datafile_name_patterns=datafile_name_patterns,
        directory=gemroot,
        codebase=codebase,
        package_adder=package_adder,
    )


class GemMetadataArchiveExtractedHandler(BaseGemHandler):
    datasource_id = 'gem_archive_extracted'
    path_patterns = ('*/metadata.gz-extract',)
    default_package_type = 'gem'
    default_primary_language = 'Ruby'
    description = 'RubyGems gem package extracted archive'
    documentation_url = (
        'https://web.archive.org/web/20220326093616/'
        'https://piotrmurach.com/articles/looking-inside-a-ruby-gem/'
    )

    @classmethod
    def parse(cls, location):
        with open(location, 'rb') as met:
            metadata = met.read()
        metadata = saneyaml.load(metadata)
        yield build_rubygem_package_data(
            gem_data=metadata,
            datasource_id=cls.datasource_id,
        )

    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder):
        yield from assemble_extracted_gem(cls, package_data, resource, codebase)


class BaseGemProjectHandler(BaseGemHandler):

    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder):
        datafile_name_patterns = (
            '*.gemspec',
            'Gemfile',
            'Gemfile.lock',
        )

        yield from cls.assemble_from_many_datafiles(
            datafile_name_patterns=datafile_name_patterns,
            directory=resource.parent(codebase),
            codebase=codebase,
            package_adder=package_adder,
        )

    @classmethod
    def assign_package_to_resources(cls, package, resource, codebase, package_adder):
        return models.DatafileHandler.assign_package_to_parent_tree(package, resource, codebase, package_adder)


class GemspecHandler(BaseGemHandler):
    datasource_id = 'gemspec'
    path_patterns = ('*.gemspec',)
    default_package_type = 'gem'
    default_primary_language = 'Ruby'
    description = 'RubyGems gemspec manifest'
    documentation_url = 'https://guides.rubygems.org/specification-reference/'

    @classmethod
    def parse(cls, location):
        gemspec = spec.parse_spec(
            location=location,
            package_type=cls.default_package_type,
        )

        name = gemspec.get('name')
        version = gemspec.get('version')
        homepage_url = gemspec.get('homepage')

        description = build_description(
            summary=gemspec.get('summary'),
            description=gemspec.get('description'),
        )
        vcs_url = gemspec.get('source')

        declared_license = gemspec.get('license')
        if declared_license:
            # FIXME: why splitting here? this is a job for the license detection
            declared_license = declared_license.split(',')

        parties = get_parties(gemspec)
        dependencies = gemspec.get('dependencies') or []

        urls = get_urls(name=name, version=version)

        package_data = models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=name,
            version=version,
            parties=parties,
            homepage_url=homepage_url,
            description=description,
            declared_license=declared_license,
            primary_language=cls.default_primary_language,
            dependencies=dependencies,
            **urls
        )

        if not package_data.license_expression and package_data.declared_license:
            package_data.license_expression = models.compute_normalized_license(package_data.declared_license)

        yield package_data


class GemspecInExtractedGemHandler(GemspecHandler):
    datasource_id = 'gemspec_extracted'
    path_patterns = ('*/data.gz-extract/*.gemspec',)
    description = 'RubyGems gemspec manifest - extracted data layout'

    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder):
        yield from assemble_extracted_gem(cls, package_data, resource, codebase, package_adder)


class GemspecInInstalledVendorBundleSpecificationsHandler(GemspecHandler):
    """
    A special handler for gemspec seen in the vendor/bundle/*/specifications
    directory when installed by Bundler. In this case, we have a special layout:
    all the .gemspec are processed and compiled in a specifications/ dir by
    Bundler. But these gemspec are standing alone and have been detached from
    their original "gem" directory. They are also different from the base
    gemspec for the same gem as they have been modified (?streamlined or
    normalized?) by Bundler including freezing strings.

    We reuse the default DatafileHandler.assemble() implementation such that
    each such gemspec is considered standing alone and have no other companion
    datafile or files assigned to a Package.
    """
    datasource_id = 'gem_gemspec_installed_specifications'
    # seen in vendor/bundle/jruby/2.5.0/specifications/* style layouts
    # and bundle/specifications/* style layouts
    # TODO: also report "jruby/2.5.0/" as extra or qualifiers
    path_patterns = ('*/specifications/*.gemspec',)
    description = 'RubyGems gemspec manifest - installed vendor/bundle/specifications layout'

    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder):
        # TODO: consider assembling datafiles across vendor/ subdirs
        yield from models.DatafileHandler.assemble(package_data, resource, codebase, package_adder)


# Note: we subclass GemspecHandler as the parsing code can handle both Ruby files
# TODO: https://stackoverflow.com/questions/41454333/meaning-of-new-block-git-sourcegithub-in-gemfile
class GemfileHandler(GemspecHandler):
    datasource_id = 'gemfile'
    path_patterns = ('*/Gemfile', '*/*.gemfile', '*/Gemfile-*')
    default_package_type = 'gem'
    default_primary_language = 'Ruby'
    description = 'RubyGems Bundler Gemfile'
    documentation_url = 'https://bundler.io/man/gemfile.5.html'


class GemfileInExtractedGemHandler(GemfileHandler):
    datasource_id = 'gemfile_extracted'
    path_patterns = ('*/data.gz-extract/Gemfile',)
    description = 'RubyGems Bundler Gemfile - extracted layout'

    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder):
        return assemble_extracted_gem(cls, package_data, resource, codebase, package_adder)


class GemfileLockHandler(BaseGemProjectHandler):
    datasource_id = 'gemfile_lock'
    path_patterns = ('*/Gemfile.lock',)
    default_package_type = 'gem'
    default_primary_language = 'Ruby'
    description = 'RubyGems Bundler Gemfile.lock'
    documentation_url = 'https://bundler.io/man/gemfile.5.html'

    @classmethod
    def parse(cls, location):
        gemfile_lock = GemfileLockParser(location)
        all_gems = list(gemfile_lock.all_gems.values())
        if not all_gems:
            return

        primary_gem = gemfile_lock.primary_gem
        if primary_gem:
            deps = [
                models.DependentPackage(
                    purl=PackageURL(
                        type='gem',
                        name=dep.name,
                        version=dep.version
                    ).to_string(),
                    extracted_requirement=', '.join(dep.requirements),
                    scope='dependencies',
                    is_runtime=True,
                    is_optional=False,
                    is_resolved=True,
                ) for dep in all_gems if dep != primary_gem
            ]
            urls = get_urls(primary_gem.name, primary_gem.version)

            yield models.PackageData(
                datasource_id=cls.datasource_id,
                primary_language=cls.default_primary_language,
                type=cls.default_package_type,
                name=primary_gem.name,
                version=primary_gem.version,
                dependencies=deps,
                **urls
            )
        else:
            deps = [
                models.DependentPackage(
                    purl=PackageURL(
                        type='gem',
                        name=gem.name,
                        version=gem.version
                    ).to_string(),
                    extracted_requirement=', '.join(gem.requirements),
                    # FIXME: get proper scope... This does not seem right
                    scope='dependencies',
                    is_runtime=True,
                    is_optional=False,
                    is_resolved=True,
                ) for gem in all_gems
            ]

            yield models.PackageData(
                datasource_id=cls.datasource_id,
                type=cls.default_package_type,
                dependencies=deps,
                primary_language=cls.default_primary_language,
            )


class GemfileLockInExtractedGemHandler(GemfileLockHandler):
    datasource_id = 'gemfile_lock_extracted'
    path_patterns = ('*/data.gz-extract/Gemfile.lock',)
    description = 'RubyGems Bundler Gemfile.lock - extracted layout'

    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder):
        yield from assemble_extracted_gem(cls, package_data, resource, codebase, package_adder)


def compute_normalized_license(declared_license):
    """
    Return a normalized license expression string detected from a list of
    declared license items.
    """
    if not declared_license:
        return

    detected_licenses = []

    for declared in declared_license:
        detected_license = models.compute_normalized_license(declared)
        if detected_license:
            detected_licenses.append(detected_license)

    if detected_licenses:
        return combine_expressions(detected_licenses)


def get_urls(name, version=None, platform=None):
    """
    Return a mapping of standard URLs
    """
    dnlu = rubygems_download_url(name, version, platform)
    return dict(
        repository_homepage_url=rubygems_homepage_url(name, version),
        repository_download_url=dnlu,
        api_data_url=rubygems_api_url(name, version),
        download_url=dnlu,
    )


def rubygems_homepage_url(name, version=None):
    """
    Return a Rubygems.org homepage URL given a ``name`` and optional
    ``version``, or None if ``name`` is empty.

    For example:
    >>> url = rubygems_homepage_url(name='mocha', version='1.7.0')
    >>> assert url == 'https://rubygems.org/gems/mocha/versions/1.7.0'

    >>> url = rubygems_homepage_url(name='mocha')
    >>> assert url == 'https://rubygems.org/gems/mocha'
    """
    if not name:
        return
    if version:
        version = version.strip().strip('/')
        return f'https://rubygems.org/gems/{name}/versions/{version}'
    else:
        return f'https://rubygems.org/gems/{name}'


def rubygems_download_url(name, version, platform=None):
    """
    Return a .gem download URL given a name, version, and optional platform (e.g. java)
    and a base repo URL.

    For example:

    >>> url = rubygems_download_url(name='mocha', version='1.7.0')
    >>> assert url == 'https://rubygems.org/downloads/mocha-1.7.0.gem'
    """
    if not name or not version:
        return
    name = name.strip().strip('/')
    version = version.strip().strip('/')
    version_plat = version
    if platform  and platform != 'ruby':
        version_plat = f'{version}-{platform}'
    return f'https://rubygems.org/downloads/{name}-{version_plat}.gem'


def rubygems_api_url(name, version=None):
    """
    Return a package API data URL given a name, an optional version and a base
    repo API URL.

    For instance:
    >>> url = rubygems_api_url(name='turbolinks', version='1.0.2')
    >>> assert url == 'https://rubygems.org/api/v2/rubygems/turbolinks/versions/1.0.2.json'

    If no version, we return:
    >>> url = rubygems_api_url(name='turbolinks')
    >>> assert url == 'https://rubygems.org/api/v1/versions/turbolinks.json'

    Things we could return: a summary for the latest version, with deps
    https://rubygems.org/api/v1/gems/mqlight.json
    """
    if not name:
        return

    if version:
        return f'https://rubygems.org/api/v2/rubygems/{name}/versions/{version}.json'
    else:
        return f'https://rubygems.org/api/v1/versions/{name}.json'


# FIXME: we should unify this with handling extracted gems
def extract_gem_metadata(location):
    """
    Return the string content of the metadata of a .gem archive file at
    ``location`` or None.
    This performs an extracion to a temp directory.
    """
    extract_loc = None
    try:
        # Extract first level of tar archive
        extract_loc = fileutils.get_temp_dir(prefix='scancode-extract-')
        abs_location = abspath(expanduser(location))
        archive.extract_tar(abs_location, extract_loc)

        # The gzipped metadata is the second level of archive.
        metadata = os.path.join(extract_loc, 'metadata')
        # or it can be a plain, non-gzipped file
        metadata_gz = metadata + '.gz'

        if os.path.exists(metadata):
            with open(metadata, 'rb') as met:
                content = met.read()

        elif os.path.exists(metadata_gz):
            content = archive.get_gz_compressed_file_content(metadata_gz)

        else:
            raise Exception(f'No RubyGems metadata file found inside .gem archive: {location!r}')

        return content

    finally:
        if extract_loc:
            fileutils.delete(extract_loc)


def build_rubygem_package_data(gem_data, datasource_id):
    """
    Return a PackageData for ``datasource_id`` built from a Gem `gem_data`
    mapping or None. The ``gem_data`` can come from a .gemspec or .gem/metadata.
    Optionally use the provided ``download_url`` and `package_url`` strings.
    """
    if not gem_data:
        return

    metadata = gem_data.get('metadata') or {}

    name = gem_data.get('name')
    # there are two levels of nesting for version:
    version1 = gem_data.get('version') or {}
    version = version1.get('version') or None

    platform = gem_data.get('platform')
    if platform != 'ruby':
        qualifiers = dict(platform=platform)
    else:
        qualifiers = {}

    description = build_description(
        summary=gem_data.get('summary'),
        description=gem_data.get('description'),
    )

    # Since the gem spec doc is not clear wrt. to the default being OR or AND
    # we will treat a list of licenses and a conjunction for now (e.g. AND)
    # See https://guides.rubygems.org/specification-reference/#licenseo
    lic = gem_data.get('license')
    licenses = gem_data.get('licenses')
    declared_license = licenses_mapper(lic, licenses)

    # we may have tow homepages and one may be wrong.
    # we prefer the one from the metadata
    homepage_url = metadata.get('homepage_uri')
    if not homepage_url:
        homepage_url = gem_data.get('homepage')

    urls = get_urls(name, version, platform)
    dependencies = get_dependencies(gem_data.get('dependencies'))
    file_references = get_file_references(metadata.get('files'))

    package_data = models.PackageData(
        datasource_id=datasource_id,
        type=GemArchiveHandler.default_package_type,
        primary_language=GemArchiveHandler.default_primary_language,
        name=name,
        version=version,
        qualifiers=qualifiers,
        description=description,
        homepage_url=homepage_url,
        declared_license=declared_license,
        bug_tracking_url=metadata.get('bug_tracking_uri'),
        code_view_url=metadata.get('source_code_uri'),
        file_references=file_references,
        dependencies=dependencies,
        **urls,
    )

    # we can have one singular or a plural list of authors
    authors = gem_data.get('authors') or []
    # or a string of coma-sperated authors (in the Rubygems API)
    if isinstance(authors, str):
        authors = [a.strip() for a in authors.split(',') if a.strip()]
    authors.append(gem_data.get('author') or '')
    for author in authors:
        if author and author.strip():
            party = models.Party(name=author, role='author')
            package_data.parties.append(party)

    # TODO: we have an email that is either a string or a list of string

    # date: 2019-01-09 00:00:00.000000000 Z
    date = gem_data.get('date')
    if date and len(date) >= 10:
        date = date[:10]
        package_data.release_date = date[:10]

    # TODO: infer source purl and add purl to package_data.source_packages

    # not used for now
    #   "changelog_uri"     => "https://example.com/user/bestgemever/CHANGELOG.md",
    #   "wiki_uri"          => "https://example.com/user/bestgemever/wiki"
    #   "mailing_list_uri"  => "https://groups.example.com/bestgemever",
    #   "documentation_uri" => "https://www.example.info/gems/bestgemever/0.0.1",

    if not package_data.homepage_url:
        package_data.homepage_url = rubygems_homepage_url(name, version)

    if not package_data.license_expression and package_data.declared_license:
        package_data.license_expression = models.compute_normalized_license(package_data.declared_license)

    return package_data


def licenses_mapper(lic, lics):
    """
    Return a `declared_licenses` list based on the `lic` license and
    `lics` licenses values found in a package_data.
    """
    declared_licenses = []
    if lic:
        declared_licenses.append(str(license).strip())
    if lics:
        for lic in lics:
            lic = lic.strip()
            if lic:
                declared_licenses.append(lic)
    return declared_licenses


def get_dependencies(dependencies):
    """
    Return a list of DependentPackage from the dependencies data found in a
    .gem/metadata. Here is an example of the raw YAML:

        dependencies:
        - !ruby/object:Gem::Dependency
          requirement: !ruby/object:Gem::Requirement
            requirements:
            - - '='
              - !ruby/object:Gem::Version
                version: '10.0'
          name: rake
          prerelease: false
          type: :development
          version_requirements: !ruby/object:Gem::Requirement
            requirements:
            - - '='
              - !ruby/object:Gem::Version
                version: '10.0'
        - !ruby/object:Gem::Dependency
          requirement: !ruby/object:Gem::Requirement
            requirements:
            - - "~>"
              - !ruby/object:Gem::Version
                version: 0.7.1
          name: rake-compiler
          prerelease: false
          type: :development
          version_requirements: !ruby/object:Gem::Requirement
            requirements:
            - - "~>"
              - !ruby/object:Gem::Version
                version: 0.7.1

    And once loaded with saneyaml it looks like this with several intermediate
    nestings:
        {
          "dependencies": [
            {
              "requirement": {
                "requirements": [
                  ["=", {"version": "10.0"}]
                ]
              },
              "name": "rake",
              "prerelease": false,
              "type": ":development",
              "version_requirements": {
                "requirements": [
                  ["=", {"version": "10.0"}]
                ]
              }
            },
            {
              "requirement": {
                "requirements": [
                  ["~>", {"version": "0.7.1"}]
                ]
              },
              "name": "rake-compiler",
              "prerelease": false,
              "type": ":development",
              "version_requirements": {
                "requirements": [
                  ["~>", {"version": "0.7.1"}]
                ]
              }
            }
          ]
        }

    """
    if not dependencies:
        return []

    deps = []
    for dependency in dependencies:
        name = dependency.get('name')
        if not name:
            continue

        # the default value is runtime
        scope = dependency.get('type', '').strip(':') or 'runtime'
        is_optional = scope == 'development'
        is_runtime = scope == 'runtime'

        requirements = dependency.get('requirement', {}).get('requirements', [])
        constraints = []
        for constraint, version in requirements:
            version = version.get('version') or None

            # >= 0 allows for any version: we ignore these type of contrainsts
            # as this is the same as no constraint. We also ignore lack of
            # constraints and versions
            if ((constraint == '>=' and version == '0') or not (constraint and version)):
                continue
            version_constraint = f'{constraint} {version}'
            constraints.append(version_constraint)

        # if we have only one version constraint and this is "=" then we are resolved
        is_resolved = False
        if constraints and len(constraints) == 1:
            is_resolved = constraint == '='

        # FIXME: check this is correct and complies with vers.
        version_constraint = ', '.join(constraints)

        dep = models.DependentPackage(
            purl=str(PackageURL(type='gem', name=name)),
            extracted_requirement=version_constraint or None,
            scope=scope,
            is_runtime=is_runtime,
            is_optional=is_optional,
            is_resolved=is_resolved,
        )
        deps.append(dep)

    return deps


# mapping of {Gem license: scancode license key}
LICENSES_MAPPING = {
    'Apache 2.0': 'apache-2.0',
    'Apache-2.0': 'apache-2.0',
    'Apache': 'apache-2.0',
    'Apache License 2.0': 'apache-2.0',
    'Artistic 2.0': 'artistic-2.0',
    '2-clause BSDL': 'bsd-simplified',
    'BSD 2-Clause': 'bsd-simplified',
    'BSD-2-Clause': 'bsd-simplified',
    'BSD-3': 'bsd-new',
    'BSD': 'bsd-new',
    'GNU GPL v2': 'gpl-2.0',
    'GPL-2': 'gpl-2.0',
    'GPL2': 'gpl-2.0',
    'GPL': 'gpl-2.0',
    'GPLv2': 'gpl-2.0',
    'GPLv2+': 'gpl-2.0-plus',
    'GPLv3': 'gpl-3.0',
    'ISC': 'isc',
    'LGPL-2.1+': 'lgpl-2.1-plus',
    'LGPL-3': 'lgpl-3.0',
    'LGPL': 'lgpl',
    'LGPL': 'lgpl-2.0-plus',
    'LGPLv2.1+': 'lgpl-2.1-plus',
    'MIT': 'mit',
    'New Relic': 'new-relic',
    'None': 'unknown',
    'Perl Artistic v2': 'artistic-2.0',
    'Ruby 1.8': 'ruby',
    'Ruby': 'ruby',
    'same as ruby': 'ruby',
    'same as ruby\'s': 'ruby',
    'SIL Open Font License': 'ofl-1.0',
    'Unlicense': 'unlicense',
}


def party_mapper(role, names=[], emails=[]):
    """
    Yields Party with ``role`` objects from a ``names`` list of string.
    """
    if names:
        return (
            models.Party(type=models.party_person, name=name, role=role)
            for name in names
        )
    elif emails:
        return (
            models.Party(type=models.party_person, email=email, role=role)
            for email in emails
        )


def get_parties(gem_data):
    """
    Return a lits of Party from a mapping of ``gem_data``
    """
    parties = []
    authors = gem_data.get('author') or []
    parties.extend(party_mapper(names=authors, role='author'))
    # FIXME: emails is NOT a party
    emails = gem_data.get('email') or []
    parties.extend(party_mapper(emails=emails, role='author'))
    return parties


def get_file_references(files):
    """
    Return a list of FileReference from a ``files`` list of gem file paths.
    """
    files = files or []
    return [models.FileReference(path) for path in files]
