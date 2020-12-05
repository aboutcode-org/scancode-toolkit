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

import argparse
import os
from subprocess import run
import sys


def fetch_dependencies(links, requirement, destination_dir):
    """
    Download all dependencies into `destination_dir` as per
    OS/arch/python by taking links,requirement as an input.
    """
    run([
        'pip',
        'download',
        '--no-cache-dir',
        '--no-index',
        '--find-links', links,
        '--requirement', requirement,
        '--dest', destination_dir,
    ])


def cli(args):
    parser = argparse.ArgumentParser(
        description=
            'Download (or copy) all dependent packages listed in a requirements '
            'file from a directory or URL where to find links into a destination '
            'directory (typically the thirdparty/ directory). '
            'Only a subset of the requirements valid for the current OS, '
            'architecture and Python versions are effectively downloaded.'
        ,
    )

    parser.add_argument(
        '--find-links',
        help='Directory path or URL where to find dependent packages. '
            'See pip help for details.',
        type=str,
        required=True,
    )

    parser.add_argument(
        '--requirement',
        help='Path to an existing pip requirements file (with hashes).',
        type=str,
        required=True,
    )

    parser.add_argument(
        '--dest',
        help='Destination directory path where to download dependent packages.',
        type=str,
        required=True,
    )

    args = parser.parse_args(args=args)

    fetch_dependencies(
        find_links=args.find_links,
        requirement=args.requirement,
        dest=args.dest,
    )


if __name__ == '__main__':
    cli(sys.argv[1:])
