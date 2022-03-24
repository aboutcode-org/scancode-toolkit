#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import hashlib
import json
import re

import saneyaml
from packageurl import PackageURL

from packagedcode import models
from packagedcode.licensing import get_license_matches
from packagedcode.licensing import get_license_expression_from_matches
from packagedcode import spec
from packagedcode import utils

"""
Handle cocoapods packages manifests for macOS and iOS
and from Xcode projects, including .podspec, Podfile and Podfile.lock files,
and .podspec.json files from https://github.com/CocoaPods/Specs.
See https://cocoapods.org
"""

# TODO: consider merging Gemfile.lock and Podfile.lock in one module: this is the same format

# TODO: override the license detection to detect declared_license correctly.


def get_reponame(vcs_url):
    if isinstance(vcs_url, str):
        if vcs_url[-4:] == '.git':
            return vcs_url[:-4]


def get_podname_proper(podname):
    """
    Podnames in cocoapods sometimes are files inside a pods package (like 'OHHTTPStubs/Default')
    This returns proper podname in those cases.
    """
    if '/' in podname:
        return podname.split('/')[0]
    return podname


def get_hashed_path(name):
    """
    Returns a string with a part of the file path derived from the md5 hash.

    From https://github.com/CocoaPods/cdn.cocoapods.org:
    "There are a set of known prefixes for all Podspec paths, you take the name of the pod,
    create a hash (using md5) of it and take the first three characters."
    """
    if not name:
        return
    podname = get_podname_proper(name)
    if name != podname:
        name_to_hash = podname
    else:
        name_to_hash = name

    hash_init = get_first_three_md5_hash_characters(name_to_hash)
    hashed_path = '/'.join(list(hash_init))
    return hashed_path


def get_first_three_md5_hash_characters(podname):
    return hashlib.md5(podname.encode('utf-8')).hexdigest()[0:3]


class BasePodHandler(models.DatafileHandler):

    @classmethod
    def assemble(cls, package_data, resource, codebase):
        datafile_name_patterns = (
            '*.podspec',
            'Podfile.lock',
            'Podfile',
        )

        yield from cls.assemble_from_many_datafiles(
            datafile_name_patterns=datafile_name_patterns,
            directory=resource.parent(codebase),
            codebase=codebase,
        )


class PodspecHandler(BasePodHandler):
    datasource_id = 'cocoapods_podspec'
    path_patterns = ('*.podspec',)
    default_package_type = 'pods'
    default_primary_language = 'Objective-C'
    description = 'Cocoapods .podspec'
    documentation_url = 'https://guides.cocoapods.org/syntax/podspec.html'

    @classmethod
    def parse(cls, location):
        """
        Yield one or more Package manifest objects given a file ``location``
        pointing to a package archive, manifest or similar.
        """
        podspec = spec.parse_spec(
            location=location, 
            package_type=cls.default_package_type,
        )

        name = podspec.get('name')
        version = podspec.get('version')
        homepage_url = podspec.get('homepage_url')
        declared_license = podspec.get('license')
        description = utils.build_description(
            summary=podspec.get('summary'),
            description=podspec.get('description'),
        )
        vcs_url = podspec.get('source')
        authors = podspec.get('author') or []


        author_names = []
        author_email = []
        if authors:
            for split_author in authors:
                split_author = split_author.strip()
                author, email = parse_person(split_author)
                author_names.append(author)
                author_email.append(email)

        parties = list(party_mapper(author_names, author_email))

        urls = get_urls(
            name=name,
            version=version,
            homepage_url=homepage_url,
            vcs_url=vcs_url)

        yield models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language=cls.default_primary_language,
            name=name,
            version=version,
            vcs_url=vcs_url,
            # FIXME: a source should be a PURL, not a list of URLs
            source_packages=vcs_url.split('\n'),
            description=description,
            declared_license=declared_license,
            homepage_url=homepage_url,
            parties=parties,
            **urls,
        )


