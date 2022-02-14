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
import logging
import re

import attr
import saneyaml

from commoncode import filetype
from packagedcode import models
from packagedcode.licensing import get_license_matches
from packagedcode.licensing import get_license_expression_from_matches
from packagedcode.spec import Spec

from packageurl import PackageURL

"""
Handle cocoapods packages manifests for macOS and iOS
and from Xcode projects, including .podspec, Podfile and Podfile.lock files,
and .podspec.json files from https://github.com/CocoaPods/Specs.
See https://cocoapods.org
"""

# TODO: override the license detection to detect declared_license correctly.

TRACE = False

logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


@attr.s()
class CocoapodsPackage(models.Package):
    default_type = 'pods'
    default_primary_language = 'Objective-C'
    default_web_baseurl = 'https://cocoapods.org'
    github_specs_repo_baseurl = 'https://raw.githubusercontent.com/CocoaPods/Specs/blob/master/Specs'
    default_cdn_baseurl='https://cdn.cocoapods.org/Specs'

    def repository_homepage_url(self, baseurl=default_web_baseurl):
        return f'{baseurl}/pods/{self.name}'

    def repository_download_url(self):
        if self.homepage_url:
            return f'{self.homepage_url}/archive/{self.version}.zip'
        elif self.reponame:
            return f'{self.reponame}/archive/refs/tags/{self.version}.zip'

    def get_api_data_url(self):
        return self.specs_json_github_url

    def get_code_view_url(self):
        if isinstance(self.reponame, str):
            return self.reponame+'/tree/'+self.version

    def get_bug_tracking_url(self):
        if isinstance(self.reponame, str):
            return self.reponame+'/issues/'

    def specs_json_cdn_url(self, baseurl=default_cdn_baseurl):
        return f'{baseurl}/{self.hashed_path}/{self.name}/{self.version}/{self.name}.podspec.json'

    def specs_json_github_url(self, baseurl=github_specs_repo_baseurl):
        return f'{baseurl}/{self.hashed_path}/{self.name}/{self.version}/{self.name}.podspec.json'

    @property
    def reponame(self):
        if isinstance(self.vcs_url, str):
            if self.vcs_url[-4:] == '.git':
                return self.vcs_url[:-4]

    @property
    def hashed_path(self):
        """
        Returns a string with a part of the file path derived from the md5 hash.

        From https://github.com/CocoaPods/cdn.cocoapods.org:
        "There are a set of known prefixes for all Podspec paths, you take the name of the pod,
        create a hash (using md5) of it and take the first three characters."
        """
        podname = self.get_podname_proper(self.name)
        if self.name != podname:
            name_to_hash = podname
        else:
            name_to_hash = self.name

        hash_init = self.get_first_3_mdf_hash_characters(name_to_hash)
        hashed_path = '/'.join(list(hash_init))
        return hashed_path

    @staticmethod
    def get_first_3_mdf_hash_characters(podname):
        return hashlib.md5(podname.encode('utf-8')).hexdigest()[0:3] 

    @staticmethod
    def get_podname_proper(podname):
        """
        Podnames in cocoapods sometimes are files inside a pods package (like 'OHHTTPStubs/Default')
        This returns proper podname in those cases.
        """
        if '/' in podname:
            return podname.split('/')[0]
        return podname


@attr.s()
class Podspec(CocoapodsPackage, models.PackageManifest):

    file_patterns = ('*.podspec',)
    extensions = ('.podspec',)

    @classmethod
    def is_manifest(cls, location):
        """
        Return True if the file at ``location`` is likely a manifest of this type.
        """
        return filetype.is_file(location) and location.endswith('.podspec')

    @classmethod
    def recognize(cls, location):
        """
        Yield one or more Package manifest objects given a file ``location`` pointing to a
        package archive, manifest or similar.
        """
        podspec_object = Spec()
        data = podspec_object.parse_spec(location)

        name = data.get('name')
        version = data.get('version')
        declared_license = data.get('license')
        summary = data.get('summary', '')
        description = data.get('description', '')
        homepage_url = data.get('homepage_url')
        source = data.get('source')
        authors = data.get('author') or []
        if summary and not description.startswith(summary):
            desc = [summary]
            if description:
                desc += [description]
            description = '\n'.join(desc)

        author_names = []
        author_email = []
        if authors:
            for split_author in authors:
                split_author = split_author.strip()
                author, email = parse_person(split_author)
                author_names.append(author)
                author_email.append(email)

        parties = list(party_mapper(author_names, author_email))

        yield cls(
            name=name,
            version=version,
            vcs_url=source,
            source_packages=list(source.split('\n')),
            description=description,
            declared_license=declared_license,
            homepage_url=homepage_url,
            parties=parties
        )


