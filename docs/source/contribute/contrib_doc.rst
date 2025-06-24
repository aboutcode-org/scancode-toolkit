.. _contrib_doc_dev:

Contributing to the Documentation
=================================

.. _contrib_doc_setup_local:

Setup Local Build
-----------------

To get started, check out and configure the repository for development::

    git clone https://github.com/aboutcode-org/scancode-toolkit.git

That will create an ``/scancode-toolkit`` directory in your working directory.
Now you can install the dependencies in a virtualenv::

    cd scancode-toolkit
    ./configure --dev

(Or use "make dev")

.. note::

    In case of windows, run ``configure --dev``.

This will install and configure all requirements foer development including for docs development.

Now you can build the HTML documentation locally::

    source venv/bin/activate
    make docs

This will build a local instance of the ``docs/_build`` directory::

    open docs/_build/index.html


To validate the documentation style and content, use::

    source venv/bin/activate
    make doc8
    make docs-check


.. _doc_ci:

Continuous Integration
----------------------

The documentations are checked on every new commit, so that common errors are avoided and
documentation standards are enforced. We checks for these aspects of the documentation:

1. Successful Builds (By using ``sphinx-build``)
2. No Broken Links   (By Using ``linkcheck``)
3. Linting Errors    (By Using ``doc8``)

You myst run these scripts locally before creating a pull request::

    make doc8
    make check-docs


.. _doc_style_docs8:

Style Checks Using ``doc8``
---------------------------

How To Run Style Tests
^^^^^^^^^^^^^^^^^^^^^^

In the project root, run the following commands::

    make doc8

A sample output is::

    Scanning...
    Validating...
    docs/source/misc/licence_policy_plugin.rst:37: D002 Trailing whitespace
    docs/source/misc/faq.rst:45: D003 Tabulation used for indentation
    docs/source/misc/faq.rst:9: D001 Line too long
    docs/source/misc/support.rst:6: D005 No newline at end of file
    ========
    Total files scanned = 34
    Total files ignored = 0
    Total accumulated errors = 326
    Detailed error counts:
        - CheckCarriageReturn = 0
        - CheckIndentationNoTab = 75
        - CheckMaxLineLength = 190
        - CheckNewlineEndOfFile = 13
        - CheckTrailingWhitespace = 47
        - CheckValidity = 1

Now fix the errors and run again till there isn't any style error in the documentation.


What is Checked?
^^^^^^^^^^^^^^^^

PyCQA is an Organization for code quality tools (and plugins) for the Python programming language.
Doc8 is a sub-project of the same Organization. Refer this
`README <https://github.com/PyCQA/doc8/blob/main/README.rst>`_ for more details.

What is checked:

    - invalid rst format - D000
    - lines should not be longer than 100 characters - D001

        - RST exception: line with no whitespace except in the beginning
        - RST exception: lines with http or https URLs
        - RST exception: literal blocks
        - RST exception: rst target directives

    - no trailing whitespace - D002
    - no tabulation for indentation - D003
    - no carriage returns (use UNIX newlines) - D004
    - no newline at end of file - D005


.. _doc_interspinx:

Interspinx
----------

AboutCode documentation uses
`Intersphinx <https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html>`_
to link to other Sphinx Documentations, to maintain links to other Aboutcode Projects.

To link sections in the same documentation, standart reST labels are used. Refer
`Cross-Referencing <https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html>`_
for more information.

For example::

    .. _my-reference-label:

    Section to cross-reference
    --------------------------

    This is the text of the section.

    It refers to the section itself, see :ref:`my-reference-label`.

Now, using Intersphinx, you can create these labels in one Sphinx Documentation and then referance
these labels from another Sphinx Documentation, hosted in different locations.

You just have to add the following in the ``conf.py`` file for your Sphinx Documentation, where you
want to add the links::

    extensions = [
    'sphinx.ext.intersphinx'
    ]

    intersphinx_mapping = {'aboutcode': ('https://aboutcode.readthedocs.io/en/latest/', None)}

To show all Intersphinx links and their targets of an Intersphinx mapping file, run::

    python -msphinx.ext.intersphinx https://aboutcode.readthedocs.io/en/latest/objects.inv

.. WARNING::

    ``python -msphinx.ext.intersphinx https://aboutcode.readthedocs.io/objects.inv`` will give
    error.

