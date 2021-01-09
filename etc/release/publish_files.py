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

import hashlib
from pathlib import Path
import os
import sys

import click
from github_release_retry import github_release_retry as grr
import utils_thirdparty

"""
Create GitHub releases and upload files there.
"""


def get_files(location):
    """
    Return an iterable of (filename, Path, md5) tuples for files in the `location`
    directory tree recursively.
    """
    for top, _dirs, files in os.walk(location):
        for filename in files:
            pth = Path(os.path.join(top, filename))
            with open(pth, 'rb') as fi:
                md5 = hashlib.md5(fi.read()).hexdigest()
            yield filename, pth, md5


def get_etag_md5(url):
    """
    Return the cleaned etag of URL `url` or None.
    """
    etag = utils_thirdparty.get_remote_headers(url).get('ETag')
    if etag:
        etag = etag.strip('"').lower()
        return etag


def create_or_update_release_and_upload_directory(
        user,
        repo,
        tag_name,
        token,
        directory,
        retry_limit=10,
        description=None,
):
    """
    Create or update a GitHub release at https://github.com/<user>/<repo> for
    `tag_name` tag using the optional `description` for this release.
    Use the provided `token` as a GitHub token for API calls authentication.
    Upload all files found in the `directory` tree to that GitHub release.
    Retry API calls up to `retry_limit` time to work around instability the
    GitHub API.
    """
    base_url = f'https://github.com/{user}/{repo}/releases/{tag_name}'
    urls_by_fn = {os.path.basename(l): l
        for l in utils_thirdparty.get_paths_or_urls(links_url=base_url)
    }

    files_to_upload = []
    for filename, pth, md5 in get_files(directory):
        url = urls_by_fn.get(filename)
        if not url:
            print(f'{filename} content is NEW, will upload')
            files_to_upload.append(pth)
            continue

        out_of_date = get_etag_md5(url) != md5
        if out_of_date:
            print(f'{url} content is CHANGED based on etag, will re-upload')
            files_to_upload.append(pth)
        else:
            print(f'{url} content is IDENTICAL, skipping upload based on Etag')

    n = len(files_to_upload)
    print(f'Publishing directory {directory} with {n} files to {base_url}')
    api = grr.GithubApi(
        github_api_url='https://api.github.com',
        user=user,
        repo=repo,
        token=token,
        retry_limit=retry_limit,
    )

    release = grr.Release(tag_name=tag_name, body=description)
    grr.make_release(api, release, files_to_upload)


TOKEN_HELP = (
    'The Github personal acess token is used to authenticate API calls. '
    'Required unless you set the GITHUB_TOKEN environment variable as an alternative. '
    'See for details: https://github.com/settings/tokens and '
    'https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token'
)


@click.command()

@click.option(
    '--user-repo-tag',
    help='The GitHub qualified repository user/name/tag in which '
        'to create the release as in nexB/thirdparty/pypi',
    type=str,
    default='nexB/thirdparty-packages/pypi',
    required=False,
)
@click.option(
    '-d', '--directory',
    help='The directory that contains files to upload to the release.',
    type=click.Path(exists=True, readable=True, path_type=str, file_okay=False, resolve_path=True),
    default='thirdparty',
    required=True,
)
@click.option(
    '--token',
    help=TOKEN_HELP,
    default=os.environ.get('GITHUB_TOKEN', None),
    type=str,
    required=False,
)
@click.option(
    '--description',
    help='Text description for the release. Ignored if the release exists.',
    default=None,
    type=str,
    required=False,
)
@click.option(
    '--retry_limit',
    help='Number of retries when making failing GitHub API calls. '
        'Retrying helps work around transient failures of the GitHub API.',
    type=int,
    default=10,
)
@click.help_option('-h', '--help')
def publish_files(
    user_repo_tag,
    directory,
    retry_limit=10, token=None, description=None,
):
    """
    Publish all the files in DIRECTORY as assets to a GitHub release.
    Either create or update/replace remote files'
    """
    if not token:
        click.secho('--token required option is missing.')
        click.secho(TOKEN_HELP)
        sys.exit(1)

    user, repo, tag_name = user_repo_tag.split('/')

    create_or_update_release_and_upload_directory(
        user=user,
        repo=repo,
        tag_name=tag_name,
        description=description,
        retry_limit=retry_limit,
        token=token,
        directory=directory,
    )


if __name__ == '__main__':
    publish_files()
