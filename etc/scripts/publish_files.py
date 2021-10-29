#!/usr/bin/env python
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#
import hashlib
import os
import sys

from pathlib import Path

import click
import requests
import utils_thirdparty

from github_release_retry import github_release_retry as grr

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
            with open(pth, "rb") as fi:
                md5 = hashlib.md5(fi.read()).hexdigest()
            yield filename, pth, md5


def get_etag_md5(url):
    """
    Return the cleaned etag of URL `url` or None.
    """
    headers = utils_thirdparty.get_remote_headers(url)
    headers = {k.lower(): v for k, v in headers.items()}
    etag = headers.get("etag")
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

    Remote files that are not the same as the local files are deleted and re-
    uploaded.
    """
    release_homepage_url = f"https://github.com/{user}/{repo}/releases/{tag_name}"

    # scrape release page HTML for links
    urls_by_filename = {
        os.path.basename(l): l
        for l in utils_thirdparty.get_paths_or_urls(links_url=release_homepage_url)
    }

    # compute what is new, modified or unchanged
    print(f"Compute which files is new, modified or unchanged in {release_homepage_url}")

    new_to_upload = []
    unchanged_to_skip = []
    modified_to_delete_and_reupload = []
    for filename, pth, md5 in get_files(directory):
        url = urls_by_filename.get(filename)
        if not url:
            print(f"{filename} content is NEW, will upload")
            new_to_upload.append(pth)
            continue

        out_of_date = get_etag_md5(url) != md5
        if out_of_date:
            print(f"{url} content is CHANGED based on md5 etag, will re-upload")
            modified_to_delete_and_reupload.append(pth)
        else:
            # print(f'{url} content is IDENTICAL, skipping upload based on Etag')
            unchanged_to_skip.append(pth)
            print(".")

    ghapi = grr.GithubApi(
        github_api_url="https://api.github.com",
        user=user,
        repo=repo,
        token=token,
        retry_limit=retry_limit,
    )

    # yank modified
    print(
        f"Unpublishing {len(modified_to_delete_and_reupload)} published but "
        f"locally modified files in {release_homepage_url}"
    )

    release = ghapi.get_release_by_tag(tag_name)

    for pth in modified_to_delete_and_reupload:
        filename = os.path.basename(pth)
        asset_id = ghapi.find_asset_id_by_file_name(filename, release)
        print(f"  Unpublishing file: {filename}).")
        response = ghapi.delete_asset(asset_id)
        if response.status_code != requests.codes.no_content:  # NOQA
            raise Exception(f"failed asset deletion: {response}")

    # finally upload new and modified
    to_upload = new_to_upload + modified_to_delete_and_reupload
    print(f"Publishing with {len(to_upload)} files to {release_homepage_url}")
    release = grr.Release(tag_name=tag_name, body=description)
    grr.make_release(ghapi, release, to_upload)


TOKEN_HELP = (
    "The Github personal acess token is used to authenticate API calls. "
    "Required unless you set the GITHUB_TOKEN environment variable as an alternative. "
    "See for details: https://github.com/settings/tokens and "
    "https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token"
)


@click.command()
@click.option(
    "--user-repo-tag",
    help="The GitHub qualified repository user/name/tag in which "
    "to create the release such as in nexB/thirdparty/pypi",
    type=str,
    required=True,
)
@click.option(
    "-d",
    "--directory",
    help="The directory that contains files to upload to the release.",
    type=click.Path(exists=True, readable=True, path_type=str, file_okay=False, resolve_path=True),
    required=True,
)
@click.option(
    "--token",
    help=TOKEN_HELP,
    default=os.environ.get("GITHUB_TOKEN", None),
    type=str,
    required=False,
)
@click.option(
    "--description",
    help="Text description for the release. Ignored if the release exists.",
    default=None,
    type=str,
    required=False,
)
@click.option(
    "--retry_limit",
    help="Number of retries when making failing GitHub API calls. "
    "Retrying helps work around transient failures of the GitHub API.",
    type=int,
    default=10,
)
@click.help_option("-h", "--help")
def publish_files(
    user_repo_tag,
    directory,
    retry_limit=10,
    token=None,
    description=None,
):
    """
    Publish all the files in DIRECTORY as assets to a GitHub release.
    Either create or update/replace remote files'
    """
    if not token:
        click.secho("--token required option is missing.")
        click.secho(TOKEN_HELP)
        sys.exit(1)

    user, repo, tag_name = user_repo_tag.split("/")

    create_or_update_release_and_upload_directory(
        user=user,
        repo=repo,
        tag_name=tag_name,
        description=description,
        retry_limit=retry_limit,
        token=token,
        directory=directory,
    )


if __name__ == "__main__":
    publish_files()
