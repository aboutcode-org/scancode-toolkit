Home
====

ScanCode is a tool to scan code and detect licenses, copyrights and more.

Why ScanCode?
-------------

Discovering the origin and license for a software component is important, but it is often much
harder to accomplish than it should be because:

- A typical software project may reuse tens or hundreds of third-party software components
- Software authors do not always provide copyright and license information
- Copyright and license information that is provided may be hard to find and interpret

ScanCode tries to address this issue by offering:

- A comprehensive code scanner that can detect origin or license information inside codebase files
- A simple command line approach that runs on Windows, Linux, and Mac
- Your choice of JSON or other output formats (SPDX, HTML, CSV) for integration with other tools
- ScanCode workbench for Visualization
- Well-tested, easy to hack, and well-documented code
- Release of the code and reference data under attribution licenses (Apache 2.0 and CC-BY-1.0)
- Plugin System for easily adding new Functionality to Scans.
- Python 3 Unicode Capabilities for better supporting users from 100+ languages.
- Extensive Documentation Support.

What does ScanCode Toolkit do?
------------------------------

ScanCode finds the origin history information that is in your codebase with a focus on:

- Copyright and other origin clues (emails, urls, authors etc)
- License notices and license text with reference information about detected licenses.

Using this data you can:

- Discover the origin and license of the open source and third-party software
  components that you use,
- Create a software component Inventory for your codebase, and
- Use this data to comply with open source license obligations such as attribution
  and redistribution.

How does it work?
-----------------

Given a codebase in a directory, ScanCode will:

- Collect an inventory of the code files and classify the code using file types
- Extract files from any archive using a general purpose extractor
- Extract texts from binary files if needed
- Use an extensible rules engine to detect open source license text and notices
- Use a specialized parser to capture copyright statements
- Identify packaged code and collect metadata from packages
- Report the results in the formats of your choice (JSON, SPDX, etc.) for integration with
  other tools
- Browse the results using the `ScanCode Workbench <https://github.com/nexB/scancode-workbench>`_
  companion app to assist your analysis.

ScanCode should enable you to identify the “easy” cases on your own, but a software development
team will probably need to build internal expertise or use outside experts (like nexB) in
many cases.

ScanCode is written in Python and also uses other open source packages.

Alternatives?
--------------

There are several utilities that do some of what ScanCode does - e.g. You can grep files for
copyright and license text. This may work well for simple cases - e.g. at the single file level,
but we created ScanCode for ourselves because this approach does not help you to see the
recurring patterns of licenses and other origin history clues.

Or you can consider other tools such as:

- FOSSology (open source, written in C, Linux only, GPL-licensed)
- Ninka (open source, written in Perl, GPL-licensed)
- Commercially-licensed tools, most of them written in Java

History
-------

ScanCode was originally created by nexB to support our software audit consulting services. We have
used and continuously enhanced the underlying toolkit for six years. We decided to release
ScanCode as open source software to give software development teams the opportunity to perform
as much of the software audit function as they like on their own.

If you have questions or are interested in nexB-provided training or support for ScanCode, please
send us a note at info@scancode.io or visit http://www.nexb.com/.

We are part of nexB Inc. and most of us are located in the San Francisco Bay Area. Our mission is
to provide the tools and services that enable and accelerate component-based software development.
Reusing software components is essential for the efficient delivery of software products and
systems in every industry.

Thank you for giving ScanCode a try!

.. include::  /scancode-toolkit/rst_snippets/other_imp_doc.rst
