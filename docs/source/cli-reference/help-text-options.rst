Getting Help from the Command Line
==================================

ScanCode-Toolkit Command Line Interface can help you to search for specific options or use cases
from the command line itself. These are two options are ``--help`` and ``--examples``, and are
very helpful if you need a quick glance of the options or use cases. Or it can be useful when you
can't access, the more elaborate online documentation.

.. include::  /scancode-toolkit/rst_snippets/doc_help.rst

.. _cli_help_text:

Help text
---------

The Scancode-Toolkit Command Line Interface has a Help option displaying all the options. It also
displays basic usage, and some simple examples. The command line option for this is ``--help``.

.. Tip::

    You can also use the shorter ``-h`` option, which does the same.

To see the help text from the Terminal, execute the following command::

    $ scancode --help

.. include::  /scancode-toolkit/rst_snippets/note_snippets/synopsis_install_quickstart.rst

The Following Help Text is displayed, i.e. This is the help text for Scancode Version 3.1.1 ::

    Usage: scancode [OPTIONS] <OUTPUT FORMAT OPTION(s)> <input>...

    scan the <input> file or directory for license, origin and packages
    and save results to FILE(s) using one or more output format option.

    Error and progress are printed to stderr.

    Options:

    primary scans:
      -l, --license    Scan <input> for licenses.
      -p, --package    Scan <input> for package manifests and packages.
      -c, --copyright  Scan <input> for copyrights.

    other scans:
      -i, --info   Scan <input> for file information (size, checksums, etc).
      --generated  Classify automatically generated code files with a flag.
      -e, --email  Scan <input> for emails.
      -u, --url    Scan <input> for urls.

    scan options:
      --license-score INTEGER      Do not return license matches with a
                                   score lower than this score. A number
                                   between 0 and 100.  [default: 0]
      --license-text               Include the detected licenses matched
                                   text.
      --license-text-diagnostics   In the matched license text, include
                                   diagnostic highlights surrounding with
                                   square brackets [] words that are not
                                   matched.
      --license-url-template TEXT  Set the template URL used for the license
                                   reference URLs. Curly braces ({}) are
                                   replaced by the license key.  [default: h
                                   ttps://enterprise.dejacode.com/urn/urn:dj
                                   e:license:{}]
      --max-email INT              Report only up to INT emails found in a
                                   file. Use 0 for no limit.  [default: 50]
      --max-url INT                Report only up to INT urls found in a
                                   file. Use 0 for no limit.  [default: 50]

    output formats:
      --json FILE             Write scan output as compact JSON to FILE.
      --json-pp FILE          Write scan output as pretty-printed JSON to
                              FILE.
      --json-lines FILE       Write scan output as JSON Lines to FILE.
      --csv FILE              Write scan output as CSV to FILE.
      --html FILE             Write scan output as HTML to FILE.
      --custom-output FILE    Write scan output to FILE formatted with the
                              custom Jinja template file.
      --custom-template FILE  Use this Jinja template FILE as a custom
                              template.
      --spdx-rdf FILE         Write scan output as SPDX RDF to FILE.
      --spdx-tv FILE          Write scan output as SPDX Tag/Value to FILE.
      --html-app FILE         (DEPRECATED: use the ScanCode Workbench app
                              instead ) Write scan output as a mini HTML
                              application to FILE.

    output filters:
      --ignore-author <pattern>       Ignore a file (and all its findings)
                                      if an author contains a match to the
                                      <pattern> regular expression. Note
                                      that this will ignore a file even if
                                      it has other findings such as a
                                      license or errors.
      --ignore-copyright-holder <pattern>
                                      Ignore a file (and all its findings)
                                      if a copyright holder contains a match
                                      to the <pattern> regular expression.
                                      Note that this will ignore a file even
                                      if it has other scanned data such as a
                                      license or errors.
      --only-findings                 Only return files or directories with
                                      findings for the requested scans.
                                      Files and directories without findings
                                      are omitted (file information is not
                                      treated as findings).

    output control:
      --full-root   Report full, absolute paths.
      --strip-root  Strip the root directory segment of all paths. The
                    default is to always include the last directory segment
                    of the scanned path such that all paths have a common
                    root directory.

    pre-scan:
      --ignore <pattern>         Ignore files matching <pattern>.
      --include <pattern>        Include files matching <pattern>.
      --classify                 Classify files with flags telling if the
                                 file is a legal, or readme or test file,
                                 etc.
      --facet <facet>=<pattern>  Add the <facet> to files with a path
                                 matching <pattern>.

    post-scan:
      --consolidate            Group resources by Packages or license and
                               copyright holder and return those groupings
                               as a list of consolidated packages and a list
                               of consolidated components. This requires the
                               scan to have/be run with the copyright,
                               license, and package options active
      --filter-clues           Filter redundant duplicated clues already
                               contained in detected license and copyright
                               texts and notices.
      --is-license-text        Set the "is_license_text" flag to true for
                               files that contain mostly license texts and
                               notices (e.g over 90% of the content).
                               [EXPERIMENTAL]
      --license-clarity-score  Compute a summary license clarity score at
                               the codebase level.
      --license-policy FILE    Load a License Policy file and apply it to
                               the scan at the Resource level.
      --mark-source            Set the "is_source" to true for directories
                               that contain over 90% of source files as
                               children and descendants. Count the number of
                               source files in a directory as a new
                               source_file_counts attribute
      --summary                Summarize license, copyright and other scans
                               at the codebase level.
      --summary-by-facet       Summarize license, copyright and other scans
                               and group the results by facet.
      --summary-key-files      Summarize license, copyright and other scans
                               for key, top-level files. Key files are top-
                               level codebase files such as COPYING, README
                               and package manifests as reported by the
                               --classify option "is_legal", "is_readme",
                               "is_manifest" and "is_top_level" flags.
      --summary-with-details   Summarize license, copyright and other scans
                               at the codebase level, keeping intermediate
                               details at the file and directory level.

    core:
      --timeout <secs>         Stop an unfinished file scan after a timeout
                               in seconds.  [default: 120 seconds]
      -n, --processes INT      Set the number of parallel processes to use.
                               Disable parallel processing if 0. Also
                               disable threading if -1. [default: 1]
      --quiet                  Do not print summary or progress.
      --verbose                Print progress as file-by-file path instead
                               of a progress bar. Print verbose scan
                               counters.
      --from-json              Load codebase from an existing JSON scan
      --max-in-memory INTEGER  Maximum number of files and directories scan
                               details kept in memory during a scan.
                               Additional files and directories scan details
                               above this number are cached on-disk rather
                               than in memory. Use 0 to use unlimited memory
                               and disable on-disk caching. Use -1 to use
                               only on-disk caching.  [default: 10000]

    miscellaneous:
      --reindex-licenses  Check the license index cache and reindex if
                          needed and exit.

    documentation:
      -h, --help       Show this message and exit.
      --about          Show information about ScanCode and licensing and
                       exit.
      --version        Show the version and exit.
      --examples       Show command examples and exit.
      --list-packages  Show the list of supported package types and exit.
      --plugins        Show the list of available ScanCode plugins and exit.
      --print-options  Show the list of selected options and exit.

    Examples (use --examples for more):

    Scan the 'samples' directory for licenses and copyrights.
    Save scan results to the 'scancode_result.json' JSON file:

        scancode --license --copyright --json-pp scancode_result.json
        samples

    Scan the 'samples' directory for licenses and package manifests. Print scan
    results on screen as pretty-formatted JSON (using the special '-' FILE to print
    to on screen/to stdout):

        scancode --json-pp - --license --package  samples

    Note: when you run scancode, a progress bar is displayed with a
    counter of the number of files processed. Use --verbose to display
    file-by-file progress.

