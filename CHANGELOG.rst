Release notes
=============

Version 32.0.0 - (2024-09-05)
-----------------------------

- Add new optional argument to generate YAML test data files from a template
- Migrate URLs to new aboutcode.org org
- Drop support for Python 3.7
- Replace charset_normalizer by chardet because of unstable behavior between minor versions
  See https://github.com/jawah/charset_normalizer/issues/520
- Adopt black and isort style


Version 31.2.1 - (2024-05-16)
-----------------------------

- Remove ``commoncode.system.get_etc_os_release_info`` and replace it with ``commoncode.distro_os_release_parser``.


Version 31.2.0 - (2024-05-16)
-----------------------------

- Add ``commoncode.distro.os_release_parser`` from container-inspector to commoncode.


Version 31.1.0 - (2024-05-15)
------------------------------

- Add ``on_macos_arm64`` and ``on_ubuntu_22`` markers to ``commoncode.system``.


Version 31.0.3 - (2023-08-25)
------------------------------

- Mark our use of MD5 as NOT for security #54
- Fix VirtualCodebase walk issue when the root directory name is repeated #57


Version 31.0.2 - (2023-02-23)
------------------------------

- Update requirements in requirements.txt and requirements-dev.txt
- v31.0.1 was uploaded to PyPI without updating requirements.txt and
  requirements-dev.txt


Version 31.0.1 - (2023-02-23)
------------------------------

- Fix issue when instantiating a ``VirtualCodebase`` from a JSON where if there
  is no codebase attribute with the same name in the scan, then None is assigned
  to the codebase attribute instead of the default value that was passed in when
  VirtualCodebase was instantiated.
  https://github.com/nexB/commoncode/issues/48

- Update spdx-tools to 0.7.0rc0
  https://github.com/nexB/commoncode/pull/50


Version 31.0.0 - (2022-08-24)
------------------------------

This is a major version with API-breaking changes in the resource module.

- Drop support for Python 3.6

- The Resource has no rid (resource id) and no pid (parent id). Instead
  we now use internally a simpler mapping of {path: Resource} object.
  As a result the iteration on a Codebase is faster but this requires more
  memory.

- The Codebase and VirtualCodebase accepts a new "paths" argument that is list
  of paths. When provided, the Codebase will only contain Resources with these
  paths and no other resources. This handy to create a Codebase with only a
  subset of paths of interest. When we create a Codebase or VirtualCodebase
  with paths, we also always create any intermediate directories. So if you
  ask for a path of "root/dir/file", we create three resources: "root",
  "root/dir" and "root/dir/file". We accumulate codebase errors if the paths
  does not exists in the Codebase or VirtualCodebase. The paths must start with
  the root path segment and must be POSIX paths.

- When you create a VirtualCodebase with multiple scans, we now prefix each
  scan path with a codebase-1/, codebase-2/, etc. directory in addition to the
  "virtual_root" shared root directory. Otherwise files data was overwritten
  and inconsistent when each location "files" were sharing leading path
  segments. So if you provide to JSON inputs with that each contain the path
  "root/dir/file", the VirtualCodebase will contain these paths:

    - "virtual_root/codebase-1/root/dir/file"
    - "virtual_root/codebase-2/root/dir/file"

  It is otherwise practically impossible to correctly merge file data from
  multiple codebases reliably, so adding this prefix ensures that we are doing
  the right thing

- The Resource.path now never contains leading or trailing slash. We also
  normalize the path everywhere. In particular this behaviour is visible when
  you create a Codebase with a "full_root" argument. Previously, the paths of a
  "full_root" Codebase were prefixed with a slash "/".

- When you create a VirtualCodebase with more than one Resource, we now recreate
  the directory tree for any intermediary directory used in a path that is
  otherwise missing from files path list.
  In particular this behaviour changed when you create a VirtualCodebase from
  a previous Codebase created with a "full_root" argument. Previously, the
  missing paths of a "full_root" Codebase were kept unchanged.
  Note that the VirtualCodebase has always ignored the "full_root" argument.

- The Codebase and VirtualCodebase are now iterable. Iterating on a codebase
  is the same as a top-down walk.

- The "Codebase.original_location" attributed has been removed.
  No known users of commoncode used this.

