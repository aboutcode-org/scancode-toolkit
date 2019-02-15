Changelog
=========

v3.0.2 (2019-02-15)
-------------------

Minor bug fixes:

 - A tracing flag was turned on in the summary module by mistake. Reported by @tdruez #1374
 - Correct a Maven parsing error. Reported and fixed by @linexb #1373
 - Set proper links in the README. Reported and fixed by @sschubert #1371
 - No changes from v3.0.1


v3.0.0 (2019-02-14)
-------------------

License detection:
 * Add new and improved licenses and license detection rules #1334 #1335 #1336 #1337 ##1357 
 * Fix-up the license text inside the `bsl-*.LICENSE` files #1338 by @fviernau
 * Add tests for commnon NuGet license bare URLs (until recently NuGet nupsec
   only had a license URL as licensing documentation) 
 * Add a license for the `PSK` contributions to OpenSSL #1341 by @fviernau
 * Improve License Match scoring and filtering for very short rules
 * Do not run license and copyright detection on media files: Media should not
   contain text #1347 #1348 
 * Detect scea-1.0 license correctly #1346
 * Do not detect warranty disclaimer as GPL #1345
 * Support quoted SPDX expressions and more comment marker prefixes
 * Use Free Restricted category for fraunhofer-fdk-aac-codec #1352 by @LeChasseur
 * Remove the spdx_license_key from here-proprietary #1360 by @sschuberth
 * Add new post-scan plugin to tag a file containing only license #1366
 * Add new license  #1365 and rules #1358

Packages:
 * Improve npm vcs_url handling #1314 by @majurg
 * Improve Maven POM license detection #1344
 * Add Maven POM URL detection 
 * Recognize .gem archives as packages 
 * Improve parsing of Pypi Python setup.py 
 * Improve package summaries. Add new plugin to improve package classification #1339

Other:
 * Fix doc typo by #1329 @farialima
 * Add new experimental pre-scan plugin to ignore binaries


v2.9.9 (2018-12-12)
-------------------

This is the penultimate pre-release of what will come up for 3.0 with some API change for packages.

API changes:
 * Streamline Package models #1226 #1324 and #1327. In particular the way checksums are managed has changed

Other changes:
 * Copyright detection improvements #1305 by @JonoYang
 * Correct CC-BY V3.0 and V4.0 license texts by correct one by @sschuberth #1320
 * Add new and improved licenses and license detection rules including the latest SPDX list 3.4 and #1322 #1324 
 * Rename proprietary license key to proprietary-license 
 * Rename commercial license key to commercial-license 
 * Improve npm package.json handling #1308 and #1314 by @majurg


v2.9.8 (2018-12-12)
-------------------

This is a close-to-final pre-release of what will come up for 3.0 with some API change for packages.

API changes:
 * In Package models, rename normalized_license to license_expression and 
   add license detection on the declared_license to populate the license_expression #1092 #1268 #1278

Outputs:
 * Do not open output files until the command lines are validated as correct #1266
 * The html-app output is marked as DEPRECATED. Use the AboutCode manager app instead #
 * Ensure HTML outputs can deal with non-ASCII file paths without crashsing #1292
 * JSON outputs now use a "headers" attributes for top-level scan headers #
 * SPDX output is now possible even without "--info" SHA1 checksums. This creates a partially valid document
 * LicenseRef for non-SPDX ScanCode licenses are named as "LicenseRef-scancode-<scancode key>" #
 * license_expression are correctly included in the CSV output #1238
 * do not crash with multiple outputs  #1199
 * Ensure CSV output include packages #1145

License detection:
 * Ensure license expressions are present in CSV output #1238
 * Fix 'license detection tests' collection on Windows #1182
 * An optional  "relevance" attribute has been added to the license YAML
   attributes. This is to store the relevance to e matched .LICENSE text when used
   as a rule.
 * Licenses have been synchronized with the latest v3.3 SPDX license list and the latest DejaCode licenses #1242
 * Duplicated SPDX keys have been fixed #1264
 * Add new and improved license detection rules #1313 #1306 #1302 #1298 #1293 
   #1291 #1289 #1270 #1269 #1192 #1186 #1170 #1164 #1128 #1124 #1112 #1110 #1108
   #1098 #1069 #1063 #1058 #1052 #1050 #1039 #987 #962 #929

