#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

import itertools
import operator
import os
import re
import subprocess
import time

import attr
import packaging_dists
import pip_compatibility_tags
import pip_wheel
import requests
import saneyaml
from packaging.utils import canonicalize_name

"""
Utilities to build scancode releases and manage Python thirparty libraries.

- create and update locked/pinned requirement files (optionally with hashes)

- build individual wheels for all supported OSes and Python combos and upload
  them all to a PyPI-like repository.

- use a public alternative PyPI-like repository to keep all dependent packages
  as pre-built wheels for each supported Python/OS combo, their source code and
  ABOUT and LICENSE files.

- build application release archives as plaform-specific tarballs with bundled
  pre-built dependencies.

"""

# Supported environments
PYTHON_VERSIONS = '36', '37', '38', '39'

PLATFORMS = {
    'linux': [
        'linux_x86_64',
        'manylinux1_x86_64',
        'manylinux2014_x86_64',
        'manylinux2010_x86_64',
    ],
    'macosx': [
        'macosx_10_6_intel', 'macosx_10_6_intel_x86_64', 'macosx_10_6_x86_64',
        'macosx_10_9_intel', 'macosx_10_9_intel_x86_64', 'macosx_10_9_x86_64',
        'macosx_10_10_intel', 'macosx_10_10_intel_x86_64', 'macosx_10_10_x86_64',
        'macosx_10_11_intel', 'macosx_10_11_intel_x86_64', 'macosx_10_11_x86_64',
        'macosx_10_12_intel', 'macosx_10_12_intel_x86_64', 'macosx_10_12_x86_64',
        'macosx_10_13_intel', 'macosx_10_13_intel_x86_64', 'macosx_10_13_x86_64',
    ],
    'windows': [
        'win_amd64',
    ],
}

THIRDPARTY_DIR = 'thirdparty'

BASE_URL = 'https://github.com'
LINKS_URL = 'https://github.com/nexB/thirdparty-packages/releases/pypi'
PREFIX = '/nexB/thirdparty-packages/releases/download/'

EXTENSIONS_APP = '.pyz',
EXTENSIONS_INSTALLABLE = '.whl', '.tar.gz', '.tar.bz2', '.zip',
EXTENSIONS_ABOUT = '.ABOUT', '.LICENSE', '.NOTICE',
EXTENSIONS = EXTENSIONS_INSTALLABLE + EXTENSIONS_ABOUT + EXTENSIONS_APP


@attr.attributes
class Package:
    """
    A Python package with its "distributions", e.g. wheels and source
    distribution , ABOUT files and licenses or notices.
    """
    name = attr.ib(
        type=str,
        metadata=dict(help='Python package name, lowercase and normalized.'),
    )
    version = attr.ib(
        type=str,
        metadata=dict(help='Python package version.'),
    )

    sdist = attr.ib(
        type=str,
        default='',
        metadata=dict(help='packaging_dists.Sdist depicting a source distribution}'),
    )

    wheels = attr.ib(
        type=list,
        default=attr.Factory(list),
        metadata=dict(help='List of packaging_dists.Wheel'),
    )

    def get_supported_wheels(self, environment):
        """
        Yield all Wheel of this Package supported and compatible with the
        Environment `environment`.
        """
        if not environment:
            for wheel in self.wheels:
                yield wheel

        envt_tags = set(pip_compatibility_tags.get_supported(
            version=environment.python_version,
            platforms=environment.platforms,
            impl=environment.implementation,
            abis=[environment.abi],
        ))

        for wheel in self.wheels:
            pwhl = pip_wheel.Wheel(wheel.file_name)
            if pwhl.supported(envt_tags):
                yield wheel

    @classmethod
    def from_dists(cls, dists):
        """
        Return a new Package built from an iterable of Distribution objects all
        for the same package name and version.
        For example:
        >>> import packaging_dists as pd
        >>> from packaging.version import Version
        >>> w1 = pd.Wheel(project='bitarray', version=Version('0.8.1'), build='',
        ...        python='cp36', abi='cp36m', platform='linux_x86_64')
        >>> w2 = pd.Wheel(project='bitarray', version=Version('0.8.1'), build='',
        ...         python='cp36', abi='cp36m', platform='macosx_10_9_x86_64.macosx_10_10_x86_64')
        >>> sd = pd.Sdist(project='bitarray', version=Version('0.8.1'))
        >>> package = Package.from_dists(dists=[w1, w2, sd])
        >>> assert package.name == 'bitarray'
        >>> assert package.version == '0.8.1'
        >>> assert package.sdist == sd
        >>> assert package.wheels == [w1, w2]
        """
        dists = list(dists)
        if not dists:
            return
        base = dists[0]
        package = Package(name=base.project, version=str(base.version))
        for dist in dists:
            if isinstance(dist, packaging_dists.Sdist):
                package.sdist = dist
            elif isinstance(dist, packaging_dists.Wheel):
                package.wheels.append(dist)
            else:
                raise Exception(f'Unknown distribution type: {dist}')
        return package

    @classmethod
    def from_paths_or_urls(cls, paths_or_urls):
        """
        Yield Packages built from a list of of paths or URLs.
        """
        key = operator.attrgetter('project', 'version')
        dists = sorted(get_distributions(paths_or_urls), key=key)
        for _project, package_dists in itertools.groupby(dists, key=key):
            yield Package.from_dists(package_dists)


