
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#
import base64
import io
import json
import re
import urllib.parse
from functools import partial
from itertools import islice

from packageurl import PackageURL

from packagedcode import models
from packagedcode.utils import combine_expressions
from packagedcode.utils import normalize_vcs_url
from packagedcode.utils import yield_dependencies_from_package_data
from packagedcode.utils import yield_dependencies_from_package_resource
import saneyaml

"""
Handle Node.js npm packages
per https://docs.npmjs.com/files/package.json
"""

"""
To check https://github.com/npm/normalize-package-data
"""

# TODO: add os and engines from package.json??
# TODO: add new yarn v2 lock file format
# TODO: add pnp.js and pnpm-lock.yaml https://pnpm.io/
# TODO: add support for "lockfileVersion": 2 for package-lock.json and lockfileVersion: 3


class BaseNpmHandler(models.DatafileHandler):

    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder):
        """
        If ``resource``, or one of its siblings, is a package.json file, use it
        to create and yield the package, the package dependencies, and the
        package resources.

        When reporting the resources of a package, we alk the codebase, skipping
        the node_modules directory, assign resources to the package and yield
        resources.

        For each lock file, assign dependencies to package instances and yield dependencies.

        If there is no package.json, we do not have a package instance. In this
        case, we yield each of the dependencies in each lock file.
        """
        lockfile_names = {
            'package-lock.json',
            '.package-lock.json',
            'npm-shrinkwrap.json',
            'yarn.lock',
        }

        package_resource = None
        if resource.name == 'package.json':
            package_resource = resource
        elif resource.name in lockfile_names:
            if resource.has_parent():
                siblings = resource.siblings(codebase)
                package_resource = [r for r in siblings if r.name == 'package.json']
                if package_resource:
                    package_resource = package_resource[0]

        if package_resource:
            assert len(package_resource.package_data) == 1, f'Invalid package.json for {package_resource.path}'
            pkg_data = package_resource.package_data[0]
            pkg_data = models.PackageData.from_dict(pkg_data)

            # do we have enough to create a package?
            if pkg_data.purl:
                package = models.Package.from_package_data(
                    package_data=pkg_data,
                    datafile_path=package_resource.path,
                )
                package_uid = package.package_uid

                if not package.license_expression:
                    package.license_expression = compute_normalized_license(package.declared_license)

                # Always yield the package resource in all cases and first!
                yield package

                root = package_resource.parent(codebase)
                if root:
                    for npm_res in cls.walk_npm(resource=root, codebase=codebase):
                        if package_uid and package_uid not in npm_res.for_packages:
                            package_adder(package_uid, npm_res, codebase)
                        yield npm_res
                elif codebase.has_single_resource:
                    if package_uid and package_uid not in package_resource.for_packages:
                        package_adder(package_uid, package_resource, codebase)
                yield package_resource

            else:
                # we have no package, so deps are not for a specific package uid
                package_uid = None

            # in all cases yield possible dependencies
            yield from yield_dependencies_from_package_data(pkg_data, package_resource.path, package_uid)

            # we yield this as we do not want this further processed
            yield package_resource

            for lock_file in package_resource.siblings(codebase):
                if lock_file.name in lockfile_names:
                    yield from yield_dependencies_from_package_resource(lock_file, package_uid)

                    if package_uid and package_uid not in lock_file.for_packages:
                        package_adder(package_uid, lock_file, codebase)
                    yield lock_file
        else:
            # we do not have a package.json
            yield from yield_dependencies_from_package_resource(resource)

    @classmethod
    def walk_npm(cls, resource, codebase, depth=0):
        """
        Walk the ``codebase`` Codebase top-down, breadth-first starting from the
        ``resource`` Resource.

        Skip a first level child directory named "node_modules": this avoids
        reporting nested vendored packages as being part of their parent.
        Instead they will be reported on their own.
        """
        for child in resource.children(codebase):
            if depth == 0 and child.name == 'node_modules':
                continue

            yield child

            if child.is_dir:
                depth += 1
                for subchild in cls.walk_npm(child, codebase, depth=depth):
                    yield subchild


def get_urls(namespace, name, version):
    return dict(
        repository_homepage_url=npm_homepage_url(namespace, name, registry='https://www.npmjs.com/package'),
        repository_download_url=npm_download_url(namespace, name, version, registry='https://registry.npmjs.org'),
        api_data_url=npm_api_url(namespace, name, version, registry='https://registry.npmjs.org'),
    )