Packages:
 * Add support for haxe "haxelib" package manifests #1227
 * Remove code_type attribute from Package models
 * In Package models, rename normalized_license  to license_expression and 
   add license detection on the declared_license to populate the license_expression #1092 #1268 #1278
 * Improve data returned for PHP Composer packages
 * Add PackageURL to top level ouput for packages
 * Report nuget as proper packages #1088

Summary:
 * improve summary and license score computation #1180

Misc:
 * Minor copyright detection improvements #1248 #1244 #1234 #1198 #1123 #1087
 * Ensure all temporary directories are prefixed with "scancode-"
 * Drop support for Linux 32 bits #1259
 * Do not attempt to scan encrypted PDF documents
 * Improve "data" files detection 
 * ScanCode can be installed from Pypi correctly #1214 #1183
 * Improve reporting of programming languages #1194 
 * Fix running post scan plugins #1141 

Command line:
 * Always delete temporary files when no longer needed. #1231
 * Add a new --keep-temp-files option to keep temp files which is false by default. #1231
 * Improve dependent plugin activation so it is done only when needed #1235

Internals:
 * Improve reusing resource.VirtualCode
 * Place all third-party packages under thirdparty #1219 and update ABOUT files


Credits: Many thanks to everyone that contributed to this release with code and bug reports

 * @nicoddemus
 * @chinyeungli
 * @johnmhoran
 * @jonasob
 * @DennisClark
 * @arthur657834
 * @JonoYang
 * @armijnhemel
 * @furuholm
 * @mjherzog
 * @sschuberth
 * @MartinPetkov
 * @jhgoebbert
 * @bobgob
 * @majurg
 * @tdruez
 * @tomeks666
 * @geneh
 * @jonassmedegaard

and many other that I may have missed. 



v2.9.7 (2018-10-25)
-------------------

No changes.



v2.9.6 (2018-10-25)
-------------------

 * Add declared license normalization #1092 
 * Add new and improved license rules
 * Add mising and clean up ABOUT files for all embedded third-party libraries
 * Improve npm package.json handling (better keuword support)
 * Update thirdparty libraries #1224

Credits: Many thanks to everyone that contributed to this release with code and bug reports


v2.9.5 (2018-10-22)
-------------------

This is a minor pre-release of what will come up for 3.0 with no API change.

 * Place all third-party packages under thirdparty #1219

Credits: Many thanks to everyone that contributed to this release with code and bug reports

 * @JonoYang


v2.9.4 (2018-10-19)
-------------------

This is a pre-release of what will come up for 3.0 with several API changes
related to packages.

 * Add Package URL field to top-level package output #1149
 * --package option should collect homepage URL for packages #645
 * Support installation from Pypi and update various third-parties to their
   latest version #1183 
 * Fix bug where multiple outputs with --html would crash scancode #
 * Add new and improved licenses and license detection rules #1192 #1186
 * Ensure that plugin failure trigger a proper error exit code #1199
 * Allow plugins to contribute codebase-level attributes in addition to
   resource-level attributes.
 * Output plugins can now be called from code #1148
 * Fix incorrect copyright detection #1198
 * Detect programming language more strictly and efficiently #1194
 * Use simpler list of source package URLs/purls #1206
 * Add purl to the packages data #1149 
 * Use direct attributes for package checksums #1189 
 * Remove package_manifest attribute for packages
 * Add new Package "manifest_path" attribute which is a relative path to
   the manifest file if any, such as a Maven .pom or a npm package.json.
 
Credits: Many thanks to everyone that contributed to this release with code and bug reports

 * @MartinPetkov 
 * @majurg
 * @JonoYang


v2.9.3 (2018-09-27)
-------------------

This is a pre-release of what will come up for 3.0 with an API change.

API change:
 * The returned copyright data structure has changed and is now simpler and less nested

Licenses:
 * Add new license and rules and improve licene rules #1186 #1108 #1124 #1171 #1173 #1039 #1098 #1111
 * Add new license clarity scoring #1180
   This is also for use in the ClearlyDefined project
 * Add is_exception to license scan results #1159 

Copyrights:
 * Copyright detection  has been improved #930 #965 #1103
 * Copyright data structure has been updated

