#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import logging
import re

from oelint_parser.cls_stash import Stash
from packageurl import PackageURL

from packagedcode import models

TRACE = True

logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


class BitbakeBbManifestHandler(models.DatafileHandler):
    datasource_id = 'bitbake_bb_recipe'
    # note that there are .bbappend, .bbclass and bitbake.conf files.
    path_patterns = ('*.bb',)
    default_package_type = 'bitbake'
    description = 'BitBake bb recipe manifest'
    documentation_url = 'https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-metadata.html'

    @classmethod
    def parse(cls, location):

        oestash = Stash(quiet=True)

        # add any bitbake like-file
        # TODO: may be we should handle the bbclass and bbappend here?
        oestash.AddFile(location)

        # Resolves proper cross file dependencies
        oestash.Finalize()

        # collect all variables of interest.
        # TODO: we should not get list values. Instead plain strings
        data = {
            k: ' '.join(v) if isinstance(v, (list, tuple)) else v
            for k, v in oestash.ExpandVar(filename=location).items()
            if v
        }
        name = data.get('PN')
        version = data.get('PV')
        description = data.get('DESCRIPTION')
        homepage_url = data.get('HOMEPAGE')
        download_url = data.get('PREMIRRORS')
        declared_license = data.get('LICENSE')

        # The item.VarName for SRC_URI[*] from the parser are SRC_URI
        # Therefore, I cannot differentiate md5, sha1, or src file location reference
        # See: https://github.com/priv-kweihmann/oelint-parser/issues/3
        sha1 = data.get('SRC_URI[sha1sum]')
        md5 = data.get('SRC_URI[md5sum]')
        sha256 = data.get('SRC_URI[sha256sum]')
        sha512 = data.get('SRC_URI[sha512sum]')

        dependencies = []

        # Build deps: this is a list of plain BB recipes names
        # https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-ref-variables.html#term-DEPENDS
        build_deps = data.get('DEPENDS', '').split()
        for build_dep in build_deps:
            dep_purl = PackageURL(
                type=cls.default_package_type,
                name=build_dep,
            ).to_string()

            dependency = models.DependentPackage(
                purl=dep_purl,
                extracted_requirement=build_dep,
                scope='build',
                is_runtime=False,
                is_optional=True,
                is_resolved=False,
            )
            dependencies.append(dependency)

        # Runtime deps:this is a list of Package names with an optional (=> 12) version constraint
        # https://docs.yoctoproject.org/bitbake/bitbake-user-manual/bitbake-user-manual-ref-variables.html#term-RDEPENDS
        # FIXME: There are some fields such as "RDEPENDS_${PN}" so these may not be correct in all cases
        for key, value in data.items():
            if not key.startswith('RDEPENDS'):
                continue
            if not value:
                continue
            for name, constraint in get_bitbake_deps(dependencies=value):
                if TRACE:
                    logger.debug(f'RDEPENDS: name={name}, constraint={constraint}')
                dep_purl = PackageURL(
                    type=cls.default_package_type,
                    name=name,
                ).to_string()

                extracted_requirement = name
                if constraint:
                    extracted_requirement += f' ({constraint})'

                dependency = models.DependentPackage(
                    purl=dep_purl,
                    extracted_requirement=extracted_requirement,
                    scope='install',
                    is_runtime=True,
                    is_optional=False,
                    is_resolved=False,
                )

                dependencies.append(dependency)

        yield models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=name,
            version=version,
            description=description,
            homepage_url=homepage_url,
            download_url=download_url,
            sha1=sha1,
            md5=md5,
            sha256=sha256,
            sha512=sha512,
            declared_license=declared_license,
            dependencies=dependencies,
        )

    @classmethod
    def assign_package_to_resources(cls, package, resource, codebase, package_adder):
        return models.DatafileHandler.assign_package_to_parent_tree(package, resource, codebase, package_adder)


def get_bitbake_deps(dependencies):
    """
    Return a list of tuple of (name, version constraint) given a BitBake
    dependencies string. "version constraint" can be None.

    See https://docs.yoctoproject.org/ref-manual/variables.html?#term-RDEPENDS
    For example:
    >>> expected = [('ABC', None), ('abcd', '=>12312'), ('defg', None)]
    >>> result = get_bitbake_deps(" ABC abcd (= >  12312) defg ")
    >>> assert result == expected, result
    >>> expected = [('grub', '==12.23'), ('parted', None), ('e2fsprogs-mke2fs', None)]
    >>> result = get_bitbake_deps("grub (== 12.23) parted e2fsprogs-mke2fs")
    >>> assert result == expected, result
    """
    return [split_name_constraint(nc) for nc in split_deps(dependencies)]


def split_name_constraint(dependency):
    """
    Return a tuple (name, version constraint) strings given a name (version
    constraint) BitBake dependency string.
    See https://docs.yoctoproject.org/ref-manual/variables.html?#term-RDEPENDS
    For example:
    >>> assert split_name_constraint(" abcd  ( = 12312 ) ") == ("abcd", "=12312",)
    >>> assert split_name_constraint("abcd ") == ("abcd", None)
    """
    no_spaces = dependency.replace(' ', '')
    if '(' in no_spaces:
        name, _, constraint = no_spaces.partition('(')
        constraint = constraint.rstrip(')')
        return name, constraint
    return no_spaces, None


def split_deps(dependencies):
    """
    Return a list of name (version constraint) strings given a BitBake
    dependencies string.

    See https://docs.yoctoproject.org/ref-manual/variables.html?#term-RDEPENDS
    For example:
    >>> expected = ['ABC', 'abcd (= > 12312)', 'defg', 'foo', 'bar']
    >>> result = split_deps(" ABC abcd (= >  12312) defg   foo bar ")
    >>> assert result == expected, result
    """
    normalized_spaces = ' '.join(dependencies.split())
    name = r'\w[\w\d_-]+'
    version_constraint = r'\([<>= ]+[^<>= ]+\s?\)'
    splitter = re.compile(fr'({name}\s?(?:{version_constraint})?)').findall
    return [s.strip() for s in splitter(normalized_spaces)]