def get_distributions(paths_or_urls):
    """
    Return a list of packaging_dists.Distribution given a list of
    `paths_or_urls` to wheels or source distributions.

    Each Distribution receives two extra attributes:
        - the path_or_url it was created from
        - its file_name

    For example:
    >>> import packaging_dists as pd
    >>> from packaging.version import Version
    >>> paths_or_urls ='''
    ...     bitarray-0.8.1-cp36-cp36m-linux_x86_64.whl
    ...     bitarray-0.8.1-cp36-cp36m-macosx_10_9_x86_64.macosx_10_10_x86_64.whl
    ...     bitarray-0.8.1-cp36-cp36m-win_amd64.whl
    ...     bitarray-0.8.1.tar.gz
    ...     bitarray-0.8.1.tar.gz.ABOUT bit.LICENSE'''.split()
    >>> result = list(get_distributions(paths_or_urls))
    >>> expected = [
    ...     pd.Wheel(project='bitarray', version=Version('0.8.1'), build='',
    ...        python='cp36', abi='cp36m', platform='linux_x86_64'),
    ...     pd.Wheel(project='bitarray', version=Version('0.8.1'), build='',
    ...         python='cp36', abi='cp36m', platform='macosx_10_9_x86_64.macosx_10_10_x86_64'),
    ...     pd.Wheel(project='bitarray', version=Version('0.8.1'), build='',
    ...         python='cp36', abi='cp36m', platform='win_amd64'),
    ...     pd.Sdist(project='bitarray', version=Version('0.8.1'))
    ... ]
    >>> assert expected == result
    """
    installable = [f for f in paths_or_urls if f .endswith(EXTENSIONS_INSTALLABLE)]
    for path_or_url in installable:
        file_name = get_file_name(path_or_url)
        try:
            dist = packaging_dists.parse(file_name)
        except packaging_dists.InvalidDistribution:
            pass
        if dist:
            dist.path_or_url = path_or_url
            dist.file_name = file_name
            yield dist


@attr.attributes(auto_attribs=True)
class Environment:
    """
    An Environment describes a target installation environment with its
    supported Python version, ABI, platform, implementation and related
    attributes. We use these to pass as `pip download` options and force
    fetching only the subset of packages that match these Environment
    constraints as opposed to the current running Python constraints.
    """
    python_version: str
    implementation: str
    abi: str
    platforms: list

    @classmethod
    def from_pyplat(cls, python_version, platforms):
        return cls(
            python_version=python_version,
            implementation='cp',
            abi=f'cp{python_version}m',
            platforms=platforms,
        )

    def pip_cli_options(self):
        """
        Return a list of command line options for this environment.
        """
        options = [
            '--python-version', self.python_version,
            '--implementation', self.implementation,
            '--abi', self.abi,
        ]
        for platform in self.platforms:
            options.extend(['--platform', platform])
        return options

################################################################################
#
# main entry point
#
################################################################################


