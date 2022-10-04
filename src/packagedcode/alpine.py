#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#
import base64
import codecs
import email
import posixpath
import re
from functools import partial
from datetime import datetime
from os import path
from pathlib import Path

import attr
from license_expression import LicenseSymbolLike
from license_expression import Licensing
from packageurl import PackageURL

from packagedcode import bashparse
from packagedcode import models
from packagedcode.utils import combine_expressions
from packagedcode.utils import get_ancestor
from textcode.analysis import as_unicode


# TODO: implement me! See parse_pkginfo
class AlpineApkArchiveHandler(models.DatafileHandler):
    # NOTE that Android .apk are zip and Alpine .apk tar gzipped tarball
    datasource_id = 'alpine_apk_archive'
    path_patterns = ('*.apk',)
    filetypes = ('gzip compressed data',)
    default_package_type = 'alpine'
    description = 'Alpine Linux .apk package archive'
    documentation_url = 'https://wiki.alpinelinux.org/wiki/Alpine_package_format'

    @classmethod
    def compute_normalized_license(cls, package):
        _declared, detected = detect_declared_license(package.declared_license)
        return detected


class AlpineInstalledDatabaseHandler(models.DatafileHandler):
    datasource_id = 'alpine_installed_db'
    path_patterns = ('*lib/apk/db/installed',)
    default_package_type = 'alpine'
    description = 'Alpine Linux installed package database'

    @classmethod
    def parse(cls, location):
        yield from parse_alpine_installed_db(
            location=location,
            datasource_id=cls.datasource_id,
            package_type=cls.default_package_type,
        )

    @classmethod
    def compute_normalized_license(cls, package):
        _declared, detected = detect_declared_license(package.declared_license)
        return detected

    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder):
        # get the root resource of the rootfs
        levels_up = len('lib/apk/db/installed'.split('/'))
        root_resource = get_ancestor(
            levels_up=levels_up,
            resource=resource,
            codebase=codebase,
        )

        package = models.Package.from_package_data(
            package_data=package_data,
            datafile_path=resource.path,
        )
        package_uid = package.package_uid

        package.license_expression = cls.compute_normalized_license(package)

        root_path = Path(root_resource.path)
        # a file ref extends from the root of the filesystem
        file_references_by_path = {
            str(root_path / ref.path): ref
            for ref in package.file_references
        }

        resources = []
        for res in root_resource.walk(codebase):
            ref = file_references_by_path.get(res.path)
            if not ref:
                continue

            # path is found and processed: remove it, so we can check if we
            # found all of them
            del file_references_by_path[res.path]
            resources.append(res)

        # if we have left over file references, add these to extra data
        if file_references_by_path:
            missing = sorted(file_references_by_path.values(), key=lambda r:r.path)
            package.extra_data['missing_file_references'] = missing

        yield package
        for res in resources:
            package_adder(package_uid, res, codebase)
            yield res

        dependent_packages = package_data.dependencies
        if dependent_packages:
            yield from models.Dependency.from_dependent_packages(
                dependent_packages=dependent_packages,
                datafile_path=resource.path,
                datasource_id=package_data.datasource_id,
                package_uid=package_uid,
            )


class AlpineApkbuildHandler(models.DatafileHandler):
    datasource_id = 'alpine_apkbuild'
    path_patterns = ('*APKBUILD',)
    default_package_type = 'alpine'
    description = 'Alpine Linux APKBUILD package script'
    documentation_url = 'https://wiki.alpinelinux.org/wiki/APKBUILD_Reference'

    @classmethod
    def parse(cls, location):
        parsed = parse_apkbuild(location, strict=True)
        if parsed:
            yield parsed

    @classmethod
    def compute_normalized_license(cls, package):
        _declared, detected = detect_declared_license(package.declared_license)
        return detected

    @classmethod
    def assign_package_to_resources(cls, package, resource, codebase, package_adder):
        models.DatafileHandler.assign_package_to_parent_tree(
            package=package,
            resource=resource,
            codebase=codebase,
            package_adder=package_adder,
        )


def parse_alpine_installed_db(location, datasource_id, package_type):
    """
    Yield PackageData objects from an installed database file at `location`
    or None. Typically found at '/lib/apk/db/installed' in an Alpine
    installation.

    Note: http://uk.alpinelinux.org/alpine/v3.15/main/x86_64/APKINDEX.tar.gz are
    also in the same format as an installed database.
    """
    for package_fields in get_alpine_installed_db_fields(location):
        yield build_package_data(
            package_fields=package_fields,
            datasource_id=datasource_id,
            package_type=package_type,
        )


def get_alpine_installed_db_fields(location):
    """
    Yield lists of (name, value) pairs, one list for each package found in an
    installed Alpine packages database file at `location` (typically found at
    '/lib/apk/db/installed' in an Alpine installation.)

    Note: APKINDEX index files are also in the same format.
    See: http://uk.alpinelinux.org/alpine/v3.11/main/x86_64/APKINDEX.tar.gz
    """
    if not path.exists(location):
        return

    with open(location, 'rb') as f:
        installed = as_unicode(f.read())

    if installed:
        # each installed package paragraph is separated by LFLF
        packages = (p for p in re.split('\n\n', installed) if p)
        for pkg in packages:
            try:
                fields = email.message_from_string(pkg)
            except UnicodeEncodeError:
                fields = email.message_from_string(pkg.encode('utf-8'))
            yield [(n.strip(), v.strip(),) for n, v in fields.items()]


# these variables need to be resolved or else this is a parsing error
# we also only use these variables
APKBUILD_VARIABLES = set([
    'pkgname',
    'pkgver',
    'pkgrel',
    'pkgdesc',
    'license',
    'url'
    'arch',
    # 'subpackages',
    # depends
    # 'depend',
    # makedepends
    'source',
    'sha512sums',
    'sha256sums',
    'md5sums',
])

ESSENTIAL_APKBUILD_VARIABLES = set([
    'pkgname',
    'pkgver',
    'license',
    'url'
    'arch',
    'source',
    'sha512sums',
    'sha256sums',
    'md5sums',
])


def parse_apkbuild(location, strict=False):
    """
    Return a PackageData object from an APKBUILD file at ``location`` or None.

    If ``strict`` is True, raise ApkbuildParseFailure error if any attribute
    value cannot be fully resolved for shell variables.
    """
    with open(location, 'rb') as f:
        apkbuild = as_unicode(f.read())

    return parse_apkbuild_text(
        text=apkbuild,
        datasource_id=AlpineApkbuildHandler.datasource_id,
        package_type=AlpineApkbuildHandler.default_package_type,
        strict=strict,
    )


class ApkbuildParseFailure(Exception):
    pass


def get_apkbuild_variables(text):
    """
    Parse ``text`` and return a tuple of (variables, errors) where variables is
    a list of bashparse.ShellVariables with a name listed in the ``names`` set.
    """
    fixed_text = fix_apkbuild(text)

    variables, errors = bashparse.collect_shell_variables_from_text(
        text=fixed_text,
        resolve=True,
        needed_variables=APKBUILD_VARIABLES,
    )
    return variables, errors


def replace_fix(text, source, target, *args):
    """
    Replace ``source`` by ``target`` in ``text`` and return ``text``.
    """
    return text.replace(source, target)


def extract_var(text, varname):
    """
    Return the a single line attribute with variable named ``varname `` found in
    the ``text`` APKBUILD or an empty string.

    For example::
    >>> t='''
    ... pkgname=sqlite-tcl
    ... pkgrel=0
    ... '''
    >>> extract_var(t, 'pkgname')
    'sqlite-tcl'
    """
    try:
        variable = [
            l for l in text.splitlines(False)
            if l.startswith(f'{varname}=')
        ][0]
    except Exception:
        variable = ''

    _, _, value = variable.partition('=')
    return value