class NpmPackageJsonHandler(BaseNpmHandler):
    datasource_id = 'npm_package_json'
    path_patterns = ('*/package.json',)
    default_package_type = 'npm'
    default_primary_language = 'JavaScript'
    description = 'npm package.json'
    documentation_url = 'https://docs.npmjs.com/cli/v8/configuring-npm/package-json'

    @classmethod
    def parse(cls, location):
        with io.open(location, encoding='utf-8') as loc:
            package_data = json.load(loc)

        name = package_data.get('name')
        version = package_data.get('version')
        homepage_url = package_data.get('homepage', '')

        # a package.json without name and version can be a private package

        if homepage_url and isinstance(homepage_url, list):
            # TODO: should we keep other URLs
            homepage_url = homepage_url[0]
        homepage_url = homepage_url.strip() or None

        namespace, name = split_scoped_package_name(name)

        urls = get_urls(namespace, name, version)
        package = models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language=cls.default_primary_language,
            namespace=namespace or None,
            name=name,
            version=version or None,
            description=package_data.get('description', '').strip() or None,
            homepage_url=homepage_url,
            **urls,
        )
        vcs_revision = package_data.get('gitHead') or None

        # mapping of top level package.json items to a function accepting as
        # arguments the package.json element value and returning an iterable of (key,
        # values) to update on a package
        field_mappers = [
            ('author', partial(party_mapper, party_type='author')),
            ('contributors', partial(party_mapper, party_type='contributor')),
            ('maintainers', partial(party_mapper, party_type='maintainer')),

            ('dependencies', partial(deps_mapper, field_name='dependencies')),
            ('devDependencies', partial(deps_mapper, field_name='devDependencies')),
            ('peerDependencies', partial(deps_mapper, field_name='peerDependencies')),
            ('optionalDependencies', partial(deps_mapper, field_name='optionalDependencies')),
            ('bundledDependencies', bundle_deps_mapper),
            ('repository', partial(vcs_repository_mapper, vcs_revision=vcs_revision)),
            ('keywords', keywords_mapper,),
            ('bugs', bugs_mapper),
            ('dist', dist_mapper),
        ]

        for source, func in field_mappers:
            value = package_data.get(source) or None
            if value:
                if isinstance(value, str):
                    value = value.strip()
                if value:
                    func(value, package)

        if not package.download_url:
            # Only add a synthetic download URL if there is none from the dist mapping.
            package.download_url = npm_download_url(package.namespace, package.name, package.version)

        # licenses are a tad special with many different data structures
        lic = package_data.get('license')
        lics = package_data.get('licenses')
        package = licenses_mapper(lic, lics, package)

        if not package.license_expression and package.declared_license:
            package.license_expression = compute_normalized_license(package.declared_license)

        yield package

    @classmethod
    def compute_normalized_license(cls, package):
        return compute_normalized_license(package.declared_license)


class BaseNpmLockHandler(BaseNpmHandler):

    @classmethod
    def parse(cls, location):

        with io.open(location, encoding='utf-8') as loc:
            package_data = json.load(loc)

        # we have two formats: v1 and v2
        lockfile_version = package_data.get('lockfileVersion', 1)
        root_name = package_data.get('name')
        root_version = package_data.get('version')
        root_ns, _ , root_name = root_name.rpartition('/')

        extra_data = dict(lockfile_version=lockfile_version)
        # this is the top level element that we return
        root_package_data = models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language=cls.default_primary_language,
            namespace=root_ns,
            name=root_name,
            version=root_version,
            extra_data=extra_data,
            **get_urls(root_ns, root_name, root_version)
        )

        # https://docs.npmjs.com/cli/v8/configuring-npm/package-lock-json#lockfileversion
        if lockfile_version == 1:
            deps_key = 'dependencies'
        else:
            # v2 and may be v3???
            deps_key = 'packages'

        deps_mapping = package_data.get(deps_key) or {}

        dependencies = []

        for dep, dep_data in deps_mapping.items():
            is_dev = dep_data.get('dev', False)
            is_optional = dep_data.get('optional', False)
            is_devoptional = dep_data.get('devOptional', False)
            if is_dev or is_devoptional:
                is_runtime = False
                is_optional = True
                scope = 'devDependencies'
            else:
                is_runtime = True
                is_optional = is_optional
                scope = 'dependencies'

            if not dep:
                # in v2 format the first dep is the same as the top level
                # package and has no name
                pass

            # only present for first top level
            # otherwise get name from dep
            name = dep_data.get('name')
            if not name:
                if 'node_modules/' in dep:
                    # the name is the last segment as the dep can be:
                    # "node_modules/ansi-align/node_modules/ansi-regex"
                    _, _, name = dep.rpartition('node_modules/')
                else:
                    name = dep
            ns, _ , name = name.rpartition('/')
            version = dep_data.get('version')

            dep_purl = PackageURL(
                type=cls.default_package_type,
                namespace=ns,
                name=name,
                version=version,
            ).to_string()

            dependency = models.DependentPackage(
                purl=dep_purl,
                extracted_requirement=version,
                scope=scope,
                is_runtime=is_runtime,
                is_optional=is_optional,
                is_resolved=True,
            )

            # only seen in v2 for the top level package... but good to keep
            declared_license = dep_data.get('license')

            # URLs and checksums
            misc = get_urls(ns, name, version)
            resolved = dep_data.get('resolved')
            misc.update(get_checksum_and_url(resolved).items())
            integrity = dep_data.get('integrity')
            misc.update(get_algo_hexsum(integrity).items())

            resolved_package = models.PackageData(
                datasource_id=cls.datasource_id,
                type=cls.default_package_type,
                primary_language=cls.default_primary_language,
                namespace=ns,
                name=name,
                version=version,
                declared_license=declared_license,
                **misc,
            )
            # these are paths t the root of the installed package in v2
            if dep:
                resolved_package.file_references = [models.FileReference(path=dep)],

            # v1 as name/constraint pairs
            subrequires = dep_data.get('requires') or {}

            # in v1 these are further nested dependencies
            # in v2 these are name/constraint pairs like v1 requires
            subdependencies = dep_data.get('dependencies')

            # v2? ignored for now
            dev_subdependencies = dep_data.get('devDependencies')
            optional_subdependencies = dep_data.get('optionalDependencies')
            engines = dep_data.get('engines')
            funding = dep_data.get('funding')

            if lockfile_version == 1:
                subdeps_data = subrequires
            else:
                subdeps_data = subdependencies
            subdeps_data = subdeps_data or {}

            sub_deps = []
            for subdep, subdep_req in subdeps_data.items():
                sdns, _ , sdname = subdep.rpartition('/')
                sdpurl = PackageURL(
                    type=cls.default_package_type,
                    namespace=sdns,
                    name=sdname
                ).to_string()
                sub_deps.append(
                    models.DependentPackage(
                        purl=sdpurl,
                        scope=scope,
                        extracted_requirement=subdep_req,
                        is_runtime=is_runtime,
                        is_optional=is_optional,
                        is_resolved=False,
                    )
                )
            resolved_package.dependencies = sub_deps
            dependency.resolved_package = resolved_package.to_dict()
            dependencies.append(dependency)

        root_package_data.dependencies = dependencies

        yield root_package_data


