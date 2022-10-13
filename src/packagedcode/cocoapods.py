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
import os
import logging

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

TRACE = os.environ.get('SCANCODE_DEBUG_PACKAGE', False)

def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(
            ' '.join(isinstance(a, str) and a or repr(a) for a in args)
        )

# TODO: consider merging Gemfile.lock and Podfile.lock in one module: this is the same format

# TODO: override the license detection to detect declared_license correctly.


def get_repo_base_url(vcs_url):
    """
    Return the repository base_url given a ``vcs_url`` version control URL or
    None.

    For example::
    >>> assert get_repo_base_url('https://github.com/jogendra/BadgeHub.git') == 'https://github.com/jogendra/BadgeHub'
    >>> assert get_repo_base_url('https://github.com/jogendra/BadgeHub') == 'https://github.com/jogendra/BadgeHub'
    >>> assert get_repo_base_url(None) == None
    """
    if not vcs_url:
        return

    if not vcs_url.startswith('https://github.com/'):
        # TODO: we may not know what to do if this is not a GH repo?
        pass

    if vcs_url.endswith('.git'):
        reponame, _, _ = vcs_url.partition('.git')
    else:
        reponame = vcs_url

    return reponame


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
    def assemble(cls, package_data, resource, codebase, package_adder):
        """
        Assemble pod packages and dependencies and handle the specific cases where
        there are more than one podspec in the same directory.
        This is designed to process .podspec, Podfile and Podfile.lock
        """
        if codebase.has_single_resource:
            yield from models.DatafileHandler.assemble(package_data, resource, codebase)
        else:
            # do we have more than one podspec?
            parent = resource.parent(codebase)
            sibling_podspecs = [
                r for r in parent.children(codebase)
                if r.name.endswith('.podspec')
            ]

            siblings_counts = len(sibling_podspecs)
            has_single_podspec = siblings_counts == 1
            has_multiple_podspec = siblings_counts > 1

            datafile_name_patterns = (
                'Podfile.lock',
                'Podfile',
            )

            if has_single_podspec:
                # we can treat all podfile/spec as being for one package
                datafile_name_patterns = (sibling_podspecs[0].name,) + datafile_name_patterns

                yield from models.DatafileHandler.assemble_from_many_datafiles(
                    datafile_name_patterns=datafile_name_patterns,
                    directory=parent,
                    codebase=codebase,
                    package_adder=package_adder,
                )

            elif has_multiple_podspec:
                # treat each of podspec and podfile alone without meraging
                # as we cannot determine easily which podfile is for which
                # podspec
                podspec = sibling_podspecs.pop()
                datafile_name_patterns = (podspec.name,) + datafile_name_patterns

                yield from models.DatafileHandler.assemble_from_many_datafiles(
                    datafile_name_patterns=datafile_name_patterns,
                    directory=parent,
                    codebase=codebase,
                    package_adder=package_adder,
                )

                for resource in sibling_podspecs:
                    datafile_path = resource.path
                    for package_data in resource.package_data:
                        package_data = models.PackageData.from_dict(package_data)
                        package = models.Package.from_package_data(
                            package_data=package_data,
                            datafile_path=datafile_path,
                        )
                        cls.assign_package_to_resources(
                            package=package,
                            resource=resource,
                            codebase=codebase,
                            package_adder=package_adder,
                        )
                        yield package
                    yield resource

            else:
                # has_no_podspec:
                yield from models.DatafileHandler.assemble_from_many_datafiles(
                    datafile_name_patterns=datafile_name_patterns,
                    directory=parent,
                    codebase=codebase,
                    package_adder=package_adder,
                )