- The Codebase and VirtualCodebase no longer have a "full_root" and
  "strip_root" constructor arguments and attributes. These can still be
  passed but they will be ignored.

  - Resource.path is now always the plain path where the first segment
    is the last segment of the root location, e.g. the root fiename.

  - The Resource now has new "full_root_path" and "strip_root_path"
    properties that return the corresponding paths.

  - The Resource.to_dict and the new Codebase.to_list both have a new
    "full_root" and "strip_root" arguments

  - The Resource.get_path() method accepts "full_root" and "strip_root" arguments.

- The Resource.create_child() method has been removed.

Other changes:

- Remove Python upper version limit.
- Merge latest skeleton
- fileutils.parent_directory() now accepts a "with_trail" argument.
  The returned directory has a trailing path separator unless with_trail is False.
  The default is True and the default behaviour is unchanged.

- Add ``posix_only`` option to ``commoncode.paths.portable_filename`` and
  ``commoncode.paths.safe_path``. This option prevents
  ``commoncode.paths.portable_filename`` and ``commoncode.paths.safe_path`` from
  replacing filenames and punctuation in filenames that are valid on POSIX
  operating systems, but not Windows.

- Remove unused intbitset dependency.


Version 30.2.0 - (2022-05-02)
------------------------------

- Relax dependencies version requirements by removing upper bounds.
- Use latest skeleton.


Version 30.1.2 - (2022-04-29)
------------------------------

- Minor improved utilities
- More robust handling of Codebase with a single Resource


Version 30.1.1 (2022-04-18)
------------------------------

- Remove usage of deprecated ``click.get_terminal_size()``.


Version 30.1.0 (2022-04-05)
------------------------------

- Add ``warning`` field to ``commoncode.Codebase`` headers.
- Add new functions ``get_jar_nv()`` and ``get_nupkg_nv()`` that accepts
  a filename of a JAR or nupkg and return a name/version tuple extracted
  using multiple heuristics.


Version 30.0.0 (2021-09-24)
------------------------------

- Switch back from calver to semver.
- Adopt latest skeleton. The default virtualenv directory is now venv and no
  longer tmp
- Fix issue with Click progressbar API #23 that prohibited to use all supported
  Click versions. Since Click is widely used that was a frequent source of
  installation conflicts.


Version 21.8.31
---------------

- Add an attribute to the header for scancode output format versioning.
  This is for https://github.com/nexB/scancode-toolkit/issues/2653


Version 21.8.27
---------------

- Ensure that the progressbar displays a counter correctly.
  This is a fix for https://github.com/nexB/scancode-toolkit/issues/2583


Version 21.7.23
---------------

- Add preserve_spaces argument in commoncode.paths.portable_filename.
  This argument will prevent the replacement of spaces in filenames.


Version 21.6.11
---------------

- Do not fail if a Codebase does not have a common shared root #23
- Consider all Resource attributes when building a VirtualCodebase #23
- Do not ignore by default sccs and rcs dirs https://github.com/nexB/scancode-toolkit/issues/1422


Version 21.6.10
---------------

- Do not fail if a Codebase file.size is None and not zero
- Bump pinned dependencies including pkg:pypi/urllib3 for CVE-2021-33503


Version 21.5.25
---------------

- Fix click-related bug https://github.com/nexB/scancode-toolkit/issues/2529
- Add tests to run on the latest of every dependency


Version 21.5.12
---------------

- Add new function to find a command or shared object file in the PATH (e.g. in
  environment variables). See commoncode.command.find_in_path()
- Add new simplified the commoncode.command.execute() function.
- Add support for Python 3.10
- Update tests to cope with Python 3.6 bug https://bugs.python.org/issue26919
- Adopt latest skeleton with configure scripts updates

Breaking API changes:

- commoncode.command.load_shared_library() now ignores the lib_dir argument
- commoncode.command.execute2() is deprecated and ignores the lib_dir argument
  it is replaced by commoncode.command.execute()
- In commoncode.testcase get_test_loc() "exists" argument has been renamed to
  "must_exist". It has also been added to FileDrivenTesting.get_test_loc()
  method.


Version 21.4.28
---------------

- Add new function to get a Resource path stripped from its root path segment


Version 21.1.21
---------------

- Improve error reporting when oding missing DLLs
- Clean config and improve basic documentation


Version 21.1.14
---------------

- Update dependencies
- Add Azure Pipelines CI support
- Drop Python 2 support
- Update license


Version 20.10.08
----------------

- Add support for both python 2 + 3
- Add CI support for python 2 + 3


Version 20.10
-------------

* Minimal fixes needed for proper release


Version 20.09.30
----------------

- Update to PEP 517/518 development practices
- Add some minimal documentation


Version 20.09
-------------

- Initial release.