def extract_pkgver(text):
    """
    Return the pkgver version attribute found in the ``text`` APKBUILD or an
    empty string.

    For example::
    >>> t='''
    ... pkgname=sqlite-tcl
    ... pkgver=3.35.5
    ... pkgrel=0
    ... '''
    >>> extract_pkgver(t)
    '3.35.5'
    """
    return extract_var(text, varname='pkgver')


def get_pkgver_substring(text, version_segments=2):
    """
    Return a pkgver version substring from ``text`` APKBUILD using up to
    ``version_segments`` segments of the version (dot-separated).
    """
    version = extract_pkgver(text)
    # keep only first few segments using "version_segments"
    segments = version.split('.')[:version_segments]
    return '.'.join(segments)


def add_version_substring_variable(text, varname, version_segments=2):
    """
    Fix things in ``text`` such as :
    case $pkgver in
        *.*.*)    _kernver=${pkgver%.*};;
        *.*) _kernver=$pkgver;;
    esac

    This is a common pattern in APKBUILD to extract some segments from a version
    """
    version = get_pkgver_substring(text, version_segments=version_segments)
    return f'{varname}={version} #fixed by scancode\n\n{text}'


def fix_sqsh_2_segments_version(text, *args):
    """
    Fix this in ``text``:
        pkgver=2.5.16.1
        case $pkgver in
        *.*.*.*) _v=${pkgver%.*.*};;
        *.*.*) _v=${pkgver%.*};;
        *) _v=$pkgver;;
        esac
    """
    return add_version_substring_variable(text, varname='_v', version_segments=2)


def fix_libreoffice_version(text, *args):
    """
    Fix this in ``text``:
    pkgname=libreoffice
    pkgver=6.4.2
    case $pkgver in
       *.*.*.*) _v=${pkgver%.*};;
       *.*.*) _v=$pkgver;;
    esac
    """
    return add_version_substring_variable(text, varname='_v', version_segments=3)


def fix_kernver_version(text, *args):
    """
    Fix things in ``text`` such as :
        case $pkgver in
            *.*.*)    _kernver=${pkgver%.*};;
            *.*) _kernver=$pkgver;;
        esac

    and:
        case $pkgver in
        *.*.*)    _kernver=${pkgver%.*};;
        *.*)    _kernver=${pkgver};;
        esac
    """
    return add_version_substring_variable(text, varname='_kernver', version_segments=2)


def fix_dunder_v_version(text, *args):
    """
    Fix things in ``text`` such as :
        case $pkgver in
            *.*.*) _v=${pkgver%.*};;
            *.*) _v=$pkgver;;
        esac
    """
    return add_version_substring_variable(text, varname='_v', version_segments=2)


def fix_kde_version(text, *args):
    """
    Fix this in ``text``:
    case "$pkgver" in
        *.90*) _rel=unstable;;
        *) _rel=stable;;
    esac
    """
    version = extract_pkgver(text)
    if '.90' in version:
        rel = 'unstable'
    else:
        rel = 'stable'
    return f'_rel={rel} #fixed by scancode\n\n{text}'


def fix_sudo_realver(text, *args):
    """
    sudo-1.9.6p1.tar.gz

    pkgver=1.9.6_p1
    if [ "${pkgver%_*}" != "$pkgver" ]; then
        _realver=${pkgver%_*}${pkgver#*_}
    else
        _realver=$pkgver
    fi
    source="https://www.sudo.ws/dist/sudo-$_realver.tar.gz
    """
    _realver = extract_pkgver(text).replace('_', '')
    return f'_realver={_realver} #fixed by scancode\n\n{text}'


def convert_sqlite_version(version):
    """
    Return a version converted from the sqlite human version format to the
    download version format.

    For instance:
    >>> convert_sqlite_version('3.36.0')
    '3360000'
    >>> convert_sqlite_version('3.36.0.2')
    '3360002'

    See also: https://www.sqlite.org/versionnumbers.html
    From https://www.sqlite.org/download.html

        Build Product Names and Info

        Build products are named using one of the following templates:

            sqlite-product-version.zip
            sqlite-product-date.zip
        [...]
        The version is encoded so that filenames sort in order of increasing
        version number when viewed using "ls". For version 3.X.Y the filename
        encoding is 3XXYY00. For branch version 3.X.Y.Z, the encoding is
        3XXYYZZ.

        The date in template (4) is of the form: YYYYMMDDHHMM
    """
    segments = [int(s) for s in version.strip().split('.')]
    if len(segments) == 3:
        # all version should have 4 segments. Add it if missing
        segments.append(0)

    try:
        major, minor, patch, branch = segments
    except Exception:
        raise Exception(
            f'Unsupported sqlite version format. Should have 3 or 4 segments: '
            f'{version}'
        )
    # pad each segments except the first on the left with zeroes 3XXYY00
    return f'{major}{minor:>02d}{patch:>02d}{branch:>02d}'


def fix_sqlite_version(text, *args):
    """
    Fix the complex SQLite version conversion.
    See  https://www.sqlite.org/download.html

    case $pkgver in
        *.*.*.*)_d=${pkgver##*.};;
        *.*.*)    _d=0;;
    esac
    """
    converted = convert_sqlite_version(extract_pkgver(text))
    vers = '_ver=${_a}${_b}${_c}$_d\n'
    text = text.replace(
        vers,
        f'{vers}'
        f'_ver={converted} #fixed by scancode\n\n'
    )
    return text


def extract_lua__pkgname(text):
    """
    For example:
    >>> t='''
    ... pkgname=lua-unit
    ... foo=bar
    ... '''
    >>> extract_lua__pkgname(t)
    'LUAUNIT'
    """
    return extract_var(text, varname='pkgname').replace('-', '').upper()


def fix_lua_pkgname(text, *args):
    """
    Fix things in ``text`` such as:
    pkgname=lua-unit
    _pkgname=$(echo ${pkgname/-/} | tr '[:lower:]' '[:upper:]')
    """
    converted = extract_lua__pkgname(text)
    _pkgname = "_pkgname=$(echo ${pkgname/-/} | tr '[:lower:]' '[:upper:]')\n"
    # comment out original
    return text.replace(
        _pkgname,
        f'#{_pkgname}' + f'_pkgname={converted} #fixed by scancode\n\n'
    )


def fix_liburn_prereleases(text, *args):
    """
    pkgname=libburn
    pkgver=1.5.4
    _ver=${pkgver%_p*}
    if [ "$_ver" != "$pkgver" ]; then
        _pver=".pl${pkgver##*_p}"
    fi
    """
    return f'_pver="" #fixed by scancode\n\n{text}'


def fix_cmake(text, *args):
    """
    case $pkgver in
    *.*.*.*) _v=v${pkgver%.*.*};;
    *.*.*) _v=v${pkgver%.*};;
    esac
    """
    version = get_pkgver_substring(text, version_segments=2)
    return f'_v=v{version} #fixed by scancode\n\n{text}'


def fix_kamailio(text, *args):
    """
    pkgname=kamailio
    pkgver=5.4.5
    pkgrel=0

    # If building from a git snapshot, specify the gitcommit
    # If building a proper release, leave gitcommit blank or commented
    #_gitcommit=991fe9b28e0e201309048f3b38a135037e40357a

    [ -n "$_gitcommit" ] && pkgver="$pkgver.$(date +%Y%m%d)"
    [ -n "$_gitcommit" ] && _suffix="-${_gitcommit:0:7}"
    [ -n "$_gitcommit" ] && builddir="$srcdir/$pkgname-$_gitcommit" || builddir="$srcdir/$pkgname-$pkgver"
    [ -z "$_gitcommit" ] && _gitcommit="$pkgver"
    """
    return (
        f'_gitcommit="$pkgver" #fixed by scancode\n'
        f'_suffix="" #fixed by scancode\n'
        f'\n{text}'
    )


