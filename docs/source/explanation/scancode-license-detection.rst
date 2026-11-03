.. _scancode-license-detection:

ScanCode License Detection
==========================

For license detection, ScanCode uses a large number of license texts and license detection
rules that are compiled into a search index. When scanning, the text of the target file is
extracted and used to query the license search index to find license matches.

For copyright detection, ScanCode uses a grammar that defines the most common and less common
forms of copyright statements. When scanning, the target file text is extracted and parsed
using this grammar to identify copyright statements.

ScanCode Toolkit performs the scan on a codebase in the following steps:

1. Collect an inventory of the code files and classify them using file types.
2. Extract files from any archive using a general-purpose extractor.
3. Extract text from binary files if needed.
4. Use an extensible rules engine to detect open source license text and notices.
5. Use a specialized parser to capture copyright statements.
6. Identify packaged code and collect metadata from packages.
7. Report the results in the format of your choice (JSON, CSV, etc.) for integration
   with other tools.

Scan results are provided in various formats:

* JSON (simple or pretty-printed),
* SPDX tag-value, XML, or RDF formats,
* CSV,
* a simple unformatted HTML file that can be opened in a browser or as a spreadsheet.

For each scanned file, the result contains:

* its location in the codebase,
* the detected licenses and copyright statements,
* the start and end line numbers identifying where the license or copyright was found in the
  scanned file, and
* reference information for the detected license.

Text Normalization During License Matching
------------------------------------------

Before comparing file text against the license search index, ScanCode applies basic
normalization to improve matching accuracy. This ensures that minor textual variations
do not prevent a valid license from being detected.

Normalization includes the following:

* **Whitespace handling**: Extra spaces, tabs, and line breaks are normalized so that
  differences in formatting do not affect the matching result.

* **Punctuation handling**: Minor variations in punctuation — such as differences in
  the use of commas, periods, or hyphens — are accounted for during matching, so that
  slightly reformatted license text can still be recognized correctly.

* **Case normalization**: Text is compared in a case-insensitive manner, so differences
  in capitalization do not prevent a match.

These normalization steps make license detection more robust across real-world codebases,
where license text may appear in varying styles and formats.

For archive extraction, ScanCode uses a combination of Python modules, 7zip, and
libarchive/bsdtar to detect archive types and extract them recursively.
Several other utility modules are used, such as libmagic for file and MIME type detection.
