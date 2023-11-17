============
Contributing
============

Contributions are welcome and appreciated!
Every little bit helps, and a credit will always be given.

.. _issues : https://github.com/nexB/scancode-toolkit/issues
__ issues_

If you are new to ScanCode and want to find easy tickets to work on,
check `easy issues <https://github.com/nexB/scancode-toolkit/labels/easy>`_

When contributing to ScanCode (such as code, bugs, documentation, etc.) you
agree to the Developer `Certificate of Origin <http://developercertificate.org/>`_
and the ScanCode license (see the `NOTICE <https://github.com/nexB/scancode-toolkit/blob/develop/NOTICE>`_ file).
The same approach is used by Linux Kernel developers and several other projects.

For commits, it is best to simply add a line like this to your commit message,
with your name and email::

    Signed-off-by: Jane Doe <developer@example.com>

Please try to write a good commit message, see `good commit message wiki
<https://aboutcode.readthedocs.io/en/latest/contributing/writing_good_commit_messages.html>`_ for
details. In particular use the imperative for your commit subject: think that
you are giving an order to the codebase to update itself.


Feature requests and feedback
=============================

To send feedback or ask a question, `file an issue <issues_>`_

If you are proposing a feature:

* Explain how it would work.
* Keep the scope as simple as possible to make it easier to implement.
* Remember that your contributions are welcomed to implement this feature!


Chat with other developers
==========================

For other questions, discussions, and chats, we have:

- an official Gitter channel at https://gitter.im/aboutcode-org/discuss
  Gitter also has an IRC bridge at https://irc.gitter.im/
  This is the main place where we chat and meet.

- an official #aboutcode IRC channel on liberachat (server web.libera.chat)
  for scancode and other related tools. You can use your
  favorite IRC client or use the web chat at https://web.libera.chat/?#aboutcode .
  This is a busy place with a lot of CI and commit notifications that makes
  actual chat sometimes difficult!

- a Gitter channel to discuss Documentation at https://gitter.im/aboutcode-org/gsod-season-of-docs

Bug reports
===========

When `reporting a bug`__ please include:

* Your operating system name, version, and architecture (32 or 64 bits).
* Your Python version.
* Your ScanCode version.
* Any additional details about your local setup that might be helpful to
  diagnose this bug.
* Detailed steps to reproduce the bug, such as the commands you ran and a link
  to the code you are scanning.
* The error messages or failure trace if any.
* If helpful, you can add a screenshot as an issue attachment when relevant or
  some extra file as a link to a `Gist <https://gist.github.com>`_.


Documentation improvements
==========================

Documentation can come in the form of new documentation pages/sections, tutorials/how-to documents,
any other general upgrades, etc. Even a minor typo fix is welcomed. 

If something is missing in the documentation or if you found some part confusing,
please file an issue with your suggestions for improvement. Use the “Documentation Improvement”
template. Your help and contribution make ScanCode docs better, we love hearing from you!

The ScanCode documentation is hosted at `scancode-toolkit.readthedocs.io <https://scancode-toolkit.readthedocs.io/en/latest/>`_.

If you want to contribute to Scancode Documentation, you'll find `this guide here <https://scancode-toolkit.readthedocs.io/en/latest/contribute/contrib_doc.html>`_ helpful.

Development
===========

To set up ScanCode for local development:

1. Fork the scancode-toolkit on GitHub, click `fork <https://github.com/nexb/scancode-toolkit/fork>`_ button

2. Clone your fork locally:

   Use SSH::

    git clone git@github.com:your_name_here/scancode-toolkit.git

   Or use HTTPS::

    git clone https://github.com/your_name_here/scancode-toolkit.git

   See also GitHub docs for `SSH <https://help.github.com/articles/connecting-to-github-with-ssh/>`_ 
   or `HTTPS <https://help.github.com/articles/which-remote-url-should-i-use/#cloning-with-https-urls-recommended>`_
    
   If you want to change the connection type, do following
     
    SSH to HTTPS ::
     
      git remote set-url <repository-alias-name> https://github.com/your_name_here/scancode-toolkit.git
     
    HTTPS to SSH ::
     
      git remote set-url <repository-alias-name> git@github.com:your_name_here/scancode-toolkit.git
     
   Generally <repository-alias-name> is named origin, but in the case of multiple fetch/pull source of repository you can choose whatever name you want
     
3. Create a branch for local development::

    git checkout -b name-of-your-bugfix-or-feature
    
4. Check out the Contributing to Code Development `documentation <https://scancode-toolkit.readthedocs.io/en/stable/contribute/contrib_dev.html>`_, as it contains more in-depth guide for contributing code and documentation.

5. To configure your local environment for development, locate to the main
   directory of the local repository, and run the configure script.
   The configure script creates an isolated Python `virtual environment` in
   your checkout directory, the Python `pip` tool, and installs the third-party
   libraries (from the `thirdparty/ directory`), setup the paths, etc.
   See https://virtualenv.pypa.io/en/latest/ for more details. 

   Run this command to configure ScanCode::

        ./configure --dev

   On Windows use instead::

        configure --dev

   Then activate the virtual environment::

        source venv/bin/activate

        or

        . venv/bin/activate

   On Windows use::

        venv\Scripts\activate

   When you create a new terminal/shell to work on ScanCode rerun the activate step.

   When you pull new code from git, rerun ./configure


6. Now you can make your code changes in your local clone.
   Please create new unit tests for your code. We love tests!

7. An update to the ``CHANGELOG`` is required if any important changes are made that needs to be communicated such as:

   * Changes in the API.

   * Addition or deletion of CLI options.

   * Addition of any new feature or any other miscellaneous changes to the program.
   
8. If there is a code change, a significant document, or any other changes, you must update the ``AUTHORS`` to include your own name.

9. When you are done with your changes, run all the tests.
   Use this command::

        py.test

   Or use the -n6 option to run on 6 threads in parallel and run tests faster::

       py.test -n6

   If you are running this on a RedHat-based OS you may come across this
   failure::

       OSError: libbz2.so.1.0: cannot open shared object file: No such file or directory

   Try creating a symbolic link to libbz2.so.1.0 to solve this issue::

       locate libbz2.so.1.0
       cd <resulting libbz2.so directory>
       sudo ln -s <your version of libbz2.so> libbz2.so.1.0

   See `this issue <https://github.com/nexB/scancode-toolkit/issues/443>`_ for more information.

10. Check the status of your local repository before committing, regarding files changed::

     git status


11. Commit your changes and push your branch to your GitHub fork::

     git add <file-changed-1> <file-changed-2> <file-changed-3>
     git commit -m "Your detailed description of your changes." --signoff
     git push <repository-alias-name> name-of-your-bugfix-or-feature

12. Submit a pull request through the GitHub website for this branch.


Pull Request Guidelines
-----------------------

If you need a code review or feedback while you are developing the code just
create a pull request. You can add new commits to your branch as needed.

For merging, your request would need to:

1. Include unit tests that are passing (run ``py.test``).
2. Update documentation as needed for new API, functionality, etc.
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