def fix_qt(text, *args):
    """
    case $pkgver in
        *_alpha*|*_beta*|*_rc*) _rel=development_releases;;
        *) _rel=official_releases;;
    esac
    """
    pkgver = extract_pkgver(text)
    if any(s in pkgver for s in ('_alpha', '_beta', '_rc')):
        _rel = 'development_releases'
    else:
        _rel = 'official_releases'
    return (
        f'_rel={_rel} #fixed by scancode\n\n'
        f'\n{text}'
    )


def fix_parole(text, *args):
    """
    pkgname=parole
    pkgver=1.0.5
    pkgrel=0
    case $pkgver in
        *.*.*.*) _branch=${pkgver%.*.*};;
        *.*.*) _branch=${pkgver%.*};;
    esac
    """
    return add_version_substring_variable(text, varname='_branch', version_segments=2)


def fix_mpd(text, *args):
    """
    pkgname=mpd
    pkgver=0.22.8
    case $pkgver in
    *.*.*) _branch=${pkgver%.*};;
    *.*) _branch=$pkgver;;
    esac
    """
    return add_version_substring_variable(text, varname='_branch', version_segments=2)


@attr.s
class ApkBuildFixer:
    """
    Represent an APKBUILD syntax fix:

    ``if_these_strings_are_present`` in ``text``, call ``function(text, *args)``
    that returns ``text``.
    """
    if_these_strings_are_present = attr.ib(default=tuple())
    function = attr.ib(default=replace_fix)
    args = attr.ib(default=tuple())


def fix_apkbuild(text):
    """
    Return a ``text`` applying some refinements and fixes.

    This applies a list of special cases fixes represented by ApkBuildFixer
    instances. These are unfortunate hacks to cope with limitations of shell
    parameter expansion that would be hard to fix OR to handle parameters that
    are not available OR just because it would require executing a build
    otherwise.

    """
    replacements = [
        ApkBuildFixer(
            if_these_strings_are_present=('pkgname=qt',),
            function=fix_qt,
        ),
        ApkBuildFixer(
            if_these_strings_are_present=('pkgname=gcc\n',),
            function=replace_fix,
            args=('$_target', ''),
        ),
        ApkBuildFixer(
            if_these_strings_are_present=('jool', 'For custom kernels set $FLAVOR.', '_flavor="$FLAVOR"',),
            function=replace_fix,
            args=('_flavor="$FLAVOR"', '_flavor=lts'),
        ),
        ApkBuildFixer(
            if_these_strings_are_present=('pkgname=ufw\n',),
            function=replace_fix,
            args=('$(echo $pkgver|cut -c1-4)', '$pkgver'),
        ),
        ApkBuildFixer(
            if_these_strings_are_present=('pkgname=rtpengine-$_flavor',),
            function=replace_fix,
            args=('# rtpengine version\n', '_flavor=lts\n'),
        ),
        ApkBuildFixer(
            if_these_strings_are_present=('\t*.*.*.*) _v=${pkgver%.*};;', '\t*.*.*) _v=$pkgver;;'),
            function=fix_libreoffice_version,
        ),
        ApkBuildFixer(
            if_these_strings_are_present=('\t*.90*) _rel=unstable;;', '\t*) _rel=stable;;'),
            function=fix_kde_version,
        ),
        ApkBuildFixer(
            if_these_strings_are_present=('_kernver=${pkgver%.*};;', '_kernver=$pkgver;;'),
            function=fix_kernver_version,
        ),
        ApkBuildFixer(
            if_these_strings_are_present=('_kernver=${pkgver%.*};;', '_kernver=${pkgver};;'),
            function=fix_kernver_version,
        ),

        ApkBuildFixer(
            if_these_strings_are_present=('\t*.*.*) _v=${pkgver%.*};;', '\t*.*) _v=$pkgver;;'),
            function=fix_dunder_v_version,
        ),
        ApkBuildFixer(
            if_these_strings_are_present=('_realver=${pkgver%_*}${pkgver#*_}', '_realver=$pkgver'),
            function=fix_sudo_realver,
        ),
        ApkBuildFixer(
            if_these_strings_are_present=('*.*.*.*) _v=${pkgver%.*.*};;', '*.*.*) _v=${pkgver%.*};;', '*) _v=$pkgver;;'),
            function=fix_sqsh_2_segments_version,
        ),
        ApkBuildFixer(
            if_these_strings_are_present=('pkgname=sqlite',),
            function=fix_sqlite_version,
        ),
        ApkBuildFixer(
            if_these_strings_are_present=("_pkgname=$(echo ${pkgname/-/} | tr '[:lower:]' '[:upper:]')",),
            function=fix_lua_pkgname,
        ),
        ApkBuildFixer(
            if_these_strings_are_present=('pkgname=libburn',),
            function=fix_liburn_prereleases,
        ),
        ApkBuildFixer(
            if_these_strings_are_present=('pkgname=kamailio',),
            function=fix_kamailio,
        ),
        ApkBuildFixer(
            if_these_strings_are_present=('_v=v${pkgver%.*.*};;', '_v=v${pkgver%.*};;',),
            function=fix_cmake,
        ),
        ApkBuildFixer(
            if_these_strings_are_present=('pkgname=parole',),
            function=fix_parole,
        ),
        ApkBuildFixer(
            if_these_strings_are_present=('pkgname=mpd',),
            function=fix_mpd,
        ),
    ]

    for fixer in replacements:
        if all(s in text for s in fixer.if_these_strings_are_present):
            text = fixer.function(text, *fixer.args)
    return text


def parse_apkbuild_text(text, datasource_id, package_type, strict=False):
    """
    Return a PackageData object from an APKBUILD text context or None. Only
    consider variables with a name listed in the ``names`` set.

    If ``strict`` is True, raise ApkbuildParseFailure error if any attribute
    value cannot be fully resolved for shell variables.
    """
    if not text:
        return

    variables, errors = get_apkbuild_variables(text=text)
    unresolved = [
        v for v in variables
        if not v.is_resolved()
        and v.name in ESSENTIAL_APKBUILD_VARIABLES
    ]

    if strict and unresolved:
        raise ApkbuildParseFailure(
            f'Failed to parse APKBUILD: {text}\n\n'
            f'variables: {variables}\n\n'
            f'unresolved: {unresolved}\n\n'
            f'errors: {errors}',
        )
    variables = ((v.name, v.value,) for v in variables)
    package = build_package_data(
        variables,
        datasource_id=datasource_id,
        package_type=package_type
    )

    if package and unresolved:
        unresolved = [v.to_dict() for v in unresolved]
        package.extra_data['apkbuild_variable_resolution_errors'] = unresolved
    return package


def parse_pkginfo(location):
    """
    Return a PackageData object from a .PKGINFO file at ``location`` or None.
    .PKGINFO is a metadata is found at the root of an .apk tarball and is
    derived from the package metadata in APKBUILD

    Each lines are in the format of  "name = value" such as in::

        # Generated by abuild 3.8.0_rc3-r2
        # using fakeroot version 1.25.3
        # Wed Jun  9 21:24:56 UTC 2021
        pkgname = a2ps
        pkgver = 4.14-r9
        pkgdesc = a2ps is an Any to PostScript filter
        url = https://www.gnu.org/software/a2ps/
        builddate = 1623273896
        packager = Buildozer <alpine-devel@lists.alpinelinux.org>
        size = 3362816
        arch = armv7
        origin = a2ps
        commit = 0a4f8e4e4d21ac8c83a85c534f6424f03a3b7a70
        maintainer = Natanael Copa <ncopa@alpinelinux.org>
        license = GPL-3.0
        depend = ghostscript
        depend = imagemagick

    """
    raise NotImplementedError