class NpmPackageLockJsonHandler(BaseNpmLockHandler):
    # Note that there are multiple lockfileVersion 1 and 2 (and even 3)
    # and each have a different layout
    datasource_id = 'npm_package_lock_json'
    path_patterns = (
        '*/package-lock.json',
        '*/.package-lock.json',
    )
    default_package_type = 'npm'
    default_primary_language = 'JavaScript'
    description = 'npm package-lock.json lockfile'
    documentation_url = 'https://docs.npmjs.com/cli/v8/configuring-npm/package-lock-json'


class NpmShrinkwrapJsonHandler(BaseNpmLockHandler):
    datasource_id = 'npm_shrinkwrap_json'
    path_patterns = ('*/npm-shrinkwrap.json',)
    default_package_type = 'npm'
    default_primary_language = 'JavaScript'
    description = 'npm shrinkwrap.json lockfile'
    documentation_url = 'https://docs.npmjs.com/cli/v8/configuring-npm/npm-shrinkwrap-json'


class UnknownYarnLockFormat(Exception):
    pass


def is_yarn_v2(location):
    """
    Return True if this is a yarn.lock format version 2 and False if this is
    version 1. Raise an UnknownYarnLockFormat exception if neither v1 or v2.

    v1 is a custom, almost-like-YAMl format. v2 is a proper subset of YAML.

    The start of v1 file has this:
        # THIS IS AN AUTOGENERATED FILE. DO NOT EDIT THIS FILE DIRECTLY.
        # yarn lockfile v1

    The start of v2 file has this:
        # This file is generated by running "yarn install" inside your project.
        # Manual changes might be lost - proceed with caution!

        __metadata:
    """
    with open(location) as ylf:
        # check only in the first 10 lines
        for line in islice(ylf, 0, 10):
            if '__metadata:' in line:
                return True
            if 'yarn lockfile v1' in line:
                return False

    raise UnknownYarnLockFormat(location)


class YarnLockV2Handler(BaseNpmHandler):
    """
    Handle yarn.lock v2 format, which is YAML
    """
    datasource_id = 'yarn_lock_v2'
    path_patterns = ('*/yarn.lock',)
    default_package_type = 'npm'
    default_primary_language = 'JavaScript'
    description = 'yarn.lock lockfile v2 format'
    documentation_url = 'https://classic.yarnpkg.com/lang/en/docs/yarn-lock/'

    @classmethod
    def is_datafile(cls, location, filetypes=tuple()):
        return super().is_datafile(location, filetypes=filetypes) and is_yarn_v2(location)

    @classmethod
    def parse(cls, location):
        """
        Parse a bew yarn.lock v2 YAML format which looks like this:

        "@algolia/cache-browser-local-storage@npm:4.2.0":
          version: 4.2.0
          resolution: "@algolia/cache-browser-local-storage@npm:4.2.0"
          dependencies:
            "@algolia/cache-common": 4.2.0
          checksum: 72ac158925eb5a51e015aa22df5d2026fc0c0b6b58eb8c1290712e0
          languageName: node
          linkType: hard

        Yield a single PackageData
        """
        with open(location) as yl:
            lock_data = saneyaml.load(yl.read())
        top_dependencies = []

        for spec, details in lock_data.items():
            if spec == '__metadata':
                continue
            version = details.get('version')
            resolution = details.get('resolution')
            ns_name, _, version = resolution.rpartition('@')
            ns, _, name = ns_name.rpartition('/')
            if version.startswith('npm:'):
                _npm, _, version = version.partition(':')
            purl = PackageURL(
                type=cls.default_package_type,
                namespace=ns,
                name=name,
                version=version,
            )

            # TODO: add resolved_package with its own deps
            checksum = details.get('checksum')
            dependencies = details.get('dependencies') or {}
            peer_dependencies = details.get('peerDependencies') or {}
            dependencies_meta = details.get('dependenciesMeta') or {}
            # these are file references
            bin = details.get('bin') or []

            dependency = models.DependentPackage(
                    purl=str(purl),
                    extracted_requirement=version,
                    is_resolved=True,
                    # FIXME: these are NOT correct
                    scope='dependencies',
                    # TODO: get details  from metadata
                    is_optional=False,
                    is_runtime=True,
                )
            top_dependencies.append(dependency)

        yield models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language=cls.default_primary_language,
            dependencies=top_dependencies,
        )


