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
import subprocess
import shutil
import sys

python_version = str(sys.version_info[0]) + str(sys.version_info[1])
py_abi = "{0}cp{1}{0}".format("*", python_version)


def generate_req_text(input_dir, output_file=False, package_name=False):
    """
    Generate a requirement.txt file of all dependencies present in thirdparty.
    """
    thirdparty = list(resource_iter(input_dir, with_dirs=False))
    # FIXME this code is for py 3.6 and later we will update for all version
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
    if not (os.path.isdir("required_deps")):
        os.mkdir("required_deps")
    for deps in dependencies:
        shutil.copy(deps, "required_deps")
    subprocess.run(
        [
            "pip-compile",
            "--generate-hashes",
            "--find-links",
            "required_deps",
            "--upgrade",
            "--output-file",
            output_file,
            "--verbose",
            "--upgrade-package",
            "package_name",
            "--pip-args",
            "--no-index",
        ]
    )
    shutil.rmtree("required_deps")


def main_with_args(args: str) -> None:
    parser = argparse.ArgumentParser(
        description="""Creates a archive for specific OS and specific python.
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
        help="Required: Thirdparty Dependencies directory to be archived. ",
        type=str,
        required=True,
    )

    parser.add_argument(
        "--output",
        help="Output file name. Required if more than one input file is given. Will be derived from input file otherwise. ",
        type=str,
        default="requirements.txt",
    )

    parser.add_argument(
        "--upgrade",
        help="Upgrade all dependencies to new version. ",
        action="store_true",
    )

    parser.add_argument(
        "--upgrade_package",
        help="Specify particular packages to upgrade. ",
        type=str,
        default=None,
    )

    args = parser.parse_args()

    tpdir = args.deps_directory
    output_file = args.output
    package_name = args.upgrade_package
    upgrade = args.upgrade or None
    generate_req_text(tpdir, output_file, package_name)


def main() -> None:
    main_with_args(sys.argv[1:])


if __name__ == "__main__":
    main()