def fetch_dependencies(
        environment=None,
        requirement='requirements.txt',
        dest_dir=THIRDPARTY_DIR,
        paths_or_urls=(),
        include_source=False,
):
    """
    Download all dependencies for the `environment` Enviromnent constraints in
    the `requirement` requirements file or package requirement into `dest_dir`
    directory. Use direct downloads to achieve this (not pip download).

    Use only the packages found in the `links` list of links or paths ignoring.

    If the provided `environment` is None then the current Python interpreter
    environment is used implicitly.

    These items are fetched:
        - the binary wheels
        - the source distribution sdist if `include_source` is True.
    """
    required_name_versions = get_pinned_requirements(requirement)
    available_packages = {
        (p.name, p.version): p for p in Package.from_paths_or_urls(paths_or_urls)
    }
    for name_version in required_name_versions:
        package = available_packages.get(name_version)

        if not package:
            name, version = name_version
            raise Exception(f'Missing package in links: {name}=={version}', available_packages)

        for wheel in package.get_supported_wheels(environment):
            fetch_and_save_path_or_url(
                file_name=wheel.file_name,
                dest_dir=dest_dir,
                path_or_url=wheel.path_or_url,
                as_text=False,
            )

        if include_source:
            if not package.sdist:
                name, version = name_version
                msg = f'Missing sdist in links: {name}=={version}'
                # raise Exception(msg)
                print(msg)
            else:
                fetch_and_save_path_or_url(
                    file_name=package.sdist.file_name,
                    dest_dir=dest_dir,
                    path_or_url=package.sdist.path_or_url,
                    as_text=False,
                )

################################################################################
#
# Basic file and URL-based operation usimg a cache
#
################################################################################


@attr.s(auto_attribs=True)
class Cache:
    """
    A simple cache for files based only on a file_name presence.
    """

    directory = '.cache/thirdparty'

    def __attrs_post_init__(self):
        os.makedirs(self.directory, exist_ok=True)

    def clear(self):
        import shutil
        shutil.rmtree(self.directory)

    def get(self, path_or_url, as_text=True):
        """
        Get a file from a `path_or_url` through the cache.
        `path_or_url` can be a path or a URL to a file.
        """
        file_name = get_file_name(path_or_url)
        cached = os.path.join(self.directory, file_name)
        if not os.path.exists(cached):
            print(f'Fetching {path_or_url}')
            content = get_file_content(path_or_url=path_or_url, as_text=as_text)
            wmode = 'w' if as_text else 'wb'
            with open(cached, wmode) as fo:
                fo.write(content)
            return content
        else:
            return get_local_file_content(path=cached, as_text=as_text)

    def put(self, file_name, content):
        """
        Put in the cache the `content` of `file_name`.
        """
        cached = os.path.join(self.directory, file_name)
        wmode = 'wb' if isinstance(content, bytes) else 'w'
        with open(cached, wmode) as fo:
            fo.write(content)


def fetch_and_save_path_or_url(file_name, dest_dir, path_or_url, as_text=True, cache=Cache()):
    """
    Return the content from fetching the `file_name` file name at URL or path
    and save to `dest_dir`. Raise an Exception on errors. Treats the content as
    text if as_text is True otherwise as treat as binary.
    Use the provided file cache
    """
    output = os.path.join(dest_dir, file_name)
    content = cache.get(path_or_url=path_or_url, as_text=as_text)
    wmode = 'w' if as_text else 'wb'
    with open(output, wmode) as fo:
        fo.write(content)
    return content


def get_file_content(path_or_url, as_text=True):
    """
    Fetch and return the content at `path_or_url` from either a local path or a
    remote URL. Return the content as bytes is `as_text` is False.
    """
    if path_or_url.startswith('file://'):
        return get_local_file_content(path=path_or_url, as_text=as_text)
    elif path_or_url.startswith('https://'):
        return get_remote_file_content(url=path_or_url, as_text=as_text)
    else:
        raise Exception(f'Unsupported URL scheme: {path_or_url}')


def get_local_file_content(path, as_text=True):
    """
    Return the content at `url` as text. Return the content as bytes is
    `as_text` is False.
    """
    if path.startswith('file://'):
        path = path[7:]

    mode = 'r' if as_text else 'rb'
    with open(path, mode) as fo:
        return fo.read()


