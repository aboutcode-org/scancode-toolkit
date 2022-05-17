#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from container_inspector.distro import Distro

from packagedcode import models
from packagedcode import utils

"""
Check for files to determine the Linux distro or operating system of a codebase.
"""


class EtcOsReleaseHandler(models.NonAssemblableDatafileHandler):
    datasource_id = 'etc_os_release'
    default_package_type = 'linux-distro'
    path_patterns = ('*etc/os-release', '*usr/lib/os-release',)
    description = 'Linux OS release metadata file'
    documentation_url = 'https://www.freedesktop.org/software/systemd/man/os-release.html'

    @classmethod
    def parse(cls, location):
        distro = Distro.from_os_release_file(location)
        distro_identifier = distro.identifier
        pretty_name = distro.pretty_name and distro.pretty_name.lower() or ''

        if distro_identifier == 'debian':
            namespace = 'debian'

            if 'distroless' in pretty_name:
                name = 'distroless'
            elif pretty_name.startswith('debian'):
                name = 'distroless'

        elif distro_identifier == 'ubuntu' and distro.id_like == 'debian':
            namespace = 'debian'
            name = 'ubuntu'

        elif distro_identifier.startswith('fedora') or  distro.id_like == 'fedora':
            namespace = distro_identifier
            name = distro.id_like or distro_identifier

        else:
            # FIXME: this needs to be seriously updated
            namespace = distro_identifier
            name = distro.id_like or distro_identifier

        version = distro.version_id

        yield models.PackageData(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            namespace=namespace,
            name=name,
            version=version,
        )

    @classmethod
    def find_linux_rootfs_root_resource(cls, resource, codebase):
        """
        Given a ``codebase`` ``resource`` for an "os-release" file, return the
        resource for the root directory of this filesystem or None.
        """
        paths = ('etc/os-release', 'usr/lib/os-release',)
        return utils.find_root_from_paths(paths, resource, codebase)