Packages:
 * Add support for FreeBSD packages (ports) #1073
 * Add support for package root detection
 * Detect nuget packages correctly @1088

Misc:

 * Add facet, classification and summarizer plugins #357 
 * Fix file counts #1055
 * Fix corrupted license cache error
 * Upgrade all thridparty libraries #1070
 * De-vendor prebuilt binaries to ease packaging for Linux distros #469

Credits: Many thanks to everyone that contributed to this release with code and bug reports

 * @selmf
 * @paralax
 * @majurg
 * @mueller-ma
 * @MartinPetkov
 * @techytushar
 


v2.9.2 (2018-05-08)
-------------------
This is a major pre-release of what will come up for 3.0. with significant
packages and license API changes.

API changes:
 * Simplify output option names #789 
 * Update the packages data structure and introduce Package URLs #275
 * Add support for license expressions #74 with full exceptions support

Licenses:
 * Add support for license expressions #74 with full exceptions support
 * Enable SPDX license identifier match #81
 * Update and change handling of composite licenses now that we support expressions 
 * Symchronize licenses with latest from SPDX and DejaCode #41
 * Add new licenses ofr odds and ends: other-permissive and other-copyleft
 * refine license index cache handling
 * remove tests without value
 * Add new license policy plugin #214, #880

Packages:
 * Split packages from package_manifest #1027. This is experimental
   The packages scan return now a single package_manifest key (not a list)
   And a post_scan plugin (responding to the same --package) option perform
   a roll-up of the manifest informationat the proper level for a package
   type as the "packages" attribute (which is still a list). For instance
   a package.json "package_manifest" will end up having a "packages" entry
   in its parent directory.
 * Include and return Package URLs (purl) #805 and #275
 * Major rework of the package data structure #275
   * Rename asserted_license to declared_licensing #275
   * Add basic Godeps parsing support #275
   * Add basic gemspec and Rubygems parsing support #275
   * Add basic Gemfile.lock parsing support #275 
   * Add basic Win DLL parsing support #275
   * Replace MD5/SHA1 by a list of checksums #275 
   * Use a single download_url, not a list #275 
   * Add namespace to npm. Compute defaults URL #275 

Misc:
 * multiple minor bug fixes
 * do not ignore .repo files #881

Credits: Many thanks to everyone that contributed to this release with code and bug reports

 * @JonoYang
 * @majurg
 * @pombredanne
 * @yash-nisar
 * @ThorstenHarter


v2.9.1 (2018-03-22)
-------------------

This is a minor pre-release of what will come up for 3.0 with no API change.

Licenses:
 * There are new and improved licenses and license detection rules #994 #991 #695 #983 #998 #969

Copyrights:
 * Copyright detection  has been improved #930 #965
 
Misc:
 * Improve support for JavaScript map files: they may contain both debugging
   information and whole package source code.
 * multiple minor bug fixes

Credits: Many thanks to everyone that contributed to this release with code and bug reports

 * @haikoschol
 * @jamesward
 * @JonoYang
 * @DennisClark
 * @swinslow


v2.9.0b1 (2018-03-02)
---------------------

This is a major pre-release of what will come up for 3.0

This has a lot of new changes including improved plugins, speed and detection 
that are not yet fully documented but it can be used for testing.

API changes:
 * Command line API

  * `--diag` option renamed to `--license-diag`

  * `--format <format code>` option has been replaced by multiple options one
    for each format such as `--format-csv` `--format-json` and multiple formats
    can be requested at once

  * new experimental `--cache-dir` option and `SCANCODE_CACHE` environment variable
    and `--temp-dir` and `SCANCODE_TMP` environment variable to set the temp and
    cache directories.

 * JSON data output format: no major changes

 * programmatic API in scancode/api.py:

  * get_urls(location, threshold=50): new threshold argument

  * get_emails(location, threshold=50): new threshold argument

  * get_file_infos renamed to get_file_info

  * Resource moved to scancode.resource and significantly updated

  * get_package_infos renamed to get_package_info


Command line
 * You can select multiple outputs at once (e.g. JSON and CSV, etc.) #789
 * There is a new capability to reload a JSON scan to reprocess it with postcsan
   plugins and or converting a JSON scan to CSV or else.