class YarnLockV1Handler(BaseNpmHandler):
    """
    Handle yarn.lock v1 format, which is more or less but not quite like YAML
    """
    datasource_id = 'yarn_lock_v1'
    path_patterns = ('*/yarn.lock',)
    default_package_type = 'npm'
    default_primary_language = 'JavaScript'
    description = 'yarn.lock lockfile v1 format'
    documentation_url = 'https://classic.yarnpkg.com/lang/en/docs/yarn-lock/'

    @classmethod
    def is_datafile(cls, location, filetypes=tuple()):
        return super().is_datafile(location, filetypes=filetypes) and not is_yarn_v2(location)

    @classmethod
    def parse(cls, location):
        """
        Parse a classic yarn.lock format which looks like this:
            "@babel/core@^7.1.0", "@babel/core@^7.3.4":
              version "7.3.4"
              resolved "https://registry.yarnpkg.com/@babel/core/-/core-7.3.4.tgz#921a5a13746c21e32445bf0798680e9d11a6530b"
              integrity sha512-jRsuseXBo9pN197KnDwhhaaBzyZr2oIcLHHTt2oDdQrej5Qp57dCCJafWx5ivU8/alEYDpssYqv1MUqcxwQlrA==
              dependencies:
                "@babel/code-frame" "^7.0.0"
                "@babel/generator" "^7.3.4"

        Yield a single PackageData
        """
        with io.open(location, encoding='utf-8') as yl:
            yl_dependencies = yl.read().split('\n\n')

        dependencies = []
        for yl_dependency in yl_dependencies:
            lines = yl_dependency.splitlines(False)
            if all(l.startswith('#') or not l.strip() for l in lines):
                # header or empty blocks are all comments or empties
                continue

            top_requirements = []
            dependency_data = {}
            sub_dependencies = []

            for line in lines:
                stripped = line.strip()
                comment = line.startswith('#')
                if not stripped or comment:
                    continue

                if line.startswith(' ' * 4):
                    # "@babel/code-frame" "^7.0.0"
                    # hosted-git-info "^2.1.4"
                    # semver "2 || 3 || 4 || 5"
                    ns_name, _, constraint = stripped.partition(' ')
                    ns, _ , name = ns_name.rpartition('/')
                    sub_dependencies.append((ns, name, constraint,))

                elif line.startswith(' ' * 2) :
                    # version "7.3.4"
                    # resolved "https://registry.yarnpkg.com/@babel...."
                    # integrity sha512-jRsuseXBo9
                    key, _, value = stripped.partition(' ')
                    value = value.strip().strip("\"'")
                    key = key.strip()
                    if key != 'dependencies':
                        dependency_data[key] = value

                elif not line.startswith(' ') and stripped.endswith(':'):
                    # the first line of a dependency has the name and requirements
                    # "@babel/core@^7.1.0", "@babel/core@^7.3.4":
                    requirements = stripped.strip(':').split(', ')
                    requirements = [r.strip().strip("\"'") for r in requirements]
                    for req in requirements:
                        if req.startswith('@'):
                            assert req.count('@') == 2

                        ns_name, _, constraint = req.rpartition('@')
                        ns, _ , name = ns_name.rpartition('/')
                        constraint = constraint.strip("\"'")
                        top_requirements.append((ns, name, constraint,))

                else:
                    raise Exception('Inconsistent content')

            # top_requirements should be all for the same package
            ns_names = set([(ns, name) for ns, name, _constraint in top_requirements])
            assert len(ns_names) == 1, f'Different names for same dependency is not supported: {ns_names!r}'
            ns, name = ns_names.pop()
            version = dependency_data.get('version')
            extracted_requirement = ' '.join(constraint for _ns, _name, constraint in top_requirements)

            misc = get_urls(ns, name, version)
            resolved = dependency_data.get('resolved')
            misc.update(get_checksum_and_url(resolved).items())
            integrity = dependency_data.get('integrity')
            misc.update(get_algo_hexsum(integrity).items())

            # we create a resolve package with the details
            resolved_package_data = models.PackageData(
                datasource_id=cls.datasource_id,
                type=cls.default_package_type,
                namespace=ns,
                name=name,
                version=version,
                primary_language=cls.default_primary_language,
                **misc,
            )

            # we add the sub-deps to the resolved package
            for subns, subname, subconstraint in sub_dependencies:
                subpurl = PackageURL(type=cls.default_package_type, namespace=subns, name=subname)
                subconstraint = subconstraint.strip("\"'")
                subdep = models.DependentPackage(
                    purl=str(subpurl),
                    extracted_requirement=subconstraint,
                    # FIXME: these are NOT correct
                    scope='dependencies',
                    is_optional=False,
                    is_runtime=True,
                )
                resolved_package_data.dependencies.append(subdep)

            # we create a purl with a version, since we are resolved
            dep_purl = PackageURL(
                type=cls.default_package_type,
                namespace=ns,
                name=name,
                version=version,
            )

            dep = models.DependentPackage(
                purl=str(dep_purl),
                extracted_requirement=extracted_requirement,
                is_resolved=True,
                # FIXME: these are NOT correct
                scope='dependencies',
                is_optional=False,
                is_runtime=True,
                resolved_package=resolved_package_data.to_dict(),
            )
            dependencies.append(dep)

        yield models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language=cls.default_primary_language,
            dependencies=dependencies,
        )


