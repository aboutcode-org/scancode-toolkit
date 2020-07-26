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
from fnmatch import fnmatchcase
import os
from subprocess import run
import sys

from commoncode.fileutils import resource_iter

python_version = str(sys.version_info[0]) + str(sys.version_info[1])
py_abi = '{0}cp{1}{0}'.format('*', python_version)


def release_asset(token, tag, repo, body_string, user, retry_limit, asset_dir):
    """
    Release .whl,.ABOUT,.NOTICE,.LICENSE to github repository(repo) from asset_directory.
    It takes user and token as credential and tag_name,body_string for description of 
    release. By default retry_limit is 10.
    """

    os.environ['GITHUB_TOKEN'] = token
    thirdparty = list(resource_iter(asset_dir, with_dirs=False))
    dependencies = [
        files
        for files in thirdparty
        if fnmatchcase(files, '*py3*')
        or fnmatchcase(files, py_abi)
        or (
            fnmatchcase(files, '*tar.gz*')
            and not fnmatchcase(files, '*py2-ipaddress-3.4.1.tar.gz*')
        )
    ]
    for deps in dependencies:
        github_args = [
            'python3',
            '-m',
            'github_release_retry.github_release_retry',
            '--user',
            user,
            '--repo',
            repo,
            '--tag_name',
            tag,
            '--body_string',
            body_string,
            '--retry_limit',
            retry_limit,
            deps
        ]
        run(github_args)


def main_with_args(args: str) -> None:
    parser = argparse.ArgumentParser(
        description="""Creates a GitHub release (if it does not already exist) and uploads files to the release.
Please pass the GITHUB_TOKEN as an argument.
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        '--user',
        help='Required: The GitHub username or organization name in which the repo resides.',
        type=str,
        required=True,
    )

    parser.add_argument(
        '--token',
        help='Required: The Github token is required to acess the repository where you want to upload.',
        type=str,
        required=True,
    )

    parser.add_argument(
        '--repo',
        help='Required: The GitHub repo name in which to make the release.',
        type=str,
        required=True,
    )

    parser.add_argument(
        '--tag-name',
        help='Required: The name of the tag to create or use.',
        type=str,
        required=True,
    )

    parser.add_argument(
        '--body-string',
        help='Required : Text describing the release. Ignored if the release already exists.',
        type=str,
        required=True,
    )

    parser.add_argument(
        '--retry-limit',
        help='The number of times to retry creating/getting the release and/or uploading each file.',
        type=str,
        default='10',
    )

    parser.add_argument(
        '--directory',
         help='Required: The directory that contains files to upload to the release.',
         type=str,
         required=True,
    )

    args = parser.parse_args()

    token = args.token
    tag_name = args.tag_name
    repo = args.repo
    body_string = args.body_string
    user = args.user
    retry_limit = args.retry_limit
    directory = args.directory

    release_asset(token, tag_name, repo, body_string, user, retry_limit, directory)


def main() -> None:
    main_with_args(sys.argv[1:])


if __name__ == '__main__':
    main()
