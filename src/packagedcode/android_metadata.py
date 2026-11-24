#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

"""
Handle Android third_party METADATA files. These are protobuf text format files
with a top-level `third_party { ... }` message.
"""

import os
import re

from packagedcode import models

TOKEN_RE = re.compile(
    r"\s+|\#[^\n]*"
    r'|(?P<str>"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')'
    r"|(?P<punct>[{}:])"
    r'|(?P<word>[^\s{}:"\']+)'
)


def tokenize(text):
    tokens = []
    for m in TOKEN_RE.finditer(text):
        if m.group("str") is not None:
            s = m.group("str")[1:-1].replace('\\"', '"').replace("\\\\", "\\")
            tokens.append(("str", s))
        elif m.group("punct"):
            tokens.append(("punct", m.group("punct")))
        elif m.group("word"):
            tokens.append(("word", m.group("word")))
    return tokens


def parse_message(tokens, pos=0):
    """
    Return a tuple of (mapping of key -> list of values, new position).
    Nested messages are mappings too.
    """
    result = {}
    while pos < len(tokens):
        kind, tok = tokens[pos]
        if (kind, tok) == ("punct", "}"):
            return result, pos + 1
        if kind != "word":
            raise ValueError(f"Unexpected token {tok!r}")
        key = tok
        pos += 1
        if pos < len(tokens) and tokens[pos] == ("punct", ":"):
            pos += 1
        if pos >= len(tokens):
            raise ValueError("Unexpected end of file")
        if tokens[pos] == ("punct", "{"):
            value, pos = parse_message(tokens, pos + 1)
        else:
            value = tokens[pos][1]
            pos += 1
        result.setdefault(key, []).append(value)
    return result, pos


def first(mapping, key):
    values = mapping.get(key) or []
    return values[0] if values else None


class AndroidMetadataHandler(models.NonAssemblableDatafileHandler):
    datasource_id = "android_metadata"
    path_patterns = ("*/METADATA",)
    default_package_type = "generic"
    description = "Android third_party METADATA file"
    documentation_url = "https://android.googlesource.com/platform/external/"

    @classmethod
    def is_datafile(cls, location, filetypes=tuple(), _bare_filename=False):
        if not super().is_datafile(location, filetypes=filetypes):
            return False
        # do not steal PyPI wheel and egg-info METADATA files
        parent = os.path.basename(os.path.dirname(location))
        if parent.endswith((".dist-info", ".egg-info")):
            return False
        with open(location, "r", errors="replace") as f:
            return "third_party" in f.read(4096)

    @classmethod
    def parse(cls, location, package_only=False):
        with open(location, "r", errors="replace") as f:
            text = f.read()
        try:
            data, _ = parse_message(tokenize(text))
        except ValueError:
            return

        tp = first(data, "third_party") or {}
        homepage_url = download_url = vcs_url = None
        for url in tp.get("url", []):
            url_type, value = first(url, "type"), first(url, "value")
            if url_type == "HOMEPAGE":
                homepage_url = value
            elif url_type == "GIT":
                vcs_url = value
            elif url_type == "ARCHIVE":
                download_url = value

        extra_data = {}
        license_type = first(tp, "license_type")
        if license_type:
            extra_data["license_type"] = license_type
        d = first(tp, "last_upgrade_date")
        if d:
            extra_data["last_upgrade_date"] = "{:0>4}-{:0>2}-{:0>2}".format(
                first(d, "year") or "",
                first(d, "month") or "",
                first(d, "day") or "",
            )

        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            name=first(data, "name"),
            description=first(data, "description"),
            version=first(tp, "version"),
            homepage_url=homepage_url,
            download_url=download_url,
            vcs_url=vcs_url,
            extra_data=extra_data,
        )
        yield models.PackageData.from_data(package_data, package_only=package_only)
