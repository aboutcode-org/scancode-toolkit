.. note::

    Once you install a external license plugin, you have to reconfigure
    scancode-toolkit (or use pip uninstall) to uninstall the plugin to
    completely remove it. Otherwise using the --only-builtin option only
    regenerates the index without the installed plugins, but another Reindex
    would have the licenses/rules from the installed plugins.
