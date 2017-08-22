============
Contributing
============

Contributions are welcome and appreciated!
Every little bit helps, and credit will always be given.

If you are new to ScanCode and want to find easy tickets to work on, check https://github.com/nexB/scancode-toolkit/labels/easy

When contributing to ScanCode (such as code, bugs, documentation, etc.) you
agree to the Developer Certificate of Origin http://developercertificate.org/
and the ScanCode license (see the NOTICE file).  The same approach is used
by the Linux Kernel developers and several other projects.

For commits, it is best to simply add a line like this to your commit message,
with your name and email::

    Signed-off-by: Jane Doe <developer@example.com>

Please try to write a good commit message.
See https://github.com/nexB/aboutcode/wiki/Writing-good-commit-messages for details.



Feature requests and feedback
=============================

To send feedback or ask a question file an issue at
https://github.com/scancode/scancode-toolkit/issues

If you are proposing a feature:

* Explain how it would work.
* Keep the scope simple possible to make it easier to implement.
* Remember that your contributions are welcomed to implement this feature!


Chat with other developers
==========================

You can join the official #aboutcode IRC channel on freenode
(server chat.freenode.net) to chat about scancode and other related tools.
You can use your favorite IRC client or use the web chat at https://webchat.freenode.net/


Bug reports
===========

When reporting a bug at https://github.com/nexb/scancode-toolkit/issues please
include:

* Your operating system name, version and architecture (32 or 64 bits).
* Your Python version.
* Your ScanCode version.
* Any additional details about your local setup that might be helpful to
  diagnose this bug.
* Detailed steps to reproduce the bug, such as the commands you ran and a link
  to the code you are scanning.
* The errors messages or failure trace if any.
* If helpful, you can add a screenshot as an issue attachment when relevant or
  some extra file as a link to a Gist https://gist.github.com


Documentation improvements
==========================

Documentation can come in the form of wiki pages, docstrings, blog posts,
articles, etc. Even a minor typo fix is welcomed.


Development
===========

To set up ScanCode for local development:

1. Fork the scancode-toolkit on GitHub at 
   https://github.com/nexb/scancode-toolkit/fork

2. Clone your fork locally:

   Use SSH::

    git clone git@github.com:your_name_here/scancode-toolkit.git

   Or use HTTPS::

    git clone https://github.com/your_name_here/scancode-toolkit.git

3. Create a branch for local development::

    git checkout -b name-of-your-bugfix-or-feature

4. Configure your local environment for development, run the configure script.
   The configure script creates an isolated Python `virtual environment` in
   your checkout directory, the Python `pip` tool, and installs the thirdparty
   libraries (from the `thirdparty/ directory`), setup the paths, etc.
   See https://virtualenv.pypa.io/en/latest/ for more details. 

   Run this command to configure ScanCode::

        source configure

   On Windows use instead::

        configure 

   When you create a new terminal/shell to work on ScanCode, either rerun the
   configure script or `source bin/activate` (or run `bin\\activate` on Windows)

5. Now you can make your code changes in your local clone.
   Please create new unit tests for your code.

6. When you are done with your changes, run all the tests.
   Use this command:: 

        py.test

   Or use the -n6 option to run on 6 threads in parallel and run tests faster::

       py.test -n6

7. Commit your changes and push your branch to your GitHub fork::

    git add .
    git commit -m "Your detailed description of your changes."
    git push origin name-of-your-bugfix-or-feature

8. Submit a pull request through the GitHub website for this branch.


Pull Request Guidelines
-----------------------

If you need a code review or feedback while you are developing the code just
create a pull request. You can add new commits to your branch as needed.

For merging, your request would need to:

1. Include unit tests that are passing (run ``py.test``).
2. Update documentation as needed for new API, functionality etc. 
3. Add a note to ``CHANGELOG.rst`` about the changes.
4. Add your name to ``AUTHORS.rst``.


Test tips
---------

To run a subset of test functions containing test_myfeature in their name use::

    py.test -k test_myfeature

To run the tests from a single test file::

    py.test  tests/commoncode/test_fileutils.py

To run tests in parallel on eight processors::

    py.test  -n 8

To run tests verbosely, displaying all print statements to terminal::

    py.test  -vvs