def build_package_data(package_fields, datasource_id, package_type):
    """
    Return a PackageData object from a ``package_fields`` iterable of (name,
    value) tuples.

    The ``package_fields`` names are either:

    - the short form one-letter field names used in an APKINDEX and an installed
      database file

    - the long form field names seen in an APKBUILD build manifest/script and an
      APKINFO data file.

    Note: we do NOT use a dict for ``package_fields`` because some fields names
    may occur more than once.

    See for details:
    https://wiki.alpinelinux.org/wiki/Apk_spec#Install_DB
    https://wiki.alpinelinux.org/wiki/APKBUILD_Reference
    https://wiki.alpinelinux.org/wiki/Alpine_package_format
    https://git.alpinelinux.org/apk-tools/tree/src/package.c?id=82de29cf7bad3d9cbb0aeb4dbe756ad2bde73eb3#n774
    """
    package_fields = list(package_fields)
    all_fields = dict(package_fields)

    # mapping of actual Package field name -> value that have been converted to
    # the expected normalized format
    converted_fields = {
        'datasource_id': datasource_id,
        'type': package_type,
    }
    for name, value in package_fields:
        handler = package_handlers_by_field_name.get(name)
        if handler:
            try:
                converted = handler(value, all_fields=all_fields, **converted_fields)
            except:
                raise Exception(*list(package_fields))

            # for extra data we update the existing
            extra_data = converted.pop('extra_data', {}) or {}
            if extra_data:
                existing_extra_data = converted_fields.get('extra_data')
                if existing_extra_data:
                    existing_extra_data.update(extra_data)
                else:
                    converted_fields['extra_data'] = dict(extra_data)

            converted_fields.update(converted)

    return models.PackageData.from_dict(converted_fields)

#####################################
# Note: all handlers MUST accept **kwargs as they also receive the current data
# being processed so far as a processed_data kwarg, but most do not use it


def build_name_value_str_handler(name):
    """
    Return a generic handler callable function for plain string fields with the
    name ``name``.
    """

    def handler(value, **kwargs):
        return {name: value}

    return handler


def apkbuild_version_handler(value, all_fields, **kwargs):
    """
    Return a version suffixed with its release.

    TODO: should this be used everywhere?
    """
    pkgrel = all_fields.get('pkgrel')
    rel_suffix = f'-r{pkgrel}' if pkgrel else ''
    return {'version': f'{value}{rel_suffix}'}


def L_license_handler(value, **kwargs):
    """
    Return a normalized declared license and a detected license expression.
    """
    original = value
    _declared, detected = detect_declared_license(value)
    return {
        'declared_license': original,
        'license_expression': detected,
    }


def S_size_handler(value, **kwargs):
    return {'size': int(value)}


def t_release_date_handler(value, **kwargs):
    """
    Return a Package data mapping for a buiddate timestamp.
    """
    value = int(value)
    dt = datetime.utcfromtimestamp(value)
    stamp = dt.isoformat()
    # we get 2020-01-15T10:36:22, but care only for the date part
    date, _, _time = stamp.partition('T')
    return {'release_date': date}


get_maintainers = re.compile(
    r'(?P<name>[^<]+)'
    r'\s?'
    r'(?P<email><[^>]+>)'
).findall


def m_maintainer_handler(value, **kwargs):
    """
    Return a Package data mapping as a list of parties a maintainer Party.
    A maintainer value may be one or more mail name <email@example.com> parts, space-separated.
    """
    parties = []
    for name, email in get_maintainers(value):
        maintainer = models.Party(
            type='person',
            role='maintainer',
            name=name,
            email=email,
        )
        parties.append(maintainer.to_dict())
    return {'parties': parties}


# this will return a three tuple if there is a split or a single item otherwise
split_name_and_requirement = re.compile('(=~|>~|<~|~=|~>|~<|=>|>=|=<|<=|<|>|=)').split


def D_dependencies_handler(value, dependencies=None, **kwargs):
    """
    Return a list of dependent packages from a dependency string and from previous dependencies.
    Dependencies can be either:
    - a package name with or without a version constraint
    - a path to something that is provided by some package(similar to RPMs) such as /bin/sh
    - a shared object (prefixed with so:)
    - a pkgconfig dependency where pkgconfig is typically also part of the deps
      and these are prefixed with pc:
    - a command prefixed with cmd:

    Note that these exist the same way in the p: provides field.

    An exclamation prefix negates the dependency.
    The operators can be ><=~

    For example:
        D:aaudit a52dec=0.7.4-r7 acf-alpine-baselayout>=0.5.7 /bin/sh
        D:so:libc.musl-x86_64.so.1 so:libmilter.so.1.0.2
        D:freeradius>3
        D:lua5.1-bit32<26
        D:!bison so:libc.musl-x86_64.so.1
        D:python3 pc:atk>=2.15.1 pc:cairo pc:xkbcommon>=0.2.0 pkgconfig
        D:bash colordiff cmd:ssh cmd:ssh-keygen cmd:ssh-keyscan cmd:column
        D:cmd:nginx nginx-mod-devel-kit so:libc.musl-aarch64.so.1
        D:mu=1.4.12-r0 cmd:emacs
    """
    # operate on a copy for safety and create an empty list on first use
    dependencies = dependencies[:] if dependencies else []
    for dep in value.split():
        if dep.startswith('!'):
            # ignore the "negative" deps, we cannot do much with it
            # they are more of a hints for the dep solver than something
            # actionable for origin reporting
            continue
        if dep.startswith('/'):
            # ignore paths to a command for now as we cannot do
            # much with them yet until we can have a Package URL for them.
            continue
        if dep.startswith('cmd:'):
            # ignore commands for now as we cannot do much with them yet until
            # we can have a Package URL for them.
            continue
        if dep.startswith('so:'):
            # ignore the shared object with an so: prexi for now as we cannot do
            # much with them yet until we can have a Package URL for them.
            # TODO: see how we could handle these and similar used elsewhere
            continue
        is_pc = False
        if dep.startswith('pc:'):
            is_pc = True
            # we strip the 'pc:' prefix and treat a pc: dependency the same as
            # other depends
            dep = dep[3:]

        requirement = None
        version = None
        is_resolved = False
        segments = split_name_and_requirement(dep)
        if len(segments) == 1:
            # we have no requirement...just a plain name
            name = dep
        else:
            if len(segments) != 3:
                raise Exception(dependencies, kwargs)
            name, operator, ver = segments
            # normalize operator tsuch that >= and => become =>
            operator = ''.join(sorted(operator))
            if operator == '=':
                version = ver
                is_resolved = True

            requirement = operator + ver

        purl = PackageURL(type='alpine', name=name, version=version).to_string()

        # that the only scope we have for now
        scope = 'depend'
        if is_pc:
            scope += ':pkgconfig'

        dependency = models.DependentPackage(
            purl=purl,
            scope=scope,
            extracted_requirement=requirement,
            is_resolved=is_resolved,
        )
        if dependency not in dependencies:
            dependencies.append(dependency.to_dict())

    return {'dependencies': dependencies}


def o_source_package_handler(value, version=None, **kwargs):
    """
    Return a source_packages list of Package URLs
    """
    # the version value will be that of the current package
    origin = PackageURL(type='alpine', name=value, version=version).to_string()
    return {'source_packages': [origin]}