def get_checksum_and_url(url):
    """
    Return a mapping of {download_url, sha1} where the checksum can be a
    fragment for a sha1.
    """
    if not url:
        return {}

    url, checksum = urllib.parse.urldefrag(url)
    sha1_hex_len = 40
    if checksum and len(checksum) == sha1_hex_len:
        return dict(download_url=url, sha1=checksum)
    else:
        return dict(download_url=url)


def get_algo_hexsum(checksum):
    """
    Return a mapping of {alogo: checksum in hex} given a prefixed checksum from
    an npm manifest.
    """
    if not checksum or '-' not in checksum:
        return {}

    algo, _, checksum = checksum.partition('-')
    # value is base64 encoded: we convert to hex
    checksum = base64.b64decode(checksum.encode('ascii')).hex()
    return {algo: checksum}


def compute_normalized_license(declared_license):
    """
    Return a normalized license expression string detected from a list of
    declared license items.
    """
    if not declared_license:
        return

    detected_licenses = []

    for declared in declared_license:
        if isinstance(declared, str):
            detected_license = models.compute_normalized_license(declared)
            if detected_license:
                detected_licenses.append(detected_license)

        elif isinstance(declared, dict):
            # 1. try detection on the value of type if not empty and keep this
            ltype = declared.get('type')
            via_type = models.compute_normalized_license(ltype)

            # 2. try detection on the value of url  if not empty and keep this
            url = declared.get('url')
            via_url = models.compute_normalized_license(url)

            if via_type:
                # The type should have precedence and any unknowns
                # in url should be ignored.
                # TODO: find a better way to detect unknown licenses
                if via_url in ('unknown', 'unknown-license-reference',):
                    via_url = None

            if via_type:
                if via_type == via_url:
                    detected_licenses.append(via_type)
                else:
                    if not via_url:
                        detected_licenses.append(via_type)
                    else:
                        combined_expression = combine_expressions([via_type, via_url])
                        detected_licenses.append(combined_expression)
            elif via_url:
                detected_licenses.append(via_url)

    if detected_licenses:
        return combine_expressions(detected_licenses)


def npm_homepage_url(namespace, name, registry='https://www.npmjs.com/package'):
    """
    Return an npm package registry homepage URL given a namespace, name,
    version and a base registry web interface URL.

    For example:
    >>> expected = 'https://www.npmjs.com/package/@invisionag/eslint-config-ivx'
    >>> assert npm_homepage_url('@invisionag', 'eslint-config-ivx') == expected

    >>> expected = 'https://www.npmjs.com/package/angular'
    >>> assert npm_homepage_url(None, 'angular') == expected

    >>> expected = 'https://www.npmjs.com/package/angular'
    >>> assert npm_homepage_url('', 'angular') == expected

    >>> expected = 'https://yarnpkg.com/en/package/angular'
    >>> assert npm_homepage_url('', 'angular', 'https://yarnpkg.com/en/package') == expected

    >>> expected = 'https://yarnpkg.com/en/package/@ang/angular'
    >>> assert npm_homepage_url('@ang', 'angular', 'https://yarnpkg.com/en/package') == expected

    >>> assert not npm_homepage_url(None, None)
    """
    if name:
        if namespace:
            ns_name = f'{namespace}/{name}'
        else:
            ns_name = name
        return f'{registry}/{ns_name}'


def npm_download_url(namespace, name, version, registry='https://registry.npmjs.org'):
    """
    Return an npm package tarball download URL given a namespace, name, version
    and a base registry URL.

    For example:
    >>> expected = 'https://registry.npmjs.org/@invisionag/eslint-config-ivx/-/eslint-config-ivx-0.1.4.tgz'
    >>> assert npm_download_url('@invisionag', 'eslint-config-ivx', '0.1.4') == expected

    >>> expected = 'https://registry.npmjs.org/angular/-/angular-1.6.6.tgz'
    >>> assert npm_download_url('', 'angular', '1.6.6') == expected

    >>> expected = 'https://registry.npmjs.org/angular/-/angular-1.6.6.tgz'
    >>> assert npm_download_url(None, 'angular', '1.6.6') == expected

    >>> assert not npm_download_url(None, None, None)
    """
    if name and version:
        if namespace:
            ns_name = f'{namespace}/{name}'
        else:
            ns_name = name
        return f'{registry}/{ns_name}/-/{name}-{version}.tgz'


