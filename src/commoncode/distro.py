#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/aboutcode-org/commoncode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import shlex


def parse_os_release(location):
    """
    Return a mapping built from an os-release-like file at `location`.

    See https://www.linux.org/docs/man5/os-release.html

    $ cat /etc/os-release
    NAME="Ubuntu"
    VERSION="16.04.6 LTS (Xenial Xerus)"
    ID=ubuntu
    ID_LIKE=debian
    PRETTY_NAME="Ubuntu 16.04.6 LTS"
    VERSION_ID="16.04"
    HOME_URL="http://www.ubuntu.com/"
    SUPPORT_URL="http://help.ubuntu.com/"
    BUG_REPORT_URL="http://bugs.launchpad.net/ubuntu/"
    VERSION_CODENAME=xenial
    UBUNTU_CODENAME=xenial

    Note the /etc/lsb-release file has the same format, but different tags.
    """
    with open(location) as osrl:
        lines = (line.strip() for line in osrl)
        lines = (line.partition("=") for line in lines if line and not line.startswith("#"))
        return {key.strip(): "".join(shlex.split(value)) for key, _, value in lines}
