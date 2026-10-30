#!/usr/bin/env python
#
# Copyright (c) nexB Inc. AboutCode, and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/aboutcode-org/skeleton for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from pathlib import Path
import os
import subprocess

import click


ABOUTCODE_PUBLIC_REPO_NAMES = [
    "aboutcode-toolkit",
    "ahocode",
    "bitcode",
    "clearcode-toolkit",
    "commoncode",
    "container-inspector",
    "debian-inspector",
    "deltacode",
    "elf-inspector",
    "extractcode",
    "fetchcode",
    "gemfileparser2",
    "gh-issue-sandbox",
    "go-inspector",
    "heritedcode",
    "license-expression",
    "license_copyright_pipeline",
    "nuget-inspector",
    "pip-requirements-parser",
    "plugincode",
    "purldb",
    "pygmars",
    "python-inspector",
    "sanexml",
    "saneyaml",
    "scancode-analyzer",
    "scancode-toolkit-contrib",
    "scancode-toolkit-reference-scans",
    "thirdparty-toolkit",
    "tracecode-toolkit",
    "tracecode-toolkit-strace",
    "turbo-spdx",
    "typecode",
    "univers",
]


@click.command()
@click.help_option("-h", "--help")
def update_skeleton_files(repo_names=ABOUTCODE_PUBLIC_REPO_NAMES):
    """
    Update project files of AboutCode projects that use the skeleton

    This script will:
    - Clone the repo
    - Add the skeleton repo as a new origin
    - Create a new branch named "update-skeleton-files"
    - Merge in the new skeleton files into the "update-skeleton-files" branch

    The user will need to save merge commit messages that pop up when running
    this script in addition to resolving the merge conflicts on repos that have
    them.
    """

    # Create working directory
    work_dir_path = Path("/tmp/update_skeleton/")
    if not os.path.exists(work_dir_path):
        os.makedirs(work_dir_path, exist_ok=True)

    for repo_name in repo_names:
        # Move to work directory
        os.chdir(work_dir_path)

        # Clone repo
        repo_git = f"git@github.com:aboutcode-org/{repo_name}.git"
        subprocess.run(["git", "clone", repo_git])

        # Go into cloned repo
        os.chdir(work_dir_path / repo_name)

        # Add skeleton as an origin
        subprocess.run(
            ["git", "remote", "add", "skeleton", "git@github.com:aboutcode-org/skeleton.git"]
        )

        # Fetch skeleton files
        subprocess.run(["git", "fetch", "skeleton"])

        # Create and checkout new branch
        subprocess.run(["git", "checkout", "-b", "update-skeleton-files"])

        # Merge skeleton files into the repo
        subprocess.run(["git", "merge", "skeleton/main", "--allow-unrelated-histories"])


if __name__ == "__main__":
    update_skeleton_files()
