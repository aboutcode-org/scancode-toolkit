"""
This base config script gets automatically executed for all platforms via
configure if the "dev" sub-configuration is specified (which is the default).
"""

import os


def setup_dev_mode():
    """
    Create the development mode tag file. In development mode, ScanCode does
    not rely on license data to remain untouched and will always check the
    license index cache for consistency, rebuilding it if necessary.
    """
    from scancode_config import scancode_root_dir
    with open(os.path.join(scancode_root_dir, 'SCANCODE_DEV_MODE'), 'wb') as sdm:
        sdm.write('This is a tag file to notify that ScanCode is used in development mode.')


def setup_vscode():
    """
    Add base settings for .vscode
    """
    from scancode_config import scancode_root_dir
    from commoncode.fileutils import create_dir
    from commoncode.fileutils import copyfile

    settings = os.path.join(scancode_root_dir, 'etc', 'vscode', 'settings.json')

    if os.path.exists(settings):
        vscode = os.path.join(scancode_root_dir, '.vscode')
        create_dir(vscode)
        copyfile(settings, vscode)


setup_dev_mode()
setup_vscode()
