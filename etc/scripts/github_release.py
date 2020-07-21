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
from commoncode.fileutils import resource_iter
import fnmatch
import os
import subprocess
import sys

python_version = str(sys.version_info[0]) + str(sys.version_info[1])
py_abi = "{0}cp{1}{0}".format("*", python_version)


def release_asset(token, tag, repo, body, user, limit, asset_dir):
    """
    Release .whl,.ABOUT,.NOTICE,.LICENSE to github repository from 
    given directory.
    """

    os.environ["GITHUB_TOKEN"] = token
    thirdparty = list(resource_iter(asset_dir, with_dirs=False))
    dependencies = [
        files
        for files in thirdparty
        if fnmatch.fnmatchcase(files, "*py3*")
        or fnmatch.fnmatchcase(files, py_abi)
        or (
            fnmatch.fnmatchcase(files, "*tar.gz*")
            and not fnmatch.fnmatchcase(files, "*py2-ipaddress-3.4.1.tar.gz*")
        )
    ]
    for deps in dependencies:
        subprocess.run(
            [
                "python3",
                "-m",
                "github_release_retry.github_release_retry",
                "--user",
                user,
                "--repo",
                repo,
                "--tag_name",
                tag,
                "--body_string",
                body,
                "--retry_limit",
                limit,
                deps,
            ]
        )


def main_with_args(args: str) -> None:
    parser = argparse.ArgumentParser(
        description="""Creates a GitHub release (if it does not already exist) and uploads files to the release.
Please pass the GITHUB_TOKEN as an argument.
EXAMPLE:
github-release-asset \\
  --user Abhishek-Dev09 \\
  --repo thirdparty \\
  --tag_name v1.0 \\
  --body_string "Python 3.6 wheels" \\
  hello-world.zip RELEASE_NOTES.txt
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--user",
        help="Required: The GitHub username or organization name in which the repo resides.",
        type=str,
        required=True,
    )

    parser.add_argument(
        "--token",
        help="Required: The Github token is required to acess the repository where you want to upload.",
        type=str,
        required=True,
    )

    parser.add_argument(
        "--repo",
        help="Required: The GitHub repo name in which to make the release.",
        type=str,
        required=True,
    )

    parser.add_argument(
        "--tag_name",
        help="Required: The name of the tag to create or use.",
        type=str,
        required=True,
    )

    parser.add_argument(
        "--body_string",
        help="Required (or use --body_file): Text describing the release. Ignored if the release already exists.",
        type=str,
    )

    parser.add_argument(
        "--retry_limit",
        help="The number of times to retry creating/getting the release and/or uploading each file.",
        type=str,
        default="10",
    )

    parser.add_argument(
        "--files", type=str, help="The files to upload to the release.",
    )

    args = parser.parse_args()

    token = args.token
    tag = args.tag_name
    repo = args.repo
    body = args.body_string
    user = args.user
    limit = args.retry_limit
    deps_dir = args.files

    release_asset(token, tag, repo, body, user, limit, deps_dir)


def main() -> None:
    main_with_args(sys.argv[1:])


if __name__ == "__main__":
    main()