Licenses:
 * There are several new and improved licenses and license detection rules #799 #774 #589
 * Licenses data now contains the full name as well as the short name.

 * License match have a notion of "coverage" which is the number of matched
   words compared to the number of words in the matched rule.
 * The license cache is not checked anymore for consistency once created which
   improved startup times. (unless you are using a Git checkout and you are 
   developping with a SCANCODE_DEV_MODE tag file present)
 * License catagory names have been improved

Copyrights:
 * Copyright detection in binary files has been improved
 * There are several improvements to the copyright detection quality fixing these
   tickets: #795 #677 #305 #795
 * There is a new post scan plugin that can be used to ignore certain copyright in
   the results

Summaries:
 * Add new support for  copyright summaries using smart holder deduplication #930

Misc:
 * Add options to limit the number of emails and urls that are collected from
   each file (with a default to 50) #384
 * When configuring in dev mode, VS Code settings are created
 * Archive detection has been improved
 * There is a new cache and temporary file configuration with --cache-dir and 
   --temp-dir CLI options. The --no-cache option has been removed
 * Add new --examples to show usage examples help
 * Move essential configuration to a scancode_config.py module
 * Only read a few pages from PDF files by default
 * Improve handling of files with weird characters in their names on all OSses
 * Improve detection of archive vs. comrpessed files
 * Make all copyright tests data driven using YAML files like for license tests
 

Plugins
 * Prescan plugins can now exclude files from the scans 
 * Plugins can now contribute arbitrary command line options #787 and #748
 * there is a new plugin stage called output_filter to optionally filter a scan before output.
   One example is to keep "only findings" #787
 * The core processing is centered now on a Codebase and Resource abstraction
   that represents the scanned filesystem in memory #717 #736
   All plugins operate on this abstraction
 * All scanners are also plugins #698 and now everything is a plugin including the scans
 * The interface for output plugins is the same as other plugins #715

 
Credits: Many thanks to everyone that contributed to this release with code and bug reports
(and this list is likely missing some)

 * @SaravananOffl
 * @jpopelka
 * @yashdsaraf
 * @haikoschol
 * @jdaguil
 * @ajeans
 * @DennisClark
 * @susg
 * @pombredane
 * @mjherzog
 * @Sidsharik
 * @nishakm
 * @yasharmaster
 * @techytushar
 * @JonoYang
 * @majurg
 * @aviral1701
 * @haikoschol
 * @chinyeungli
 * @vivonk
 * @Chaitya62
 * @inishchith


v2.2.1 (2017-10-05)
-------------------

This is a minor release with several bug fixes, one new feature
and one (minor) API change.

* API change:

 * Licenses data now contains a new reference_url attribute instead of a
   dejacode_url attribute. This defaults to the public DejaCode URL and
   can be configured with the new --license-url-template command line
   option.

* New feature:

 * There is a new "--format jsonlines" output format option.
   In this format, each line in the output is a valid JSON document. The
   first line contains a "header" object with header-level data such as
   notice, version, etc. Each line after the first contains the scan
   results for a single file formatted with the same structure as a
   whole scan results JSON documents but without any header-level
   attributes. See also http://jsonlines.org/

* Other changes:

 * Several new and improved license detection rules have been added.
   The logic of detection has been refined to handle some rare corner
   cases. The underscore character "_" is treated as part of a license
   word and the handling of negative and false_positive license rules
   has been simplified.

 * Several issues with dealing with codebase with non-ASCII,
   non-UTF-decodable file paths and other filesystem encodings-related
   bug have been fixed.

 * Several copyright detection bugs have been fixed.
 * PHP Composer and RPM packages are now detected with --package
 * Several other package types are now detected with --package even
   though only a few attribute may be returned for now until full parser
   are added.
 * Several parsing NPM packages bugs have been fixed. 
 * There are some minor performance improvements when scanning some
   large file for licenses.


v2.1.0 (2017-09-22)
-------------------

