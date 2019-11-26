.. note::

    Unlike previous 2.x versions, -c, -l, and -p are not default. If any of combination of these
    options are used, ScanCode only performs that specific task, and not the others.
    ``scancode -e`` only scans for emails, and doesn't scan for copyright/license/packages/general
    information.

.. note::

    These options, i.e. -c, -l, -p, -e, -u, and -i can be used together. As in, instead of
    ``scancode -c -i -p``, you can write ``scancode -cip`` and it will be the same.
