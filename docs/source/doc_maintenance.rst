Document Maintenance
====================

Document Software Setup
-----------------------

ScanCode Toolkit documentation is built using Sphinx.
See http://www.sphinx-doc.org/en/master/index.html

ScanCode Toolkit documentation is distributed using "Read the Docs".
See https://readthedocs.org/

Individual document files are in reStructuredText format.
See http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html

You create, build, and preview ScanCode Toolkit documentation on your local machine.

You commit your updates to the ScanCode Toolkit repository on GitHub, which triggers an automatic rebuild of https://scancode-toolkit.readthedocs.io/en/latest/index.html


Clone ScanCode Toolkit
----------------------

To get started, create or identify a working directory on your local machine.

Open that directory and execute the following command in a terminal session::

    git clone https://github.com/nexB/scancode-toolkit.git

That will create an /scancode-toolkit directory in your working directory.
Now you can install the dependencies in a virtualenv::

    cd scancode-toolkit
    python3.6 -m venv .
    cd docs
    source bin/activate

Now you can install Sphinx and the format theme used by readthedocs::

    pip install Sphinx sphinx_rtd_theme

Now you can build the HTML documents locally::

    cd docs
    make html

Assuming that your Sphinx installation was successful, Sphinx should build a local instance of the
documentation .html files::

    open build/html/index.html

You now have a local build of the ScanCode Toolkit documents.

Improve ScanCode Toolkit Documents
----------------------------------

Before you begin creating and modifying ScanCode Toolkit documents, be sure that you understand the basics of reStructuredText as explained at http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html

Ensure that you have the latest ScanCode Toolkit files::

    git pull
    git status

Use your favorite text editor to create and modify .rst files to make your documentation
improvements.

Review your work::

    cd docs
    make html
    open build/html/index.html

Share ScanCode Toolkit Document Improvements
--------------------------------------------

Follow standard git procedures to upload your new and modified files. The following commands are
examples::

    git status
    git add source/index.rst
    git add source/how-to-scan.rst
    git status
    git commit -m "New how-to document that explains how to scan"
    git status
    git push
    git status

The ScanCode Toolkit webhook with ReadTheDocs should rebuild the documentation. You can review your
results online.
