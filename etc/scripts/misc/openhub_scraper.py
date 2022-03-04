#!/usr/bin/python
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#
import io
import json
import os
import time

from urllib.request import urlopen

from bs4 import BeautifulSoup

LICENSES_LIST_FILE = "openhub_licenses.json"


def get_page(page_no):
    """
    Return the text content of an openhub ``page_no`` page number.
    """
    url = f"https://www.openhub.net/licenses?page={page_no}"
    print(f"Fetching: {url}")
    return urlopen(url).read()


def fetch_all_licenses():
    """
    Save list of license and all license texts
    """
    if not os.path.exists(LICENSES_LIST_FILE):
        licenses = save_licenses(filename=LICENSES_LIST_FILE)
    else:
        with open(LICENSES_LIST_FILE) as ip:
            licenses = json.load(ip)
    print()
    for lic in licenses:
        fetch_and_save_license(lic["url"])


def list_all_licenses(pages_count=18):
    """
    Yield mappings of openhub license {name:xxx, url:zzz} extracted from the
    all the openhub license pages
    """
    for page_no in range(1, pages_count + 1):
        time.sleep(5)
        page = get_page(page_no)
        for lic in list_licenses_on_page(page):
            yield lic


def fetch_and_save_license(url, force=False, directory="openhub_licenses"):
    """
    Return the text for license page at url
    """
    filename = url.split("/")[-1]
    lic_file = os.path.join(directory, filename)
    if not force and os.path.exists(lic_file):
        return

    os.makedirs(directory, exist_ok=True)
    print(f" Fetching: {url}")
    time.sleep(.1)
    content = urlopen(url).read()
    with open(lic_file, "wb") as of:
        of.write(content)


def list_licenses_on_page(page):
    """
    Yield mappings of openhub license {name:xxx, url:zzz} extracted from the
    ``page`` text of an HTML page.
    """
    parsed_page = BeautifulSoup(page, "html.parser")
    all_licenses = parsed_page.find(id="license").select(
        "table.table-striped.table-condensed.table"
    )
    licenses = all_licenses[0].find_all("a", href=True)
    for license in licenses:  # NOQA
        yield dict(url=license["href"], name=license.get_text())


def save_licenses(filename=LICENSES_LIST_FILE):
    """
    Write to the ``filename`` file the list of scrapped openhub license as JSON.
    """
    licenses = list(list_all_licenses())
    with io.open(filename, "w") as f:
        json.dump(licenses, f, indent=2)
    return licenses


if __name__ == "__main__":
    fetch_all_licenses()
