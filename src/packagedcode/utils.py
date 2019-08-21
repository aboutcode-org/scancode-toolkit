#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict

from license_expression import Licensing
from six import string_types


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
    if not repo_url or not isinstance(repo_url, string_types):
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
        return 'https://github.com/%(repo_url)s' % locals()

    return repo_url


# for legacy compat
parse_repo_url = normalize_vcs_url


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


def combine_expressions(expressions, relation='AND', licensing=Licensing()):
    """
    Return a combined license expression string with relation, given a list of
    license expressions strings.

    For example:
    >>> a = 'mit'
    >>> b = 'gpl'
    >>> combine_expressions([a, b])
    'mit AND gpl'
    >>> assert 'mit' == combine_expressions([a])
    >>> combine_expressions([])
    >>> combine_expressions(None)
    >>> combine_expressions(('gpl', 'mit', 'apache',))
    'gpl AND mit AND apache'
    """
    if not expressions:
        return

    if not isinstance(expressions, (list, tuple)):
        raise TypeError(
            'expressions should be a list or tuple and not: {}'.format(
                type(expressions)))

    # Remove duplicate element in the expressions list
    expressions = list(OrderedDict((x, True) for x in expressions).keys())

    if len(expressions) == 1:
        return expressions[0]

    expressions = [licensing.parse(le, simple=True) for le in expressions]
    if relation == 'OR':
        return str(licensing.OR(*expressions))
    else:
        return str(licensing.AND(*expressions))