def npm_api_url(namespace, name, version=None, registry='https://registry.npmjs.org'):
    """
    Return a package API data URL given a namespace, name, version and a base
    registry URL.

    Note that for scoped packages (with a namespace), the URL is not version
    specific but contains the data for all versions as the default behvior of
    the registries is to return nothing in this case. Special quoting rules are
    applied for scoped npms.

    For example:
    >>> result = npm_api_url('@invisionag', 'eslint-config-ivx', '0.1.4', 'https://registry.yarnpkg.com')
    >>> assert result == 'https://registry.yarnpkg.com/@invisionag%2feslint-config-ivx'

    >>> assert npm_api_url(None, 'angular', '1.6.6') == 'https://registry.npmjs.org/angular/1.6.6'

    >>> assert not npm_api_url(None, None, None)
    """
    if name:
        if namespace:
            # this is a legacy wart: older registries used to always encode this /
            # FIXME: do NOT encode and use plain / instead
            ns_name = '%2f'.join([namespace, name])
            # there is no version-specific URL for scoped packages
            version = ''
        else:
            ns_name = name

        if version:
            version = f'/{version}'
        else:
            version = ''

        return f'{registry}/{ns_name}{version}'


def is_scoped_package(name):
    """
    Return True if name contains a namespace.

    For example::
    >>> is_scoped_package('@angular')
    True
    >>> is_scoped_package('some@angular')
    False
    >>> is_scoped_package('linq')
    False
    >>> is_scoped_package('%40angular')
    True
    """
    return name.startswith(('@', '%40',))


def split_scoped_package_name(name):
    """
    Return a tuple of (namespace, name) given a package name.
    Namespace is the "scope" of a scoped package.
    / and @ can be url-quoted and will be unquoted.

    For example:
    >>> nsn = split_scoped_package_name('@linclark/pkg')
    >>> assert ('@linclark', 'pkg') == nsn, nsn
    >>> nsn = split_scoped_package_name('@linclark%2fpkg')
    >>> assert ('@linclark', 'pkg') == nsn, nsn
    >>> nsn = split_scoped_package_name('angular')
    >>> assert (None, 'angular') == nsn, nsn
    >>> nsn = split_scoped_package_name('%40angular%2fthat')
    >>> assert ('@angular', 'that') == nsn, nsn
    >>> nsn = split_scoped_package_name('%40angular')
    >>> assert ('@angular', None) == nsn, nsn
    >>> nsn = split_scoped_package_name('@angular')
    >>> assert ('@angular', None) == nsn, nsn
    >>> nsn = split_scoped_package_name('angular/')
    >>> assert (None, 'angular') == nsn, nsn
    >>> nsn = split_scoped_package_name('%2fangular%2f/ ')
    >>> assert (None, 'angular') == nsn, nsn
    """
    if not name:
        return None, None

    name = name and name.strip()
    if not name:
        return None, None

    # FIXME: this legacy percent encoding/decoding should no longer be needed
    name = name.replace('%40', '@').replace('%2f', '/').replace('%2F', '/')
    name = name.rstrip('@').strip('/').strip()
    if not name:
        return None, None

    # this should never happen: wee only have a scope.
    # TODO: raise an  exception?
    if is_scoped_package(name) and '/' not in name:
        return name, None

    ns, _, name = name.rpartition('/')
    ns = ns.strip() or None
    name = name.strip() or None
    return ns, name


def get_declared_licenses(license_object):
    """
    Return a list of declared licenses, either strings or dicts.
    """
    if not license_object:
        return []

    if isinstance(license_object, str):
        # current, up to date form
        return [license_object]

    declared_licenses = []
    if isinstance(license_object, dict):
        # old, deprecated forms
        """
         "license": {
            "type": "MIT",
            "url": "http://github.com/kriskowal/q/raw/master/LICENSE"
          }
        """
        declared_licenses.append(license_object)

    elif isinstance(license_object, list):
        # old, deprecated forms
        """
        "licenses": [{"type": "Apache License, Version 2.0",
                      "url": "http://www.apache.org/licenses/LICENSE-2.0" } ]
        or
        "licenses": ["MIT"],
        """
        declared_licenses.extend(license_object)
    return declared_licenses


def licenses_mapper(license, licenses, package):  # NOQA
    """
    Update package licensing and return package based on the `license` and
    `licenses` values found in a package.

    Licensing data structure has evolved over time and is a tad messy.
    https://docs.npmjs.com/files/package.json#license
    license(s) is either:
    - a string with:
     - an SPDX id or expression { "license" : "(ISC OR GPL-3.0)" }
     - some license name or id
     - "SEE LICENSE IN <filename>"
    - (Deprecated) an array or a list of arrays of type, url.
    -  "license": "UNLICENSED" means this is proprietary
    """
    declared_license = get_declared_licenses(license) or []
    declared_license.extend(get_declared_licenses(licenses)  or [])
    package.declared_license = declared_license
    return package


def party_mapper(party, package, party_type):
    """
    Update package parties with party of `party_type` and return package.
    https://docs.npmjs.com/files/package.json#people-fields-author-contributors
    """
    if isinstance(party, list):
        for auth in party:
            name, email, url = parse_person(auth)
            package.parties.append(models.Party(
                type=models.party_person,
                name=name,
                role=party_type,
                email=email,
                url=url))
    else:
        # a string or dict
        name, email, url = parse_person(party)
        package.parties.append(models.Party(
            type=models.party_person,
            name=name,
            role=party_type,
            email=email,
            url=url))

    return package