def c_git_commit_handler(value, **kwargs):
    """
    Return a git VCS URL from a package commit.
    """
    return {f'vcs_url': f'git+http://git.alpinelinux.org/aports/commit/?id={value}'}


def A_arch_handler(value, **kwargs):
    """
    Return a Package URL qualifiers for the arch.
    """
    # TODO: should arch={value} be rather a mapping of {arch: value} ?
    return {'qualifiers': f'arch={value}'}

# Note that we use a little trick for handling package file references. Each
# handler receives a copy of the data processed so far. As it happens, the data
# about files starts with a directory entry then one or more files, each
# normally followed by their checksums We return and use the current_dir and
# current_file from these handlers to properly create a file in its directory
# (which is the current one) and add the checksum to its file (which is the
# current one). 'current_file' and 'current_dir' are not actual package fields,
# but we ignore these when we create the PackageData object.


def F_directory_handler(value, **kwargs):
    return {'current_dir': value}


def R_filename_handler(value, current_dir, file_references=None, **kwargs):
    """
    Return a new current_file FileReference in current_dir.  Add to the
    ``file_references`` list (create it if not provided)

    Return a mapping of {'current_file': current_file, 'file_references': file_references}
    """
    # operate on a copy for safety and create an empty list on first use
    file_references = file_references[:] if file_references else []

    current_file = models.FileReference(path=posixpath.join(current_dir, value))
    file_references.append(current_file.to_dict())
    return {'current_file': current_file, 'file_references': file_references}


def Z_checksum_handler(value, current_file, **kwargs):
    """
    Update the ``current_file`` FileReference with its updated SHA1 hex-encoded
    checksum.

    Return a mapping of {'current_file': current_file}

    'Z' is a file checksum (for files and links)
    For example: Z:Q1WTc55xfvPogzA0YUV24D0Ym+MKE=

    The 1st char is an encoding code: Q means base64 and the 2nd char is
    the type of checksum: 1 means SHA1 so Q1 means based64-encoded SHA1
    """
    assert value.startswith('Q1'), (
        f'Unknown checksum or encoding: should start with Q1 for base64-encoded SHA1: {value}')
    sha1 = base64.b64decode(value[2:])
    sha1 = codecs.encode(sha1, 'hex').decode('utf-8').lower()
    current_file.sha1 = sha1
    return {'current_file': current_file}


def get_checksum_entries(value):
    """
    Yield tuples of (file_name, checksum) for each checksum found in
    an APKBUILD checksums ``value`` variable.

    See https://wiki.alpinelinux.org/wiki/APKBUILD_Reference#md5sums.2Fsha256sums.2Fsha512sums

        > Checksums for the files/URLs listed in source. The checksums are
        > normally generated and updated by executing abuild checksum and should
        > be the last item in the APKBUILD.

    The shape of this is one entry per line and two spaces separator with filenames::
    sha512sums="db2e3cf88d8d18  a52dec-0.7.4.tar.gz
        db2e3cf88d8d12  automake.patch
        21d44824109ea6  fix-globals-test-x86-pie.patch
        29e7269873806e  a52dec-0.7.4-build.patch"        "
    """
    for entry in value.strip().splitlines(False):
        entry = entry.strip()
        if not entry:
            continue
        if not '  ' in entry:
            raise Exception(f'Invalid APKBUILD checksums format: {value!r}')
        checksum, _, file_name = entry.partition('  ')
        checksum = checksum.strip()
        file_name = file_name.strip()
        yield file_name, checksum


def checksums_handler(value, checksum_name, **kwargs):
    """
    Return a Package extra data mapping as a list of checksums mappings for
    checksums variable ``value`` using ``checksum_name`` as attribute name.
    """
    checksums = [
        {'file_name': fn, checksum_name: val}
        for fn, val in  get_checksum_entries(value=value)
    ]

    return {'extra_data': {'checksums': checksums}}


def get_source_entries(source):
    """
    Yield source file tuples as (file_name, URL) where URL is None if this is a
    lcoal file (i.e. for patches) given an APKBUILD ``source`` attribue string.

    See https://wiki.alpinelinux.org/wiki/APKBUILD_Reference:
    The shape of this is one entry per line::

    source="http://liba52.sourceforge.net/files/$pkgname-$pkgver.tar.gz
        automake.patch
        fix-globals-test-x86-pie.patch
        $pkgname-$pkgver-build.patch
        "
    or::

    source="lua-mqtt-publish-$pkgver.tar.gz::https://github.com/ncopa/lua-mqtt-publish/archive/v$pkgver.tar.gz"
    """
    schemes = 'https://', 'http://', 'ftp://',
    for entry in source.strip().splitlines(False):
        entry = entry.strip()
        if not entry:
            continue

        has_url = any(scheme in entry for scheme in schemes)
        is_url = entry.startswith(schemes)

        if is_url:
            url = entry
            file_name = None
        elif '::' in entry and has_url:
            file_name, _, url = entry.partition('::')
            file_name = file_name.strip()
            url = url.strip()
        else:
            file_name = entry
            url = None
        yield file_name, url


def source_handler(value, **kwargs):
    """
    Return a Package extra data mapping as a list of sources entry mappings.
    """
    sources = []
    for fn, url in get_source_entries(value):
        sources.append(dict(file_name=fn, url=url))
    return {'extra_data': {'sources': sources}}