This is a minor release with several new and improved features and bug
fixes but no significant API changes.

 * New plugin architecture by @yashdsaraf

  * we can now have pre-scan, post-scan and output format plugins
  * there is a new CSV output format and some example, experimental plugins
  * the CLI UI has changed to better support these plugins

 * New and improved licenses and license detection rules including
   support for EPL-2.0 and OpenJDK-related licensing and synchronization
   with the latest SPDX license list

 * Multiple bug fixes such as:

   * Ensure that authors are reported even if there is no copyright #669
   * Fix Maven package POM parsing infinite loop #721
   * Improve handling of weird non-unicode byte paths #688 and #706
   * Improve PDF parsing to avoid some crash #723

Credits: Many thanks to everyone that contributed to this release with code and bug reports
(and this list is likely missing some)

* @abuhman
* @chinyeungli
* @jimjag
* @JonoYang
* @jpopelka
* @majurg
* @mjherzog
* @pgier
* @pkajaba
* @pombredanne
* @scottctr
* @sschuberth
* @yahalom5776
* @yashdsaraf


v2.0.1 (2017-07-03)
-------------------

 This is a minor release with minor new and improved features and bug
 fixes.

 * New and improved license detection, including refined match scoring
   for #534
 * Bug fixed in License detection leading to a very long scan time for some
   rare JavaScript files. Reported by @jarnugirdhar
 * New "base_name" attribute returned with file information. Reported by
   @chinyeungli
 * Bug fixed in Maven POM package detection. Reported by @kalagp
 

v2.0.0 (2017-06-23)
-------------------

 This is a major release with several new and improved features and bug
 fixes.
 
 Some of the key highlights include:

 * License:

   * Brand new, faster and accurate detection engine using multiple
     techniques eventually doing multiple exhaustive comparisons of
     a scanned file content against all the license and rule texts.

   * Several new licenses and over 2500+ new and improved licenses
     detection rules have been added making the detection significantly
     better (and weirdly enough faster too as a side-effect of the new
     detection engine)

   * the matched license text can be optionally returned with the
     `--license-text` option

   * The detection accuracy has been benchmarked against other detection
     engine and ScanCode has shown to be more accurate and
     comprehensive than all the other engines reviewed.

   * improved scoring of license matches


 * Package and dependencies:

  * new and improved detection of multiple package formats: NPM, Maven,
    NuGet, PHP Composer, Python Pypi and RPM. In most cases direct,
    declared dependencies are also reported.

  * several additional package formats will be reported in the future
    version.

  * note: the structure of Packages data is evolving and should not be
    considered API at this stage


 * Scan outputs: 

  * New SPDX tag/values and RDF outputs.

  * new compact JSON format (the pretty printed format is still
    available with the the `json-pp` format).
    The JSON format has been changed significantly and is closer to a
    documented, standard format that we call the ABC data format.

  * Minor refinements on the html and html-app format. Note that the
    html-app format will be deprecated and replaced by the new AboutCode
    Manager desktop app (electron-based) in future versions.


 * Copyright: Improved copyright detection: several false positive are
   no longer returned and copyrights are more accurate


 * Archive: support for shallow extraction and support for new archive
   types (such as Spring boot shell archives)


 * Performance:

  * Everything is generally faster, and license detection performance
    has been significantly improved.

  * Scans can run on multiple processes in parallel with the new 
    `--processes` option speeding up things even further. A scan of a
    full Debian pool of source packages was reported to scan in about
    11 hours (on a rather beefy 144 cores, 256GB machine)

  * Reduced memory usage with the use of caching

 * Other notes:

   * This is the last release with Linux 32 bits architecture support
   * The scan of a file can be interrupted after a timeout with a 120
     seconds default
   * ScanCode is now available as a library on the Pypi Python package
     index for use as a library. The documentation for the library usage
     will follow in future versions
   * New `--ignore` option: You can optionally ignore certain file and
     paths during a scan
   * New `--diag option`: display additional debug and diagnostic data
   * The scanned file paths can now reported as relative, rooted or
     absolute with new command line options with a default to a rooted
     path. 


 Thank you to all contributors to this release and the 200+ stars
 and 60+ forks on GitHub!

 * Credits in alphabetical order:

  Alexander Lisianoi
  Avi Aryan
  Benedikt Spranger
  Chin Yeung
  Dennis Clark
  Hugo Jacob
  Jakub Wilk
  Jericho @attritionorg
  Jillian Daguil
  Jiri Popelka
  John M. Horan
  Jonathan "Jono" Yang
  Li Ha
  Michael Herzog
  Michael Rupprecht
  Nusrat Sultana
  Paul Kunz
  Philippe Ombredanne
  Rakesh Balusa
  Ranvir Singh
  Richard Fontana
  Sebastian Schuberth
  Steven Esser
  Thomas Gleixner
  Tisoga @forrestchang
  Yash D. Saraf
  Yash Sharma


