#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

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


def yield_dependencies_from_package_resource(resource, package_uid=None):
    """
    Yield a Dependency for each dependency from each package from``resource.package_data``
    """
    from packagedcode import models
    for pkg_data in resource.package_data:
        pkg_data = models.PackageData.from_dict(pkg_data)
        yield from yield_dependencies_from_package_data(pkg_data, resource.path, package_uid)