# mapping of:
# - the package field one letter name in the installed db,
# - an handler for that field
package_handlers_by_field_name = {

    ############################################################################
    # per-package fields
    ############################################################################

    # name of the package
    # For example: P:busybox
    # 'pkgname' in .PKGINFO and APKBUILD
    'P': build_name_value_str_handler('name'),
    'pkgname': build_name_value_str_handler('name'),

    # TODO: add subpackages
    # this can be composed of two or three segments: epoch:version-release
    # For example: V:1.31.1-r9
    # 'pkver' in .PKGINFO and APKBUILD
    'V': build_name_value_str_handler('version'),
    'pkgver': apkbuild_version_handler,

    # For example: T:Size optimized toolbox of many common UNIX utilities
    # 'pkgdesc' in .PKGINFO and APKBUILD
    'T': build_name_value_str_handler('description'),
    'pkgdesc': build_name_value_str_handler('description'),

    # For example: U:https://busybox.net/
    # 'url' in .PKGINFO and APKBUILD
    'U': build_name_value_str_handler('homepage_url'),
    'url': build_name_value_str_handler('homepage_url'),

    # The license. For example: L:GPL2
    # 'license' in .PKGINFO and APKBUILD
    'L': L_license_handler,
    'license': L_license_handler,

    # For example: m:Natanael Copa <ncopa@alpinelinux.org>
    # 'maintainer' in .PKGINFO and APKBUILD
    'm': m_maintainer_handler,
    # TODO: this is more often just a comment in the APKBUILD
    'maintainer': m_maintainer_handler,

    # For example: A:x86_64
    # 'arch' in .PKGINFO and APKBUILD
    'A':  A_arch_handler,
    'arch':  A_arch_handler,

    # Compressed package size in bytes.
    # For example: S:507134
    # 'size' in .PKGINFO and APKBUILD
    'S': S_size_handler,
    'size': S_size_handler,

    # a build timestamp as in second since epoch
    # For example: t:1573846491
    # 'builddate' in .PKGINFO and APKBUILD
    't': t_release_date_handler,
    'builddate': t_release_date_handler,

    # origin and build_time are not set for virtual packages so we can skip these
    # name of the source package
    # For example: o:apk-tools
    # 'origin' in .PKGINFO and APKBUILD
    'o':  o_source_package_handler,
    'origin':  o_source_package_handler,

    # c is the sha1 "id" for the git commit in
    # https://git.alpinelinux.org/aports
    # e.g.: https://git.alpinelinux.org/aports/commit/?id=e5c984f68aabb28de623a7e3ada5a223c2b66d77
    # the commit is for the source package
    # For example: c:72048e01f0eef23b1300eb4c7d8eb2afb601f156
    # 'commit' in .PKGINFO and APKBUILD
    'c': c_git_commit_handler,
    'commit': c_git_commit_handler,

    # For example: D:scanelf so:libc.musl-x86_64.so.1
    # For example: D:so:libc.musl-x86_64.so.1 so:libcrypto.so.1.1 so:libssl.so.1.1 so:libz.so.1
    # Can occur more than once
    # 'depend' in .PKGINFO and APKBUILD
    # TODO: add other dependencies (e.g. makedepends)
    'D': D_dependencies_handler,
    'depend': D_dependencies_handler,

    # For example: source="http://liba52.sourceforge.net/files/$pkgname-$pkgver.tar.gz
    #         automake.patch
    #         fix-globals-test-x86-pie.patch"
    # Should occur only once and only in APKBUILD
    # we treat these as extra data for now
    'source': source_handler,

    # checksums in APKBUILD
    # See https://wiki.alpinelinux.org/wiki/APKBUILD_Reference#md5sums.2Fsha256sums.2Fsha512sums
    'sha256sums': partial(checksums_handler, checksum_name='sha256'),
    'sha512sums': partial(checksums_handler, checksum_name='sha512'),
    'md5sums': partial(checksums_handler, checksum_name='md5sums'),

    ############################################################################
    # ignored per-package fields. from here on, these fields are not used yet
    ############################################################################
    # For example: p:cmd:getconf cmd:getent cmd:iconv cmd:ldconfig cmd:ldd
    # ('p', 'provides'),

    # The as-installed size in bytes. For example: I:962560
    # ('I', 'installed_size'),

    # TODO: Checksum
    # also in APKBUILD we have sha512sums
    # For example: C:Q1sVrQyQ5Ek9/clI1rkKjgINqJNu8=
    # like for the file checksums "Z", Q means base64 encoding adn 1 means SHA1
    # The content used for this SHA1 is TBD.
    # ('C', 'checksum'),

    # not sure what this is for: TBD
    # ('i', 'install_if'),
    # 'r' if for dependencies replaces. For example: r:libiconv
    # For example: r:libiconv
    # ('r', 'replaces'),
    # not sure what this is for: TBD
    # ('k', 'provider_priority'),

    # 'q': Replaces Priority
    # 's': Get Tag Id?  or broken_script
    # 'f': broken_files?
    # 'x': broken_xattr?
    ############################################################################

    ############################################################################
    # per-file fields
    ############################################################################

    # - 'F': this is a folder path from the root and until there is a new F value
    #    all files defined with an R are under that folder
    'F': F_directory_handler,

    # - 'Z' is a file checksum (for files and links)
    'Z': Z_checksum_handler,

    # - 'R': this is a file name that is under the current F Folder
    'R': R_filename_handler,

    # - 'M' is a set of permissions for a folder as user:group:mode e.g. M:0:0:1777
    # - 'a' is a set of permissions for a file as user:group:mode e.g. a:0:0:755
    ############################################################################
}


def detect_declared_license(declared):
    """
    Return a tuple of (cleaned declared license, detected license expression)
    strings from a ``declared`` license text. Both can be None.
    """
    # cleaning first to fix syntax quirks and try to get something we can parse
    cleaned = normalize_and_cleanup_declared_license(declared)
    if not cleaned:
        return None, None

    # then we apply mappings for known non-standard symbols
    # the output should be a proper SPDX expression
    mapped = apply_expressions_mapping(cleaned)

    # Finally perform SPDX expressions detection: Alpine uses mostly SPDX, but
    # with some quirks such as some non standard symbols (in addition to the
    # non-standard syntax)
    extra_licenses = {}
    expression_symbols = get_license_symbols(extra_licenses=extra_licenses)

    detected = models.compute_normalized_license(
        declared_license=mapped,
        expression_symbols=expression_symbols,
    )

    return cleaned, detected


def get_license_symbols(extra_licenses):
    """
    Return a mapping of {lowercased key: LicenseSymbolLike} where
    LicenseSymbolLike wraps a License object. This is a combo of the SPDX
    licenses keys and the Alpine-specific extra symbols.
    """
    from licensedcode.cache import get_spdx_symbols
    from licensedcode.cache import get_licenses_db

    # make a copy
    symbols = dict(get_spdx_symbols())
    ref_licenses = get_licenses_db()

    for alpine_key, license_key in extra_licenses.items():
        # check that there are no dupe keys
        assert alpine_key not in symbols

        lic = ref_licenses[license_key]
        symbols[alpine_key] = LicenseSymbolLike(lic)

    return symbols


def normalize_and_cleanup_declared_license(declared):
    """
    Return a cleaned and normalized declared license.

    The expression should be valida SPDX but are far from this in practice.

    Several fixes are applied:

    - plain text replacemnet aka. syntax fixes are plain text replacements
      to make the expression parsable

    - common fixes includes also nadling space-separated and comma-separated
      lists of licenses
    """
    declared = declared or ''

    # normalize spaces
    declared = ' '.join(declared.split())

    declared = declared.lower()

    # performa replacements
    declared = apply_syntax_fixes(declared)

    # comma-separated as in gpl-2.0+, lgpl-2.1+, zlib
    if ',' in declared:
        comma_separated = [lic.strip() for lic in declared.split(',')]
        declared = combine_expressions(comma_separated, unique=False)

    elif ' ' in declared:
    # space-separated as in apache-2.0 gpl-3.0-or-later lgpl-3.0-or-later
        expression_keywords = '(', ')', ' or ', ' and ', ' with '
        lowered = declared.lower()
        if not any(s in lowered for s in expression_keywords):
            space_separated = declared.split()
            declared = combine_expressions(space_separated, unique=False)
    return declared


# these are basic text replacement that make the expression parsable
EXPRESSION_SYNTAX_FIXES = {

    ' and and ': ' and ',

    '(gpl-2.0-only and lgpl-2.1-or-later) with openssl-exception':
        '(gpl-2.0-only with licenseref-scancode-generic-exception '
        'and lgpl-2.1-or-later with licenseref-scancode-generic-exception)',

    '(gpl-2.0-or-later and gpl-2.1-or-later) with openssl-exception':
        '(gpl-2.0-or-later with licenseref-scancode-generic-exception '
        'and lgpl-2.1-or-later with licenseref-scancode-generic-exception)',

    'artistic-2.0 license': 'artistic-2.0',
    'artistic license 2.0': 'artistic-2.0',
    'perl artistic': 'artistic-1.0-perl',

    'bsd 3-clause': 'bsd-3-clause',
    'bsd with advertising': 'bsd-4-clause',
    'and bsd-3-clause mit and': 'and bsd-3-clause and mit and',
    'bsd-3-clause(variant)': 'bsd-3-clause AND licenseref-scancode-other-permissive',

    'public domain': 'licenseref-scancode-public-domain',

    'with openssl exception': 'with openssl-exception',
    'osf-1990(variant)': 'licenseref-scancode-osf-1990',
    'mit/x': 'mit',

    'gfdl-1.3-or-later gpl-2.0-or-later with font-exception-2.0':
        'gfdl-1.3-or-later and gpl-2.0-or-later with font-exception-2.0',

    'lgpl 2.1': 'lgpl-2.1',

    'gpl-3.0+ with exception': 'gpl-3.0+ with licenseref-scancode-generic-exception',

    'gpl-2.0-or-later (lgpl-2.1-only or lgpl-3.0-only)': 'gpl-2.0-or-later and (lgpl-2.1-only or lgpl-3.0-only)',

    # ORTP license is now GPL-3
    'lgpl-2.0-or-later vsl': 'gpl-3.0 or licenseref-scancode-commercial-license',

    # hunspell dictionaries
    'lgpl-2.0-or-later scowl':
        'lgpl-2.0-or-later and licenseref-scancode-other-permissive and '
        'licenseref-scancode-mit-old-style and licenseref-scancode-public-domain',

    'mit and (lgpl-2.1-only or lgpl-3.0-only':
        'mit and (lgpl-2.1-only or lgpl-3.0-only)',

    'gpl-2.0-or-later fipl': 'gpl-2.0-or-later and freeimage',

    'apache-2.0 and mit ofl-1.1 gpl-3.0-or-later gpl-3.0-with-gcc-exception cc-by-sa-3.0 lgpl-3.0':
        'apache-2.0 and mit and ofl-1.1 and gpl-3.0-or-later and gpl-3.0-with-gcc-exception and cc-by-sa-3.0 and lgpl-3.0',

    'custom:xiph lgpl gpl fdl': 'bsd-3-clause AND gpl-2.0-or-later AND gpl-3.0-or-later AND lgpl-2.1-or-later AND gfdl-1.1-or-later',

    'asl 2.0': 'apache-2.0',
    'Apache 2.0': 'apache-2.0',

}