def get_remote_file_content(url, as_text=True, _delay=0):
    """
    Fetch and return the content at `url` as text. Return the content as bytes
    is `as_text` is False. Retries multiple times to fetch if there is a HTTP
    429 throttling response and this with an increasing delay.
    """
    time.sleep(_delay)
    response = requests.get(url)
    status = response.status_code
    if status != requests.codes.ok:  # NOQA
        if status == 429 and _delay < 20:
            # too many requests: start some exponential delay
            increased_delay = (_delay * 2) or 1
            return get_remote_file_content(url, as_text=True, _delay=increased_delay)
        else:
            raise Exception('Failed HTTP request for %(url)r: %(status)r' % locals())
    return response.text if as_text else response.content

################################################################################
#
# Function to handle remote or local repo used to "find-links"
#
################################################################################


def get_link_for_filename(file_name, paths_or_urls):
    """
    Return a link for `file_name` found in the `links` list of URLs or paths. Raise an
    exception if no link is found or if there are more than one link for that
    file name.
    """
    path_or_url = [l for l in paths_or_urls if l.endswith(f'/{file_name}')]
    if not path_or_url:
        raise Exception(f'Missing link to file: {file_name}')
    if not len(path_or_url) == 1:
        raise Exception(f'Multiple links to file: {file_name}: \n' + '\n'.join(path_or_url))
    return path_or_url[0]


def get_paths_or_urls(links_url):
    if links_url.startswith('https:'):
        paths_or_urls = find_links_from_url(links_url)
    else:
        paths_or_urls = find_links_from_dir(links_url)
    return paths_or_urls


def find_links_from_dir(directory=THIRDPARTY_DIR, extensions=EXTENSIONS):
    """
    Return a list of path to files in `directory` for any file that ends with
    any of the extension in the list of `extensions` strings.
    """
    base = os.path.abspath(directory)
    files = [os.path.join(base, f) for f in os.listdir(base) if f.endswith(extensions)]
    return files


def find_links_from_url(links_url=LINKS_URL, base_url=BASE_URL, prefix=PREFIX, extensions=EXTENSIONS):
    """
    Return a list of download link URLs found in the HTML page at `links_url`
    URL that starts with the `prefix` string and ends with any of the extension
    in the list of `extensions` strings. Use the `base_url` to prefix the links.
    """
    text = get_remote_file_content(links_url)
    hrefs = find_hrefs(text, prefix=prefix, extensions=extensions)
    links = [f'{base_url}{lnk}' for lnk in hrefs]
    return links


def find_hrefs(text, prefix=PREFIX, extensions=EXTENSIONS):
    """
    Return all the links found in the HTML page `text` that start with the
    `prefix` string and end with any of the extension in the list of
    `extensions` strings.
    """
    get_links = re.compile('href="([^"]+)"').findall
    links = get_links(text)
    return [l for l in links if l.startswith(prefix) and l.endswith(extensions)]

################################################################################
#
# Requirements processing
#
################################################################################


def get_pinned_requirements(requirement='requirements.txt'):
    """
    Yield package (name, version) tuples for each requirement in a `requirement`
    file. Every requirement versions must be pinned exactly
    """
    with open(requirement) as reqs:
        for req in reqs:
            req = req.strip()
            if not req or req.startswith('#'):
                continue
            if '==' not in req:
                raise Exception(f'Requirement version is not pinned: {req}')
            name, _, version = req.partition('==')
            name = canonicalize_name(name.strip())
            yield name, version.strip()


def lock_requirements(requirement='requirements.txt'):
    """
    Freeze and lock current requirements and save this to the `requirement`
    requirements file.
    """
    options = [
        'pip', 'freeze',
        '--exclude-editable',
        '--all',
        '--requirement', requirement,
    ]
    call(options)


def upgrade_requirements(package_name, new_version, requirement='requirements.txt'):
    """
    Upgrade or add `package_name` with `new_version` in the `requirement`
    requirements file. Write back requirements sorted.
    """
    name_versions = list(get_pinned_requirements(requirement))
    package_name = canonicalize_name(package_name)

    updated_nvs = []

    has_package = False
    for name, version in name_versions:
        if name == package_name:
            version = new_version
            has_package = True
        updated_nvs.append((name, version,))

    if not has_package:
        updated_nvs.append((package_name, package_name,))

    nvs = (f'{name}=={version}\n' for name, version in sorted(updated_nvs))
    with open(requirement, 'w') as fo:
        fo.writelines(nvs)


