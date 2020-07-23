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
from commoncode.system import on_windows
import os
from shutil import make_archive
import subprocess
import sys


def generate_os_archive(links, requirement, output_file):
    """
    Generate an archive for dependencies for specific OS and
    given version of python by taking directory as an input.
    """
    subprocess.run(
        [
            "pip",
            "download",
            "--verbose",
            "--no-cache-dir",
            "--no-index",
            "--find-links",
            links,
            "-r",
            requirement,
            "--dest",
            "my_deps",
        ]
    )
    root_dir = os.path.abspath("my_deps")
    output_dir = os.path.abspath(output_file)
    if on_windows:
        make_archive(output_dir, "zip", root_dir)
    else:
        make_archive(output_dir, "gztar", root_dir)


def main_with_args(args: str) -> None:
    parser = argparse.ArgumentParser(
        description="""Creates a archive for specific OS and specific python.
EXAMPLE:
deps_archive.py \\
  --input thirdparty \\
  --r requirements.txt
  --output_file macOS_py36 \\
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--find_links",
        help="Required: A url or path to an html file, then parse for links to archives. If a local path or file://url that's a directory, then look for archives in the directory listing",
        type=str,
        required=True,
    )

    parser.add_argument(
        "--req",
        help="A requirement_file with hashes",
        type=str,
        default="requirements.txt",
    )

    parser.add_argument(
        "--output_file",
        help="Required: The Generated archive file name without extension.",
        type=str,
        required=True,
    )

    args = parser.parse_args()

    link = args.find_links
    req = args.req
    output = args.output_file
    generate_os_archive(link, req, output)


def main() -> None:
    main_with_args(sys.argv[1:])


if __name__ == "__main__":
    main()
