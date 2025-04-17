#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from packageurl import PackageURL

try:
    from license_expression import Licensing
    from license_expression import combine_expressions as le_combine_expressions
except:
    Licensing = None
    le_combine_expressions = None

PLAIN_URLS = (
    'https://',
    'http://',
)

VCS_URLS = (
    'git://',
    'git+git://',
    'git+https://',
    'git+http://',

    'hg://',
    'hg+http://',
    'hg+https://',

    'svn://',
    'svn+https://',
    'svn+http://',
)


# TODO this does not really normalize the URL
# TODO handle vcs_tool
def normalize_vcs_url(repo_url, vcs_tool=None):
    """
    Return a normalized vcs_url version control URL given some `repo_url` and an
    optional `vcs_tool` hint (such as 'git', 'hg', etc.

    Handles shortcuts for GitHub, GitHub gist, Bitbucket, or GitLab repositories
    and more using the same approach as npm install:

    See https://docs.npmjs.com/files/package.json#repository
    or https://getcomposer.org/doc/05-repositories.md

    This is done here in npm:
    https://github.com/npm/npm/blob/d3c858ce4cfb3aee515bb299eb034fe1b5e44344/node_modules/hosted-git-info/git-host-info.js

    These should be resolved:
        npm/npm
        gist:11081aaa281
        bitbucket:example/repo
        gitlab:another/repo
        expressjs/serve-static
        git://github.com/angular/di.js.git
        git://github.com/hapijs/boom
        git@github.com:balderdashy/waterline-criteria.git
        http://github.com/ariya/esprima.git
        http://github.com/isaacs/nopt
        https://github.com/chaijs/chai
        https://github.com/christkv/kerberos.git
        https://gitlab.com/foo/private.git
        git@gitlab.com:foo/private.git
    """
    if not repo_url or not isinstance(repo_url, str):
        return

    repo_url = repo_url.strip()
    if not repo_url:
        return

    # TODO: If we match http and https, we may should add more check in
    # case if the url is not a repo one. For example, check the domain
    # name in the url...
    if repo_url.startswith(VCS_URLS + PLAIN_URLS):
        return repo_url

    if repo_url.startswith('git@'):
        tool, _, right = repo_url.partition('@')
        if ':' in repo_url:
            host, _, repo = right.partition(':')
        else:
            # git@github.com/Filirom1/npm2aur.git
            host, _, repo = right.partition('/')

        if any(r in host for r in ('bitbucket', 'gitlab', 'github')):
            scheme = 'https'
        else:
            scheme = 'git'

        return '%(scheme)s://%(host)s/%(repo)s' % locals()

    # FIXME: where these URL schemes come from??
    if repo_url.startswith(('bitbucket:', 'gitlab:', 'github:', 'gist:')):
        hoster_urls = {
            'bitbucket': 'https://bitbucket.org/%(repo)s',
            'github': 'https://github.com/%(repo)s',
            'gitlab': 'https://gitlab.com/%(repo)s',
            'gist': 'https://gist.github.com/%(repo)s', }
        hoster, _, repo = repo_url.partition(':')
        return hoster_urls[hoster] % locals()

    if len(repo_url.split('/')) == 2:
        # implicit github, but that's only on NPM?
        return f'https://github.com/{repo_url}'

    return repo_url


def build_description(summary, description):
    """
    Return a description string from a summary and description
    """
    summary = (summary or '').strip()
    description = (description or '').strip()

    if not description:
        description = summary
    else:
        if summary and summary not in description:
            description = '\n'.join([summary , description])

    return description


_LICENSING = Licensing and Licensing() or None


def combine_expressions(
    expressions,
    relation='AND',
    unique=True,
    licensing=_LICENSING,
):
    """
    Return a combined license expression string with relation, given a sequence of
    license ``expressions`` strings or LicenseExpression objects.
    """
    if not licensing:
        raise Exception('combine_expressions: cannot combine combine_expressions without license_expression package.')
    return expressions and str(le_combine_expressions(expressions, relation, unique, licensing)) or None