class PodspecHandler(BasePodHandler):
    datasource_id = 'cocoapods_podspec'
    path_patterns = ('*.podspec',)
    default_package_type = 'cocoapods'
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
        homepage_url = podspec.get('homepage')
        declared_license = podspec.get('license')
        license_expression = None
        if declared_license:
            license_expression = models.compute_normalized_license(declared_license)
        summary = podspec.get('summary')
        description = podspec.get('description')
        description = utils.build_description(
            summary=summary,
            description=description,
        )
        vcs_url = podspec.get('source') or ''
        authors = podspec.get('author') or []

        # FIXME: we are doing nothing with the email list
        parties = []
        if authors:
            for author in authors:
                auth, email = parse_person(author)
                party = models.Party(
                    type=models.party_person,
                    name=auth,
                    email=email,
                    role='author',
                )
                parties.append(party)

        urls = get_urls(
            name=name,
            version=version,
            homepage_url=homepage_url,
            vcs_url=vcs_url)

        yield models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=name,
            version=version,
            primary_language=cls.default_primary_language,
            vcs_url=vcs_url,
            # FIXME: a source should be a PURL, not a list of URLs
            # source_packages=vcs_url.split('\n'),
            description=description,
            declared_license=declared_license,
            license_expression=license_expression,
            homepage_url=homepage_url,
            parties=parties,
            **urls,
        )


class PodfileHandler(PodspecHandler):
    datasource_id = 'cocoapods_podfile'
    path_patterns = ('*Podfile',)
    default_package_type = 'cocoapods'
    default_primary_language = 'Objective-C'
    description = 'Cocoapods Podfile'
    documentation_url = 'https://guides.cocoapods.org/using/the-podfile.html'


class PodfileLockHandler(BasePodHandler):
    datasource_id = 'cocoapods_podfile_lock'
    path_patterns = ('*Podfile.lock',)
    default_package_type = 'cocoapods'
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

                    purl, xreq = parse_dep_requirements(main_pod)

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

                purl, xreq = parse_dep_requirements(pod)

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
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language=cls.default_primary_language,
            dependencies=dependencies,
        )


class PodspecJsonHandler(models.DatafileHandler):
    datasource_id = 'cocoapods_podspec_json'
    path_patterns = ('*.podspec.json',)
    default_package_type = 'cocoapods'
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
        elif isinstance(source, str):
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
    reponame = get_repo_base_url(vcs_url) or ''

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
        repository_download_url=repository_download_url or None,
        repository_homepage_url=name and f'https://cocoapods.org/pods/{name}' or None,
        code_view_url=reponame and version and f'{reponame}/tree/{version}' or None,
        bug_tracking_url=reponame and f'{reponame}/issues/' or None,
        api_data_url=api_data_url or None,
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


def parse_person(person):
    """
    Return name and email from person string.

    https://guides.cocoapods.org/syntax/podspec.html#authors
    Author can be in the form:
        s.author = 'Rohit Potter'
        or
        s.author = 'Rohit Potter=>rohit@gmail.com'

    >>> p = parse_person('Rohit Potter=>rohit@gmail.com')
    >>> assert p == ('Rohit Potter', 'rohit@gmail.com'), p
    >>> p = parse_person('Rohit Potter')
    >>> assert p == ('Rohit Potter', None), p
    """
    if '=>' in person:
        name, _, email = person.partition('=>')
        email = email.strip('\'" =')
    elif '=' in person:
        name, _, email = person.partition('=')
        email = email.strip('\'" ')
    else:
        name = person
        email = None

    name = name.strip('\'"')

    return name, email


def parse_dep_requirements(dep):
    """
    Return a tuple of (Package URL, version constraint) given a ``dep``
    dependency requirement string extracted from a podspec.

    For example:

    >>> expected = PackageURL.from_string('pkg:cocoapods/OHHTTPStubs@9.0.0'), '9.0.0'
    >>> assert parse_dep_requirements('OHHTTPStubs (9.0.0)') == expected

    >>> expected = PackageURL.from_string('pkg:cocoapods/OHHTTPStubs/NSURLSession'), None
    >>> result = parse_dep_requirements('OHHTTPStubs/NSURLSession')
    >>> assert result == expected, result

    >>> expected = PackageURL.from_string('pkg:cocoapods/AFNetworking/Serialization@3.0.4'), '= 3.0.4'
    >>> result = parse_dep_requirements(' AFNetworking/Serialization (= 3.0.4) ')
    >>> assert result == expected, result
    """
    if '(' in dep:
        name, _, version = dep.partition('(')
        version = version.strip(')( ')
        requirement = version
        version = requirement.strip('= ')

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
        type='cocoapods',
        namespace=namespace,
        name=name,
        version=version,
    )
    return purl, requirement