def get_setup_cfg_requirements(setup_cfg, extra=None):
    """
    Return a mapping of {type of requirement: list of requirements lines}
     extracted from a `setup_cfg` file *_requires sections.
    """
    import configparser
    config = configparser.ConfigParser()
    with open(setup_cfg) as cfg:
        config.read(cfg)

    requirements = {}
    install_requires = config.get('options', 'install_requires', fallback='')
    requirements['install_requires'] = parse_requires(install_requires)

    setup_requires = config.get('options', 'setup_requires', fallback='')
    requirements['setup_requires'] = parse_requires(setup_requires)

    extras_require = config.get('options', 'extras_require', fallback=[])
    for extra in extras_require:
        exreq = config.get('options.extras_require', extra, fallback='')
        requirements[f'extras_require:{extra}'] = parse_requires(exreq)

    return requirements


def parse_requires(requires):
    """
    Return a list of requirement lines extracted from the `requires` text from
    setup.cfg *_requires sections.
    """
    requires = (c.strip() for c in requires.splitlines())
    requires = [c for c in requires if c]
    if not requires:
        return []

    requires = [''.join(r.split()) for r in requires if r and r.strip()]
    return sorted(requires)

################################################################################
#
# ABOUT and license files functions
#
################################################################################


def fetch_and_save_using_paths_or_urls(file_name, dest_dir, paths_or_urls, as_text=True):
    """
    Return the content from fetching the `file_name` file name found in the
    `paths_or_urls` list of URLs or paths and save to `dest_dir`. Raise an
    Exception on errors. Treats the content as text if `as_text` is True otherwise
    as binary.
    """
    path_or_url = get_link_for_filename(
        file_name=file_name,
        paths_or_urls=paths_or_urls,
    )

    return fetch_and_save_path_or_url(
        file_name=file_name,
        dest_dir=dest_dir,
        path_or_url=path_or_url,
        as_text=as_text,
    )


def fetch_abouts_and_licenses(dest_dir, paths_or_urls, strict=False):
    """
    Download to `dest_dir` all the .ABOUT files and their corresponding .LICENSE
    and .NOTICE files for all the files in `dest_dir` that should have an .ABOUT fdocumentation
    using URLs or path from the `paths_or_urls` list.

    Documentable files (typically archives, sdists, wheels, etc.) are assumed to
    have a corresponding .ABOUT file named <archive_file_name>.ABOUT.

    If strict is True, an Exception is raised if any ABOUT, LICENSE or NOTICE
    file is missing from paths_or_urls or cannot be downloaded.
    """
    # these are the files that should have a matching ABOUT file
    aboutables = [fn for fn in os.listdir(dest_dir)
        if not fn.endswith(EXTENSIONS_ABOUT)
    ]

    errors = []
    for aboutable in aboutables:
        about_file = f'{aboutable}.ABOUT'
        try:
            about_url = get_link_for_filename(
                file_name=about_file,
                paths_or_urls=paths_or_urls,
            )
            about_content = fetch_and_save_path_or_url(
                file_name=about_file,
                dest_dir=dest_dir,
                path_or_url=about_url,
                as_text=True,
            )

        except Exception as e:
            errors.append(str(e))

        for lic_file in get_license_and_notice_file_names(about_content):
            try:

                lic_url = get_link_for_filename(
                    file_name=lic_file,
                    paths_or_urls=paths_or_urls,
                )

                _lic_content = fetch_and_save_path_or_url(
                    file_name=lic_file,
                    dest_dir=dest_dir,
                    path_or_url=lic_url,
                    as_text=True,
                )
            except Exception as e:
                errors.append(str(e))
                continue
    if errors:
        msg = '\n'.join(errors)
        if strict:
            raise Exception(msg)
        else:
            print(msg)


