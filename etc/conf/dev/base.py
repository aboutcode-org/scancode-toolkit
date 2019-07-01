from __future__ import absolute_import

"""
This base config script gets automatically executed for all platforms via
configure if the "dev" sub-configuration is specified (which is the default).
"""

from os import makedirs
from os import path
import shutil


scancode_root_dir = path.dirname(
    # etc
    path.dirname(
        # conf
        path.dirname(
            # dev
            path.dirname(__file__)
        )
    )
)


def setup_dev_mode():
    """
    Create the development mode tag file. In development mode, ScanCode does
    not rely on license data to remain untouched and will always check the
    license index cache for consistency, rebuilding it if necessary.
    """
    with open(path.join(scancode_root_dir, 'SCANCODE_DEV_MODE'), 'w') as sdm:
        sdm.write('This is a tag file to notify that ScanCode is used in development mode.')


def setup_vscode():
    """
    Add base settings for .vscode
    """
    settings = path.join('vscode', 'settings.json')
    source = path.join(scancode_root_dir, 'etc', settings)
    vscode = path.join(scancode_root_dir, '.vscode')
    target = path.join(scancode_root_dir, settings)

    if path.exists(settings):
        if not path.exists(vscode):
            makedirs(vscode)
        shutil.copyfile(source, target)


setup_dev_mode()
setup_vscode()