This enables you to create links to the ``aboutcode`` Documentation in your own Documentation,
where you modified the configuration file. Links can be added like this::

    For more details refer :ref:`aboutcode:doc_style_guide`.

You can also not use the ``aboutcode`` label assigned to all links from aboutcode.readthedocs.io,
if you don't have a label having the same name in your Sphinx Documentation. Example::

    For more details refer :ref:`doc_style_guide`.

If you have a label in your documentation which is also present in the documentation linked by
Intersphinx, and you link to that label, it will create a link to the local label.

For more information, refer this tutorial named
`Using Intersphinx <https://my-favorite-documentation-test.readthedocs.io/en/latest/using_intersphinx.html>`_.


.. _doc_style_conv:

Style Conventions for the Documentaion
--------------------------------------

1. Headings

    (`Refer <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#sections>`_)
    Normally, there are no heading levels assigned to certain characters as the structure is
    determined from the succession of headings. However, this convention is used in Python’s Style
    Guide for documenting which you may follow:

    # with overline, for parts

    * with overline, for chapters

    =, for sections

    -, for subsections

    ^, for sub-subsections

    ", for paragraphs

2. Heading Underlines

    Do not use underlines that are longer/shorter than the title headline itself. As in:

    ::

        Correct :

        Extra Style Checks
        ------------------

        Incorrect :

        Extra Style Checks
        ------------------------

.. note::

    Underlines shorter than the Title text generates Errors on sphinx-build.


3. Internal Links

    Using ``:ref:`` is advised over standard reStructuredText links to sections (like
    ```Section title`_``) because it works across files, when section headings are changed, will
    raise warnings if incorrect, and works for all builders that support cross-references.
    However, external links are created by using the standard ```Section title`_`` method.

4. Eliminate Redundancy

    If a section/file has to be repeated somewhere else, do not write the exact same section/file
    twice. Use ``.. include: ../README.rst`` instead. Here, ``../`` refers to the documentation
    root, so file location can be used accordingly. This enables us to link documents from other
    upstream folders.

5. Using ``:ref:`` only when necessary

    Use ``:ref:`` to create internal links only when needed, i.e. it is referenced somewhere.
    Do not create references for all the sections and then only reference some of them, because
    this created unnecessary references. This also generates ERROR in ``restructuredtext-lint``.

6. Spelling

    You should check for spelling errors before you push changes. `Aspell <http://aspell.net/>`_
    is a GNU project Command Line tool you can use for this purpose. Download and install Aspell,
    then execute ``aspell check <file-name>`` for all the files changed. Be careful about not
    changing commands or other stuff as Aspell gives prompts for a lot of them. Also delete the
    temporary ``.bak`` files generated. Refer the `manual <http://aspell.net/man-html/>`_ for more
    information on how to use.

7. Notes and Warning Snippets

    Every ``Note`` and ``Warning`` sections are to be kept in ``rst_snippets/note_snippets/`` and
    ``rst_snippets/warning_snippets/`` and then included to eliminate redundancy, as these are
    frequently used in multiple files.

8. Redirects

    If layouts of doc pages are being changed and these could be referenced elsewhere, these should
    be added in the `redirects` mapping in `conf.py`. For examples on using these see
    https://documatt.gitlab.io/sphinx-reredirects/usage.html

Converting from Markdown
------------------------

If you want to convert a ``.md`` file to a ``.rst`` file, this
`tool <https://github.com/chrissimpkins/md2rst>`_ does it pretty well.
You will still have to clean up and check for errors as this contains a lot of bugs. But this is
definitely better than converting everything by yourself.

This will be helpful in converting GitHub wiki's (Markdown Files) to reStructuredtext files for
Sphinx/ReadTheDocs hosting.

Automatic Docs Generation
-------------------------

It's possible to generate docs automatically from data by using a combination of:

- `shell scripts: example <https://github.com/aboutcode-org/scancode-toolkit/blob/develop/docs/scripts/regen_package_docs.sh>`_
- `python scripts: example <https://github.com/aboutcode-org/scancode-toolkit/blob/develop/src/packagedcode/regen_package_docs.py>`_
- `jinja templates: example <https://github.com/aboutcode-org/scancode-toolkit/blob/develop/src/packagedcode/templates/available_package_parsers.rst>`_

And we do this currently to keep a documentation page for all the supported package formats.
See :ref:`supported_packages` for details.
