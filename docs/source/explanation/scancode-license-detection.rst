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

Ignorable Attributes in License Detection
------------------------------------------

During license detection, ScanCode may encounter certain elements that should be excluded
from the scan results. These are referred to as **ignorable attributes**. They allow
ScanCode to skip over specific values that are not meaningful for a given detection context.

The following ignorable attributes are supported:

``ignorable_urls``
    A list of URLs that should be ignored during detection. These are URLs found in license
    or copyright text that are not relevant to the scan results.

``ignorable_copyrights``
    A list of copyright statements that should be excluded from the detected results.
    Use this to suppress known or irrelevant copyright notices.

``ignorable_authors``
    A list of author names to be excluded from detection results. Useful for filtering
    out authors that are not relevant to the license or copyright analysis.

``ignorable_holders``
    A list of copyright holders to be ignored. This allows suppression of known
    institutional or organizational holders that do not need to appear in the output.

``ignorable_emails``
    A list of email addresses to be excluded from detection results. These are typically
    contact addresses embedded in license headers or copyright notices.

These attributes can be defined in license detection rules to refine and filter scan output,
ensuring results contain only the most relevant license and copyright information.

For archive extraction, ScanCode uses a combination of Python modules, 7zip, and
libarchive/bsdtar to detect archive types and extract them recursively.
Several other utility modules are used, such as libmagic for file and MIME type detection.