class PodfileHandler(PodspecHandler):
    datasource_id = 'cocoapods_podfile'
    path_patterns = ('*Podfile',)
    default_package_type = 'pods'
    default_primary_language = 'Objective-C'
    description = 'Cocoapods Podfile'
    documentation_url = 'https://guides.cocoapods.org/using/the-podfile.html'


class PodfileLockHandler(BasePodHandler):
    datasource_id = 'cocoapods_podfile_lock'
    path_patterns = ('*Podfile.lock',)
    default_package_type = 'pods'
    default_primary_language = 'Objective-C'
    description = 'Cocoapods Podfile.lock'
    documentation_url = 'https://guides.cocoapods.org/using/the-podfile.html'

    @classmethod
    def parse(cls, location):
        """
        Yield PackageData from a YAML Podfile.lock.
        """
        with open(location) as pfl:
            data = saneyaml.load(pfl)

        pods = data['PODS']
        dependencies = []

        for pod in pods:
            if isinstance(pod, dict):
                for main_pod, _dep_pods in pod.items():

                    purl, xreq = parse_dep_requirements(main_pod).to_string()

                    dependencies.append(
                        models.DependentPackage(
                            purl=str(purl),
                            # FIXME: why dev?
                            scope='requires',
                            extracted_requirement=xreq,
                            is_runtime=False,
                            is_optional=True,
                            is_resolved=True,
                        )
                    )

            elif isinstance(pod, str):

                purl, xreq = parse_dep_requirements(pod).to_string()

                dependencies.append(
                    models.DependentPackage(
                        purl=str(purl),
                        # FIXME: why dev?
                        scope='requires',
                        extracted_requirement=xreq,
                        is_runtime=False,
                        is_optional=True,
                        is_resolved=True,
                    )
                )

        yield models.PackageData(
            datasouource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language=cls.default_primary_language,
            dependencies=dependencies,
        )


class PodspecJsonHandler(models.DatafileHandler):
    datasource_id = 'cocoapods_podspec_json'
    path_patterns = ('*.podspec.json',)
    default_package_type = 'pods'
    default_primary_language = 'Objective-C'
    description = 'Cocoapods .podspec.json'
    documentation_url = 'https://guides.cocoapods.org/syntax/podspec.html'

    @classmethod
    def parse(cls, location):
        with open(location) as psj:
            data = json.load(psj)

        name = data.get('name')
        version = data.get('version')
        summary = data.get('summary', '')
        description = data.get('description', '')
        homepage_url = data.get('homepage')

        lic = data.get('license')
        if isinstance(lic, dict):
            declared_license = ' '.join(list(lic.values()))
        else:
            declared_license = lic

        source = data.get('source')
        vcs_url = None
        download_url = None

        if isinstance(source, dict):
            git_url = source.get('git', '')
            http_url = source.get('http', '')
            if git_url:
                vcs_url = git_url
            elif http_url:
                download_url = http_url

        if not vcs_url:
            vcs_url = source

        authors = data.get('authors') or {}

        license_matches = get_license_matches(query_string=declared_license)
        if not license_matches:
            license_expression = 'unknown'
        else:
            license_expression = get_license_expression_from_matches(license_matches)

        if summary and not description.startswith(summary):
            desc = [summary]
            if description:
                desc += [description]
            description = '. '.join(desc)

        parties = []
        if authors:
            if isinstance(authors, dict):
                for key, value in authors.items():
                    party = models.Party(
                        type=models.party_org,
                        name=key,
                        url=value + '.com',
                        role='owner'
                    )
                    parties.append(party)
            else:
                party = models.Party(
                    type=models.party_org,
                    name=authors,
                    role='owner'
                )
                parties.append(party)

        extra_data = {}
        extra_data['source'] = data['source']
        dependencies = data.get('dependencies', '')
        if dependencies:
            extra_data['dependencies'] = dependencies
        extra_data['podspec.json'] = data

        urls = get_urls(
            name=name,
            version=version, homepage_url=homepage_url, vcs_url=vcs_url)

        yield models.PackageData(
            datasource_id=cls.datasource_id,
            primary_language=cls.default_primary_language,
            type=cls.default_package_type,
            name=name,
            version=version,
            description=description,
            declared_license=declared_license,
            license_expression=license_expression,
            parties=parties,
            vcs_url=vcs_url,
            homepage_url=homepage_url,
            download_url=download_url,
            **urls,
        )


