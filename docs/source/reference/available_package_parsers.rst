

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

   * - Description
     - Path Patterns
     - Package type
     - Datasource ID
     - Primary Language
     - Documentation URL
   * - AboutCode ABOUT file
     - ``*.ABOUT``
     - ``about``
     - ``about_file``
     - None
     - https://aboutcode-toolkit.readthedocs.io/en/latest/specification.html
   * - Alpine Linux .apk package archive
     - ``*.apk``
     - ``alpine``
     - ``alpine_apk_archive``
     - None
     - https://wiki.alpinelinux.org/wiki/Alpine_package_format
   * - Alpine Linux APKBUILD package script
     - ``*APKBUILD``
     - ``alpine``
     - ``alpine_apkbuild``
     - None
     - https://wiki.alpinelinux.org/wiki/APKBUILD_Reference
   * - Alpine Linux installed package database
     - ``*lib/apk/db/installed``
     - ``alpine``
     - ``alpine_installed_db``
     - None
     - None
   * - Android application package
     - ``*.apk``
     - ``android``
     - ``android_apk``
     - Java
     - https://en.wikipedia.org/wiki/Apk_(file_format)
   * - Android library archive
     - ``*.aar``
     - ``android_lib``
     - ``android_aar_library``
     - Java
     - https://developer.android.com/studio/projects/android-library
   * - Autotools configure script
     - ``*/configure``
       ``*/configure.ac``
     - ``autotools``
     - ``autotools_configure``
     - None
     - https://www.gnu.org/software/automake/
   * - Apache Axis2 module archive
     - ``*.mar``
     - ``axis2``
     - ``axis2_mar``
     - Java
     - https://axis.apache.org/axis2/java/core/docs/modules.html
   * - Apache Axis2 module.xml
     - ``*/meta-inf/module.xml``
     - ``axis2``
     - ``axis2_module_xml``
     - Java
     - https://axis.apache.org/axis2/java/core/docs/modules.html
   * - Bazel BUILD
     - ``*/BUILD``
     - ``bazel``
     - ``bazel_build``
     - None
     - https://bazel.build/
   * - Bower package
     - ``*/bower.json``
       ``*/.bower.json``
     - ``bower``
     - ``bower_json``
     - JavaScript
     - https://bower.io
   * - Buck file
     - ``*/BUCK``
     - ``buck``
     - ``buck_file``
     - None
     - https://buck.build/
   * - Buck metadata file
     - ``*/METADATA.bzl``
     - ``buck``
     - ``buck_metadata``
     - None
     - https://buck.build/
   * - Microsoft cabinet archive
     - ``*.cab``
     - ``cab``
     - ``microsoft_cabinet``
     - C
     - https://docs.microsoft.com/en-us/windows/win32/msi/cabinet-files
   * - Rust Cargo.lock dependencies lockfile
     - ``*/Cargo.lock``
       ``*/cargo.lock``
     - ``cargo``
     - ``cargo_lock``
     - Rust
     - https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html
   * - Rust Cargo.toml package manifest
     - ``*/Cargo.toml``
       ``*/cargo.toml``
     - ``cargo``
     - ``cargo_toml``
     - Rust
     - https://doc.rust-lang.org/cargo/reference/manifest.html
   * - Chef cookbook metadata.json
     - ``*/metadata.json``
     - ``chef``
     - ``chef_cookbook_metadata_json``
     - Ruby
     - https://docs.chef.io/config_rb_metadata/
   * - Chef cookbook metadata.rb
     - ``*/metadata.rb``
     - ``chef``
     - ``chef_cookbook_metadata_rb``
     - Ruby
     - https://docs.chef.io/config_rb_metadata/
   * - Chrome extension
     - ``*.crx``
     - ``chrome``
     - ``chrome_crx``
     - JavaScript
     - https://chrome.google.com/extensions
   * - Cocoapods Podfile
     - ``*Podfile``
     - ``cocoapods``
     - ``cocoapods_podfile``
     - Objective-C
     - https://guides.cocoapods.org/using/the-podfile.html
   * - Cocoapods Podfile.lock
     - ``*Podfile.lock``
     - ``cocoapods``
     - ``cocoapods_podfile_lock``
     - Objective-C
     - https://guides.cocoapods.org/using/the-podfile.html
   * - Cocoapods .podspec
     - ``*.podspec``
     - ``cocoapods``
     - ``cocoapods_podspec``
     - Objective-C
     - https://guides.cocoapods.org/syntax/podspec.html
   * - Cocoapods .podspec.json
     - ``*.podspec.json``
     - ``cocoapods``
     - ``cocoapods_podspec_json``
     - Objective-C
     - https://guides.cocoapods.org/syntax/podspec.html
   * - PHP composer manifest
     - ``*composer.json``
     - ``composer``
     - ``php_composer_json``
     - PHP
     - https://getcomposer.org/doc/04-schema.md
   * - PHP composer lockfile
     - ``*composer.lock``
     - ``composer``
     - ``php_composer_lock``
     - PHP
     - https://getcomposer.org/doc/01-basic-usage.md#commit-your-composer-lock-file-to-version-control
   * - Conda meta.yml manifest
     - ``*/meta.yaml``
     - ``conda``
     - ``conda_meta_yaml``
     - None
     - https://docs.conda.io/
   * - CPAN Perl dist.ini
     - ``*/dist.ini``
     - ``cpan``
     - ``cpan_dist_ini``
     - Perl
     - https://metacpan.org/pod/Dist::Zilla::Tutorial
   * - CPAN Perl Makefile.PL
     - ``*/Makefile.PL``
     - ``cpan``
     - ``cpan_makefile``
     - Perl
     - https://www.perlmonks.org/?node_id=128077
   * - CPAN Perl module MANIFEST
     - ``*/MANIFEST``
     - ``cpan``
     - ``cpan_manifest``
     - Perl
     - https://metacpan.org/pod/Module::Manifest
   * - CPAN Perl META.json
     - ``*/META.json``
     - ``cpan``
     - ``cpan_meta_json``
     - Perl
     - https://metacpan.org/pod/Parse::CPAN::Meta
   * - CPAN Perl META.yml
     - ``*/META.yml``
     - ``cpan``
     - ``cpan_meta_yml``
     - Perl
     - https://metacpan.org/pod/CPAN::Meta::YAML
   * - CRAN package DESCRIPTION
     - ``*/DESCRIPTION``
     - ``cran``
     - ``cran_description``
     - R
     - https://r-pkgs.org/description.html
   * - Debian control file - extracted layout
     - ``*/control.tar.gz-extract/control``
     - ``deb``
     - ``debian_control_extracted_deb``
     - None
     - https://www.debian.org/doc/debian-policy/ch-controlfields.html
   * - Debian control file - source layout
     - ``*/debian/control``
     - ``deb``
     - ``debian_control_in_source``
     - None
     - https://www.debian.org/doc/debian-policy/ch-controlfields.html
   * - Debian machine readable file in source
     - ``*usr/share/doc/*/copyright``
     - ``deb``
     - ``debian_copyright_in_package``
     - None
     - https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
   * - Debian machine readable file in source
     - ``*/debian/copyright``
     - ``deb``
     - ``debian_copyright_in_source``
     - None
     - https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
   * - Debian binary package archive
     - ``*.deb``
     - ``deb``
     - ``debian_deb``
     - None
     - https://manpages.debian.org/unstable/dpkg-dev/deb.5.en.html
   * - Debian distroless installed database
     - ``*var/lib/dpkg/status.d/*``
     - ``deb``
     - ``debian_distroless_installed_db``
     - None
     - https://www.debian.org/doc/debian-policy/ch-controlfields.html
   * - Debian installed file paths list
     - ``*var/lib/dpkg/info/*.list``
     - ``deb``
     - ``debian_installed_files_list``
     - None
     - None
   * - Debian installed file MD5 and paths list
     - ``*var/lib/dpkg/info/*.md5sums``
     - ``deb``
     - ``debian_installed_md5sums``
     - None
     - https://www.debian.org/doc/manuals/debian-handbook/sect.package-meta-information.en.html#sect.configuration-scripts
   * - Debian installed packages database
     - ``*var/lib/dpkg/status``
     - ``deb``
     - ``debian_installed_status_db``
     - None
     - https://www.debian.org/doc/debian-policy/ch-controlfields.html
   * - Debian file MD5 and paths list in .deb archive
     - ``*/control.tar.gz-extract/md5sums``
       ``*/control.tar.xz-extract/md5sums``
     - ``deb``
     - ``debian_md5sums_in_extracted_deb``
     - None
     - https://www.debian.org/doc/manuals/debian-handbook/sect.package-meta-information.en.html#sect.configuration-scripts
   * - Debian package original source archive
     - ``*.orig.tar.xz``
       ``*.orig.tar.gz``
     - ``deb``
     - ``debian_original_source_tarball``
     - None
     - https://manpages.debian.org/unstable/dpkg-dev/deb.5.en.html
   * - Debian source control file
     - ``*.dsc``
     - ``deb``
     - ``debian_source_control_dsc``
     - None
     - https://wiki.debian.org/dsc
   * - Debian source package metadata archive
     - ``*.debian.tar.xz``
       ``*.debian.tar.gz``
     - ``deb``
     - ``debian_source_metadata_tarball``
     - None
     - https://manpages.debian.org/unstable/dpkg-dev/deb.5.en.html
   * - macOS disk image file
     - ``*.dmg``
       ``*.sparseimage``
     - ``dmg``
     - ``apple_dmg``
     - None
     - https://en.wikipedia.org/wiki/Apple_Disk_Image
   * - Java EAR application.xml
     - ``*/META-INF/application.xml``
     - ``ear``
     - ``java_ear_application_xml``
     - Java
     - https://en.wikipedia.org/wiki/EAR_(file_format)
   * - Java EAR Enterprise application archive
     - ``*.ear``
     - ``ear``
     - ``java_ear_archive``
     - Java
     - https://en.wikipedia.org/wiki/EAR_(file_format)
   * - FreeBSD compact package manifest
     - ``*/+COMPACT_MANIFEST``
     - ``freebsd``
     - ``freebsd_compact_manifest``
     - None
     - https://www.freebsd.org/cgi/man.cgi?pkg-create(8)#MANIFEST_FILE_DETAILS
   * - RubyGems gem package archive
     - ``*.gem``
     - ``gem``
     - ``gem_archive``
     - Ruby
     - https://web.archive.org/web/20220326093616/https://piotrmurach.com/articles/looking-inside-a-ruby-gem/
   * - RubyGems gem package extracted archive
     - ``*/metadata.gz-extract``
     - ``gem``
     - ``gem_archive_extracted``
     - Ruby
     - https://web.archive.org/web/20220326093616/https://piotrmurach.com/articles/looking-inside-a-ruby-gem/
   * - RubyGems gemspec manifest - installed vendor/bundle/specifications layout
     - ``*/specifications/*.gemspec``
     - ``gem``
     - ``gem_gemspec_installed_specifications``
     - Ruby
     - https://guides.rubygems.org/specification-reference/
   * - RubyGems Bundler Gemfile
     - ``*/Gemfile``
       ``*/*.gemfile``
       ``*/Gemfile-*``
     - ``gem``
     - ``gemfile``
     - Ruby
     - https://bundler.io/man/gemfile.5.html
   * - RubyGems Bundler Gemfile - extracted layout
     - ``*/data.gz-extract/Gemfile``
     - ``gem``
     - ``gemfile_extracted``
     - Ruby
     - https://bundler.io/man/gemfile.5.html
   * - RubyGems Bundler Gemfile.lock
     - ``*/Gemfile.lock``
     - ``gem``
     - ``gemfile_lock``
     - Ruby
     - https://bundler.io/man/gemfile.5.html
   * - RubyGems Bundler Gemfile.lock - extracted layout
     - ``*/data.gz-extract/Gemfile.lock``
     - ``gem``
     - ``gemfile_lock_extracted``
     - Ruby
     - https://bundler.io/man/gemfile.5.html
   * - RubyGems gemspec manifest
     - ``*.gemspec``
     - ``gem``
     - ``gemspec``
     - Ruby
     - https://guides.rubygems.org/specification-reference/
   * - RubyGems gemspec manifest - extracted data layout
     - ``*/data.gz-extract/*.gemspec``
     - ``gem``
     - ``gemspec_extracted``
     - Ruby
     - https://guides.rubygems.org/specification-reference/
   * - Go modules file
     - ``*/go.mod``
     - ``golang``
     - ``go_mod``
     - Go
     - https://go.dev/ref/mod
   * - Go module cheksums file
     - ``*/go.sum``
     - ``golang``
     - ``go_sum``
     - Go
     - https://go.dev/ref/mod#go-sum-files
   * - Go Godeps
     - ``*/Godeps.json``
     - ``golang``
     - ``godeps``
     - Go
     - https://github.com/tools/godep
   * - Haxe haxelib.json metadata file
     - ``*/haxelib.json``
     - ``haxe``
     - ``haxelib_json``
     - Haxe
     - https://lib.haxe.org/documentation/creating-a-haxelib-package/
   * - InstallShield installer
     - ``*.exe``
     - ``installshield``
     - ``installshield_installer``
     - None
     - https://www.revenera.com/install/products/installshield
   * - iOS package archive
     - ``*.ipa``
     - ``ios``
     - ``ios_ipa``
     - Objective-C
     - https://en.wikipedia.org/wiki/.ipa
   * - ISO disk image
     - ``*.iso``
       ``*.udf``
       ``*.img``
     - ``iso``
     - ``iso_disk_image``
     - None
     - https://en.wikipedia.org/wiki/ISO_9660
   * - Ant IVY dependency file
     - ``*/ivy.xml``
     - ``ivy``
     - ``ant_ivy_xml``
     - Java
     - https://ant.apache.org/ivy/history/latest-milestone/ivyfile.html
   * - JAR Java Archive
     - ``*.jar``
     - ``jar``
     - ``java_jar``
     - None
     - https://en.wikipedia.org/wiki/JAR_(file_format)
   * - Java JAR MANIFEST.MF
     - ``*/META-INF/MANIFEST.MF``
     - ``jar``
     - ``java_jar_manifest``
     - Java
     - https://docs.oracle.com/javase/tutorial/deployment/jar/manifestindex.html
   * - JBOSS service archive
     - ``*.sar``
     - ``jboss-service``
     - ``jboss_sar``
     - Java
     - https://docs.jboss.org/jbossas/docs/Server_Configuration_Guide/4/html/ch02s01.html
   * - JBOSS service.xml
     - ``*/meta-inf/jboss-service.xml``
     - ``jboss-service``
     - ``jboss_service_xml``
     - Java
     - https://docs.jboss.org/jbossas/docs/Server_Configuration_Guide/4/html/ch02s01.html
   * - Linux OS release metadata file
     - ``*etc/os-release``
       ``*usr/lib/os-release``
     - ``linux-distro``
     - ``etc_os_release``
     - None
     - https://www.freedesktop.org/software/systemd/man/os-release.html
   * - Gradle build script
     - ``*/build.gradle``
       ``*/build.gradle.kts``
     - ``maven``
     - ``build_gradle``
     - None
     - None
   * - Apache Maven pom
     - ``*.pom``
       ``*pom.xml``
     - ``maven``
     - ``maven_pom``
     - Java
     - https://maven.apache.org/pom.html
   * - Apache Maven pom properties file
     - ``*/pom.properties``
     - ``maven``
     - ``maven_pom_properties``
     - Java
     - https://maven.apache.org/pom.html
   * - Meteor package.js
     - ``*/package.js``
     - ``meteor``
     - ``meteor_package``
     - JavaScript
     - https://docs.meteor.com/api/packagejs.html
   * - Mozilla XPI extension
     - ``*.xpi``
     - ``mozilla``
     - ``mozilla_xpi``
     - JavaScript
     - https://en.wikipedia.org/wiki/XPInstall
   * - Microsoft MSI installer
     - ``*.msi``
     - ``msi``
     - ``msi_installer``
     - None
     - https://docs.microsoft.com/en-us/windows/win32/msi/windows-installer-portal
   * - npm package.json
     - ``*/package.json``
     - ``npm``
     - ``npm_package_json``
     - JavaScript
     - https://docs.npmjs.com/cli/v8/configuring-npm/package-json
   * - npm package-lock.json lockfile
     - ``*/package-lock.json``
       ``*/.package-lock.json``
     - ``npm``
     - ``npm_package_lock_json``
     - JavaScript
     - https://docs.npmjs.com/cli/v8/configuring-npm/package-lock-json
   * - npm shrinkwrap.json lockfile
     - ``*/npm-shrinkwrap.json``
     - ``npm``
     - ``npm_shrinkwrap_json``
     - JavaScript
     - https://docs.npmjs.com/cli/v8/configuring-npm/npm-shrinkwrap-json
   * - yarn.lock lockfile v1 format
     - ``*/yarn.lock``
     - ``npm``
     - ``yarn_lock_v1``
     - JavaScript
     - https://classic.yarnpkg.com/lang/en/docs/yarn-lock/
   * - yarn.lock lockfile v2 format
     - ``*/yarn.lock``
     - ``npm``
     - ``yarn_lock_v2``
     - JavaScript
     - https://classic.yarnpkg.com/lang/en/docs/yarn-lock/
   * - NSIS installer
     - ``*.exe``
     - ``nsis``
     - ``nsis_installer``
     - None
     - https://nsis.sourceforge.io/Main_Page
   * - NuGet nupkg package archive
     - ``*.nupkg``
     - ``nuget``
     - ``nuget_nupkg``
     - None
     - https://en.wikipedia.org/wiki/Open_Packaging_Conventions
   * - NuGet nuspec package manifest
     - ``*.nuspec``
     - ``nuget``
     - ``nuget_nupsec``
     - None
     - https://docs.microsoft.com/en-us/nuget/reference/nuspec
   * - Ocaml Opam file
     - ``*opam``
     - ``opam``
     - ``opam_file``
     - Ocaml
     - https://opam.ocaml.org/doc/Manual.html#Common-file-format
   * - Java OSGi MANIFEST.MF
     - None
     - ``osgi``
     - ``java_osgi_manifest``
     - Java
     - https://docs.oracle.com/javase/tutorial/deployment/jar/manifestindex.html
   * - Dart pubspec lockfile
     - ``*pubspec.lock``
     - ``pubspec``
     - ``pubspec_lock``
     - dart
     - https://web.archive.org/web/20220330081004/https://gpalma.pt/blog/what-is-the-pubspec-lock/
   * - Dart pubspec manifest
     - ``*pubspec.yaml``
     - ``pubspec``
     - ``pubspec_yaml``
     - dart
     - https://dart.dev/tools/pub/pubspec
   * - Conda yaml manifest
     - ``*conda.yaml``
       ``*conda.yml``
     - ``pypi``
     - ``conda_yaml``
     - Python
     - https://docs.conda.io/
   * - pip requirements file
     - ``*requirement*.txt``
       ``*requirement*.pip``
       ``*requirement*.in``
       ``*requires.txt``
       ``*requirements/*.txt``
       ``*requirements/*.pip``
       ``*requirements/*.in``
       ``*reqs.txt``
     - ``pypi``
     - ``pip_requirements``
     - Python
     - https://pip.pypa.io/en/latest/reference/requirements-file-format/
   * - Pipfile
     - ``*Pipfile``
     - ``pypi``
     - ``pipfile``
     - Python
     - https://github.com/pypa/pipfile
   * - Pipfile.lock
     - ``*Pipfile.lock``
     - ``pypi``
     - ``pipfile_lock``
     - Python
     - https://github.com/pypa/pipfile
   * - PyPI editable local installation PKG-INFO
     - ``*.egg-info/PKG-INFO``
     - ``pypi``
     - ``pypi_editable_egg_pkginfo``
     - Python
     - https://peps.python.org/pep-0376/
   * - PyPI egg
     - ``*.egg``
     - ``pypi``
     - ``pypi_egg``
     - Python
     - https://web.archive.org/web/20210604075235/http://peak.telecommunity.com/DevCenter/PythonEggs
   * - PyPI extracted egg PKG-INFO
     - ``*/EGG-INFO/PKG-INFO``
     - ``pypi``
     - ``pypi_egg_pkginfo``
     - Python
     - https://peps.python.org/pep-0376/
   * - Python pyproject.toml
     - ``*pyproject.toml``
     - ``pypi``
     - ``pypi_pyproject_toml``
     - Python
     - https://peps.python.org/pep-0621/
   * - PyPI extracted sdist PKG-INFO
     - ``*/PKG-INFO``
     - ``pypi``
     - ``pypi_sdist_pkginfo``
     - Python
     - https://peps.python.org/pep-0314/
   * - Python setup.cfg
     - ``*setup.cfg``
     - ``pypi``
     - ``pypi_setup_cfg``
     - Python
     - https://peps.python.org/pep-0390/
   * - Python setup.py
     - ``*setup.py``
     - ``pypi``
     - ``pypi_setup_py``
     - Python
     - https://docs.python.org/3/distutils/setupscript.html
   * - PyPI wheel
     - ``*.whl``
     - ``pypi``
     - ``pypi_wheel``
     - Python
     - https://peps.python.org/pep-0427/
   * - PyPI installed wheel METADATA
     - ``*.dist-info/METADATA``
     - ``pypi``
     - ``pypi_wheel_metadata``
     - Python
     - https://packaging.python.org/en/latest/specifications/core-metadata/
   * - None
     - ``*/README.android``
       ``*/README.chromium``
       ``*/README.facebook``
       ``*/README.google``
       ``*/README.thirdparty``
     - ``readme``
     - ``readme``
     - None
     - None
   * - RPM package archive
     - ``*.rpm``
       ``*.src.rpm``
       ``*.srpm``
       ``*.mvl``
       ``*.vip``
     - ``rpm``
     - ``rpm_archive``
     - None
     - https://en.wikipedia.org/wiki/RPM_Package_Manager
   * - RPM installed package BDB database
     - ``*var/lib/rpm/Packages``
     - ``rpm``
     - ``rpm_installed_database_bdb``
     - None
     - https://man7.org/linux/man-pages/man8/rpmdb.8.html
   * - RPM installed package NDB database
     - ``*usr/lib/sysimage/rpm/Packages.db``
     - ``rpm``
     - ``rpm_installed_database_ndb``
     - None
     - https://fedoraproject.org/wiki/Changes/NewRpmDBFormat
   * - RPM installed package SQLite database
     - ``*var/lib/rpm/rpmdb.sqlite``
     - ``rpm``
     - ``rpm_installed_database_sqlite``
     - None
     - https://fedoraproject.org/wiki/Changes/Sqlite_Rpmdb
   * - RPM specfile
     - ``*.spec``
     - ``rpm``
     - ``rpm_spefile``
     - None
     - https://en.wikipedia.org/wiki/RPM_Package_Manager
   * - shell archive
     - ``*.shar``
     - ``shar``
     - ``shar_shell_archive``
     - None
     - https://en.wikipedia.org/wiki/Shar
   * - Squashfs disk image
     - None
     - ``squashfs``
     - ``squashfs_disk_image``
     - None
     - https://en.wikipedia.org/wiki/SquashFS
   * - Java Web Application Archive
     - ``*.war``
     - ``war``
     - ``java_war_archive``
     - Java
     - https://en.wikipedia.org/wiki/WAR_(file_format)
   * - Java WAR web/xml
     - ``*/WEB-INF/web.xml``
     - ``war``
     - ``java_war_web_xml``
     - Java
     - https://en.wikipedia.org/wiki/WAR_(file_format)
   * - Windows Registry Installed Program - Docker SOFTWARE
     - ``*/Files/Windows/System32/config/SOFTWARE``
     - ``windows-program``
     - ``win_reg_installed_programs_docker_file_software``
     - None
     - https://en.wikipedia.org/wiki/Windows_Registry
   * - Windows Registry Installed Program - Docker Software Delta
     - ``*/Hives/Software_Delta``
     - ``windows-program``
     - ``win_reg_installed_programs_docker_software_delta``
     - None
     - https://en.wikipedia.org/wiki/Windows_Registry
   * - Windows Registry Installed Program - Docker UtilityVM SOFTWARE
     - ``*/UtilityVM/Files/Windows/System32/config/SOFTWARE``
     - ``windows-program``
     - ``win_reg_installed_programs_docker_utility_software``
     - None
     - https://en.wikipedia.org/wiki/Windows_Registry
   * - Microsoft Update Manifest .mum file
     - ``*.mum``
     - ``windows-update``
     - ``microsoft_update_manifest_mum``
     - None
     - None
   * - Windows Portable Executable metadata
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
     - ``winexe``
     - ``windows_executable``
     - None
     - https://en.wikipedia.org/wiki/Portable_Executable
