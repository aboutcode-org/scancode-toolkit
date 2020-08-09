# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
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

import argparse
from pathlib import Path
import os
import sys

from github_release_retry import github_release_retry as grr

from commoncode.fileutils import resource_iter


"""
Create GitHUb releases and upload  files there.
This depends on the `github_release_retry` utility
https://github.com/google/github-release-retry
"""


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

    api = grr.GithubApi(
        github_api_url='https://api.github.com',
        user=user,
        repo=repo,
        token=token,
        retry_limit=retry_limit,
    )
    release = grr.Release(tag_name=tag_name, body=description)
    files = [Path(r) for r in resource_iter(directory, with_dirs=False)]
    grr.make_release(api, release, files)


def main_with_args(args):
    parser = argparse.ArgumentParser(
        description=(
            'Create (or update) a GitHub release and upload all the '
            'files of DIRECTORY to that release.'
        ),
    )

    parser.add_argument(
        '--user',
        help='The GitHub username or organization in which the repository resides.',
        type=str,
        required=True,
    )

    parser.add_argument(
        '--repo',
        help=' The GitHub repository name in which to create the release.',
        type=str,
        required=True,
    )

    parser.add_argument(
        '--tag-name',
        help='The name of the tag to create (or re-use) for this release.',
        type=str,
        required=True,
    )

    parser.add_argument(
        '--directory',
         help='The directory that contains files to upload to the release.',
         type=str,
         required=True,
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
        help=(
            'Number of retries when making failing GitHub API calls. '
            'Retrying helps work around transient failures of the GitHub API.'
        ),
        type=int,
        default=10,
    )

    args = parser.parse_args()
    token = args.token or os.environ.get('GITHUB_TOKEN', None)
    if not token:
        print('--token required option is missing.')
        print(TOKEN_HELP)
        sys.exit(1)

    create_or_update_release_and_upload_directory(
        user=args.user,
        repo=args.repo,
        tag_name=args.tag_name,
        description=args.description,
        retry_limit=args.retry_limit,
        token=token,
        directory=args.directory,
    )


def main():
    main_with_args(sys.argv[1:])


if __name__ == '__main__':
    main()
