# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re

"""
Wheel platform checking

Copied and modified on 2020-12-24 from
https://github.com/pypa/warehouse/blob/37a83dd342d9e3b3ab4f6bde47ca30e6883e2c4d/warehouse/forklift/legacy.py

This contains the basic functions to check if a wheel file name is would be
supported for uploading to PyPI.
"""

# These platforms can be handled by a simple static list:
_allowed_platforms = {
    "any",
    "win32",
    "win_amd64",
    "win_ia64",
    "manylinux1_x86_64",
    "manylinux1_i686",
    "manylinux2010_x86_64",
    "manylinux2010_i686",
    "manylinux2014_x86_64",
    "manylinux2014_i686",
    "manylinux2014_aarch64",
    "manylinux2014_armv7l",
    "manylinux2014_ppc64",
    "manylinux2014_ppc64le",
    "manylinux2014_s390x",
    "linux_armv6l",
    "linux_armv7l",
}
# macosx is a little more complicated:
_macosx_platform_re = re.compile(r"macosx_(?P<major>\d+)_(\d+)_(?P<arch>.*)")
_macosx_arches = {
    "ppc",
    "ppc64",
    "i386",
    "x86_64",
    "arm64",
    "intel",
    "fat",
    "fat32",
    "fat64",
    "universal",
    "universal2",
}
_macosx_major_versions = {
    "10",
    "11",
}

# manylinux pep600 is a little more complicated:
_manylinux_platform_re = re.compile(r"manylinux_(\d+)_(\d+)_(?P<arch>.*)")
_manylinux_arches = {
    "x86_64",
    "i686",
    "aarch64",
    "armv7l",
    "ppc64",
    "ppc64le",
    "s390x",
}


def is_supported_platform_tag(platform_tag):
    """
    Return True if the ``platform_tag`` is supported on PyPI.
    """
    if platform_tag in _allowed_platforms:
        return True
    m = _macosx_platform_re.match(platform_tag)
    if m and m.group("major") in _macosx_major_versions and m.group("arch") in _macosx_arches:
        return True
    m = _manylinux_platform_re.match(platform_tag)
    if m and m.group("arch") in _manylinux_arches:
        return True
    return False


def validate_platforms_for_pypi(platforms):
    """
    Validate if the wheel platforms are supported platform tags on Pypi. Return
    a list of unsupported platform tags or an empty list if all tags are
    supported.
    """

    # Check that if it's a binary wheel, it's on a supported platform
    invalid_tags = []
    for plat in platforms:
        if not is_supported_platform_tag(plat):
            invalid_tags.append(plat)
    return invalid_tags
