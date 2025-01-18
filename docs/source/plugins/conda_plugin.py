from  plugins import ScancodePlugin
from conda_package_scanner import CondaPackageScanner

class CondaPlugin(ScancodePlugin):
    """
    A custom ScanCode plugin that adds the CondaPackageScanner to the scanning pipeline.
    """

    def __init__(self):
        self.scanners = [CondaPackageScanner]

# Register the plugin
plugin = CondaPlugin()
plugin.enable()