def get_urls(name=None, version=None, homepage_url=None, vcs_url=None):
    """
    Return a mapping of podspec URLS.
    """
    reponame = get_reponame(vcs_url)

    repository_download_url = None
    if version:
        if homepage_url:
            repository_download_url = f'{homepage_url}/archive/{version}.zip'
        if reponame:
            repository_download_url = f'{reponame}/archive/refs/tags/{version}.zip'

    hashed_path = get_hashed_path(name)
    # not used yet, alternative for api_data_url
    specs_json_cdn_url = f'https://cdn.cocoapods.org/Specs/{hashed_path}/{name}/{version}/{name}.podspec.json'

    api_data_url = (
        hashed_path
        and name
        and version
        and f'https://raw.githubusercontent.com/CocoaPods/Specs/blob/master/Specs/{hashed_path}/{name}/{version}/{name}.podspec.json'
    )

    return dict(
        repository_download_url=repository_download_url,
        repository_homepage_url=name and f'https://cocoapods.org/pods/{name}',
        code_view_url=reponame and version and f'{reponame}/tree/{version}',
        bug_tracking_url=reponame and f'{reponame}/issues/',
        api_data_url=api_data_url,
    )


def party_mapper(author, email):
    """
    Yields a Party object with author and email.
    """
    for person in author:
        yield models.Party(
            type=models.party_person,
            name=person,
            role='author',
        )

    for person in email:
        yield models.Party(
            type=models.party_person,
            email=person,
            role='email',
        )


person_parser = re.compile(
    r'^(?P<name>[\w\s(),-_.,]+)'
    r'=>'
    r'(?P<email>[\S+]+$)'
).match

person_parser_only_name = re.compile(
    r'^(?P<name>[\w\s(),-_.,]+)'
).match


def parse_person(person):
    """
    Return name and email from person string.

    https://guides.cocoapods.org/syntax/podspec.html#authors
    Author can be in the form:
        s.author = 'Rohit Potter'
        or
        s.author = 'Rohit Potter=>rohit@gmail.com'
    Author check:
    >>> p = parse_person('Rohit Potter=>rohit@gmail.com')
    >>> assert p == ('Rohit Potter', 'rohit@gmail.com')
    >>> p = parse_person('Rohit Potter')
    >>> assert p == ('Rohit Potter', None)
    """
    parsed = person_parser(person)
    if not parsed:
        parsed = person_parser_only_name(person)
        name = parsed.group('name')
        email = None
    else:
        name = parsed.group('name')
        email = parsed.group('email')

    return name, email


def parse_dep_requirements(dep):
    """
    Return a tuple of (pods Package URL, and a version requirement) given a
    ``dep`` extracted pod requirements string.

    For example:

    >>> expected = PackageURL.from_string('pkg:pods/OHHTTPStubs@9.0.0'), '9.0.0'
    >>> assert get_purl_from_dep('OHHTTPStubs (9.0.0)') == expected

    >>> expected = PackageURL.from_string('pkg:pods/OHHTTPStubs/NSURLSession'), None
    >>> assert get_purl_from_dep('OHHTTPStubs/NSURLSession') == expected

    >>> expected = PackageURL.from_string('pkg:pods/AFNetworking/Serialization@3.0.4'), '= 3.0.4'
    >>> assert get_purl_from_dep(' AFNetworking/Serialization (= 3.0.4) ') == expected
    """
    if '(' in dep:
        name, _, version = dep.partition('(')
        version = version.strip(')')
        requirement = version
        if '=' in version:
            version = version.strip('=')

    else:
        version = None
        requirement = None
        name = dep

    name = name.strip(')')
    if '/' in name:
        namespace, _, name = name.partition('/')
    else:
        namespace = None

    purl = PackageURL(
        type='pods',
        namespace=namespace,
        name=name,
        version=version,
    )
    return purl, requirement