def bugs_mapper(bugs, package):
    """
    Update package bug tracker and support email and return package.
    https://docs.npmjs.com/files/package.json#bugs
    The url to your project's issue tracker and / or the email address to
    which issues should be reported.
    { "url" : "https://github.com/owner/project/issues"
    , "email" : "project@hostname.com"
    }
    You can specify either one or both values. If you want to provide only a
    url, you can specify the value for "bugs" as a simple string instead of an
    object.
    """
    if isinstance(bugs, str):
        package.bug_tracking_url = bugs
    elif isinstance(bugs, dict):
        # we ignore the bugs email for now
        package.bug_tracking_url = bugs.get('url')
    return package


def vcs_repository_mapper(repo, package, vcs_revision=None):
    """
    https://docs.npmjs.com/files/package.json#repository
    "repository" :
      { "type" : "git"
      , "url" : "https://github.com/npm/npm.git"
      }
    "repository" :
      { "type" : "svn"
      , "url" : "https://v8.googlecode.com/svn/trunk/"
      }
    """
    if not repo:
        return package

    if isinstance(repo, list):
        # There is a case where we can have a list with a single element
        repo = repo[0]

    vcs_tool = ''
    vcs_repository = ''

    if isinstance(repo, str):
        vcs_repository = normalize_vcs_url(repo)

    elif isinstance(repo, dict):
        repo_url = normalize_vcs_url(repo.get('url'))
        if repo_url:
            vcs_tool = repo.get('type') or 'git'
            # remove vcs_tool string if repo_url already contains it
            if repo_url.startswith(vcs_tool):
                vcs_tool = ''
            vcs_repository = repo_url

    if vcs_repository:
        if vcs_tool:
            vcs_url = '{}+{}'.format(vcs_tool, vcs_repository)
        else:
            vcs_url = vcs_repository

        if vcs_revision:
            vcs_url += '@' + vcs_revision
        package.vcs_url = vcs_url
    return package


def dist_mapper(dist, package):
    """
    Only present in some package.json forms (as installed or from a
    registry). Not documented.
    "dist": {
      "integrity: "sha512-VmqXvL6aSOb+rmswek7prvdFKsFbfMshcRRi07SdFyDqgG6uXsP276NkPTcrD0DiwVQ8rfnCUP8S90x0OD+2gQ==",
      "shasum": "a124386bce4a90506f28ad4b1d1a804a17baaf32",
      "dnl_url": "http://registry.npmjs.org/npm/-/npm-2.13.5.tgz"
      },
    """
    if not isinstance(dist, dict):
        return

    integrity = dist.get('integrity')
    for algo, hexsum in get_algo_hexsum(integrity).items():
        if hasattr(package, algo):
            setattr(package, algo, hexsum)

    package.sha1 = dist.get('shasum') or None

    dnl_url = dist.get('dnl_url')
    if not dnl_url:
        # Only add a synthetic download URL if there is none from the dist mapping.
        dnl_url = npm_download_url(package.namespace, package.name, package.version)
    package.download_url = dnl_url.strip()

    return package


def bundle_deps_mapper(bundle_deps, package):
    """
    https://docs.npmjs.com/files/package.json#bundleddependencies
        "This defines an array of package names that will be bundled
        when publishing the package."
    """
    for bdep in (bundle_deps or []):
        bdep = bdep and bdep.strip()
        if not bdep:
            continue

        ns, name = split_scoped_package_name(bdep)
        purl = models.PackageURL(type='npm', namespace=ns, name=name)

        dep = models.DependentPackage(purl=purl.to_string(),
            scope='bundledDependencies', is_runtime=True,
        )
        package.dependencies.append(dep)

    return package


def deps_mapper(deps, package, field_name):
    """
    Handle deps such as dependencies, devDependencies, peerDependencies, optionalDependencies
    return a tuple of (dep type, list of deps)
    https://docs.npmjs.com/files/package.json#dependencies
    https://docs.npmjs.com/files/package.json#peerdependencies
    https://docs.npmjs.com/files/package.json#devdependencies
    https://docs.npmjs.com/files/package.json#optionaldependencies
    """
    npm_dependency_scopes_attributes = {
        'dependencies': dict(is_runtime=True, is_optional=False),
        'devDependencies': dict(is_runtime=False, is_optional=True),
        'peerDependencies': dict(is_runtime=True, is_optional=False),
        'optionalDependencies': dict(is_runtime=True, is_optional=True),
    }
    dependencies = package.dependencies

    deps_by_name = {}
    if field_name == 'optionalDependencies':
        # optionalDependencies override the dependencies with the same name
        # so we build a map of name->dep object for use later
        for d in dependencies:
            if d.scope != 'dependencies':
                continue
            purl = PackageURL.from_string(d.purl)
            npm_name = purl.name
            if purl.namespace:
                npm_name = '/'.join([purl.namespace, purl.name])
            deps_by_name[npm_name] = d

    for fqname, requirement in deps.items():
        ns, name = split_scoped_package_name(fqname)
        if not name:
            continue
        purl = PackageURL(type='npm', namespace=ns, name=name).to_string()

        # optionalDependencies override the dependencies with the same name
        # https://docs.npmjs.com/files/package.json#optionaldependencies
        # therefore we update/override the dependency of the same name
        overridable = deps_by_name.get(fqname)

        if overridable and field_name == 'optionalDependencies':
            overridable.purl = purl
            overridable.is_optional = True
            overridable.scope = field_name
        else:
            dependency_attributes = npm_dependency_scopes_attributes.get(field_name, dict())
            dep = models.DependentPackage(
                purl=purl,
                scope=field_name,
                extracted_requirement=requirement,
                **dependency_attributes
            )
            dependencies.append(dep)

    return package


