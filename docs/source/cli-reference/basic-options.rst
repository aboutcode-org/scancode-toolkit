`Basic` Options
===============

.. include::  /rst_snippets/basic_options.rst

----

.. include::  /rst_snippets/note_snippets/synopsis_install_quickstart.rst

----

``--generated`` Options
-----------------------

    The ``--generated`` option classifies automatically generated code files with a flag.

    An example of using ``--generated`` in a scan::

        scancode -clpieu --json-pp output.json samples --generated

    In the results, for each file the following attribute is added with it's corresponding
    ``true``/``false`` value ::

        "is_generated": true

    In the samples folder, the following files have a true value for their is_generated attribute::

        "samples/zlib/dotzlib/LICENSE_1_0.txt"
        "samples/JGroups/licenses/apache-2.0.txt"

    ..
        [ToDo] Research and Write Better

----

``--max-email`` Options
-----------------------

    .. admonition:: Dependency

        The option ``--max-email`` is a sub-option of and requires the option ``--email``.

    If in the files that are scanned, in individual files, there are a lot of emails (i.e lists) which
    are unnecessary and clutter the scan results, ``--max-email`` option can be used to report emails
    only up to a limit in individual files.

    Some important INTEGER values of the ``--max-email INTEGER`` option:

    - 0  - No limit, include all emails.
    - 50 - Default.

    An example usage::

        scancode -clpieu --json-pp output.json samples --max-email 5

    This only reports 5 email addresses per file and ignores the rest.

----

``--max-url`` Options
---------------------

    .. admonition:: Dependency

        The option ``--max-url`` is a sub-option of and requires the option ``--url``.

    If in the files that are scanned, in individual files, there are a lot of links to other websites
    (i.e url lists) which are unnecessary and clutter the scan results, ``--max-url`` option can be
    used to report urls only up to a limit in individual files.

    Some important INTEGER values of the ``--max-url INTEGER`` option:

    - 0  - No limit, include all urls.
    - 50 - Default.

    An example usage::

        scancode -clpieu --json-pp output.json samples --max-url 10

    This only reports 10 urls per file and ignores the rest.

----

``--license-score`` Options
---------------------------

    .. admonition:: Dependency

        The option ``--license-score`` is a sub-option of and requires the option ``--license``.

    ..
        [ToDo] Research and Write License Matching Better

    License matching strictness, i.e. How closely matched licenses are detected in a scan, can be
    modified by using this ``--license-score`` option.

    Some important INTEGER values of the ``--license-score INTEGER`` option:

    - **0**     - Default and Lowest Value, All matches are reported.
    - **100**    - Highest Value, Only licenses with a much better match are reported

    Here, a bigger number means a better match, i.e. Setting a higher license score translates to a
    higher threshold for matching licenses (with equal or less number of license matches).

    An example usage::

        scancode -clpieu --json-pp output.json samples --license-score 70

    Here's the license results on setting the integer value to 100, Vs. the default value 0. This is
    visualized using ScanCode workbench in the License Info Dashboard.

    .. list-table:: License scan results of Samples Directory.

        * - .. figure:: data/core_lic_score_0.png

               License Score 0 (Default).

          - .. figure:: data/core_lic_score_100.png

               License Score 100.

----

``--license-text`` Options
--------------------------

    .. admonition:: Dependency

        The option ``--license-text`` is a sub-option of and requires the option ``--license``.

    .. admonition:: Sub-Option

        The option ``--license-text-diagnostics`` and ``--is-license-text`` are sub-options of
        ``--license-text``. ``--is-license-text`` is a Post-Scan Option.

    With the ``--license-text`` option, the scan results attribute "matched text" includes the matched text
    for the detected license.

    An example Scan::

        scancode -cplieu --json-pp output.json samples --license-text

    An example matched text included in the results is as follows::

        "matched_text":
         "  This software is provided 'as-is', without any express or implied
         warranty.  In no event will the authors be held liable for any damages
         arising from the use of this software.
         Permission is granted to anyone to use this software for any purpose,
         including commercial applications, and to alter it and redistribute it
         freely, subject to the following restrictions:
         1. The origin of this software must not be misrepresented; you must not
         claim that you wrote the original software. If you use this software
         in a product, an acknowledgment in the product documentation would be
         appreciated but is not required.
         2. Altered source versions must be plainly marked as such, and must not be
         misrepresented as being the original software.
         3. This notice may not be removed or altered from any source distribution.

         Jean-loup Gailly        Mark Adler
         jloup@gzip.org          madler@alumni.caltech.edu"

    - The file in which this license was detected: ``samples/arch/zlib.tar.gz-extract/zlib-1.2.8/zlib.h``
    - License name: "ZLIB License"

----

``--license-url-template`` Options
----------------------------------

    .. admonition:: Dependency

        The option ``--license-url-template`` is a sub-option of and requires the option
        ``--license``.

    The ``--license-url-template`` option sets the template URL used for the license reference URLs.

    The default template URL is : [https://enterprise.dejacode.com/urn/urn:dje:license:{}]
    In a template URL, curly braces ({}) are replaced by the license key.

    So, by default the license reference URL points to the dejacode page for that license.

    A scan example using the ``--license-url-template TEXT`` option ::

        scancode -clpieu --json-pp output.json samples --license-url-template https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/licenses/{}.yml

    In a normal scan, reference url for "ZLIB License" is as follows::

        "reference_url": "https://enterprise.dejacode.com/urn/urn:dje:license:zlib",

    After using the option in the following manner::

        ``--license-url-template https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/licenses/{}``

    the reference URL changes to this `zlib.yml file <https://github.com/nexB/scancode-toolkit/blob/develop/src/licensedcode/data/licenses/zlib.yml>`_::

        "reference_url": "https://github.com/nexB/scancode-toolkit/tree/develop/src/licensedcode/data/licenses/zlib.yml",

    The reference URL changes for all detected licenses in the scan, across the scan result file.

----

``--license-text-diagnostics`` Options
--------------------------------------

    .. admonition:: Dependency

        The option ``--license-text-diagnostics`` is a sub-option of and requires the options
        ``--license`` and ``--license-text``.

    In the matched license text, include diagnostic highlights surrounding with square brackets []
    words that are not matched.

    In a normal scan, whole lines of text are included in the matched license text, including parts
    that are possibly unmatched.

    An example Scan::

        scancode -cplieu --json-pp output.json samples --license-text --license-text-diagnostics

    Running a scan on the samples directory with ``--license-text --license-text-diagnostics`` options,
    causes the following difference in the scan result of the file
    ``samples/JGroups/licenses/bouncycastle.txt``.

    Without Diagnostics::

        "matched_text":
        "License Copyright (c) 2000 - 2006 The Legion Of The Bouncy Castle
        (http://www.bouncycastle.org) Permission is hereby granted, free of charge, to any person
        obtaining a copy of this software and associated documentation files (the \"Software\"),
        to deal in the Software without restriction

    With Diagnostics on::

        "matched_text":
        "License [Copyright] ([c]) [2000] - [2006] [The] [Legion] [Of] [The] [Bouncy] [Castle]
        ([http]://[www].[bouncycastle].[org]) Permission is hereby granted, free of charge, to any person
        obtaining a copy of this software and associated documentation files (the \"Software\"),
        to deal in the Software without restriction,
