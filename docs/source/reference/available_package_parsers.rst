

.. _supported_packages:

Supported package manifests and package datafiles
-------------------------------------------------

Scancode supports a wide variety of package manifests, lockfiles
and other package datafiles containing package and dependency
information.

This documentation page is generated automatically from available package
parsers in scancode-toolkit during documentation builds.


.. list-table:: Supported Package Parsers
   :widths: 10 10 20 10 10 2
   :header-rows: 1

   * - Package type
     - Datasource ID
     - Path Patterns
     - Primary Language
     - Documentation URL
     - Description
   * - None
     - ``java_jar``
     - ``*.jar``
     - None
     - https://en.wikipedia.org/wiki/JAR_(file_format)
     - JAR Java Archive
   * - ``about``
     - ``about_file``
     - ``*.ABOUT``
     - None
     - https://aboutcode-toolkit.readthedocs.io/en/latest/specification.html
     - AboutCode ABOUT file
   * - ``alpine``
     - ``alpine_apk_archive``
     - ``*.apk``
     - None
     - https://wiki.alpinelinux.org/wiki/Alpine_package_format
     - Alpine Linux .apk package archive
   * - ``alpine``
     - ``alpine_apkbuild``
     - ``*APKBUILD``
     - None
     - https://wiki.alpinelinux.org/wiki/APKBUILD_Reference
     - Alpine Linux APKBUILD package script
   * - ``alpine``
     - ``alpine_installed_db``
     - ``*lib/apk/db/installed``
     - None
     - None
     - Alpine Linux installed package database
   * - ``android``
     - ``android_apk``
     - ``*.apk``
     - Java
     - https://en.wikipedia.org/wiki/Apk_(file_format)
     - Android application package
   * - ``android_lib``
     - ``android_aar_library``
     - ``*.aar``
     - Java
     - https://developer.android.com/studio/projects/android-library
     - Android library archive
   * - ``autotools``
     - ``autotools_configure``
     - ``*/configure``
       ``*/configure.ac``
     - None
     - https://www.gnu.org/software/automake/
     - Autotools configure script
   * - ``axis2``
     - ``axis2_mar``
     - ``*.mar``
     - Java
     - https://axis.apache.org/axis2/java/core/docs/modules.html
     - Apache Axis2 module archive
   * - ``axis2``
     - ``axis2_module_xml``
     - ``*/meta-inf/module.xml``
     - Java
     - https://axis.apache.org/axis2/java/core/docs/modules.html
     - Apache Axis2 module.xml
   * - ``bazel``
     - ``bazel_build``
     - ``*/BUILD``
     - None
     - https://bazel.build/
     - Bazel BUILD
   * - ``bower``
     - ``bower_json``
     - ``*/bower.json``
       ``*/.bower.json``
     - JavaScript
     - https://bower.io
     - Bower package
   * - ``buck``
     - ``buck_file``
     - ``*/BUCK``
     - None
     - https://buck.build/
     - Buck file
   * - ``buck``
     - ``buck_metadata``
     - ``*/METADATA.bzl``
     - None
     - https://buck.build/
     - Buck metadata file
   * - ``cab``
     - ``microsoft_cabinet``
     - ``*.cab``
     - C
     - https://docs.microsoft.com/en-us/windows/win32/msi/cabinet-files
     - Microsoft cabinet archive
   * - ``cargo``
     - ``cargo_lock``
     - ``*/Cargo.lock``
       ``*/cargo.lock``
     - Rust
     - https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html
     - Rust Cargo.lock dependencies lockfile
   * - ``cargo``
     - ``cargo_toml``
     - ``*/Cargo.toml``
       ``*/cargo.toml``
     - Rust
     - https://doc.rust-lang.org/cargo/reference/manifest.html
     - Rust Cargo.toml package manifest
   * - ``chef``
     - ``chef_cookbook_metadata_json``
     - ``*/metadata.json``
     - Ruby
     - https://docs.chef.io/config_rb_metadata/
     - Chef cookbook metadata.json
   * - ``chef``
     - ``chef_cookbook_metadata_rb``
     - ``*/metadata.rb``
     - Ruby
     - https://docs.chef.io/config_rb_metadata/
     - Chef cookbook metadata.rb
   * - ``chrome``
     - ``chrome_crx``
     - ``*.crx``
     - JavaScript
     - https://chrome.google.com/extensions
     - Chrome extension
   * - ``cocoapods``
     - ``cocoapods_podfile``
     - ``*Podfile``
     - Objective-C
     - https://guides.cocoapods.org/using/the-podfile.html
     - Cocoapods Podfile
   * - ``cocoapods``
     - ``cocoapods_podfile_lock``
     - ``*Podfile.lock``
     - Objective-C
     - https://guides.cocoapods.org/using/the-podfile.html
     - Cocoapods Podfile.lock
   * - ``cocoapods``
     - ``cocoapods_podspec``
     - ``*.podspec``
     - Objective-C
     - https://guides.cocoapods.org/syntax/podspec.html
     - Cocoapods .podspec
   * - ``cocoapods``
     - ``cocoapods_podspec_json``
     - ``*.podspec.json``
     - Objective-C
     - https://guides.cocoapods.org/syntax/podspec.html
     - Cocoapods .podspec.json
   * - ``composer``
     - ``php_composer_json``
     - ``*composer.json``
     - PHP
     - https://getcomposer.org/doc/04-schema.md
     - PHP composer manifest
   * - ``composer``
     - ``php_composer_lock``
     - ``*composer.lock``
     - PHP
     - https://getcomposer.org/doc/01-basic-usage.md#commit-your-composer-lock-file-to-version-control
     - PHP composer lockfile
   * - ``conda``
     - ``conda_meta_yaml``
     - ``*/meta.yaml``
     - None
     - https://docs.conda.io/
     - Conda meta.yml manifest
   * - ``cpan``
     - ``cpan_dist_ini``
     - ``*/dist.ini``
     - Perl
     - https://metacpan.org/pod/Dist::Zilla::Tutorial
     - CPAN Perl dist.ini
   * - ``cpan``
     - ``cpan_makefile``
     - ``*/Makefile.PL``
     - Perl
     - https://www.perlmonks.org/?node_id=128077
     - CPAN Perl Makefile.PL
   * - ``cpan``
     - ``cpan_manifest``
     - ``*/MANIFEST``
     - Perl
     - https://metacpan.org/pod/Module::Manifest
     - CPAN Perl module MANIFEST
   * - ``cpan``
     - ``cpan_meta_json``
     - ``*/META.json``
     - Perl
     - https://metacpan.org/pod/Parse::CPAN::Meta
     - CPAN Perl META.json
   * - ``cpan``
     - ``cpan_meta_yml``
     - ``*/META.yml``
     - Perl
     - https://metacpan.org/pod/CPAN::Meta::YAML
     - CPAN Perl META.yml
   * - ``cran``
     - ``cran_description``
     - ``*/DESCRIPTION``
     - R
     - https://r-pkgs.org/description.html
     - CRAN package DESCRIPTION
   * - ``deb``
     - ``debian_control_extracted_deb``
     - ``*/control.tar.gz-extract/control``
     - None
     - https://www.debian.org/doc/debian-policy/ch-controlfields.html
     - Debian control file - extracted layout
   * - ``deb``
     - ``debian_control_in_source``
     - ``*/debian/control``
     - None
     - https://www.debian.org/doc/debian-policy/ch-controlfields.html
     - Debian control file - source layout
   * - ``deb``
     - ``debian_copyright_in_package``
     - ``*usr/share/doc/*/copyright``
     - None
     - https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
     - Debian machine readable file in source
   * - ``deb``
     - ``debian_copyright_in_source``
     - ``*/debian/copyright``
     - None
     - https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
     - Debian machine readable file in source
   * - ``deb``
     - ``debian_deb``
     - ``*.deb``
     - None
     - https://manpages.debian.org/unstable/dpkg-dev/deb.5.en.html
     - Debian binary package archive
   * - ``deb``
     - ``debian_distroless_installed_db``
     - ``*var/lib/dpkg/status.d/*``
     - None
     - https://www.debian.org/doc/debian-policy/ch-controlfields.html
     - Debian distroless installed database
   * - ``deb``
     - ``debian_installed_files_list``
     - ``*var/lib/dpkg/info/*.list``
     - None
     - None
     - Debian installed file paths list
   * - ``deb``
     - ``debian_installed_md5sums``
     - ``*var/lib/dpkg/info/*.md5sums``
     - None
     - https://www.debian.org/doc/manuals/debian-handbook/sect.package-meta-information.en.html#sect.configuration-scripts
     - Debian installed file MD5 and paths list
   * - ``deb``
     - ``debian_installed_status_db``
     - ``*var/lib/dpkg/status``
     - None
     - https://www.debian.org/doc/debian-policy/ch-controlfields.html
     - Debian installed packages database
   * - ``deb``
     - ``debian_md5sums_in_extracted_deb``
     - ``*/control.tar.gz-extract/md5sums``
       ``*/control.tar.xz-extract/md5sums``
     - None
     - https://www.debian.org/doc/manuals/debian-handbook/sect.package-meta-information.en.html#sect.configuration-scripts
     - Debian file MD5 and paths list in .deb archive
   * - ``deb``
     - ``debian_original_source_tarball``
     - ``*.orig.tar.xz``
       ``*.orig.tar.gz``
     - None
     - https://manpages.debian.org/unstable/dpkg-dev/deb.5.en.html
     - Debian package original source archive
   * - ``deb``
     - ``debian_source_control_dsc``
     - ``*.dsc``
     - None
     - https://wiki.debian.org/dsc
     - Debian source control file
   * - ``deb``
     - ``debian_source_metadata_tarball``
     - ``*.debian.tar.xz``
       ``*.debian.tar.gz``
     - None
     - https://manpages.debian.org/unstable/dpkg-dev/deb.5.en.html
     - Debian source package metadata archive
   * - ``dmg``
     - ``apple_dmg``
     - ``*.dmg``
       ``*.sparseimage``
     - None
     - None
     - None
   * - ``ear``
     - ``java_ear_application_xml``
     - ``*/META-INF/application.xml``
     - Java
     - https://en.wikipedia.org/wiki/EAR_(file_format)
     - Java EAR application.xml
   * - ``ear``
     - ``java_ear_archive``
     - ``*.ear``
     - Java
     - https://en.wikipedia.org/wiki/EAR_(file_format)
     - Java EAR Enterprise application archive
   * - ``freebsd``
     - ``freebsd_compact_manifest``
     - ``*/+COMPACT_MANIFEST``
     - None
     - https://www.freebsd.org/cgi/man.cgi?pkg-create(8)#MANIFEST_FILE_DETAILS
     - FreeBSD compact package manifest
   * - ``gem``
     - ``gem_archive``
     - ``*.gem``
     - Ruby
     - https://web.archive.org/web/20220326093616/https://piotrmurach.com/articles/looking-inside-a-ruby-gem/
     - RubyGems gem package archive
   * - ``gem``
     - ``gem_archive_extracted``
     - ``*/metadata.gz-extract``
     - Ruby
     - https://web.archive.org/web/20220326093616/https://piotrmurach.com/articles/looking-inside-a-ruby-gem/
     - RubyGems gem package extracted archive
   * - ``gem``
     - ``gem_gemspec_installed_specifications``
     - ``*/specifications/*.gemspec``
     - Ruby
     - https://guides.rubygems.org/specification-reference/
     - RubyGems gemspec manifest - installed vendor/bundle/specifications layout
   * - ``gem``
     - ``gemfile``
     - ``*/Gemfile``
       ``*/*.gemfile``
       ``*/Gemfile-*``
     - Ruby
     - https://bundler.io/man/gemfile.5.html
     - RubyGems Bundler Gemfile
   * - ``gem``
     - ``gemfile_extracted``
     - ``*/data.gz-extract/Gemfile``
     - Ruby
     - https://bundler.io/man/gemfile.5.html
     - RubyGems Bundler Gemfile - extracted layout
   * - ``gem``
     - ``gemfile_lock``
     - ``*/Gemfile.lock``
     - Ruby
     - https://bundler.io/man/gemfile.5.html
     - RubyGems Bundler Gemfile.lock
   * - ``gem``
     - ``gemfile_lock_extracted``
     - ``*/data.gz-extract/Gemfile.lock``
     - Ruby
     - https://bundler.io/man/gemfile.5.html
     - RubyGems Bundler Gemfile.lock - extracted layout
   * - ``gem``
     - ``gemspec``
     - ``*.gemspec``
     - Ruby
     - https://guides.rubygems.org/specification-reference/
     - RubyGems gemspec manifest
   * - ``gem``
     - ``gemspec_extracted``
     - ``*/data.gz-extract/*.gemspec``
     - Ruby
     - https://guides.rubygems.org/specification-reference/
     - RubyGems gemspec manifest - extracted data layout
   * - ``golang``
     - ``go_mod``
     - ``*/go.mod``
     - Go
     - https://go.dev/ref/mod
     - Go modules file
   * - ``golang``
     - ``go_sum``
     - ``*/go.sum``
     - Go
     - https://go.dev/ref/mod#go-sum-files
     - Go module cheksums file
   * - ``golang``
     - ``godeps``
     - ``*/Godeps.json``
     - Go
     - https://github.com/tools/godep
     - Go Godeps
   * - ``haxe``
     - ``haxelib_json``
     - ``*/haxelib.json``
     - Haxe
     - https://lib.haxe.org/documentation/creating-a-haxelib-package/
     - Haxe haxelib.json metadata file
   * - ``installshield``
     - ``installshield_installer``
     - ``*.exe``
     - None
     - https://www.revenera.com/install/products/installshield
     - InstallShield installer
   * - ``ios``
     - ``ios_ipa``
     - ``*.ipa``
     - Objective-C
     - https://en.wikipedia.org/wiki/.ipa
     - iOS package archive
   * - ``iso``
     - ``iso_disk_image``
     - ``*.iso``
       ``*.udf``
       ``*.img``
     - None
     - https://en.wikipedia.org/wiki/ISO_9660
     - ISO disk image
   * - ``ivy``
     - ``ant_ivy_xml``
     - ``*/ivy.xml``
     - Java
     - https://ant.apache.org/ivy/history/latest-milestone/ivyfile.html
     - Ant IVY dependency file
   * - ``jar``
     - ``java_jar_manifest``
     - ``*/META-INF/MANIFEST.MF``
     - Java
     - https://docs.oracle.com/javase/tutorial/deployment/jar/manifestindex.html
     - Java JAR MANIFEST.MF
   * - ``jboss-service``
     - ``jboss_sar``
     - ``*.sar``
     - Java
     - https://docs.jboss.org/jbossas/docs/Server_Configuration_Guide/4/html/ch02s01.html
     - JBOSS service archive
   * - ``jboss-service``
     - ``jboss_service_xml``
     - ``*/meta-inf/jboss-service.xml``
     - Java
     - https://docs.jboss.org/jbossas/docs/Server_Configuration_Guide/4/html/ch02s01.html
     - JBOSS service.xml
   * - ``linux-distro``
     - ``etc_os_release``
     - ``*etc/os-release``
       ``*usr/lib/os-release``
     - None
     - https://www.freedesktop.org/software/systemd/man/os-release.html
     - Linux OS release metadata file
   * - ``maven``
     - ``build_gradle``
     - ``*/build.gradle``
       ``*/build.gradle.kts``
     - None
     - None
     - Gradle build script
   * - ``maven``
     - ``maven_pom``
     - ``*.pom``
       ``*pom.xml``
     - Java
     - https://maven.apache.org/pom.html
     - Apache Maven pom
   * - ``maven``
     - ``maven_pom_properties``
     - ``*/pom.properties``
     - Java
     - https://maven.apache.org/pom.html
     - Apache Maven pom properties file
   * - ``meteor``
     - ``meteor_package``
     - ``*/package.js``
     - JavaScript
     - https://docs.meteor.com/api/packagejs.html
     - Meteor package.js
   * - ``mozilla``
     - ``mozilla_xpi``
     - ``*.xpi``
     - JavaScript
     - https://en.wikipedia.org/wiki/XPInstall
     - Mozilla XPI extension
   * - ``msi``
     - ``msi_installer``
     - ``*.msi``
     - None
     - https://docs.microsoft.com/en-us/windows/win32/msi/windows-installer-portal
     - Microsoft MSI installer
   * - ``npm``
     - ``npm_package_json``
     - ``*/package.json``
     - JavaScript
     - https://docs.npmjs.com/cli/v8/configuring-npm/package-json
     - npm package.json
   * - ``npm``
     - ``npm_package_lock_json``
     - ``*/package-lock.json``
       ``*/.package-lock.json``
     - JavaScript
     - https://docs.npmjs.com/cli/v8/configuring-npm/package-lock-json
     - npm package-lock.json lockfile
   * - ``npm``
     - ``npm_shrinkwrap_json``
     - ``*/npm-shrinkwrap.json``
     - JavaScript
     - https://docs.npmjs.com/cli/v8/configuring-npm/npm-shrinkwrap-json
     - npm shrinkwrap.json lockfile
   * - ``npm``
     - ``yarn_lock_v1``
     - ``*/yarn.lock``
     - JavaScript
     - https://classic.yarnpkg.com/lang/en/docs/yarn-lock/
     - yarn.lock lockfile v1 format
   * - ``npm``
     - ``yarn_lock_v2``
     - ``*/yarn.lock``
     - JavaScript
     - https://classic.yarnpkg.com/lang/en/docs/yarn-lock/
     - yarn.lock lockfile v2 format
   * - ``nsis``
     - ``nsis_installer``
     - ``*.exe``
     - None
     - https://nsis.sourceforge.io/Main_Page
     - NSIS installer
   * - ``nuget``
     - ``nuget_nupkg``
     - ``*.nupkg``
     - None
     - https://en.wikipedia.org/wiki/Open_Packaging_Conventions
     - NuGet nupkg package archive
   * - ``nuget``
     - ``nuget_nupsec``
     - ``*.nuspec``
     - None
     - https://docs.microsoft.com/en-us/nuget/reference/nuspec
     - NuGet nuspec package manifest
   * - ``opam``
     - ``opam_file``
     - ``*opam``
     - Ocaml
     - https://opam.ocaml.org/doc/Manual.html#Common-file-format
     - Ocaml Opam file
   * - ``pubspec``
     - ``pubspec_lock``
     - ``*pubspec.lock``
     - dart
     - https://web.archive.org/web/20220330081004/https://gpalma.pt/blog/what-is-the-pubspec-lock/
     - Dart pubspec lockfile
   * - ``pubspec``
     - ``pubspec_yaml``
     - ``*pubspec.yaml``
     - dart
     - https://dart.dev/tools/pub/pubspec
     - Dart pubspec manifest
   * - ``pypi``
     - ``conda_yaml``
     - ``*conda.yaml``
       ``*conda.yml``
     - Python
     - https://docs.conda.io/
     - Conda yaml manifest
   * - ``pypi``
     - ``pip_requirements``
     - ``*requirement*.txt``
       ``*requirement*.pip``
       ``*requirement*.in``
       ``*requires.txt``
       ``*requirements/*.txt``
       ``*requirements/*.pip``
       ``*requirements/*.in``
       ``*reqs.txt``
     - Python
     - https://pip.pypa.io/en/latest/reference/requirements-file-format/
     - pip requirements file
   * - ``pypi``
     - ``pipfile``
     - ``*Pipfile``
     - Python
     - https://github.com/pypa/pipfile
     - Pipfile
   * - ``pypi``
     - ``pipfile_lock``
     - ``*Pipfile.lock``
     - Python
     - https://github.com/pypa/pipfile
     - Pipfile.lock
   * - ``pypi``
     - ``pypi_editable_egg_pkginfo``
     - ``*.egg-info/PKG-INFO``
     - Python
     - https://peps.python.org/pep-0376/
     - PyPI editable local installation PKG-INFO
   * - ``pypi``
     - ``pypi_egg``
     - ``*.egg``
     - Python
     - https://web.archive.org/web/20210604075235/http://peak.telecommunity.com/DevCenter/PythonEggs
     - PyPI egg
   * - ``pypi``
     - ``pypi_egg_pkginfo``
     - ``*/EGG-INFO/PKG-INFO``
     - Python
     - https://peps.python.org/pep-0376/
     - PyPI extracted egg PKG-INFO
   * - ``pypi``
     - ``pypi_pyproject_toml``
     - ``*pyproject.toml``
     - Python
     - https://peps.python.org/pep-0621/
     - Python pyproject.toml
   * - ``pypi``
     - ``pypi_sdist_pkginfo``
     - ``*/PKG-INFO``
     - Python
     - https://peps.python.org/pep-0314/
     - PyPI extracted sdist PKG-INFO
   * - ``pypi``
     - ``pypi_setup_cfg``
     - ``*setup.cfg``
     - Python
     - https://peps.python.org/pep-0390/
     - Python setup.cfg
   * - ``pypi``
     - ``pypi_setup_py``
     - ``*setup.py``
     - Python
     - https://docs.python.org/3/distutils/setupscript.html
     - Python setup.py
   * - ``pypi``
     - ``pypi_wheel``
     - ``*.whl``
     - Python
     - https://peps.python.org/pep-0427/
     - PyPI wheel
   * - ``pypi``
     - ``pypi_wheel_metadata``
     - ``*.dist-info/METADATA``
     - Python
     - https://packaging.python.org/en/latest/specifications/core-metadata/
     - PyPI installed wheel METADATA
   * - ``readme``
     - ``readme``
     - ``*/README.android``
       ``*/README.chromium``
       ``*/README.facebook``
       ``*/README.google``
       ``*/README.thirdparty``
     - None
     - None
     - None
   * - ``rpm``
     - ``rpm_archive``
     - ``*.rpm``
       ``*.src.rpm``
       ``*.srpm``
       ``*.mvl``
       ``*.vip``
     - None
     - https://en.wikipedia.org/wiki/RPM_Package_Manager
     - RPM package archive
   * - ``rpm``
     - ``rpm_installed_database_bdb``
     - ``*var/lib/rpm/Packages``
     - None
     - https://man7.org/linux/man-pages/man8/rpmdb.8.html
     - RPM installed package BDB database
   * - ``rpm``
     - ``rpm_installed_database_ndb``
     - ``*usr/lib/sysimage/rpm/Packages.db``
     - None
     - https://fedoraproject.org/wiki/Changes/NewRpmDBFormat
     - RPM installed package NDB database
   * - ``rpm``
     - ``rpm_installed_database_sqlite``
     - ``*var/lib/rpm/rpmdb.sqlite``
     - None
     - https://fedoraproject.org/wiki/Changes/Sqlite_Rpmdb
     - RPM installed package SQLite database
   * - ``rpm``
     - ``rpm_spefile``
     - ``*.spec``
     - None
     - https://en.wikipedia.org/wiki/RPM_Package_Manager
     - RPM specfile
   * - ``shar``
     - ``shar_shell_archive``
     - ``*.shar``
     - None
     - https://en.wikipedia.org/wiki/Shar
     - shell archive
   * - ``squashfs``
     - ``squashfs_disk_image``
     - None
     - None
     - https://en.wikipedia.org/wiki/SquashFS
     - Squashfs disk image
   * - ``war``
     - ``java_war_archive``
     - ``*.war``
     - Java
     - https://en.wikipedia.org/wiki/WAR_(file_format)
     - Java Web Application Archive
   * - ``war``
     - ``java_war_web_xml``
     - ``*/WEB-INF/web.xml``
     - Java
     - https://en.wikipedia.org/wiki/WAR_(file_format)
     - Java WAR web/xml
   * - ``windows-program``
     - ``win_reg_installed_programs_docker_file_software``
     - ``*/Files/Windows/System32/config/SOFTWARE``
     - None
     - https://en.wikipedia.org/wiki/Windows_Registry
     - Windows Registry Installed Program - Docker SOFTWARE
   * - ``windows-program``
     - ``win_reg_installed_programs_docker_software_delta``
     - ``*/Hives/Software_Delta``
     - None
     - https://en.wikipedia.org/wiki/Windows_Registry
     - Windows Registry Installed Program - Docker Software Delta
   * - ``windows-program``
     - ``win_reg_installed_programs_docker_utility_software``
     - ``*/UtilityVM/Files/Windows/System32/config/SOFTWARE``
     - None
     - https://en.wikipedia.org/wiki/Windows_Registry
     - Windows Registry Installed Program - Docker UtilityVM SOFTWARE
   * - ``windows-update``
     - ``microsoft_update_manifest_mum``
     - ``*.mum``
     - None
     - None
     - Microsoft Update Manifest .mum file
   * - ``winexe``
     - ``windows_executable``
     - ``*.exe``
       ``*.dll``
       ``*.mui``
       ``*.mun``
       ``*.com``
       ``*.winmd``
       ``*.sys``
       ``*.tlb``
       ``*.exe_*``
       ``*.dll_*``
       ``*.mui_*``
       ``*.mun_*``
       ``*.com_*``
       ``*.winmd_*``
       ``*.sys_*``
       ``*.tlb_*``
       ``*.ocx``
     - None
     - https://en.wikipedia.org/wiki/Portable_Executable
     - Windows Portable Executable metadata