def get_license_and_notice_file_names(about_content):
    """
    Return a list of license and notice file names found in the `about_content`
    YAML data string loaded from an .ABOUT file.
    """
    about_data = saneyaml.load(about_content)
    # collect all the license and notice files
    # - first explicitly listed as licenses.file
    licenses = about_data.get('licenses', [])
    license_files = [l.get('file') for l in licenses]
    # - then implied by the license exprssion
    license_expression = about_data.get('license_expression', '')
    expression_files = [f'{l}.LICENSE' for l in license_keys(license_expression)]
    notice_file = about_data.get('notice_file')
    license_files = license_files + expression_files + [notice_file]
    return sorted(set([f for f in license_files if f]))


def license_keys(license_expression):
    """
    Return a list of license keys from a `license_expression` string.
    """
    cleaned = (license_expression
        .lower()
        .replace('(', ' ')
        .replace(')', ' ')
        .replace(' and ', ' ')
        .replace(' or ', ' ')
        .replace(' with ', ' ')
    )
    return cleaned.split()

################################################################################
#
# pip-based functions running pip as if called from the command line
#
################################################################################


def call(args):
    """
    Call args in a subprocess and display output on the fly.
    Return or raise stdout, stderr, returncode
    """

    with subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding='utf-8'
    ) as process:

        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            print(line.rstrip(), flush=True)

        stdout, stderr = process.communicate()
        returncode = process.returncode
        if returncode == 0:
            return stdout, stderr, returncode
        else:
            raise Exception(stdout, stderr, returncode)


def fetch_dependencies_using_pip(
        environment=None,
        requirement='requirements.txt',
        dest_dir=THIRDPARTY_DIR,
        links_url=LINKS_URL,
):
    """
    Download all dependencies for the `environment` Enviromnent constraints in
    the `requirement` requirements file or package requirement into `dest_dir`
    directory.

    Use only the packages found in the `links_url` HTML page ignoring PyPI
    packages unless `links_url` is None or empty in which case we use instead
    the public PyPI packages.

    If the provided `environment` is None then the current Python interpreter
    environment is used implicitly.

    These items are fetched:
        - binary wheels
    """

    options = [
        'pip', 'download',
        '--requirement', requirement,
        '--dest', dest_dir,
        '--only-binary=:all:',
        '--no-deps',
    ]

    if links_url:
        find_link = [
            '--no-index',
            '--find-links', links_url,
        ]
        options += find_link

    if environment:
        options += environment.pip_cli_options()

    try:
        call(options)
    except:
        print('Failed to run:')
        print(' '.join(options))
        raise


def fetch_dependencies_from_pypi_using_pip(
    environment=None,
    requirement='requirements.txt',
    dest_dir=THIRDPARTY_DIR,
):
    """
    Download all dependencies for the `environment` Enviromnent constraints in
    the `requirement` requirements file or package requirement into `dest_dir`
    directory using packages from PyPI.

    These items are fetched:
        - binary wheels
        - source distributions
    """
    fetch_dependencies_using_pip(
        environment=environment,
        requirement=requirement,
        dest_dir=dest_dir,
        links_url=None,
    )


def fetch_dependency_sources_using_pip(
        requirement='requirements.txt',
        dest_dir=THIRDPARTY_DIR,
        links_url=LINKS_URL,
):
    """
    Download all dependency source distributions for the `environment`
    Enviromnent constraints in the `requirement` requirements file or package
    requirement into `dest_dir` directory.

    Use only the source packages found in the `links_url` HTML page ignoring
    PyPI packages unless `links_url` is None or empty in which case we use
    instead the public PyPI packages.

    These items are fetched:
        - source distributions
    """

    options = [
        'pip', 'download',
        '--requirement', requirement,
        '--dest', dest_dir,
        '--no-binary=:all:'
        '--no-deps',
    ] + [
        # temporary workaround
        '--only-binary=extractcode-7z',
        '--only-binary=extractcode-libarchive',
        '--only-binary=typecode-libmagic',
    ]

    if links_url:
        options += [
            '--no-index',
            '--find-links', links_url,
        ]

    try:
        call(options)
    except:
        print('Failed to run:')
        print(' '.join(options))
        raise

################################################################################
#
# misc utilities
#
################################################################################


def get_file_name(path_or_url):
    return os.path.basename(path_or_url.strip('/'))

