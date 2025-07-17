

.. _supported_packages:

Supported package manifests and package datafiles
-------------------------------------------------

ScanCode supports a wide variety of package manifests, lockfiles
and other package datafiles containing package and dependency
information.

This documentation page is generated automatically from available package
parsers in scancode-toolkit during documentation builds.


.. list-table:: Supported Package Parsers
   :widths: 10 10 20 10 10 10 2
   :header-rows: 1

   * - Description
     - Path Patterns
     - Package type
     - Supported OS for detection
     - Datasource ID
     - Primary Language
     - Documentation URL
   * - AboutCode ABOUT file
     - ``*.ABOUT``
     - ``about``
     - ``linux``, ``win``, ``mac``
     - ``about_file``
     - None
     - https://aboutcode-toolkit.readthedocs.io/en/latest/specification.html
   * - Alpine Linux .apk package archive
     - ``*.apk``
     - ``alpine``
     - ``linux``, ``win``, ``mac``
     - ``alpine_apk_archive``
     - None
     - https://wiki.alpinelinux.org/wiki/Alpine_package_format
   * - Alpine Linux APKBUILD package script
     - ``*APKBUILD``
     - ``alpine``
     - ``linux``, ``win``, ``mac``
     - ``alpine_apkbuild``
     - None
     - https://wiki.alpinelinux.org/wiki/APKBUILD_Reference
   * - Alpine Linux installed package database
     - ``*lib/apk/db/installed``
     - ``alpine``
     - ``linux``, ``win``, ``mac``
     - ``alpine_installed_db``
     - None
     - None
   * - Android application package
     - ``*.apk``
     - ``android``
     - ``linux``, ``win``, ``mac``
     - ``android_apk``
     - Java
     - https://en.wikipedia.org/wiki/Apk_(file_format)
   * - Android library archive
     - ``*.aar``
     - ``android_lib``
     - ``linux``, ``win``, ``mac``
     - ``android_aar_library``
     - Java
     - https://developer.android.com/studio/projects/android-library
   * - Autotools configure script
     - ``*/configure``
       ``*/configure.ac``
     - ``autotools``
     - ``linux``, ``win``, ``mac``
     - ``autotools_configure``
     - None
     - https://www.gnu.org/software/automake/
   * - Apache Axis2 module archive
     - ``*.mar``
     - ``axis2``
     - ``linux``, ``win``, ``mac``
     - ``axis2_mar``
     - Java
     - https://axis.apache.org/axis2/java/core/docs/modules.html
   * - Apache Axis2 module.xml
     - ``*/meta-inf/module.xml``
     - ``axis2``
     - ``linux``, ``win``, ``mac``
     - ``axis2_module_xml``
     - Java
     - https://axis.apache.org/axis2/java/core/docs/modules.html
   * - Bazel BUILD
     - ``*/BUILD``
     - ``bazel``
     - ``linux``, ``win``, ``mac``
     - ``bazel_build``
     - None
     - https://bazel.build/
   * - Bower package
     - ``*/bower.json``
       ``*/.bower.json``
     - ``bower``
     - ``linux``, ``win``, ``mac``
     - ``bower_json``
     - JavaScript
     - https://bower.io
   * - Buck file
     - ``*/BUCK``
     - ``buck``
     - ``linux``, ``win``, ``mac``
     - ``buck_file``
     - None
     - https://buck.build/
   * - Buck metadata file
     - ``*/METADATA.bzl``
     - ``buck``
     - ``linux``, ``win``, ``mac``
     - ``buck_metadata``
     - None
     - https://buck.build/
   * - Microsoft cabinet archive
     - ``*.cab``
     - ``cab``
     - ``linux``, ``win``, ``mac``
     - ``microsoft_cabinet``
     - C
     - https://docs.microsoft.com/en-us/windows/win32/msi/cabinet-files
   * - Rust Cargo.lock dependencies lockfile
     - ``*/Cargo.lock``
       ``*/cargo.lock``
     - ``cargo``
     - ``linux``, ``win``, ``mac``
     - ``cargo_lock``
     - Rust
     - https://doc.rust-lang.org/cargo/guide/cargo-toml-vs-cargo-lock.html
   * - Rust Cargo.toml package manifest
     - ``*/Cargo.toml``
       ``*/cargo.toml``
     - ``cargo``
     - ``linux``, ``win``, ``mac``
     - ``cargo_toml``
     - Rust
     - https://doc.rust-lang.org/cargo/reference/manifest.html
   * - Rust binary
     - None
     - ``cargo``
     - ``linux``, ``win``, ``mac``
     - ``rust_binary``
     - Rust
     - https://github.com/rust-secure-code/cargo-auditable/blob/master/PARSING.md
   * - Chef cookbook metadata.json
     - ``*/metadata.json``
     - ``chef``
     - ``linux``, ``win``, ``mac``
     - ``chef_cookbook_metadata_json``
     - Ruby
     - https://docs.chef.io/config_rb_metadata/
   * - Chef cookbook metadata.rb
     - ``*/metadata.rb``
     - ``chef``
     - ``linux``, ``win``, ``mac``
     - ``chef_cookbook_metadata_rb``
     - Ruby
     - https://docs.chef.io/config_rb_metadata/
   * - Chrome extension
     - ``*.crx``
     - ``chrome``
     - ``linux``, ``win``, ``mac``
     - ``chrome_crx``
     - JavaScript
     - https://chrome.google.com/extensions
   * - Cocoapods Podfile
     - ``*Podfile``
     - ``cocoapods``
     - ``linux``, ``win``, ``mac``
     - ``cocoapods_podfile``
     - Objective-C
     - https://guides.cocoapods.org/using/the-podfile.html
   * - Cocoapods Podfile.lock
     - ``*Podfile.lock``
     - ``cocoapods``
     - ``linux``, ``win``, ``mac``
     - ``cocoapods_podfile_lock``
     - Objective-C
     - https://guides.cocoapods.org/using/the-podfile.html
   * - Cocoapods .podspec
     - ``*.podspec``
     - ``cocoapods``
     - ``linux``, ``win``, ``mac``
     - ``cocoapods_podspec``
     - Objective-C
     - https://guides.cocoapods.org/syntax/podspec.html
   * - Cocoapods .podspec.json
     - ``*.podspec.json``
     - ``cocoapods``
     - ``linux``, ``win``, ``mac``
     - ``cocoapods_podspec_json``
     - Objective-C
     - https://guides.cocoapods.org/syntax/podspec.html
   * - PHP composer manifest
     - ``*composer.json``
     - ``composer``
     - ``linux``, ``win``, ``mac``
     - ``php_composer_json``
     - PHP
     - https://getcomposer.org/doc/04-schema.md
   * - PHP composer lockfile
     - ``*composer.lock``
     - ``composer``
     - ``linux``, ``win``, ``mac``
     - ``php_composer_lock``
     - PHP
     - https://getcomposer.org/doc/01-basic-usage.md#commit-your-composer-lock-file-to-version-control
   * - conan external source
     - ``*/conandata.yml``
     - ``conan``
     - ``linux``, ``win``, ``mac``
     - ``conan_conandata_yml``
     - C++
     - https://docs.conan.io/2/tutorial/creating_packages/handle_sources_in_packages.html#using-the-conandata-yml-file
   * - conan recipe
     - ``*/conanfile.py``
     - ``conan``
     - ``linux``, ``win``, ``mac``
     - ``conan_conanfile_py``
     - C++
     - https://docs.conan.io/2.0/reference/conanfile.html
   * - Conda metadata JSON in rootfs
     - ``*conda-meta/*.json``
     - ``conda``
     - ``linux``, ``win``, ``mac``
     - ``conda_meta_json``
     - Python
     - https://docs.conda.io/
   * - Conda meta.yml manifest
     - ``*/meta.yaml``
     - ``conda``
     - ``linux``, ``win``, ``mac``
     - ``conda_meta_yaml``
     - None
     - https://docs.conda.io/
   * - Conda yaml manifest
     - ``*conda*.yaml``
       ``*env*.yaml``
       ``*environment*.yaml``
     - ``conda``
     - ``linux``, ``win``, ``mac``
     - ``conda_yaml``
     - Python
     - https://docs.conda.io/
   * - CPAN Perl dist.ini
     - ``*/dist.ini``
     - ``cpan``
     - ``linux``, ``win``, ``mac``
     - ``cpan_dist_ini``
     - Perl
     - https://metacpan.org/pod/Dist::Zilla::Tutorial
   * - CPAN Perl Makefile.PL
     - ``*/Makefile.PL``
     - ``cpan``
     - ``linux``, ``win``, ``mac``
     - ``cpan_makefile``
     - Perl
     - https://www.perlmonks.org/?node_id=128077
   * - CPAN Perl module MANIFEST
     - ``*/MANIFEST``
     - ``cpan``
     - ``linux``, ``win``, ``mac``
     - ``cpan_manifest``
     - Perl
     - https://metacpan.org/pod/Module::Manifest
   * - CPAN Perl META.json
     - ``*/META.json``
     - ``cpan``
     - ``linux``, ``win``, ``mac``
     - ``cpan_meta_json``
     - Perl
     - https://metacpan.org/pod/Parse::CPAN::Meta
   * - CPAN Perl META.yml
     - ``*/META.yml``
     - ``cpan``
     - ``linux``, ``win``, ``mac``
     - ``cpan_meta_yml``
     - Perl
     - https://metacpan.org/pod/CPAN::Meta::YAML
   * - CRAN package DESCRIPTION
     - ``*/DESCRIPTION``
     - ``cran``
     - ``linux``, ``win``, ``mac``
     - ``cran_description``
     - R
     - https://r-pkgs.org/description.html
   * - Debian control file - extracted layout
     - ``*/control.tar.gz-extract/control``
       ``*/control.tar.xz-extract/control``
     - ``deb``
     - ``linux``, ``win``, ``mac``
     - ``debian_control_extracted_deb``
     - None
     - https://www.debian.org/doc/debian-policy/ch-controlfields.html
   * - Debian control file - source layout
     - ``*/debian/control``
     - ``deb``
     - ``linux``, ``win``, ``mac``
     - ``debian_control_in_source``
     - None
     - https://www.debian.org/doc/debian-policy/ch-controlfields.html
   * - Debian machine readable file in source
     - ``*usr/share/doc/*/copyright``
     - ``deb``
     - ``linux``, ``win``, ``mac``
     - ``debian_copyright_in_package``
     - None
     - https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
   * - Debian machine readable file in source
     - ``*/debian/copyright``
     - ``deb``
     - ``linux``, ``win``, ``mac``
     - ``debian_copyright_in_source``
     - None
     - https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
   * - Debian machine readable file standalone
     - ``*/copyright``
       ``*_copyright``
     - ``deb``
     - ``linux``, ``win``, ``mac``
     - ``debian_copyright_standalone``
     - None
     - https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
   * - Debian binary package archive
     - ``*.deb``
     - ``deb``
     - ``linux``, ``win``, ``mac``
     - ``debian_deb``
     - None
     - https://manpages.debian.org/unstable/dpkg-dev/deb.5.en.html
   * - Debian distroless installed database
     - ``*var/lib/dpkg/status.d/*``
     - ``deb``
     - ``linux``, ``win``, ``mac``
     - ``debian_distroless_installed_db``
     - None
     - https://www.debian.org/doc/debian-policy/ch-controlfields.html
   * - Debian installed file paths list
     - ``*var/lib/dpkg/info/*.list``
     - ``deb``
     - ``linux``, ``win``, ``mac``
     - ``debian_installed_files_list``
     - None
     - None
   * - Debian installed file MD5 and paths list
     - ``*var/lib/dpkg/info/*.md5sums``
     - ``deb``
     - ``linux``, ``win``, ``mac``
     - ``debian_installed_md5sums``
     - None
     - https://www.debian.org/doc/manuals/debian-handbook/sect.package-meta-information.en.html#sect.configuration-scripts
   * - Debian installed packages database
     - ``*var/lib/dpkg/status``
     - ``deb``
     - ``linux``, ``win``, ``mac``
     - ``debian_installed_status_db``
     - None
     - https://www.debian.org/doc/debian-policy/ch-controlfields.html
   * - Debian file MD5 and paths list in .deb archive
     - ``*/control.tar.gz-extract/md5sums``
       ``*/control.tar.xz-extract/md5sums``
     - ``deb``
     - ``linux``, ``win``, ``mac``
     - ``debian_md5sums_in_extracted_deb``
     - None
     - https://www.debian.org/doc/manuals/debian-handbook/sect.package-meta-information.en.html#sect.configuration-scripts
   * - Debian package original source archive
     - ``*.orig.tar.xz``
       ``*.orig.tar.gz``
     - ``deb``
     - ``linux``, ``win``, ``mac``
     - ``debian_original_source_tarball``
     - None
     - https://manpages.debian.org/unstable/dpkg-dev/deb.5.en.html
   * - Debian source control file
     - ``*.dsc``
     - ``deb``
     - ``linux``, ``win``, ``mac``
     - ``debian_source_control_dsc``
     - None
     - https://wiki.debian.org/dsc
   * - Debian source package metadata archive
     - ``*.debian.tar.xz``
       ``*.debian.tar.gz``
     - ``deb``
     - ``linux``, ``win``, ``mac``
     - ``debian_source_metadata_tarball``
     - None
     - https://manpages.debian.org/unstable/dpkg-dev/deb.5.en.html
   * - macOS disk image file
     - ``*.dmg``
       ``*.sparseimage``
     - ``dmg``
     - ``linux``, ``win``, ``mac``
     - ``apple_dmg``
     - None
     - https://en.wikipedia.org/wiki/Apple_Disk_Image
   * - Java EAR application.xml
     - ``*/META-INF/application.xml``
     - ``ear``
     - ``linux``, ``win``, ``mac``
     - ``java_ear_application_xml``
     - Java
     - https://en.wikipedia.org/wiki/EAR_(file_format)
   * - Java EAR Enterprise application archive
     - ``*.ear``
     - ``ear``
     - ``linux``, ``win``, ``mac``
     - ``java_ear_archive``
     - Java
     - https://en.wikipedia.org/wiki/EAR_(file_format)
   * - FreeBSD compact package manifest
     - ``*/+COMPACT_MANIFEST``
     - ``freebsd``
     - ``linux``, ``win``, ``mac``
     - ``freebsd_compact_manifest``
     - None
     - https://www.freebsd.org/cgi/man.cgi?pkg-create(8)#MANIFEST_FILE_DETAILS
   * - RubyGems gem package archive
     - ``*.gem``
     - ``gem``
     - ``linux``, ``win``, ``mac``
     - ``gem_archive``
     - Ruby
     - https://web.archive.org/web/20220326093616/https://piotrmurach.com/articles/looking-inside-a-ruby-gem/
   * - RubyGems gem package extracted archive
     - ``*/metadata.gz-extract``
     - ``gem``
     - ``linux``, ``win``, ``mac``
     - ``gem_archive_extracted``
     - Ruby
     - https://web.archive.org/web/20220326093616/https://piotrmurach.com/articles/looking-inside-a-ruby-gem/
   * - RubyGems gemspec manifest - installed vendor/bundle/specifications layout
     - ``*/specifications/*.gemspec``
     - ``gem``
     - ``linux``, ``win``, ``mac``
     - ``gem_gemspec_installed_specifications``
     - Ruby
     - https://guides.rubygems.org/specification-reference/
   * - RubyGems Bundler Gemfile
     - ``*/Gemfile``
       ``*/*.gemfile``
       ``*/Gemfile-*``
     - ``gem``
     - ``linux``, ``win``, ``mac``
     - ``gemfile``
     - Ruby
     - https://bundler.io/man/gemfile.5.html
   * - RubyGems Bundler Gemfile - extracted layout
     - ``*/data.gz-extract/Gemfile``
     - ``gem``
     - ``linux``, ``win``, ``mac``
     - ``gemfile_extracted``
     - Ruby
     - https://bundler.io/man/gemfile.5.html
   * - RubyGems Bundler Gemfile.lock
     - ``*/Gemfile.lock``
     - ``gem``
     - ``linux``, ``win``, ``mac``
     - ``gemfile_lock``
     - Ruby
     - https://bundler.io/man/gemfile.5.html
   * - RubyGems Bundler Gemfile.lock - extracted layout
     - ``*/data.gz-extract/Gemfile.lock``
     - ``gem``
     - ``linux``, ``win``, ``mac``
     - ``gemfile_lock_extracted``
     - Ruby
     - https://bundler.io/man/gemfile.5.html
   * - RubyGems gemspec manifest
     - ``*.gemspec``
     - ``gem``
     - ``linux``, ``win``, ``mac``
     - ``gemspec``
     - Ruby
     - https://guides.rubygems.org/specification-reference/
   * - RubyGems gemspec manifest - extracted data layout
     - ``*/data.gz-extract/*.gemspec``
     - ``gem``
     - ``linux``, ``win``, ``mac``
     - ``gemspec_extracted``
     - Ruby
     - https://guides.rubygems.org/specification-reference/
   * - Go modules file
     - ``*/go.mod``
     - ``golang``
     - ``linux``, ``win``, ``mac``
     - ``go_mod``
     - Go
     - https://go.dev/ref/mod
   * - Go module cheksums file
     - ``*/go.sum``
     - ``golang``
     - ``linux``, ``win``, ``mac``
     - ``go_sum``
     - Go
     - https://go.dev/ref/mod#go-sum-files
   * - Go Godeps
     - ``*/Godeps.json``
     - ``golang``
     - ``linux``, ``win``, ``mac``
     - ``godeps``
     - Go
     - https://github.com/tools/godep
   * - Go binary
     - None
     - ``golang``
     - ``linux``, ``win``, ``mac``
     - ``golang_binary``
     - Go
     - https://github.com/nexB/go-inspector/
   * - Haxe haxelib.json metadata file
     - ``*/haxelib.json``
     - ``haxe``
     - ``linux``, ``win``, ``mac``
     - ``haxelib_json``
     - Haxe
     - https://lib.haxe.org/documentation/creating-a-haxelib-package/
   * - InstallShield installer
     - ``*.exe``
     - ``installshield``
     - ``linux``, ``win``, ``mac``
     - ``installshield_installer``
     - None
     - https://www.revenera.com/install/products/installshield
   * - iOS package archive
     - ``*.ipa``
     - ``ios``
     - ``linux``, ``win``, ``mac``
     - ``ios_ipa``
     - Objective-C
     - https://en.wikipedia.org/wiki/.ipa
   * - ISO disk image
     - ``*.iso``
       ``*.udf``
       ``*.img``
     - ``iso``
     - ``linux``, ``win``, ``mac``
     - ``iso_disk_image``
     - None
     - https://en.wikipedia.org/wiki/ISO_9660
   * - Ant IVY dependency file
     - ``*/ivy.xml``
     - ``ivy``
     - ``linux``, ``win``, ``mac``
     - ``ant_ivy_xml``
     - Java
     - https://ant.apache.org/ivy/history/latest-milestone/ivyfile.html
   * - JAR Java Archive
     - ``*.jar``
     - ``jar``
     - ``linux``, ``win``, ``mac``
     - ``java_jar``
     - None
     - https://en.wikipedia.org/wiki/JAR_(file_format)
   * - Java JAR MANIFEST.MF
     - ``*/META-INF/MANIFEST.MF``
     - ``jar``
     - ``linux``, ``win``, ``mac``
     - ``java_jar_manifest``
     - Java
     - https://docs.oracle.com/javase/tutorial/deployment/jar/manifestindex.html
   * - JBOSS service archive
     - ``*.sar``
     - ``jboss-service``
     - ``linux``, ``win``, ``mac``
     - ``jboss_sar``
     - Java
     - https://docs.jboss.org/jbossas/docs/Server_Configuration_Guide/4/html/ch02s01.html
   * - JBOSS service.xml
     - ``*/meta-inf/jboss-service.xml``
     - ``jboss-service``
     - ``linux``, ``win``, ``mac``
     - ``jboss_service_xml``
     - Java
     - https://docs.jboss.org/jbossas/docs/Server_Configuration_Guide/4/html/ch02s01.html
   * - Linux OS release metadata file
     - ``*etc/os-release``
       ``*usr/lib/os-release``
     - ``linux-distro``
     - ``linux``, ``win``, ``mac``
     - ``etc_os_release``
     - None
     - https://www.freedesktop.org/software/systemd/man/os-release.html
   * - Gradle build script
     - ``*/build.gradle``
       ``*/build.gradle.kts``
     - ``maven``
     - ``linux``, ``win``, ``mac``
     - ``build_gradle``
     - None
     - None
   * - Apache Maven pom
     - ``*.pom``
       ``*pom.xml``
     - ``maven``
     - ``linux``, ``win``, ``mac``
     - ``maven_pom``
     - Java
     - https://maven.apache.org/pom.html
   * - Apache Maven pom properties file
     - ``*/pom.properties``
     - ``maven``
     - ``linux``, ``win``, ``mac``
     - ``maven_pom_properties``
     - Java
     - https://maven.apache.org/pom.html
   * - Meteor package.js
     - ``*/package.js``
     - ``meteor``
     - ``linux``, ``win``, ``mac``
     - ``meteor_package``
     - JavaScript
     - https://docs.meteor.com/api/packagejs.html
   * - Mozilla XPI extension
     - ``*.xpi``
     - ``mozilla``
     - ``linux``, ``win``, ``mac``
     - ``mozilla_xpi``
     - JavaScript
     - https://en.wikipedia.org/wiki/XPInstall
   * - Microsoft MSI installer
     - ``*.msi``
     - ``msi``
     - ``linux``
     - ``msi_installer``
     - None
     - https://docs.microsoft.com/en-us/windows/win32/msi/windows-installer-portal
   * - npm package.json
     - ``*/package.json``
     - ``npm``
     - ``linux``, ``win``, ``mac``
     - ``npm_package_json``
     - JavaScript
     - https://docs.npmjs.com/cli/v8/configuring-npm/package-json
   * - npm package-lock.json lockfile
     - ``*/package-lock.json``
       ``*/.package-lock.json``
     - ``npm``
     - ``linux``, ``win``, ``mac``
     - ``npm_package_lock_json``
     - JavaScript
     - https://docs.npmjs.com/cli/v8/configuring-npm/package-lock-json
   * - npm shrinkwrap.json lockfile
     - ``*/npm-shrinkwrap.json``
     - ``npm``
     - ``linux``, ``win``, ``mac``
     - ``npm_shrinkwrap_json``
     - JavaScript
     - https://docs.npmjs.com/cli/v8/configuring-npm/npm-shrinkwrap-json
   * - pnpm pnpm-lock.yaml lockfile
     - ``*/pnpm-lock.yaml``
     - ``npm``
     - ``linux``, ``win``, ``mac``
     - ``pnpm_lock_yaml``
     - JavaScript
     - https://github.com/pnpm/spec/blob/master/lockfile/6.0.md
   * - pnpm shrinkwrap.yaml lockfile
     - ``*/shrinkwrap.yaml``
     - ``npm``
     - ``linux``, ``win``, ``mac``
     - ``pnpm_shrinkwrap_yaml``
     - JavaScript
     - https://github.com/pnpm/spec/blob/master/lockfile/4.md
   * - pnpm workspace yaml file
     - ``*/pnpm-workspace.yaml``
     - ``npm``
     - ``linux``, ``win``, ``mac``
     - ``pnpm_workspace_yaml``
     - JavaScript
     - https://pnpm.io/pnpm-workspace_yaml
   * - yarn.lock lockfile v1 format
     - ``*/yarn.lock``
     - ``npm``
     - ``linux``, ``win``, ``mac``
     - ``yarn_lock_v1``
     - JavaScript
     - https://classic.yarnpkg.com/lang/en/docs/yarn-lock/
   * - yarn.lock lockfile v2 format
     - ``*/yarn.lock``
     - ``npm``
     - ``linux``, ``win``, ``mac``
     - ``yarn_lock_v2``
     - JavaScript
     - https://classic.yarnpkg.com/lang/en/docs/yarn-lock/
   * - NSIS installer
     - ``*.exe``
     - ``nsis``
     - ``linux``, ``win``, ``mac``
     - ``nsis_installer``
     - None
     - https://nsis.sourceforge.io/Main_Page
   * - NuGet nupkg package archive
     - ``*.nupkg``
     - ``nuget``
     - ``linux``, ``win``, ``mac``
     - ``nuget_nupkg``
     - None
     - https://en.wikipedia.org/wiki/Open_Packaging_Conventions
   * - NuGet nuspec package manifest
     - ``*.nuspec``
     - ``nuget``
     - ``linux``, ``win``, ``mac``
     - ``nuget_nupsec``
     - None
     - https://docs.microsoft.com/en-us/nuget/reference/nuspec
   * - NuGet packages.lock.json file
     - ``*packages.lock.json``
     - ``nuget``
     - ``linux``, ``win``, ``mac``
     - ``nuget_packages_lock``
     - None
     - https://learn.microsoft.com/en-us/nuget/reference/cli-reference/cli-ref-restore
   * - Ocaml Opam file
     - ``*opam``
     - ``opam``
     - ``linux``, ``win``, ``mac``
     - ``opam_file``
     - Ocaml
     - https://opam.ocaml.org/doc/Manual.html#Common-file-format
   * - Java OSGi MANIFEST.MF
     - None
     - ``osgi``
     - ``linux``, ``win``, ``mac``
     - ``java_osgi_manifest``
     - Java
     - https://docs.oracle.com/javase/tutorial/deployment/jar/manifestindex.html
   * - Dart pubspec lockfile
     - ``*pubspec.lock``
     - ``pubspec``
     - ``linux``, ``win``, ``mac``
     - ``pubspec_lock``
     - dart
     - https://web.archive.org/web/20220330081004/https://gpalma.pt/blog/what-is-the-pubspec-lock/
   * - Dart pubspec manifest
     - ``*pubspec.yaml``
     - ``pubspec``
     - ``linux``, ``win``, ``mac``
     - ``pubspec_yaml``
     - dart
     - https://dart.dev/tools/pub/pubspec
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
     - ``linux``, ``win``, ``mac``
     - ``pip_requirements``
     - Python
     - https://pip.pypa.io/en/latest/reference/requirements-file-format/
   * - Pipfile
     - ``*Pipfile``
     - ``pypi``
     - ``linux``, ``win``, ``mac``
     - ``pipfile``
     - Python
     - https://github.com/pypa/pipfile
   * - Pipfile.lock
     - ``*Pipfile.lock``
     - ``pypi``
     - ``linux``, ``win``, ``mac``
     - ``pipfile_lock``
     - Python
     - https://github.com/pypa/pipfile
   * - PyPI editable local installation PKG-INFO
     - ``*.egg-info/PKG-INFO``
     - ``pypi``
     - ``linux``, ``win``, ``mac``
     - ``pypi_editable_egg_pkginfo``
     - Python
     - https://peps.python.org/pep-0376/
   * - PyPI egg
     - ``*.egg``
     - ``pypi``
     - ``linux``, ``win``, ``mac``
     - ``pypi_egg``
     - Python
     - https://web.archive.org/web/20210604075235/http://peak.telecommunity.com/DevCenter/PythonEggs
   * - PyPI extracted egg PKG-INFO
     - ``*/EGG-INFO/PKG-INFO``
     - ``pypi``
     - ``linux``, ``win``, ``mac``
     - ``pypi_egg_pkginfo``
     - Python
     - https://peps.python.org/pep-0376/
   * - Python poetry pyproject.toml
     - ``*pip-inspect.deplock``
     - ``pypi``
     - ``linux``, ``win``, ``mac``
     - ``pypi_inspect_deplock``
     - Python
     - https://pip.pypa.io/en/stable/cli/pip_inspect/
   * - Python poetry lockfile
     - ``*poetry.lock``
     - ``pypi``
     - ``linux``, ``win``, ``mac``
     - ``pypi_poetry_lock``
     - Python
     - https://python-poetry.org/docs/basic-usage/#installing-with-poetrylock
   * - Python poetry pyproject.toml
     - ``*pyproject.toml``
     - ``pypi``
     - ``linux``, ``win``, ``mac``
     - ``pypi_poetry_pyproject_toml``
     - Python
     - https://packaging.python.org/en/latest/specifications/pyproject-toml/
   * - Python pyproject.toml
     - ``*pyproject.toml``
     - ``pypi``
     - ``linux``, ``win``, ``mac``
     - ``pypi_pyproject_toml``
     - Python
     - https://packaging.python.org/en/latest/specifications/pyproject-toml/
   * - PyPI extracted sdist PKG-INFO
     - ``*/PKG-INFO``
     - ``pypi``
     - ``linux``, ``win``, ``mac``
     - ``pypi_sdist_pkginfo``
     - Python
     - https://peps.python.org/pep-0314/
   * - Python setup.cfg
     - ``*setup.cfg``
     - ``pypi``
     - ``linux``, ``win``, ``mac``
     - ``pypi_setup_cfg``
     - Python
     - https://peps.python.org/pep-0390/
   * - Python setup.py
     - ``*setup.py``
     - ``pypi``
     - ``linux``, ``win``, ``mac``
     - ``pypi_setup_py``
     - Python
     - https://docs.python.org/3.11/distutils/setupscript.html
   * - PyPI wheel
     - ``*.whl``
     - ``pypi``
     - ``linux``, ``win``, ``mac``
     - ``pypi_wheel``
     - Python
     - https://peps.python.org/pep-0427/
   * - PyPI installed wheel METADATA
     - ``*.dist-info/METADATA``
     - ``pypi``
     - ``linux``, ``win``, ``mac``
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
     - ``linux``, ``win``, ``mac``
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
     - ``linux``, ``win``, ``mac``
     - ``rpm_archive``
     - None
     - https://en.wikipedia.org/wiki/RPM_Package_Manager
   * - RPM installed package BDB database
     - ``*var/lib/rpm/Packages``
     - ``rpm``
     - ``linux``
     - ``rpm_installed_database_bdb``
     - None
     - https://man7.org/linux/man-pages/man8/rpmdb.8.html
   * - RPM installed package NDB database
     - ``*usr/lib/sysimage/rpm/Packages.db``
     - ``rpm``
     - ``linux``
     - ``rpm_installed_database_ndb``
     - None
     - https://fedoraproject.org/wiki/Changes/NewRpmDBFormat
   * - RPM installed package SQLite database
     - ``*rpm/rpmdb.sqlite``
     - ``rpm``
     - ``linux``
     - ``rpm_installed_database_sqlite``
     - None
     - https://fedoraproject.org/wiki/Changes/Sqlite_Rpmdb
   * - RPM mariner distroless package manifest
     - ``*var/lib/rpmmanifest/container-manifest-2``
     - ``rpm``
     - ``linux``, ``win``, ``mac``
     - ``rpm_mariner_manifest``
     - None
     - https://github.com/microsoft/marinara/
   * - RPM mariner distroless package license files
     - ``*usr/share/licenses/*/COPYING*``
       ``*usr/share/licenses/*/LICENSE*``
     - ``rpm``
     - ``linux``, ``win``, ``mac``
     - ``rpm_package_licenses``
     - None
     - https://github.com/microsoft/marinara/
   * - RPM specfile
     - ``*.spec``
     - ``rpm``
     - ``linux``, ``win``, ``mac``
     - ``rpm_spefile``
     - None
     - https://en.wikipedia.org/wiki/RPM_Package_Manager
   * - shell archive
     - ``*.shar``
     - ``shar``
     - ``linux``, ``win``, ``mac``
     - ``shar_shell_archive``
     - None
     - https://en.wikipedia.org/wiki/Shar
   * - Squashfs disk image
     - None
     - ``squashfs``
     - ``linux``, ``win``, ``mac``
     - ``squashfs_disk_image``
     - None
     - https://en.wikipedia.org/wiki/SquashFS
   * - JSON dump of Package.swift created by DepLock or with ``swift package dump-package &gt; Package.swift.json``
     - ``*/Package.swift.json``
       ``*/Package.swift.deplock``
     - ``swift``
     - ``linux``, ``win``, ``mac``
     - ``swift_package_manifest_json``
     - Swift
     - https://docs.swift.org/package-manager/PackageDescription/PackageDescription.html
   * - Resolved full dependency lockfile for Package.swift created with ``swift package resolve``
     - ``*/Package.resolved``
       ``*/.package.resolved``
     - ``swift``
     - ``linux``, ``win``, ``mac``
     - ``swift_package_resolved``
     - swift
     - https://docs.swift.org/package-manager/PackageDescription/PackageDescription.html#package-dependency
   * - Swift dependency graph created by DepLock
     - ``*/swift-show-dependencies.deplock``
     - ``swift``
     - ``linux``, ``win``, ``mac``
     - ``swift_package_show_dependencies``
     - Swift
     - https://forums.swift.org/t/swiftpm-show-dependencies-without-fetching-dependencies/51154
   * - Java Web Application Archive
     - ``*.war``
     - ``war``
     - ``linux``, ``win``, ``mac``
     - ``java_war_archive``
     - Java
     - https://en.wikipedia.org/wiki/WAR_(file_format)
   * - Java WAR web/xml
     - ``*/WEB-INF/web.xml``
     - ``war``
     - ``linux``, ``win``, ``mac``
     - ``java_war_web_xml``
     - Java
     - https://en.wikipedia.org/wiki/WAR_(file_format)
   * - Windows Registry Installed Program - Docker SOFTWARE
     - ``*/Files/Windows/System32/config/SOFTWARE``
     - ``windows-program``
     - ``linux``
     - ``win_reg_installed_programs_docker_file_software``
     - None
     - https://en.wikipedia.org/wiki/Windows_Registry
   * - Windows Registry Installed Program - Docker Software Delta
     - ``*/Hives/Software_Delta``
     - ``windows-program``
     - ``linux``
     - ``win_reg_installed_programs_docker_software_delta``
     - None
     - https://en.wikipedia.org/wiki/Windows_Registry
   * - Windows Registry Installed Program - Docker UtilityVM SOFTWARE
     - ``*/UtilityVM/Files/Windows/System32/config/SOFTWARE``
     - ``windows-program``
     - ``linux``
     - ``win_reg_installed_programs_docker_utility_software``
     - None
     - https://en.wikipedia.org/wiki/Windows_Registry
   * - Microsoft Update Manifest .mum file
     - ``*.mum``
     - ``windows-update``
     - ``linux``, ``win``, ``mac``
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
     - ``linux``, ``win``, ``mac``
     - ``windows_executable``
     - None
     - https://en.wikipedia.org/wiki/Portable_Executable