@attr.s()
class PodfileLock(CocoapodsPackage, models.PackageManifest):

    file_patterns = ('*podfile.lock',)
    extensions = ('.lock',)

    @classmethod
    def is_manifest(cls, location):
        """
        Return True if the file at ``location`` is likely a manifest of this type.
        """
        return (filetype.is_file(location) and location.endswith(('podfile.lock', 'Podfile.lock')))

    @classmethod
    def recognize(cls, location):
        """
        Yield one or more Package manifest objects given a file ``location`` pointing to a
        package archive, manifest or similar.
        """
        data = cls.read_podfile_lock(location)

        pods = data['PODS']
        pod_deps = []

        for pod in pods:

            if isinstance(pod, dict):
                for main_pod, _dep_pods in pod.items():

                    podname, namespace, version = get_data_from_pods(main_pod)

                    purl = PackageURL(
                        type='pods',
                        namespace=namespace,
                        name=podname,
                        version=version,
                    ).to_string()

                    pod_deps.append(
                        models.DependentPackage(
                            purl=purl,
                            scope='requires-dev',
                            requirement=version,
                            is_runtime=False,
                            is_optional=True,
                            is_resolved=True,
                        )
                    )

            elif isinstance(pod, str):  
                podname, namespace, version = get_data_from_pods(pod)
                purl = PackageURL(
                    type='pods',
                    namespace=namespace,
                    name=podname,
                    version=version,
                ).to_string()

                pod_deps.append(
                    models.DependentPackage(
                        purl=purl,
                        scope='requires-dev',
                        requirement=version,
                        is_runtime=False,
                        is_optional=True,
                        is_resolved=True,
                    )
                )

        yield cls(
            dependencies=pod_deps,
            declared_license=None,
        )


    @staticmethod
    def read_podfile_lock(location):
        """
        Reads from podfile.lock file at location as YML.
        """
        with open(location, 'r') as file:
            data = saneyaml.load(file) 

        return data


@attr.s()
class PodspecJson(CocoapodsPackage, models.PackageManifest):

    file_patterns = ('*.podspec.json',)
    extensions = ('.json',)

    @classmethod
    def is_manifest(cls, location):
        """
        Return True if the file at ``location`` is likely a manifest of this type.
        """
        return filetype.is_file(location) and location.endswith('.podspec.json')

    @classmethod
    def recognize(cls, location):
        """
        Yield one or more Package manifest objects given a file ``location`` pointing to a
        package archive, manifest or similar.
        """
        data = cls.read_podspec_json(location)

        name = data.get('name')
        version = data.get('version')
        summary = data.get('summary', '')
        description = data.get('description', '')
        homepage_url = data.get('homepage')

        license = data.get('license')
        if isinstance(license, dict):
            declared_license = ' '.join(list(license.values()))
        else:
            declared_license = license

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
                        url=value+'.com',
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

        package_manifest = cls(
            name=name,
            version=version,
            vcs_url=vcs_url,
            description=description,
            declared_license=declared_license,
            license_expression=license_expression,
            homepage_url=homepage_url,
            download_url=download_url,
            parties=parties,
        )

        package_manifest.api_data_url = package_manifest.get_api_data_url()

        yield package_manifest

    @staticmethod
    def read_podspec_json(location):
        """
        Reads from podspec.json file at location as JSON.
        """
        with open(location, "r") as file:
            data = json.load(file)

        return data


@attr.s()
class CocoapodsPackageInstance(CocoapodsPackage, models.PackageInstance):
    """
    A cocoapods PackageInstance that is created out of one/multiple cocoapods package
    manifests and package-like data, with it's files.
    """

    @property
    def manifests(self):
        return [
            Podspec,
            PodspecJson,
            PodfileLock
        ]


def party_mapper(author, email):
    """
    Yields a Party object with author and email.
    """
    for person in author:
        yield models.Party(
            type=models.party_person,
            name=person,
            role='author')

    for person in email:
        yield models.Party(
            type=models.party_person,
            email=person,
            role='email')


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


def get_sha1_file(location):
    """
    Get sha1 hash for a file at location.
    """
    with open(location, "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()


def get_data_from_pods(dep_pod_version):
    
    if '(' in dep_pod_version:
        podname, _, version = dep_pod_version.strip(')').partition(' (')
    else:
        version = None
        podname = dep_pod_version
        
    if '/' in podname:
        namespace, _, podname = podname.partition('/')
    else:
        namespace = None

    return podname, namespace, version