v1.6.0 (2016-01-29)
-------------------

* New features

 * The HTML app now displays a copyright holder summary graphic
 * HTML app ui enhancements
 * File extraction fixes
 * New and improved license and detection rules
 * Other minor improvements and minor bug fixes


v1.5.0 (2015-12-15)
-------------------

* New features

 * The HTML app now display a license summary graphic
 * Copyright holders and Authors are now collected together with copyrights
 * New email and url scan options: scan for URLs and emails
 * New and improved license and detection rules

These scans are for now only available in the JSON output 


v1.4.3 (2015-12-03)
-------------------

* Minor bug fix

 * In the HTML app, the scanned path was hardcoded as
   scancode-toolkit2/scancode-toolkit/samples instead of displaying the path
   that was scanned.


v1.4.2 (2015-12-03)
-------------------

* Minor features and bug fixes

 * The release archives were missing some code (packagedcode)
 * Improved --quiet option for command line operations
 * New support for custom Jinja templates for the HTML output.
   The template also has access to the whole License object to output full
   license texts or other data. Thanks to @ened Sebastian Roth for this.


v1.4.0 (2015-11-24)
-------------------

* New features and bug fixes

 * Separated JSON data into a separate file for the html app.
   https://github.com/nexB/scancode-toolkit/issues/38
 * Added support for scanning package and file information.
 * Added file and package information to the html-app and html output.
   https://github.com/nexB/scancode-toolkit/issues/76
 * improved CSS for html format output
   https://github.com/nexB/scancode-toolkit/issues/12
 * New and improved licenses rules and licenses.
 * Added support for nuget .nupkg as archives.
 * Created new extractcode standalone command for
   https://github.com/nexB/scancode-toolkit/issues/52
   Extracting archives is no longer part of the scancode command.
 * Scancode can now be called from anywhere.
   https://github.com/nexB/scancode-toolkit/issues/55
 * Various minor improvements for copyright detection.


v1.3.1 (2015-07-27)
-------------------

* Minor bug fixes.

 * fixed --verbose option https://github.com/nexB/scancode-toolkit/issues/37
 * Improved copyright and license detections (new rules, etc.)
 * other minor improvements and minor bug fixes:
   temptative fix for https://github.com/nexB/scancode-toolkit/issues/4
 * fixed for unsupported inclusion of Linux-32 bits pre-built binaries
   https://github.com/nexB/scancode-toolkit/issues/33


v1.3.0 (2015-07-24)
-------------------

* New features and bug fixes

 * scancode now ignores version control directories by default (.svn, .git, etc)
 * Improved copyright and license detections (new rules, etc.)
 * other minor improvements and minor bug fixes.
 * experimental and unsupported inclusion of Linux-32 bits pre-built binaries


v1.2.4 (2015-07-22)
-------------------

* Minor bug fixes.

 * Improved copyright detections.
 * can scan a single file located in the installation directory
 * other minor improvements and minor bug fixes.


v1.2.3 (2015-07-16)
-------------------

* Major bug fixes on Windows.

 * This is a major bug fix release for Windows. 
   The -extract option was not working on Windows in previous 1.2.x pre-releases


v1.2.2 (2015-07-14)
-------------------

* Minor bug fixes.

 * Support relative path when doing extract.


v1.2.1 (2015-07-13)
-------------------

* Minor bug fixes.

 * Improper extract warning handling


v1.2.0 (2015-07-13)
-------------------

* Major bug fixes.

 * Fixed issue #26: Slow --extract
 * Added support for progress during extraction (#27)


v1.1.0 (2015-07-06)
-------------------

* Minor bug fixes.

 * Enforced exclusivity of --extract option
 * Improved command line help.
 * Added continuous testing with Travis and Appveyor and fixed tests


v1.0.0 (2015-06-30)
-------------------

* Initial release.

 * support for scanning licenses and copyrights
 * simple command line with html, html-app and JSON formats output