def apply_syntax_fixes(s):
    """
    Fix the expression string s by aplying replacement for various quirks.
    """
    for src, tgt in EXPRESSION_SYNTAX_FIXES.items():
        s = s.replace(src, tgt)
    return s

# These are parsed expression objects replacement that make the expression SPDX compliant


# {alpine sub-expression: SPDX subexpression}
DECLARED_TO_SPDX = {
    'openssl-exception': 'licenseref-scancode-generic-exception',
    'agpl': 'agpl-3.0-or-later',

    # this is a typo in gingerbase
    'agpl-2.1': 'lgpl-2.1 and apache-2.0 and licenseref-scancode-free-unknown',

    'gpl-3.0-or-later-with-openssl-exception': 'gpl-3.0-or-later with licenseref-scancode-generic-exception',
    'apache': 'apache-2.0',

    'bsd': 'bsd-3-clause',
    'bsd2': 'bsd-2-clause',
    'bsd-0': '0bsd',
    'bsd-2-clauase': 'bsd-2-clause',

    'closed': 'licenseref-scancode-proprietary-license',
    'proprietary': 'licenseref-scancode-proprietary-license',
    'propietary': 'licenseref-scancode-proprietary-license',
    'unifi-eula': 'licenseref-scancode-proprietary-license',
    'other': 'licenseref-scancode-proprietary-license',

    'psf': 'psf-2.0',
    'psfl': 'psf-2.0',

    'fdl': 'gfdl-1.1-or-later',

    'artistic-perl-1.0': 'artistic-1.0-perl',
    'artistic': 'artistic-1.0-perl',
    'artistic-perl': 'artistic-1.0-perl',
    'artisitc-1.0-perl': 'artistic-1.0-perl',
    'perlartistic': 'artistic-1.0-perl',
    'perl': 'gpl-1.0-or-later or artistic-1.0-perl',

    'artistic-2': 'artistic-2.0',

    'gpl': 'gpl-1.0-or-later',
    'gpl+': 'gpl-1.0-or-later',
    'lgpl': 'lgpl-2.0-or-later',
    'lgpl+': 'lgpl-2.0-or-later',
    'gpl2+': 'gpl-2.0-or-later',
    'gpl-2.0-or-later-with-sane-exception': 'gpl-2.0-or-later with licenseref-scancode-generic-exception',
    'gpl-3-or-later': 'gpl-3.0-or-later',
    'lgp-2.1-only': 'lgpl-2.1-only',

    'lpgl-2.0-or-later': 'lgpl-2.0-or-later',

    'pd or mit': 'licenseref-scancode-public-domain or mit',
    'public-domain': 'licenseref-scancode-public-domain',
    'unrestricted': 'licenseref-scancode-other-permissive',

    'open_source': 'licenseref-scancode-free-unknown',
    'as-is': 'licenseref-scancode-free-unknown',

    'elementtree': 'licenseref-scancode-secret-labs-2011 and bsd-3-clause',

    'cddl': 'cddl-1.1',

    'cc': 'cc-by-3.0 and licenseref-scancode-free-unknown',
    'cc-3.0': 'cc-by-sa-3.0',
    'cc-by-sa': 'cc-by-sa-3.0',
    'cc-3.0-by-sa': 'cc-by-sa-3.0',
    'cc-samplingplus-1.0': 'licenseref-scancode-cc-sampling-plus-1.0',
    'cc-sampling-plus-1.0': 'licenseref-scancode-cc-sampling-plus-1.0',
    'cc0': 'cc0-1.0',

    'classpath': 'classpath-exception-2.0',
    'fipl': 'licenseref-scancode-freeimage-1.0',

    'zpl': 'zpl-2.0',
    'wxwidgets': 'licenseref-scancode-wxwidgets',
    'uoi-ncsa': 'ncsa',
    'php': 'php-3.01',
    'pgpool-ii': 'ntp',

    'ofl': 'ofl-1.1',

    'exception': 'licenseref-scancode-generic-exception',
    'exceptions': 'licenseref-scancode-generic-exception',

    'mpl': 'mpl-1.1',
    'lppl-1.3': 'lppl-1.3c',
    'lsof': 'licenseref-scancode-purdue-bsd',

    'mit and ucd': 'mit and licenseref-scancode-other-permissive',

    'lgpl-2.0-or-later-with-linking-exception': 'lgpl-2.0-or-later with licenseref-scancode-generic-exception',

    'lgpl-2.1-with-linking-exception': 'lgpl-2.1-only with licenseref-scancode-generic-exception',
    'lgpl-2.1-only-with-linking-exception': 'lgpl-2.1-only with licenseref-scancode-generic-exception',
    'lgpl-2.1-or-later-with-linking-exception': 'lgpl-2.1-or-later with licenseref-scancode-generic-exception',
    'lgpl-2.1-or-later-with-linking-exception-and-mit': 'lgpl-2.1-or-later with licenseref-scancode-generic-exception and mit',

    'lgpl-2.1-or-later with ocaml-linking-exception': 'lgpl-2.1-or-later with ocaml-lgpl-linking-exception',
    'lgpl-2.1-or-later-with-ocaml-lgpl-linking-exception': 'lgpl-2.1-or-later with licenseref-scancode-generic-exception',
    'lgpl-2.1-or-later with custom-static-linking-exception': 'lgpl-2.1-or-later with licenseref-scancode-generic-exception',

    'lgpl-3.0-or-later with exceptions': 'lgpl-3.0-or-later with licenseref-scancode-generic-exception',
    'ttyp0': 'licenseref-scancode-ttyp0 and mit',

    # gopt license at https://www.purposeful.co.uk/tfl/
    'tfl': 'licenseref-scancode-public-domain-disclaimer',

    # misc custom licenses
    'custom': 'licenseref-scancode-unknown-license-reference',
    'custom:altermime':
        'licenseref-scancode-other-copyleft and licenseref-scancode-unknown-license-reference',
    'custom:bell': 'x11',

    'custom:boost': 'licenseref-scancode-unknown-license-reference',
    'custom:bsd': 'licenseref-scancode-unknown-license-reference',
    'custom:chromiumos': 'licenseref-scancode-unknown-license-reference',
    'custom:etpan': 'licenseref-scancode-unknown-license-reference',

    # seen only in gc
    'custom:gpl-like': 'licenseref-scancode-mozilla-gc',

    'custom:multiple': 'licenseref-scancode-unknown-license-reference',

    # this is a bit more than just hpnd
    'custom:pil': 'licenseref-scancode-secret-labs-2011',
    'custom:postcardware': 'licenseref-scancode-unknown-license-reference',
    'custom:sip': 'licenseref-scancode-unknown-license-reference',
    'custom:tu-berlin-2.0': 'licenseref-scancode-unknown-license-reference',

    'custom:xfree86': 'mit and x11 and hpnd-sell-variant and hpnd and mit-open-group and licenseref-scancode-other-permissive',

    'custom:xiph': 'bsd-3-clause',
    # seen in ttf-libertine
    'gpl and custom:ofl':  '(gpl-2.0 with font-exception-2.0) or ofl-1.1',

    'none': 'licenseref-scancode-unknown',
    # this is sometimes a IJG jpeg license and sometime an unknown/mitish license
    # as in https://github.com/tdtrask/lua-subprocess
    'as-is':  'licenseref-scancode-unknown-license-reference',

    # all recent versions are now MIT.
    # the happy license is otherwise licenseref-scancode-visual-idiot
    'happy': 'mit',

    # "with" mishaps
    'gpl-2.0 with classpath': 'gpl-2.0 with classpath-exception-2.0',
    'gpl-2.0-only with openssl-exception': 'gpl-2.0-only with licenseref-scancode-openssl-exception-gpl-2.0',
    'gpl-2.0-or-later with openssl-exception': 'gpl-2.0-or-later with licenseref-scancode-openssl-exception-gpl-2.0-plus',

    'gpl-3.0-only with openssl-exception': 'gpl-3.0-only with licenseref-scancode-openssl-exception-gpl-3.0-plus',
    'gpl-3.0-or-later with openssl-exception': 'gpl-3.0-or-later with licenseref-scancode-openssl-exception-gpl-3.0-plus',
    'agpl-3.0-or-later with openssl-exception': 'agpl-3.0-or-later with licenseref-scancode-openssl-exception-agpl-3.0-plus',
    'custom:tu-berlin-2.0': 'tu-berlin-2.0',

    'weird-motorola-license': 'licenseref-scancode-motorola',
}

