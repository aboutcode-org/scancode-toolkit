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

import argparse
from pathlib import Path
import os
import sys

from github_release_retry import github_release_retry as grr

"""
Create GitHub releases and upload files there.
"""


def files_iter(location):
    """
    Return an iterable of file paths at `location` recursively.
    """
    for top, _dirs, files in os.walk(location):
        for f in files:
            yield os.path.join(top, f)


def create_or_update_release_and_upload_directory(
        user,
        repo,
        tag_name,
        token,
        directory,
        retry_limit=10,
        description=None
):
    """
    Create or update a GitHub release at https://github.com/<user>/<repo> for
    `tag_name` tag using the optional `description` for this release.
    Use the provided `token` as a GitHub token for API calls authentication.
    Upload all files found in the `directory` tree to that GitHub release.
    Retry API calls up to `retry_limit` time to work around instability the
    GitHub API.
    """

    files = [Path(r) for r in files_iter(directory)]
    n = len(files)
    print(f'Publishing directory {directory} with {n} files to https://github.com/{user}/{repo}/releases/{tag_name}')
    api = grr.GithubApi(
        github_api_url='https://api.github.com',
        user=user,
        repo=repo,
        token=token,
        retry_limit=retry_limit,
    )
    release = grr.Release(tag_name=tag_name, body=description)
    grr.make_release(api, release, files)


def main(args):
    parser = argparse.ArgumentParser(
        description=(
            'Create (or update) a GitHub release and upload all the '
            'files of DIRECTORY to that release.'
        ),
    )

    parser.add_argument(
        '--user_repo_tag',
        help=' The GitHub qualified repository user/name/tag in which to create the release as in nexB/thirdparty/pypi',
        type=str,
        default='nexB/thirdparty-packages/pypi',
        required=False,
    )

    parser.add_argument(
        '--directory',
        help='The directory that contains files to upload to the release.',
        type=str,
        default='thirdparty',
        required=False,
    )

    TOKEN_HELP = (
        'The Github personal acess token is used to authenticate API calls. '
        'Required unless you set the GITHUB_TOKEN environment variable as an alternative. '
        'See for details: https://github.com/settings/tokens and '
        'https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token'
    )

    parser.add_argument(
        '--token',
        help=TOKEN_HELP,
        type=str,
        required=False,
    )

    parser.add_argument(
        '--description',
        help='Text description for the release. Ignored if the release exists.',
        type=str,
        required=False,
    )

    parser.add_argument(
        '--retry_limit',
        help='Number of retries when making failing GitHub API calls. '
            'Retrying helps work around transient failures of the GitHub API.',
        type=int,
        default=10,
    )

    args = parser.parse_args(args)
    token = args.token or os.environ.get('GITHUB_TOKEN', None)
    if not token:
        print('--token required option is missing.')
        print(TOKEN_HELP)
        sys.exit(1)

    user, repo, tag_name = args.user_repo_tag.split('/')

    create_or_update_release_and_upload_directory(
        user=user,
        repo=repo,
        tag_name=tag_name,
        description=args.description,
        retry_limit=args.retry_limit,
        token=token,
        directory=args.directory,
    )


if __name__ == '__main__':
    main(sys.argv[1:])
