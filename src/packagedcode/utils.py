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

VCS_URLS = (
    'https://',
    'http://',
    'git://',
    'git+git://',
    'hg+https://',
    'hg+http://',
    'git+https://',
    'git+http://',
    'svn+https://',
    'svn+http://',
    'svn://',
)


def parse_repo_url(repo_url):
    """
    Validate a repo_ulr and handle shortcuts for GitHub, GitHub gist,
    Bitbucket, or GitLab repositories (same syntax as npm install):

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
    if not repo_url or not isinstance(repo_url, basestring):
        return

    repo_url = repo_url.strip()
    if not repo_url:
        return

    # TODO: If we match http and https, we may should add more check in
    # case if the url is not a repo one. For example, check the domain
    # name in the url...
    is_vcs_url = repo_url.startswith(VCS_URLS)
    if is_vcs_url:
        return repo_url

    if repo_url.startswith('git@'):
        left, _, right = repo_url.partition('@')
        if ':' in repo_url:
            host, _, repo = right.partition(':')
        else:
            # git@github.com/Filirom1/npm2aur.git
            host, _, repo = right.partition('/')
        if any(h in host for h in ['github', 'bitbucket', 'gitlab']):
            return 'https://%(host)s/%(repo)s' % locals()
        else:
            return repo_url

    if repo_url.startswith(('bitbucket:', 'gitlab:', 'github:', 'gist:')):
        hoster_urls = {
            'bitbucket': 'https://bitbucket.org/%(repo)s',
            'github': 'https://github.com/%(repo)s',
            'gitlab': 'https://gitlab.com/%(repo)s',
            'gist': 'https://gist.github.com/%(repo)s',
        }
        hoster, _, repo = repo_url.partition(':')
        return hoster_urls[hoster] % locals()
    elif len(repo_url.split('/')) == 2:
        # implicit github
        return 'https://github.com/%(repo_url)s' % locals()
    return repo_url


def join_texts(*args):
    """
    Return a string joining args with new lines or None.
    """
    description = [v for v in args if v and v.strip()]
    description = u'\n'.join(description) or None
    return description.strip() or None
