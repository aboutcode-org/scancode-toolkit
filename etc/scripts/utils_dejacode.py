#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/skeleton for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#
import io
import os
import zipfile

import requests
import saneyaml

from packaging import version as packaging_version

"""
Utility to create and retrieve package and ABOUT file data from DejaCode.
"""

DEJACODE_API_KEY = os.environ.get("DEJACODE_API_KEY", "")
DEJACODE_API_URL = os.environ.get("DEJACODE_API_URL", "")

DEJACODE_API_URL_PACKAGES = f"{DEJACODE_API_URL}packages/"
DEJACODE_API_HEADERS = {
    "Authorization": "Token {}".format(DEJACODE_API_KEY),
    "Accept": "application/json; indent=4",
}


def can_do_api_calls():
    if not DEJACODE_API_KEY and DEJACODE_API_URL:
        print("DejaCode DEJACODE_API_KEY and DEJACODE_API_URL not configured. Doing nothing")
        return False
    else:
        return True


def fetch_dejacode_packages(params):
    """
    Return a list of package data mappings calling the package API with using
    `params` or an empty list.
    """
    if not can_do_api_calls():
        return []

    response = requests.get(
        DEJACODE_API_URL_PACKAGES,
        params=params,
        headers=DEJACODE_API_HEADERS,
    )

    return response.json()["results"]


def get_package_data(distribution):
    """
    Return a mapping of package data or None for a Distribution `distribution`.
    """
    results = fetch_dejacode_packages(distribution.identifiers())

    len_results = len(results)

    if len_results == 1:
        return results[0]

    elif len_results > 1:
        print(f"More than 1 entry exists, review at: {DEJACODE_API_URL_PACKAGES}")
    else:
        print("Could not find package:", distribution.download_url)


def update_with_dejacode_data(distribution):
    """
    Update the Distribution `distribution` with DejaCode package data. Return
    True if data was updated.
    """
    package_data = get_package_data(distribution)
    if package_data:
        return distribution.update(package_data, keep_extra=False)

    print(f"No package found for: {distribution}")


def update_with_dejacode_about_data(distribution):
    """
    Update the Distribution `distribution` wiht ABOUT code data fetched from
    DejaCode. Return True if data was updated.
    """
    package_data = get_package_data(distribution)
    if package_data:
        package_api_url = package_data["api_url"]
        about_url = f"{package_api_url}about"
        response = requests.get(about_url, headers=DEJACODE_API_HEADERS)
        # note that this is YAML-formatted
        about_text = response.json()["about_data"]
        about_data = saneyaml.load(about_text)

        return distribution.update(about_data, keep_extra=True)

    print(f"No package found for: {distribution}")


def fetch_and_save_about_files(distribution, dest_dir="thirdparty"):
    """
    Fetch and save in `dest_dir` the .ABOUT, .LICENSE and .NOTICE files fetched
    from DejaCode for a Distribution `distribution`. Return True if files were
    fetched.
    """
    package_data = get_package_data(distribution)
    if package_data:
        package_api_url = package_data["api_url"]
        about_url = f"{package_api_url}about_files"
        response = requests.get(about_url, headers=DEJACODE_API_HEADERS)
        about_zip = response.content
        with io.BytesIO(about_zip) as zf:
            with zipfile.ZipFile(zf) as zi:
                zi.extractall(path=dest_dir)
        return True

    print(f"No package found for: {distribution}")


def find_latest_dejacode_package(distribution):
    """
    Return a mapping of package data for the closest version to
    a Distribution `distribution` or None.
    Return the newest of the packages if prefer_newest is True.
    Filter out version-specific attributes.
    """
    ids = distribution.purl_identifiers(skinny=True)
    packages = fetch_dejacode_packages(params=ids)
    if not packages:
        return

    for package_data in packages:
        matched = (
            package_data["download_url"] == distribution.download_url
            and package_data["version"] == distribution.version
            and package_data["filename"] == distribution.filename
        )

        if matched:
            return package_data

    # there was no exact match, find the latest version
    # TODO: consider the closest version rather than the latest
    # or the version that has the best data
    with_versions = [(packaging_version.parse(p["version"]), p) for p in packages]
    with_versions = sorted(with_versions)
    latest_version, latest_package_version = sorted(with_versions)[-1]
    print(
        f"Found DejaCode latest version: {latest_version} " f"for dist: {distribution.package_url}",
    )

    return latest_package_version


def create_dejacode_package(distribution):
    """
    Create a new DejaCode Package a Distribution `distribution`.
    Return the new or existing package data.
    """
    if not can_do_api_calls():
        return

    existing_package_data = get_package_data(distribution)
    if existing_package_data:
        return existing_package_data

    print(f"Creating new DejaCode package for: {distribution}")

    new_package_payload = {
        # Trigger data collection, scan, and purl
        "collect_data": 1,
    }

    fields_to_carry_over = [
        "download_url" "type",
        "namespace",
        "name",
        "version",
        "qualifiers",
        "subpath",
        "license_expression",
        "copyright",
        "description",
        "homepage_url",
        "primary_language",
        "notice_text",
    ]

    for field in fields_to_carry_over:
        value = getattr(distribution, field, None)
        if value:
            new_package_payload[field] = value

    response = requests.post(
        DEJACODE_API_URL_PACKAGES,
        data=new_package_payload,
        headers=DEJACODE_API_HEADERS,
    )
    new_package_data = response.json()
    if response.status_code != 201:
        raise Exception(f"Error, cannot create package for: {distribution}")

    print(f'New Package created at: {new_package_data["absolute_url"]}')
    return new_package_data
