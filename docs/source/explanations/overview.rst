Overview
========

.. _explain_how_scancode_works:

How does ScanCode detect licenses?
--------------------------------------

For license detection, ScanCode uses a (large) number of license texts and license detection
'rules' that are compiled in a search index. When scanning, the text of the target file is
extracted and used to query the license search index and find license matches.

For copyright detection, ScanCode uses a grammar that defines the most common and less common
forms of copyright statements. When scanning, the target file text is extracted and 'parsed'
with this grammar to extract copyright statements.

ScanCode-Toolkit performs the scan on a codebase in the following steps :

1. Collect an inventory of the code files and classify the code using file types,
2. Extract files from any archive using a general purpose extractor
3. Extract texts from binary files if needed
4. Use an extensible rules engine to detect open source license text and notices
5. Use a specialized parser to capture copyright statements
6. Identify packaged code and collect metadata from packages
7. Report the results in the formats of your choice (JSON, CSV, etc.) for integration
   with other tools

Scan results are provided in various formats:

* a JSON file simple or pretty-printed,
* SPDX tag value or XML, RDF formats,
* CSV,
* a simple unformatted HTML file that can be opened in browser or as a spreadsheet.

For each scanned file, the result contains:

* its location in the codebase,
* the detected licenses and copyright statements,
* the start and end line numbers identifying where the license or copyright was found in the
  scanned file, and
* reference information for the detected license.

For archive extraction, ScanCode uses a combination of Python modules, 7zip and libarchive/bsdtar
to detect archive types and extract these recursively.

Several other utility modules are used such as libmagic for file and mime type detection.
