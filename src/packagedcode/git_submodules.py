#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import configparser
import re
from urllib.parse import urlparse

from packageurl import PackageURL
from packageurl.contrib.url2purl import url2purl

from packagedcode import models

SSH_GIT_URL_PATTERN = re.compile(r"^[^@/:]+@[^/:]+:.+$")


# https://github.com/aboutcode-org/scancode-toolkit/pull/5511
def get_purl_from_git_url(url, version=None):
    """Parse an HTTP(S), SSH, or relative git repo URL into a PackageURL."""
    url = url.strip()

    if url.startswith(("https://", "http://", "git://", "ssh://")):
        parsed = urlparse(url)
        domain = parsed.netloc
        raw_path = parsed.path
        lookup_url = f"https://{domain}{raw_path}" if parsed.scheme in ("git", "ssh") else url

    elif SSH_GIT_URL_PATTERN.fullmatch(url):
        host, raw_path = url.split(":", 1)
        domain = host.rsplit("@", 1)[-1]
        lookup_url = f"https://{domain}/{raw_path.lstrip('/')}"

    else:
        # Relative submodule URLs (e.g., ../FreeRTOS-Kernel.git)
        parts = [p for p in url.removesuffix(".git").split("/") if p and p != ".."]
        if not parts:
            return None

        return PackageURL(
            type="generic",
            namespace="/".join(parts[:-1]) or None,
            name=parts[-1],
            version=version,
        )

    clean_path = raw_path.strip("/").removesuffix(".git")
    if not domain or not clean_path:
        return None

    parsed_purl = url2purl(lookup_url)

    if not parsed_purl or parsed_purl.type == "generic":
        parsed_purl = PackageURL(
            type="git",
            namespace=domain,
            name=clean_path,
            version=version,
        )
    elif version and not parsed_purl.version:
        parsed_purl = PackageURL(**{**parsed_purl.to_dict(), "version": version})

    return parsed_purl


class GitSubmodulesHandler(models.DatafileHandler):
    datasource_id = "git_submodules"
    path_patterns = ("*/.gitmodules", ".gitmodules")
    default_package_type = "generic"
    description = "Git submodules manifest (.gitmodules)"
    documentation_url = "https://git-scm.com/docs/gitmodules"

    @classmethod
    def parse(cls, location, package_only=False):
        config = configparser.ConfigParser(interpolation=None, strict=False)
        try:
            config.read(location, encoding="utf-8")
        except (configparser.Error, OSError):
            return

        dependencies = []
        for section in config.sections():
            if not section.startswith("submodule "):
                continue

            sub_path = config.get(section, "path", fallback="").strip().strip("/")
            sub_url = config.get(section, "url", fallback="").strip()
            sub_branch = config.get(section, "branch", fallback="").strip()

            if not sub_path:
                continue

            purl = get_purl_from_git_url(sub_url, version=sub_branch) if sub_url else None
            dependencies.append(
                models.DependentPackage(
                    purl=str(purl) if purl else None,
                    extracted_requirement=sub_branch,
                    scope="submodule",
                    is_runtime=True,
                    is_optional=False,
                    is_pinned=False,
                ).to_dict()
            )

        if not dependencies:
            return

        package_data = dict(
            type=cls.default_package_type,
            datasource_id=cls.datasource_id,
            dependencies=dependencies,
        )
        yield models.PackageData.from_data(package_data, package_only=package_only)