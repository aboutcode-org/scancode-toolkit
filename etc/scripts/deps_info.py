# -*- coding: utf-8 -*-
#
# Copyright nexB Inc. and others. All rights reserved.
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
import fnmatch
from commoncode.fileutils import resource_iter
import sys


def search_package(package_name, target, version):
    """
    Search specific package in given directory with all corresponding files.
    """

    if version:
        package_name = "*{}-{}*".format(package_name, version)
    else:
        package_name = "*{}*".format(package_name)
    thirdparty = resource_iter(target, with_dirs=False)
    dependency = [
        files for files in thirdparty if fnmatch.fnmatchcase(files, package_name)
    ]
    if dependency:
        whl = [
            files for files in dependency if files.endswith(".whl")
        ]  ## There are multiple version of same package So list of wheel will be considered.
        sdist = [files for files in dependency if files.endswith(".tar.gz")]
        about = [files for files in dependency if files.endswith(".ABOUT")]
        notice = [files for files in dependency if files.endswith(".NOTICE")]
        license = [files for files in dependency if files.endswith(".LICENSE")]
        print(*whl, sep="\n")
        print("\n")
        if sdist:
            print(*sdist, sep="\n")
        else:
            print("Corresponding sdist does not exits in target\n")
        print("\n")
        if about:
            print(*about, sep="\n")
        else:
            print("Corresponding .ABOUT does not exits in target\n")
        print("\n")
        if license:
            print(*licence, sep="\n")
        else:
            print("Corresponding .LICENSE does not exits in target\n")
        print("\n")
        if notice:
            print(*notice, sep="\n")
        else:
            print("Corresponding .NOTICE does not exits in target\n")
        print("\n")
    else:
        print("Specified package does not exist\n")


def main_with_args(args: str) -> None:
    parser = argparse.ArgumentParser(
        description="""Fetch a specific package with version in given target like thirdparty by default.
EXAMPLE:
scancode.py \\
  --fetch PACKAGE_NAME \\
  --target TARGET_DIR \\
  --version VERSION_OF_PACKAGE \\
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--fetch",
        help="Required: Specific Dependencies  to be fetched.",
        type=str,
        required=True,
    )

    parser.add_argument(
        "--target",
        help=" a target directory where the built wheels and tarballs would be fetched.",
        type=str,
        default="thirdparty",
    )

    parser.add_argument(
        "--version",
        help="Specify version of dependencies to be fetched.",
        type=str,
        default=None,
    )

    args = parser.parse_args()

    package_name = args.fetch
    target = args.target
    version = args.version
    search_package(package_name, target, version)


def main() -> None:
    main_with_args(sys.argv[1:])


if __name__ == "__main__":
    main()
