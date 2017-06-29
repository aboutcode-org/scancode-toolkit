Changelog
=========


2.1.0 (NEXT)
------------------

 This is a minor release with minor new and improved features and bug
 fixes.

 * New and improved license detection, including refined match scoring
   for #534
 * New "base_name" attribute returned with file information. Reported by
   @chinyeungli
 * Bug fixed in Maven POM package detection. Reported by @kalagp
 * Bug fixed in License detection leading to a very long scan time for some
   rare JavaScript files. Reported by @jarnugirdhar


2.0.0 (2017-06-23)
------------------

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
   no longer returned and copyright s are more accurate


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

 * Credits in alphabetic order:

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


1.6.0 (2016-01-29)
------------------

* New features

 * The HTML app now displays a copyright holder summary graphic
 * HTML app ui enhancements
 * File extraction fixes
 * New and improved license and detection rules
 * Other minor improvements and minor bug fixes


1.5.0 (2015-12-15)
------------------

* New features

 * The HTML app now display a license summary graphic
 * Copyright holders and Authors are now collected together with copyrights
 * New email and url scan options: scan for URLs and emails
 * New and improved license and detection rules

These scans are for now only available in the JSON output 


1.4.3 (2015-12-03)
------------------

* Minor bug fix

 * In the HTML app, the scanned path was hardcoded as
   scancode-toolkit2/scancode-toolkit/samples instead of displaying the path
   that was scanned.


1.4.2 (2015-12-03)
------------------

* Minor features and bug fixes

 * The release archives were missing some code (packagedcode)
 * Improved --quiet option for command line operations
 * New support for custom Jinja templates for the HTML output.
   The template also has access to the whole License object to output full
   license texts or other data. Thanks to @ened Sebastian Roth for this.


1.4.0 (2015-11-24)
------------------

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

1.3.1 (2015-07-27)
------------------

* Minor bug fixes.

 * fixed --verbose option https://github.com/nexB/scancode-toolkit/issues/37
 * Improved copyright and license detections (new rules, etc.)
 * other minor improvements and minor bug fixes:
   temptative fix for https://github.com/nexB/scancode-toolkit/issues/4
 * fixed for unsupported inclusion of Linux-32 bits pre-built binaries
   https://github.com/nexB/scancode-toolkit/issues/33


1.3.0 (2015-07-24)
------------------

* New features and bug fixes

 * scancode now ignores version control directories by default (.svn, .git, etc)
 * Improved copyright and license detections (new rules, etc.)
 * other minor improvements and minor bug fixes.
 * experimental and unsupported inclusion of Linux-32 bits pre-built binaries


1.2.4 (2015-07-22)
------------------

* Minor bug fixes.

 * Improved copyright detections.
 * can scan a single file located in the installation directory
 * other minor improvements and minor bug fixes.


1.2.3 (2015-07-16)
------------------

* Major bug fixes on Windows.

 * This is a major bug fix release for Windows. 
   The -extract option was not working on Windows in previous 1.2.x pre-releases


1.2.2 (2015-07-14)
------------------

* Minor bug fixes.

 * Support relative path when doing extract.


1.2.1 (2015-07-13)
------------------

* Minor bug fixes.

 * Improper extract warning handling


1.2.0 (2015-07-13)
------------------

* Major bug fixes.

 * Fixed issue #26: Slow --extract
 * Added support for progress during extraction (#27)


1.1.0 (2015-07-06)
------------------

* Minor bug fixes.

 * Enforced exclusivity of --extract option
 * Improved command line help.
 * Added continuous testing with Travis and Appveyor and fixed tests


1.0.0 (2015-06-30)
------------------

* Initial release.

 * support for scanning licenses and copyrights
 * simple command line with html, html-app and JSON formats output

 
