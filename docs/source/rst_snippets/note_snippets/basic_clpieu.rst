.. note::

    Unlike previous 2.x versions, -c, -l, and -p are not default. If any of combination of these
    options are used, ScanCode only performs that specific task, and not the others.
    ``scancode -l`` only scans for licenses, and doesn't scan for copyright/packages/general
    information/emails/urls. The only notable exception being ``--package`` scan also has
    license information for package manifests and top-level packages, which are derived
    regardless of ``--license`` option being used.

.. note::

    These options, i.e. -c, -l, -p, -e, -u, and -i can be used together. As in, instead of
    ``scancode -c -i -p``, you can write ``scancode -cip`` and it will be the same.
