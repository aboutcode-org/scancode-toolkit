
Changelog
=========


next
------------------
* New features
 *  

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
 * Created new extractcode standlone command for
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
 * simple command line with html, htaml-app and JSON formats output

 
