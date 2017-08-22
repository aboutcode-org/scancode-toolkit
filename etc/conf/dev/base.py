"""
This base config script gets automatically executed for all platforms via
configure if the "dev" sub-configuration is specified (which is the default).
"""

import os


def setup_dev_mode():
    """
    Create the scancode development mode tag file.
    """
    from scancode import root_dir
    with open(os.path.join(root_dir, 'SCANCODE_DEV_MODE'), 'wb') as sdm:
        sdm.write('This is a tag file to notify that ScanCode is used in development mode.')


setup_dev_mode()
