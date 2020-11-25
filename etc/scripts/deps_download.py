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
import os
from subprocess import run
import sys

def download_req_tools(links, requirement, dir_name):
    """
    Download all dependencies into dir_name as per 
    OS/arch/python by taking links,requirement as an input.
    """
    pip_args =[
            'pip',
            'download',
            '--no-cache-dir',
            '--no-index',
            '--find-links',
            links,
            '-r',
            requirement,
            '--dest',
            dir_name,
        ]
    run(pip_args)


def main_with_args(args: str) -> None:
    parser = argparse.ArgumentParser(
        description="""Download all dependencies into directory
    (for instance thirdparty directory) as per OS/arch/python by 
    taking links,requirement as an input.""",
    )

    parser.add_argument(
        '--find-links',
        help="A directory or URL where to find packages. See pip help for details.",
        type=str,
        required=True,
    )

    parser.add_argument(
        '--requirement',
        help='An existing requirement file (with hashes) listing required packages.',
        type=str,
        required=True,
    )

    parser.add_argument(
        '--dest',
        help='Download packages into given directory(Destination)',
        type=str,
        required=True,
    )

    args = parser.parse_args()

    find_links = args.find_links
    requirement = args.requirement
    dest = args.dest
    download_req_tools(find_links, requirement, dest)


def main() -> None:
    main_with_args(sys.argv[1:])


if __name__ == '__main__':
    main()