DECLARED_TO_SPDX_SUBS = None


def apply_expressions_mapping(expression):
    """
    Return a new license expression string from an ``expression`` string
    replacing subexpressions using the DECLARED_TO_SPDX_SUBS expression
    subsitution table.
    """
    licensing = Licensing()

    global DECLARED_TO_SPDX_SUBS
    if not DECLARED_TO_SPDX_SUBS:
        DECLARED_TO_SPDX_SUBS = {
            licensing.parse(src, simple=True): licensing.parse(tgt, simple=True)
            for src, tgt in DECLARED_TO_SPDX.items()
        }

    try:
        expression = licensing.parse(expression, simple=True)
    except:
        raise Exception(expression)
    return str(expression.subs(DECLARED_TO_SPDX_SUBS))


def apkbuild_options_handler(value, **kwargs):
    """
    ``options`` is the "Build-time options for the package.". This option is
    useful:
        !spdx  Do not check if the license= field has a SPDX compliant license.
    """
    # TODO: implement me!


#################################################
# test code to test parse whole APKINDEX
if __name__ == '__main__':
    import sys

    def get_apkindex_licenses(locin, locout):
        from collections import defaultdict
        from commoncode.fileutils import resource_iter

        def collect_licenses_from_index(location):
            """
            Return packages_by_licenses with all licenses from apkindex found in the location tree
            """
            packages_by_licenses = defaultdict(list)
            for apkindex_loc in resource_iter(location, with_dirs=False):
                if not apkindex_loc.endswith('APKINDEX'):
                    continue
                """
                >>> a='/home/pombreda/tmp/alpine-indexes/apkindex-archive-master/alpine/v3.12/community/aarch64/APKINDEX'
                >>> '-'.join(a.split('/')[-4:])
                'v3.12-community-aarch64-APKINDEX'
                >>> '-'.join(a.split('/')[-4:-1])
                'v3.12-community-aarch64'
                """
                apkidx_id = '-'.join(apkindex_loc.split('/')[-4:-1])
                print(f'Processing: {apkindex_loc}')
                for package in parse_alpine_installed_db(apkindex_loc):
                    if not package:
                        continue
                    purl = package.purl
                    declared = ' '.join(package.declared_license.lower().split())
                    packages_by_licenses[declared].append((apkidx_id, purl,))
            return packages_by_licenses

        with open(locout, 'w') as output:
            line = '\t'.join(['declared_license', 'purl', 'distro', 'unique']) + '\n'
            output.write(line)
            for declared, packages in sorted(collect_licenses_from_index(locin).items()):
                if len(packages) == 1:
                    unique = 'yes'
                else:
                    unique = 'no'
                pidx, purl = packages[0]
                line = '\t'.join([declared, purl, pidx, unique]) + '\n'
                output.write(line)

    def get_apkbuild_licenses(locin, locout):
        from collections import defaultdict
        from commoncode.fileutils import resource_iter

        def collect_licenses_from_apkbuilds(location):
            """
            Return packages_by_licenses with all licenses from apkbuild found in
            the location tree
            """
            packages_by_licenses = defaultdict(list)
            for apkbuild_loc in resource_iter(location, with_dirs=False):
                """
                >>> a='/home/pombreda/tmp/alpine-indexes/apkindex-archive-master/alpine/v3.12/community/aarch64/APKINDEX'
                >>> '-'.join(a.split('/')[-4:])
                'v3.12-community-aarch64-APKINDEX'
                >>> '-'.join(a.split('/')[-4:-1])
                'v3.12-community-aarch64'
                """
                apkidx_id = '-'.join(apkbuild_loc.split('/')[-4:-1])
                print(f'Processing: {apkbuild_loc}')
                package = parse_apkbuild(apkbuild_loc)
                if not package:
                    continue
                purl = package.purl
                declic = ' '.join(package.declared_license.split())
                packages_by_licenses[declic].append((apkidx_id, purl,))
            return packages_by_licenses

        with open(locout, 'w') as output:
            line = '\t'.join(['declared', 'purl', 'distro', 'unique']) + '\n'
            output.write(line)
            for declared, packages in sorted(collect_licenses_from_apkbuilds(locin).items()):
                if len(packages) == 1:
                    unique = 'yes'
                else:
                    unique = 'no'
                pidx, purl = packages[0]
                line = '\t'.join([declared, purl, pidx, unique]) + '\n'
                output.write(line)

    def detect_licenses(locin, locout):
        """
        Run alpine license detection on the declared license found in the
        ``locin`` csv. Write results to ``locout`` csv.
        """
        with open(locin) as lines, open(locout, 'w') as output:
            line = '\t'.join(['declared', 'detected', 'purl', 'distro', 'unique']) + '\n'
            output.write(line)
            for i, line in enumerate(lines):
                line = line.strip()
                if not i or not line:
                    continue
                print('processing:', line)
                declared, purl, distro, unique = line.split('\t')
                _normalized, detected = detect_declared_license(declared)
                line = '\t'.join([declared, detected, purl, distro, unique]) + '\n'
                output.write(line)

    loc = sys.argv[1]
    # get_apkindex_licenses(loc, 'alpine-licenses.csv')
    get_apkbuild_licenses(loc, 'alpine-licenses.csv')
    detect_licenses('alpine-licenses.csv', 'alpine-licenses-detection.csv')
