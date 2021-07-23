Release notes
=============

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
