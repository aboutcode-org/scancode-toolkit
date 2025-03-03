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

import time

from datetime import datetime

import click
import requests


def timestamp():
    return datetime.utcnow().isoformat().split("T")[0]


EMPTY_COPY_TEST = """what:
  - copyrights
  - holders
copyrights:
holders:
"""


@click.command()
@click.option(
    "-u",
    "--urls",
    "urls_file",
    type=click.Path(exists=True, readable=True, path_type=str, dir_okay=False),
    metavar="URLS-FILE",
    multiple=False,
    required=True,
    help="Path to URLs file, one per line.",
)
@click.help_option("-h", "--help")
def create_copyright_tests(
    urls_file,
):
    """
    Download the URLs listed in the URLS-FILE and create a copyight test for each in the current
    directory.

    If a line number is provided as a URL fragment #L2, uses only 5 lines before and after this
    line.
    
    If the URL is a plain GitHub URL, convert the URL to a raw URL.
    If the URL does not start with http it is treated as a plain copyright text to test
    """
    
    with open(urls_file) as urls:
        for i, url in enumerate(urls):
            url = url.strip()
            if not url:
                continue

            name = ""
            if url.startswith("http"):
                print(f"Fetching URL: {url}")
                if url.startswith("https://github.com"):
                    url = url.replace("https://github.com", "https://raw.githubusercontent.com")
                    url = url.replace("/blob/", "/")
    
                if "github" in url:
                    segs = url.split("/")
                    org = segs[3]
                    repo = segs[4]
                    name = f"copyright-test-{timestamp()}-{i}-{org}-{repo}.copyright"
            else:
                print(f"Processing test: {url}")
                name = f"copyright-test-{timestamp()}-{i}.copyright"


            start_line = 0
            end_line = 0
            if "#L" in url:
                _, _, line = url.rpartition("#L")
                line = int(line)
                if line > 5:
                    start_line = line - 5
                end_line = line + 5

            if url.startswith("http"):
                _header, content = get_remote_file_content(url, as_text=True)
            else:
                content = url

            if end_line != 0:
                content = "\n".join(content.strip().splitlines()[start_line:end_line])

            with open(name, "w") as out:
                out.write(content)

            yml = EMPTY_COPY_TEST
            if url.startswith("http"):
                yml = f"{yml}\nnotes: from {url}\n"

            with open(f"{name}.yml", "w") as out:
                out.write(yml)

            if url.startswith("http"):
                time.sleep(1)


class RemoteNotFetchedException(Exception):
    pass


def get_remote_file_content(
    url,
    as_text=True,
    headers_only=False,
    headers=None,
    _delay=0,
):
    """
    Fetch and return a tuple of (headers, content) at `url`. Return content as a
    text string if `as_text` is True. Otherwise return the content as bytes.

    If `header_only` is True, return only (headers, None). Headers is a mapping
    of HTTP headers.
    Retries multiple times to fetch if there is a HTTP 429 throttling response
    and this with an increasing delay.
    """
    time.sleep(_delay)
    headers = headers or {}
    # using a GET with stream=True ensure we get the the final header from
    # several redirects and that we can ignore content there. A HEAD request may
    # not get us this last header
    print(f"    DOWNLOADING: {url}")
    with requests.get(url, allow_redirects=True, stream=True, headers=headers) as response:
        status = response.status_code
        if status != requests.codes.ok:  # NOQA
            if status == 429 and _delay < 20:
                # too many requests: start some exponential delay
                increased_delay = (_delay * 2) or 1

                return get_remote_file_content(
                    url,
                    as_text=as_text,
                    headers_only=headers_only,
                    _delay=increased_delay,
                )

            else:
                raise RemoteNotFetchedException(f"Failed HTTP request from {url} with {status}")

        if headers_only:
            return response.headers, None

        return response.headers, response.text if as_text else response.content


if __name__ == "__main__":
    create_copyright_tests()
