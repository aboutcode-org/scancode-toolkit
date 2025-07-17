How to Run a Scan
=================

In this simple tutorial example, we perform a basic scan on the ``samples`` directory distributed
by default with ScanCode.


Prerequisites
-------------

Refer to the :ref:`install` installation guide.


Looking into Files
------------------

As mentioned previously, we are going to perform the scan on the ``samples`` directory distributed
by default with ScanCode-Toolkit. Here's the directory structure and respective files:

.. image::  /tutorials/data/files_sample.png

We notice here that the sample files contain a package ``zlib.tar.gz``. So we have to extract the
archive before running the scan, to also scan the files inside this package.


Performing Extraction
---------------------

To extract the packages inside ``samples`` directory::

    extractcode samples

This extracts the zlib.tar.gz package:

.. image::  /rst_snippets/data/extractcode.png

.. note::

    Use the ``--shallow`` option to prevent recursive extraction of nested archives.


Deciding Scan Options
---------------------

These are some common scan options you should consider using before you start the actual scan,
according to your requirements.

#. The basic scan options, i.e. ``-c`` or ``--copyright``,  ``-l`` or ``--license``,
   ``-p`` or ``--package``, ``-e`` or ``--email``, ``-u`` or ``--url``, and ``-i``
   or ``--info`` can be selected according to your requirements. If you do not
   need one specific type of information (say, licenses), consider removing it
   because the more options you scan for, the longer it will take for the scan
   to complete.


#. ``--license-score INTEGER`` is to be set if license matching accuracy is desired (Default is 0,
   and increasing this means a more accurate match). Also, using ``--license-text`` includes the
   matched text to the result.

#. ``-n INTEGER`` option can be used to speed up the scan using multiple parallel processes.

#. ``--timeout FLOAT`` option can be used to skip files taking a long time to scan.

#. ``--ignore <pattern>`` can be used to skip certain group of files.

#. ``<OUTPUT FORMAT OPTION(s)>`` is also a very important decision when you want to use the output
   for specific tasks/have requirements. Here we are using ``json`` as ScanCode Workbench imports
   ``json`` files only.

For the complete list of options, refer :ref:`cli_list_options`.


Running The Scan
----------------

Now, run the scan with the options decided::

    scancode -clpeui -n 2 --ignore "*.java" --json-pp sample.json samples

A Progress report is shown::

    Setup plugins...
    Collect file inventory...
    Scan files for: info, licenses, copyrights, packages, emails, urls with 2 process(es)...
    [####################] 29
    Scanning done.
    Summary:        info, licenses, copyrights, packages, emails, urls with 2 process(es)
    Errors count:   0
    Scan Speed:     1.09 files/sec. 40.67 KB/sec.
    Initial counts: 49 resource(s): 36 file(s) and 13 directorie(s)
    Final counts:   42 resource(s): 29 file(s) and 13 directorie(s) for 1.06 MB
    Timings:
      scan_start: 2019-09-24T203514.573671
      scan_end:   2019-09-24T203545.649805
      setup_scan:licenses: 4.30s
      setup: 4.30s
      scan: 26.62s
      total: 31.14s
    Removing temporary files...done.

.. include::  /rst_snippets/other_imp_doc.rst
