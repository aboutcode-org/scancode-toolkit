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
import os
from subprocess import run
from shutil import copy, rmtree
import sys

python_version = str(sys.version_info[0]) + str(sys.version_info[1])
py_abi = "{0}cp{1}{0}".format("*", python_version)


def generate_req_text(input_dir, req_file, package_name, upgrade):
    """
    Generate a requirement file at `output_file`(by default requirements.txt) of all dependencies wheels and sdists present in the `input_dir` directory.
    If a `package_name` is provided it will be updated to its latest version.
    """
    thirdparty = resource_iter(input_dir, with_dirs=False)
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
    if not (os.path.isdir("temp dir")):
        os.mkdir("temp dir")
    for deps in dependencies:
        copy(deps, "temp dir")
    run(
        [
            "pip-compile",
            "--generate-hashes",
            "--find-links",
            "temp dir",
            "--upgrade",
            "--output-file",
            req_file,
            "--verbose",
            "--allow-unsafe",
            "--upgrade-package",
            "package_name",
            "--pip-args",
            "--no-index",
        ]
    )
    rmtree("temp dir")


def main_with_args(args: str) -> None:
    parser = argparse.ArgumentParser(
        description="""Generate a requirement file at `output_file`(by default requirements.txt) of all dependencies wheels and sdists present in the `input_dir` directory.
    If a `package_name` is provided it will be updated to its latest version.
EXAMPLE:
freeze_and_update_reqs.py \\
  --deps_directory DEPS_DIRECTORY \\
  --output OUTPUT \\
  --upgrade_package PACKAGE_NAME \\
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--deps_directory",
        help="Required: Thirdparty Dependencies directory to be archived.",
        type=str,
        required=True,
    )

    parser.add_argument(
        "--requirement",
        help="Requirement file name. Required if more than one input file is given. Will be derived from input file otherwise.",
        type=str,
        required=True,
    )

    parser.add_argument(
        "--upgrade",
        help="Upgrade all dependencies to new version.",
        action="store_true",
    )

    parser.add_argument(
        "--upgrade_package",
        help="Specify particular packages to upgrade.",
        type=str,
        default=None,
    )

    args = parser.parse_args()

    tpdir = args.deps_directory
    requirement_file = args.requirement
    package_name = args.upgrade_package
    upgrade = args.upgrade or False
    generate_req_text(tpdir, requirement_file, package_name, upgrade)


def main() -> None:
    main_with_args(sys.argv[1:])


if __name__ == "__main__":
    main()
