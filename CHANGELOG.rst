Release notes
=============

vNext
-----


Version 21.5.5
---------------

- Add new function to find a command or shared object file in the PATH (e.g. in
  environment variables). See commoncode.command.find_in_path()
- Add new simplified the commoncode.command.execute() function. 
- Add support for Python 3.10
- Update tests to cope with Python 3.6 bug https://bugs.python.org/issue26919
- Adopt new skeleton with configure scripts updates

Breaking API changes:

- commoncode.command.load_shared_library() now ignores the lib_dir argument
- commoncode.command.execute2() is deprecated and ignores the lib_dir argument
  it is replaced by commoncode.command.execute()


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
