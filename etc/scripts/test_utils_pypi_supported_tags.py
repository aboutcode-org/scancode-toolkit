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

import pytest

from utils_pypi_supported_tags import validate_platforms_for_pypi

"""
Wheel platform checking tests

Copied and modified on 2020-12-24 from
https://github.com/pypa/warehouse/blob/37a83dd342d9e3b3ab4f6bde47ca30e6883e2c4d/tests/unit/forklift/test_legacy.py
"""


def validate_wheel_filename_for_pypi(filename):
    """
    Validate if the filename is a PyPI/warehouse-uploadable wheel file name
    with supported platform tags. Return a list of unsupported platform tags or
    an empty list if all tags are supported.
    """
    from utils_thirdparty import Wheel

    wheel = Wheel.from_filename(filename)
    return validate_platforms_for_pypi(wheel.platforms)


@pytest.mark.parametrize(
    "plat",
    [
        "any",
        "win32",
        "win_amd64",
        "win_ia64",
        "manylinux1_i686",
        "manylinux1_x86_64",
        "manylinux2010_i686",
        "manylinux2010_x86_64",
        "manylinux2014_i686",
        "manylinux2014_x86_64",
        "manylinux2014_aarch64",
        "manylinux2014_armv7l",
        "manylinux2014_ppc64",
        "manylinux2014_ppc64le",
        "manylinux2014_s390x",
        "manylinux_2_5_i686",
        "manylinux_2_12_x86_64",
        "manylinux_2_17_aarch64",
        "manylinux_2_17_armv7l",
        "manylinux_2_17_ppc64",
        "manylinux_2_17_ppc64le",
        "manylinux_3_0_s390x",
        "macosx_10_6_intel",
        "macosx_10_13_x86_64",
        "macosx_11_0_x86_64",
        "macosx_10_15_arm64",
        "macosx_11_10_universal2",
        # A real tag used by e.g. some numpy wheels
        (
            "macosx_10_6_intel.macosx_10_9_intel.macosx_10_9_x86_64."
            "macosx_10_10_intel.macosx_10_10_x86_64"
        ),
    ],
)
def test_is_valid_pypi_wheel_return_true_for_supported_wheel(plat):
    filename = f"foo-1.2.3-cp34-none-{plat}.whl"
    assert not validate_wheel_filename_for_pypi(filename)


@pytest.mark.parametrize(
    "plat",
    [
        "linux_x86_64",
        "linux_x86_64.win32",
        "macosx_9_2_x86_64",
        "macosx_12_2_arm64",
        "macosx_10_15_amd64",
    ],
)
def test_is_valid_pypi_wheel_raise_exception_for_aunsupported_wheel(plat):
    filename = f"foo-1.2.3-cp34-none-{plat}.whl"
    invalid = validate_wheel_filename_for_pypi(filename)
    assert invalid
