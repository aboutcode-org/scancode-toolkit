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

from six import string_types

from license_expression import Licensing

from packagedcode import models


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


#TODO this does not really normalize the URL
#TODO handle vcs_tool
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
            'gist': 'https://gist.github.com/%(repo)s',}
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


def compute_normalized_license(declared_license):
    """
    Return a detected license expression from a declared license mapping.
    This is for maven and npm packages.
    """
    if not declared_license:
        return

    licensing = Licensing()

    detected_licenses = []
    
    if isinstance(declared_license, string_types):
        # if the declared_license is a string, use list to wrapper it and use the following loop to handle in order not to have to many if condition
        declared_license = [declared_license]
    for license_declaration in declared_license:
        if isinstance(license_declaration, string_types):
            license_declaration = models.compute_normalized_license(license_declaration)
            if license_declaration:
                detected_licenses.append(license_declaration)
        elif isinstance(license_declaration, dict):
            # 1. try detection on the value of name if not empty and keep this
            name = license_declaration.get('name')
            if not name:
                # this is for npm, npm has type field instead of name
                name = license_declaration.get('type')
            via_name = models.compute_normalized_license(name)
    
            # 2. try detection on the value of url  if not empty and keep this
            url = license_declaration.get('url')
            via_url = models.compute_normalized_license(url)
    
            # 3. try detection on the value of comment  if not empty and keep this
            comments = license_declaration.get('comments')
            via_comments = models.compute_normalized_license(comments)
    
    
            if via_name:
                # The name should have precedence and any unknowns
                # in url and comment should be ignored.
                if via_url == 'unknown':
                    via_url = None
                if via_comments == 'unknown':
                    via_comments = None
    
            # Check the three detections to decide which license to keep
            name_and_url = via_name == via_url
            name_and_comment = via_name == via_comments
            all_same = name_and_url and name_and_comment
    
            if via_name:
                if all_same:
                    detected_licenses.append(via_name)
    
                # name and (url or comment) are same
                elif name_and_url and not via_comments:
                    detected_licenses.append(via_name)
                elif name_and_comment and not via_url:
                    detected_licenses.append(via_name)
    
                else:
                    # we have some non-unknown license detected in url or comment
                    detections = via_name, via_url, via_comments
                    detections = [l for l in detections if l]
                    if detections:
                        if len(detections) == 1:
                            combined_expression = detections[0]
                        else:
                            expressions = [
                                licensing.parse(le, simple=True) for le in detections]
                            combined_expression = str(licensing.AND(*expressions))
                        detected_licenses.append(combined_expression)
    
            elif via_url:
                detected_licenses.append(via_url)
            elif via_comments:
                detected_licenses.append(via_comments)

    if len(detected_licenses) == 1:
        return detected_licenses[0]

    if detected_licenses:
        # Combine if pom contains more than one licenses declarations.
        expressions = [licensing.parse(le, simple=True) for le in detected_licenses]
        combined_expression = licensing.AND(*expressions)
        return str(combined_expression)