def get_ancestor(levels_up, resource, codebase):
    """
    Return the nth-``levels_up`` ancestor Resource of ``resource`` in
    ``codebase`` or None.

    For example, with levels_up=2 and starting  with a resource path of
    `gem-extract/metadata.gz-extract/metadata.gz-extract`,
    then `gem-extract/` should be returned.
    """
    rounds = 0
    while rounds < levels_up:
        resource = resource.parent(codebase)
        if not resource:
            return
        rounds += 1
    return resource


def find_root_from_paths(paths, resource, codebase):
    """
    Return the resource for the root directory of this filesystem or None, given
    a ``resource`` in ``codebase`` with a list of possible resource root-
    relative  ``paths`` (e.g. extending from the root directory we are looking
    for).
    """
    for path in paths:
        if not resource.path.endswith(path):
            continue
        return find_root_resource(path=path, resource=resource, codebase=codebase)


def find_root_resource(path, resource, codebase):
    """
    Return the resource for the root directory of this filesystem or None, given
    a ``resource`` in ``codebase`` with a possible resource root-relative
    ``path`` (e.g. extending from the root directory we are looking for).
    """
    if not resource.path.endswith(path):
        return
    for _seg in path.split('/'):
        resource = resource.parent(codebase)
        if not resource:
            return
    return resource


def yield_dependencies_from_package_data(package_data, datafile_path, package_uid):
    """
    Yield a Dependency for each dependency from ``package_data.dependencies``
    """
    from packagedcode import models
    dependent_packages = package_data.dependencies
    if dependent_packages:
        yield from models.Dependency.from_dependent_packages(
            dependent_packages=dependent_packages,
            datafile_path=datafile_path,
            datasource_id=package_data.datasource_id,
            package_uid=package_uid,
        )


def parse_maintainer_name_email(maintainer):
    """
    Get name and email values from a author/maintainer string.

    Example string:
    Debian systemd Maintainers <pkg-systemd-maintainers@lists.alioth.debian.org>
    """
    email_wrappers = ["<", ">"]
    has_email = "@" in maintainer and all([
        True 
        for char in email_wrappers
        if char in maintainer
    ])
    if not has_email:
        return maintainer, None

    name, _, email = maintainer.rpartition("<")
    return name.rstrip(" "), email.rstrip(">")


def yield_dependencies_from_package_resource(resource, package_uid=None):
    """
    Yield a Dependency for each dependency from each package from``resource.package_data``
    """
    from packagedcode import models
    for pkg_data in resource.package_data:
        pkg_data = models.PackageData.from_dict(pkg_data)
        yield from yield_dependencies_from_package_data(pkg_data, resource.path, package_uid)


def update_dependencies_as_resolved(dependencies):
    """
    For a list of dependency mappings with their respective
    resolved packages, update in place the dependencies for those
    resolved packages as resolved (update `is_pinned` as True),
    if the requirement is also present as a resolved package.
    """
    #TODO: Use vers to mark update `is_pinned` even in the case
    # of incomplete resolution/partially pinned dependencies

    # These are only type, namespace and name (without version and qualifiers)
    base_resolved_purls = []
    resolved_packages = [
        dep.get("resolved_package")
        for dep in dependencies
        if dep.get("resolved_package")
    ]

    # No resolved packages are present for dependencies
    if not resolved_packages:
        return

    for pkg in resolved_packages:
        purl=pkg.get("purl")
        if purl:
            base_resolved_purls.append(
                get_base_purl(purl=purl)
            )

    for dependency in dependencies:
        resolved_package = dependency.get("resolved_package")
        dependencies_from_resolved = []
        if resolved_package:
            dependencies_from_resolved = resolved_package.get("dependencies")

        if not dependencies_from_resolved:
            continue

        for dep in dependencies_from_resolved:
            dep_purl = dep.get("purl")
            if dep_purl in base_resolved_purls:
                dep["is_pinned"] = True


def get_base_purl(purl):
    """
    Get a base purl with only the type, name and namespace from
    a given purl.
    """
    base_purl_fields = ["type", "namespace", "name"]
    purl_mapping = PackageURL.from_string(purl=purl).to_dict()
    base_purl_mapping = {
        purl_field: purl_value
        for purl_field, purl_value in purl_mapping.items()
        if purl_field in base_purl_fields
    }
    return PackageURL(**base_purl_mapping).to_string()


def is_simple_path(path):
    return '*' not in path


def is_simple_path_pattern(path):
    return path.endswith('*') and path.count('*') == 1