person_parser = re.compile(
    r'^(?P<name>[^\(<]+)'
    r'\s?'
    r'(?P<email><([^>]+)>)?'
    r'\s?'
    r'(?P<url>\([^\)]+\))?$'
).match

person_parser_no_name = re.compile(
    r'(?P<email><([^>]+)>)?'
    r'\s?'
    r'(?P<url>\([^\)]+\))?$'
).match


class NpmInvalidPerson(Exception):
    pass


def parse_person(person):
    """
    https://docs.npmjs.com/files/package.json#people-fields-author-contributors
    A "person" is an object with a "name" field and optionally "url" and "email".

    Return a name, email, url tuple for a person object
    A person can be in the form:
      "author": {
        "name": "Isaac Z. Schlueter",
        "email": "i@izs.me",
        "url": "http://blog.izs.me"
      },
    or in the form:
      "author": "Isaac Z. Schlueter <i@izs.me> (http://blog.izs.me)",

    Both forms are equivalent.

    For example:
    >>> author = {
    ...   "name": "Isaac Z. Schlueter",
    ...   "email": "i@izs.me",
    ...   "url": "http://blog.izs.me"
    ... }
    >>> p = parse_person(author)
    >>> assert p == (u'Isaac Z. Schlueter', u'i@izs.me', u'http://blog.izs.me')
    >>> p = parse_person('Barney Rubble <b@rubble.com> (http://barnyrubble.tumblr.com/)')
    >>> assert p == (u'Barney Rubble', u'b@rubble.com', u'http://barnyrubble.tumblr.com/')
    >>> p = parse_person('Barney Rubble <none> (none)')
    >>> assert p == (u'Barney Rubble', None, None)
    >>> p = parse_person('Barney Rubble ')
    >>> assert p == (u'Barney Rubble', None, None)
    >>> author = {
    ...   "name": "Isaac Z. Schlueter",
    ...   "email": ["i@izs.me", "<jo2@todo.com> "],
    ...   "url": "http://blog.izs.me"
    ... }
    >>> p = parse_person(author)
    >>> assert p == (u'Isaac Z. Schlueter', u'i@izs.me\\njo2@todo.com', u'http://blog.izs.me')
    >>> p = parse_person('<b@rubble.com> (http://barnyrubble.tumblr.com/)')
    >>> assert p == (None, u'b@rubble.com', u'http://barnyrubble.tumblr.com/')
    """
    # TODO: detect if this is a person name or a company name e.g. the type?

    name = None
    email = None
    url = None

    if isinstance(person, str):
        parsed = person_parser(person)
        if not parsed:
            parsed = person_parser_no_name(person)
            if not parsed:
                return person, None, None
            else:
                name = None
                email = parsed.group('email')
                url = parsed.group('url')
        else:
            name = parsed.group('name')
            email = parsed.group('email')
            url = parsed.group('url')

    elif isinstance(person, dict):
        # ensure we have our three values
        name = person.get('name')
        email = person.get('email')
        url = person.get('url')

    else:
        return None, None, None

    if name:
        if isinstance(name, str):
            name = name.strip()
            if name.lower() == 'none':
                name = None
        else:
            name = None
    name = name or None

    if email:
        if isinstance(email, list):
            # legacy weirdness
            email = [e.strip('<> ') for e in email if e and e.strip()]
            email = '\n'.join([e.strip() for e in email
                               if e.strip() and e.strip().lower() != 'none'])
        if isinstance(email, str):
            email = email.strip('<> ').strip()
            if email.lower() == 'none':
                email = None
        else:
            email = None
    email = email or None

    if url:
        if isinstance(url, list):
            # legacy weirdness
            url = [u.strip('() ') for u in email if u and u.strip()]
            url = '\n'.join([u.strip() for u in url
                               if u.strip() and u.strip().lower() != 'none'])
        if isinstance(url, str):
            url = url.strip('() ').strip()
            if url.lower() == 'none':
                url = None
        else:
            url = None
    url = url or None

    return name, email, url


def keywords_mapper(keywords, package):
    """
    Update package keywords and return package.
    This is supposed to be an array of strings, but sometimes this is a string.
    https://docs.npmjs.com/files/package.json#keywords
    """
    if isinstance(keywords, str):
        if ',' in keywords:
            keywords = [k.strip() for k in keywords.split(',') if k.strip()]
        else:
            keywords = [keywords]

    package.keywords = keywords
    return package