.. _cli_examples_text:

Command Examples Text
---------------------

The Scancode-Toolkit Command Line Interface has an ``--examples`` option which displays some basic
examples (more than the basic synopsis in ``--help``). These examples include the following aspects
of code scanning:

- Scanning Single File/Directory
- Output Scan results to stdout (as JSON) or HTML/JSON file
- Scanning for only Copyrights/Licenses
- Ignoring Files
- Using GLOB Patterns to Scan Multiple Files
- Using Verbose Mode

The command line option for displaying these basic examples is ``--examples``.

To see the help text from the Terminal, execute the following command::

    $ scancode --examples

.. include::  /scancode-toolkit/rst_snippets/note_snippets/synopsis_install_quickstart.rst

The Following Text is displayed, i.e. This is the examples for Scancode Version 3.1.1 ::

    Scancode command lines examples:

    (Note for Windows: use '\' back slash instead of '/' forward slash for paths.)

    Scan a single file for copyrights. Print scan results to stdout as pretty JSON:

        scancode --copyright samples/zlib/zlib.h --json-pp -

    Scan a single file for licenses, print verbose progress to stderr as each
    file is scanned. Save scan to a JSON file:

        scancode --license --verbose samples/zlib/zlib.h --json licenses.json

    Scan a directory explicitly for licenses and copyrights. Redirect JSON scan
    results to a file:

        scancode --license --copyright samples/zlib/ --json - > scan.json

    Scan a directory while ignoring a single file. Scan for license, copyright and
    package manifests. Use four parallel processes.
    Print scan results to stdout as pretty formatted JSON.

        scancode -lc --package --ignore README --processes 4 --json-pp - samples/

    Scan a directory while ignoring all files with .txt extension.
    Print scan results to stdout as pretty formatted JSON.
    It is recommended to use quotes around glob patterns to prevent pattern
    expansion by the shell:

        scancode --json-pp - --ignore "*.txt" samples/

    Special characters supported in GLOB pattern:
    - *       matches everything
    - ?       matches any single character
    - [seq]   matches any character in seq
    - [!seq]  matches any character not in seq

    For a literal match, wrap the meta-characters in brackets.
    For example, '[?]' matches the character '?'.
    For details on GLOB patterns see https://en.wikipedia.org/wiki/Glob_(programming).

    Note: Glob patterns cannot be applied to path as strings.
    For example, this will not ignore "samples/JGroups/licenses".

        scancode --json - --ignore "samples*licenses" samples/


    Scan a directory while ignoring multiple files (or glob patterns).
    Print the scan results to stdout as JSON:

        scancode --json - --ignore README --ignore "*.txt" samples/

    Scan a directory for licenses and copyrights. Save scan results to an
    HTML file:

        scancode --license --copyright --html scancode_result.html samples/zlib

    To extract archives, see the 'extractcode' command instead.

Plugins Help Text
-----------------

The command line option for displaying all the plugins is:

- ``--plugins``

To see the help text from the Terminal, execute the following command::

    $ scancode --plugins

.. include::  /scancode-toolkit/rst_snippets/note_snippets/synopsis_install_quickstart.rst

.. note::

    Plugins that are shown by using ``--plugins`` include the following:

    #. Post-Scan Plugins
    #. Pre-Scan Plugins
    #. Output Options
    #. Output Control
    #. Basic Scan Options

The Following Text is displayed, i.e. This is the available plugins for Scancode Version 3.1.1 ::

    --------------------------------------------
    Plugin: scancode_output:csv  class: formattedcode.output_csv:CsvOutput
      codebase_attributes:
      resource_attributes:
      sort_order: 100
      required_plugins:
      options:
        help_group: output formats, name: csv: --csv
          help: Write scan output as CSV to FILE.
      doc: None

    --------------------------------------------
    Plugin: scancode_output:html  class: formattedcode.output_html:HtmlOutput
      codebase_attributes:
      resource_attributes:
      sort_order: 100
      required_plugins:
      options:
        help_group: output formats, name: html: --html
          help: Write scan output as HTML to FILE.
      doc: None

    --------------------------------------------
    Plugin: scancode_output:html-app  class: formattedcode.output_html:HtmlAppOutput
      codebase_attributes:
      resource_attributes:
      sort_order: 100
      required_plugins:
      options:
        help_group: output formats, name: html_app: --html-app
          help: (DEPRECATED: use the ScanCode Workbench app instead ) Write scan output as a mini HTML application to FILE.
      doc:
        Write scan output as a mini HTML application.

    --------------------------------------------
    Plugin: scancode_output:json  class: formattedcode.output_json:JsonCompactOutput
      codebase_attributes:
      resource_attributes:
      sort_order: 100
      required_plugins:
      options:
        help_group: output formats, name: output_json: --json
          help: Write scan output as compact JSON to FILE.
      doc: None

    --------------------------------------------
    Plugin: scancode_output:json-pp  class: formattedcode.output_json:JsonPrettyOutput
      codebase_attributes:
      resource_attributes:
      sort_order: 100
      required_plugins:
      options:
        help_group: output formats, name: output_json_pp: --json-pp
          help: Write scan output as pretty-printed JSON to FILE.
      doc: None

    --------------------------------------------
    Plugin: scancode_output:jsonlines  class: formattedcode.output_jsonlines:JsonLinesOutput
      codebase_attributes:
      resource_attributes:
      sort_order: 100
      required_plugins:
      options:
        help_group: output formats, name: output_json_lines: --json-lines
          help: Write scan output as JSON Lines to FILE.
      doc: None

    --------------------------------------------
    Plugin: scancode_output:spdx-rdf  class: formattedcode.output_spdx:SpdxRdfOutput
      codebase_attributes:
      resource_attributes:
      sort_order: 100
      required_plugins:
      options:
        help_group: output formats, name: spdx_rdf: --spdx-rdf
          help: Write scan output as SPDX RDF to FILE.
      doc: None

    --------------------------------------------
    Plugin: scancode_output:spdx-tv  class: formattedcode.output_spdx:SpdxTvOutput
      codebase_attributes:
      resource_attributes:
      sort_order: 100
      required_plugins:
      options:
        help_group: output formats, name: spdx_tv: --spdx-tv
          help: Write scan output as SPDX Tag/Value to FILE.
      doc: None

    --------------------------------------------
    Plugin: scancode_output:template  class: formattedcode.output_html:CustomTemplateOutput
      codebase_attributes:
      resource_attributes:
      sort_order: 100
      required_plugins:
      options:
        help_group: output formats, name: custom_output: --custom-output
          help: Write scan output to FILE formatted with the custom Jinja template file.
        help_group: output formats, name: custom_template: --custom-template
          help: Use this Jinja template FILE as a custom template.
      doc: None

    --------------------------------------------
    Plugin: scancode_output_filter:ignore-copyrights  class: cluecode.plugin_ignore_copyrights:IgnoreCopyrights
      codebase_attributes:
      resource_attributes:
      sort_order: 100
      required_plugins:
      options:
        help_group: output filters, name: ignore_copyright_holder: --ignore-copyright-holder
          help: Ignore a file (and all its findings) if a copyright holder contains a match to the <pattern> regular expression. Note that this will ignore a file even if it has other scanned data such as a license or errors.
        help_group: output filters, name: ignore_author: --ignore-author
          help: Ignore a file (and all its findings) if an author contains a match to the <pattern> regular expression. Note that this will ignore a file even if it has other findings such as a license or errors.
      doc:
        Filter findings that match given copyright holder or author patterns.
        Has no effect unless the --copyright scan is requested.

    --------------------------------------------
    Plugin: scancode_output_filter:only-findings  class: scancode.plugin_only_findings:OnlyFindings
      codebase_attributes:
      resource_attributes:
      sort_order: 100
      required_plugins:
      options:
        help_group: output filters, name: only_findings: --only-findings
          help: Only return files or directories with findings for the requested scans. Files and directories without findings are omitted (file information is not treated as findings).
      doc:
        Filter files or directories without scan findings for the requested scans.

    --------------------------------------------
    Plugin: scancode_post_scan:classify-package  class: summarycode.classify:PackageTopAndKeyFilesTagger
      codebase_attributes:
      resource_attributes:
      sort_order: 0
      required_plugins:
      options:
      doc:
        Tag resources as key or top level based on Package-type specific settings.

    --------------------------------------------
    Plugin: scancode_post_scan:consolidate  class: scancode.plugin_consolidate:Consolidator
      codebase_attributes: consolidated_components, consolidated_packages
      resource_attributes: consolidated_to
      sort_order: 8
      required_plugins:
      options:
        help_group: post-scan, name: consolidate: --consolidate
          help: Group resources by Packages or license and copyright holder and return those groupings as a list of consolidated packages and a list of consolidated components. This requires the scan to have/be run with the copyright, license, and package options active
      doc:
        A ScanCode post-scan plugin to return consolidated components and consolidated
        packages for different types of codebase summarization.

        A consolidated component is a group of Resources that have the same origin.
        Currently, consolidated components are created by grouping Resources that have
        the same license expression and copyright holders and the files that contain
        this license expression and copyright holders combination make up 75% or more of
        the files in the directory where they are found.

        A consolidated package is a detected package in the scanned codebase that has
        been enhanced with data about other licenses and holders found within it.

        If a Resource is part of a consolidated component or consolidated package, then
        the identifier of the consolidated component or consolidated package it is part
        of is in the Resource's ``consolidated_to`` field.

    --------------------------------------------
    Plugin: scancode_post_scan:filter-clues  class: cluecode.plugin_filter_clues:RedundantCluesFilter
      codebase_attributes:
      resource_attributes:
      sort_order: 1
      required_plugins:
      options:
        help_group: post-scan, name: filter_clues: --filter-clues
          help: Filter redundant duplicated clues already contained in detected license and copyright texts and notices.
      doc:
        Filter redundant clues (copyrights, authors, emails, and urls) that are already
        contained in another more important scan result.

    --------------------------------------------
    Plugin: scancode_post_scan:is-license-text  class: licensedcode.plugin_license_text:IsLicenseText
      codebase_attributes:
      resource_attributes: is_license_text
      sort_order: 80
      required_plugins:
      options:
        help_group: post-scan, name: is_license_text: --is-license-text
          help: Set the "is_license_text" flag to true for files that contain mostly license texts and notices (e.g over 90% of the content). [EXPERIMENTAL]
      doc:
        Set the "is_license_text" flag to true for at the file level for text files
        that contain mostly (as 90% of their size) license texts or notices.
        Has no effect unless --license, --license-text and --info scan data
        are available.

    --------------------------------------------
    Plugin: scancode_post_scan:license-clarity-score  class: summarycode.score:LicenseClarityScore
      codebase_attributes: license_clarity_score
      resource_attributes:
      sort_order: 110
      required_plugins:
      options:
        help_group: post-scan, name: license_clarity_score: --license-clarity-score
          help: Compute a summary license clarity score at the codebase level.
      doc:
        Compute a License clarity score at the codebase level.

    --------------------------------------------
    Plugin: scancode_post_scan:license-policy  class: licensedcode.plugin_license_policy:LicensePolicy
      codebase_attributes:
      resource_attributes: license_policy
      sort_order: 9
      required_plugins:
      options:
        help_group: post-scan, name: license_policy: --license-policy
          help: Load a License Policy file and apply it to the scan at the Resource level.
      doc:
        Add the "license_policy" attribute to a resouce if it contains a
        detected license key that is found in the license_policy.yml file

    --------------------------------------------
    Plugin: scancode_post_scan:mark-source  class: scancode.plugin_mark_source:MarkSource
      codebase_attributes:
      resource_attributes: source_count
      sort_order: 8
      required_plugins:
      options:
        help_group: post-scan, name: mark_source: --mark-source
          help: Set the "is_source" to true for directories that contain over 90% of source files as children and descendants. Count the number of source files in a directory as a new source_file_counts attribute
      doc:
        Set the "is_source" flag to true for directories that contain
        over 90% of source files as direct children.
        Has no effect unless the --info scan is requested.

    --------------------------------------------
    Plugin: scancode_post_scan:summary  class: summarycode.summarizer:ScanSummary
      codebase_attributes: summary
      resource_attributes:
      sort_order: 10
      required_plugins:
      options:
        help_group: post-scan, name: summary: --summary
          help: Summarize license, copyright and other scans at the codebase level.
      doc:
        Summarize a scan at the codebase level.

    --------------------------------------------
    Plugin: scancode_post_scan:summary-by-facet  class: summarycode.summarizer:ScanByFacetSummary
      codebase_attributes: summary_by_facet
      resource_attributes:
      sort_order: 200
      required_plugins:
      options:
        help_group: post-scan, name: summary_by_facet: --summary-by-facet
          help: Summarize license, copyright and other scans and group the results by facet.
      doc:
        Summarize a scan at the codebase level groupping by facets.

    --------------------------------------------
    Plugin: scancode_post_scan:summary-keeping-details  class: summarycode.summarizer:ScanSummaryWithDetails
      codebase_attributes: summary
      resource_attributes: summary
      sort_order: 100
      required_plugins:
      options:
        help_group: post-scan, name: summary_with_details: --summary-with-details
          help: Summarize license, copyright and other scans at the codebase level, keeping intermediate details at the file and directory level.
      doc:
        Summarize a scan at the codebase level and keep file and directory details.

    --------------------------------------------
    Plugin: scancode_post_scan:summary-key-files  class: summarycode.summarizer:ScanKeyFilesSummary
      codebase_attributes: summary_of_key_files
      resource_attributes:
      sort_order: 150
      required_plugins:
      options:
        help_group: post-scan, name: summary_key_files: --summary-key-files
          help: Summarize license, copyright and other scans for key, top-level files. Key files are top-level codebase files such as COPYING, README and package manifests as reported by the --classify option "is_legal", "is_readme", "is_manifest" and "is_top_level" flags.
      doc:
        Summarize a scan at the codebase level for only key files.

    --------------------------------------------
    Plugin: scancode_pre_scan:classify  class: summarycode.classify:FileClassifier
      codebase_attributes:
      resource_attributes: is_legal, is_manifest, is_readme, is_top_level, is_key_file
      sort_order: 50
      required_plugins:
      options:
        help_group: pre-scan, name: classify: --classify
          help: Classify files with flags telling if the file is a legal, or readme or test file, etc.
      doc:
        Classify a file such as a COPYING file or a package manifest with a flag.

    --------------------------------------------
    Plugin: scancode_pre_scan:facet  class: summarycode.facet:AddFacet
      codebase_attributes:
      resource_attributes: facets
      sort_order: 20
      required_plugins:
      options:
        help_group: pre-scan, name: facet: --facet
          help: Add the <facet> to files with a path matching <pattern>.
      doc:
        Assign one or more "facet" to each file (and NOT to directories). Facets are
        a way to qualify that some part of the scanned code may be core code vs.
        test vs. data, etc.

    --------------------------------------------
    Plugin: scancode_pre_scan:ignore  class: scancode.plugin_ignore:ProcessIgnore
      codebase_attributes:
      resource_attributes:
      sort_order: 100
      required_plugins:
      options:
        help_group: pre-scan, name: ignore: --ignore
          help: Ignore files matching <pattern>.
        help_group: pre-scan, name: include: --include
          help: Include files matching <pattern>.
      doc:
        Include or ignore files matching patterns.

    --------------------------------------------
    Plugin: scancode_scan:copyrights  class: cluecode.plugin_copyright:CopyrightScanner
      codebase_attributes:
      resource_attributes: copyrights, holders, authors
      sort_order: 4
      required_plugins:
      options:
        help_group: primary scans, name: copyright: -c, --copyright
          help: Scan <input> for copyrights.
      doc:
        Scan a Resource for copyrights.

    --------------------------------------------
    Plugin: scancode_scan:emails  class: cluecode.plugin_email:EmailScanner
      codebase_attributes:
      resource_attributes: emails
      sort_order: 8
      required_plugins:
      options:
        help_group: other scans, name: email: -e, --email
          help: Scan <input> for emails.
        help_group: scan options, name: max_email: --max-email
          help: Report only up to INT emails found in a file. Use 0 for no limit.
      doc:
        Scan a Resource for emails.

    --------------------------------------------
    Plugin: scancode_scan:generated  class: summarycode.generated:GeneratedCodeDetector
      codebase_attributes:
      resource_attributes: is_generated
      sort_order: 50
      required_plugins:
      options:
        help_group: other scans, name: generated: --generated
          help: Classify automatically generated code files with a flag.
      doc:
        Tag a file as generated.

    --------------------------------------------
    Plugin: scancode_scan:info  class: scancode.plugin_info:InfoScanner
      codebase_attributes:
      resource_attributes: date, sha1, md5, mime_type, file_type, programming_language, is_binary, is_text, is_archive, is_media, is_source, is_script
      sort_order: 0
      required_plugins:
      options:
        help_group: other scans, name: info: -i, --info
          help: Scan <input> for file information (size, checksums, etc).
      doc:
        Scan a file Resource for miscellaneous information such as mime/filetype and
        basic checksums.

    --------------------------------------------
    Plugin: scancode_scan:licenses  class: licensedcode.plugin_license:LicenseScanner
      codebase_attributes:
      resource_attributes: licenses, license_expressions
      sort_order: 2
      required_plugins:
      options:
        help_group: primary scans, name: license: -l, --license
          help: Scan <input> for licenses.
        help_group: scan options, name: license_score: --license-score
          help: Do not return license matches with a score lower than this score. A number between 0 and 100.
        help_group: scan options, name: license_text: --license-text
          help: Include the detected licenses matched text.
        help_group: scan options, name: license_text_diagnostics: --license-text-diagnostics
          help: In the matched license text, include diagnostic highlights surrounding with square brackets [] words that are not matched.
        help_group: scan options, name: license_url_template: --license-url-template
          help: Set the template URL used for the license reference URLs. Curly braces ({}) are replaced by the license key.
        help_group: scan options, name: license_diag: --license-diag
          help: (DEPRECATED: this is always included by default now). Include diagnostic information in license scan results.
        help_group: miscellaneous, name: reindex_licenses: --reindex-licenses
          help: Check the license index cache and reindex if needed and exit.
      doc:
        Scan a Resource for licenses.

    --------------------------------------------
    Plugin: scancode_scan:packages  class: packagedcode.plugin_package:PackageScanner
      codebase_attributes:
      resource_attributes: packages
      sort_order: 6
      required_plugins: scan:licenses
      options:
        help_group: primary scans, name: package: -p, --package
          help: Scan <input> for package manifests and packages.
        help_group: documentation, name: list_packages: --list-packages
          help: Show the list of supported package types and exit.
      doc:
        Scan a Resource for Package manifests and report these as "packages" at the
        right file or directory level.

    --------------------------------------------
    Plugin: scancode_scan:urls  class: cluecode.plugin_url:UrlScanner
      codebase_attributes:
      resource_attributes: urls
      sort_order: 10
      required_plugins:
      options:
        help_group: other scans, name: url: -u, --url
          help: Scan <input> for urls.
        help_group: scan options, name: max_url: --max-url
          help: Report only up to INT urls found in a file. Use 0 for no limit.
      doc:
        Scan a Resource for URLs.

``--list-packages`` Option
--------------------------

This shows all the types of packages that can be scanned using Scancode.
These are located in packagedcode i.e. Code used to parse various package formats.

..
    [ToDo]
    Check and Write docs

``--print-options`` Option
--------------------------

This option prints the options selected for one specific scan command.

If we run this command::

    scancode -clpieu --json-pp sample.json samples --classify --summary --summary-with-details --print-options

The output will be::

    Options:
      classify: True
      copyright: True
      email: True
      info: True
      license: True
      list_packages: None
      output_json_pp: <unopened file 'sample.json' wb>
      package: True
      reindex_licenses: None
      summary: True
      summary_with_details: True
      url: True
