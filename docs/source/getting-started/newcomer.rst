.. _new_to_scancode:

Are you new to ScanCode-Toolkit?
================================

This is the perfect place to start, if you are new to ScanCode-Toolkit. Have a quick look at the
table of contents below, as these are the main sections you might need help on. These sections
have extensive links to other important documentation pages, and make sure you go through them
all.

Table of Contents
-----------------

#. :ref:`newcomer_try_scancode`

    - :ref:`newcomer_before`
    - :ref:`newcomer_scan_codebase`
    - :ref:`newcomer_scancode_tips`
    - :ref:`newcomer_all_tutorials`
    - :ref:`newcomer_whats_new`

#. :ref:`newcomer_learn_scancode`

    - :ref:`newcomer_cli_ref`
    - :ref:`newcomer_explanations`
    - :ref:`newcomer_plugins`

#. :ref:`newcomer_contribute`

    - :ref:`newcomer_contribute_general_info`
    - :ref:`newcomer_code`
    - :ref:`newcomer_good_first_issue`
    - :ref:`newcomer_add_functionalirty`
    - :ref:`newcomer_update_docs`
    - :ref:`newcomer_gsoc_gsod`

----

.. _newcomer_try_scancode:

Try ScanCode-Toolkit
--------------------

This section is about using the ScanCode-Toolkit, i.e. Performing a scan on a codebase/files to
determine their license, copyrights and other information, according to your requirements.

#. The :ref:`newcomer_scan_codebase` section helps you with configuring your virtual environment,
   installing ScanCode and performing a basic scan, and subsequently visualize the results.

#. The :ref:`newcomer_scancode_tips` section helps you customize the scan according to your
   requirements, and better understand the advanced features you can use.

#. The :ref:`newcomer_all_tutorials` is essentially an exhaustive list of all Tutorials and How To's
   with a brief description on what they help you to achieve.

.. _newcomer_before:

Before you start using ScanCode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. You need to make sure :ref:`install_prerequisites` are installed. There
   are a few different ways to install ScanCode:

- :ref:`app_install` [Recommended for newcomers]
- :ref:`docker_install`
- :ref:`pip_install`
- :ref:`source_code_install`
- :ref:`fedora_install`


#. Run ``scancode -h`` to make sure ScanCode was installed properly.
   If this shows any Error, refer the `Common Installation Errors Issue <https://github.com/aboutcode-org/scancode-toolkit/issues/1837>`_
   for common errors.

.. note::

    Refer :ref:`synopsis_quickstart` to make sure you are using the scan command correctly.

.. note::

    For Windows, Refer to :ref:`windows_app_install` for installing easily using Releases.

.. _newcomer_scan_codebase:

Scan a Codebase
^^^^^^^^^^^^^^^

Once you are all set up with ScanCode-Toolkit, i.e. Running ``scancode -h`` shows the
:ref:`cli_help_text`, you can start scanning files or a codebase.

#. Refer :ref:`synopsis_quickstart` for commonly used scan commands, and commonly used
   :ref:`synopsis_output`. (The recommended output format is ``JSON``)

#. Refer :doc:`../rst_snippets/extract` for the use of ExtractCode.

#. :ref:`how_to_run_a_scan` is a sample tutorial for absolute beginners, to walk them through the
   process of running a scan. Follow this tutorial and perform a scan on the ``sample`` folder
   distributed with ScanCode, or any file/folder of your choice. Avoid advanced options, and just
   follow the basic instructions.

#. ScanCode generates output files with scan results. You can visualize ``JSON`` result files using
   `ScanCode Workbench <https://github.com/aboutcode-org/scancode-workbench>`_. Follow this tutorial :ref:`how_to_visualize_scan_results`
   to visualize the scan results.

.. _newcomer_scancode_tips:

Use ScanCode Better
^^^^^^^^^^^^^^^^^^^

#. Go through all the options in the page :ref:`cli_list_options`, to know about ScanCode Command
   Line options. You can then modify the Scan according to your requirements.

.. _newcomer_all_tutorials:

All Tutorials/How-Tos
^^^^^^^^^^^^^^^^^^^^^

The Tutorials are:

#. :ref:`how_to_run_a_scan`
#. :ref:`how_to_visualize_scan_results`
#. :ref:`how_to_set_what_scan_detects`
#. :ref:`how_to_extract_archives`
#. :ref:`how_to_specify_output_format`
#. :ref:`how_to_add_post_scan_plugin`

The How-To's are:

#. :ref:`add_new_license_for_det`
#. :ref:`add_new_license_det_rule`

.. _newcomer_whats_new:

ScanCode Versions
^^^^^^^^^^^^^^^^^

#. You can see all ScanCode-Toolkit versions on the `GitHub release page <https://github.com/aboutcode-org/scancode-toolkit/releases>`_.
#. Read the `CHANGELOG <https://github.com/aboutcode-org/scancode-toolkit/blob/develop/CHANGELOG.rst>`_ for more information on specific releases.
#. If you want to use/test a specific version of ScanCode-Toolkit, you can follow the instructions
   in :ref:`source_code_install` docs.

----

.. _newcomer_learn_scancode:

Learn more about ScanCode-Toolkit
---------------------------------

Here we give an introduction on the ScanCode-Toolkit Documentation Sections that can help you to
learn more about ScanCode-Toolkit.

.. _newcomer_cli_ref:

CLI Reference
^^^^^^^^^^^^^

This section contains a complete guide to ScanCode-Toolkit Command Line options, i.e. What the
command-line options are, how different options affect the scan and outputs, how to use these
options and examples of their use cases.

Now this section has three types of pages:

#. The :ref:`cli_synopsis` page and the :ref:`how_to_run_a_scan` page as summaries.
#. An exhaustive list of all Command Line Options at :ref:`cli_list_options`
#. All the other pages detailing the :ref:`scancode_cli_options`

Note that the page for one type of options also has a short list of all the options detailed on
that page in the beginning. The :ref:`cli_list_options` page just has all of them together, and
also the extractcode options.

.. _newcomer_explanations:

How ScanCode Works
^^^^^^^^^^^^^^^^^^

This section has documentation on :ref:`explain_how_scancode_works`.

.. _newcomer_plugins:

Plugins
^^^^^^^

Plugins are an integral part of ScanCode-Toolkit in the sense they are used to easily extend
ScanCode capabilities, and developers can code their own plugins according to their requirements.

This section has documentation on:

#. The :ref:`plugin_arch`
#. The :ref:`license_policy_plugin`
#. All :ref:`plugin_tutorials`

----

.. _newcomer_contribute:

Contribute
----------

If you are looking to Contribute to ScanCode-Toolkit, this is where you start.

.. _newcomer_contribute_general_info:

General Information
^^^^^^^^^^^^^^^^^^^

#. Also refer the `Contribution <https://github.com/aboutcode-org/scancode-toolkit/blob/develop/CONTRIBUTING.rst>`_ page here.
#. For more Project Ideas, refer :ref:`contributor_project_ideas`.
#. Before committing your work, make sure you have read this post on :ref:`good_commit_messages`.

.. _newcomer_code:

Contribute Code
^^^^^^^^^^^^^^^

If you haven't contributed to ScanCode-Toolkit refer :ref:`newcomer_good_first_issue`.

To determine where to contribute, you can refer:

#. ScanCode-Toolkit tracks issues via the `GitHub Issue tracker <https://github.com/aboutcode-org/scancode-toolkit/issues>`_
#. Broad `milestones <https://github.com/aboutcode-org/scancode-toolkit/milestones>`_ for upcoming versions are also maintained.

And documentation related to contributing code can be referred at :ref:`contrib_code_dev`.

.. _newcomer_good_first_issue:

Good First Issues
^^^^^^^^^^^^^^^^^

A `good first issue <https://github.com/aboutcode-org/scancode-toolkit/labels/good%20first%20issue>`_
means it's recommended for people who haven't contributed to ScanCode-Toolkit before.

.. _newcomer_add_functionalirty:

Add new Functionality/Enhancement to ScanCode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are two main paths you can follow to add a new functionality to ScanCode.
They are:

#. Add the functionality to ScanCode itself.
#. Add plugins if the functionality is very much application dependent.

Refer `enhancement issues <https://github.com/aboutcode-org/scancode-toolkit/labels/enhancement>`_ for the first type of
enhancements. If you want to add a plugin to implement the functionality, refer all the
:ref:`plugin_tutorials`.

.. _newcomer_update_docs:

Update our Documentation
^^^^^^^^^^^^^^^^^^^^^^^^

Maintaining a comprehensive, accurate, updated and effective documentation is very important
as that directly affects the acceptability of ScanCode-Toolkit.

To contribute to ScanCode-Toolkit Documentation, first refer the :ref:`contrib_doc_dev` section.

The sections in this page cover the following:

#. :ref:`contrib_doc_setup_local`
#. :ref:`contrib_doc_share_improvements`
#. :ref:`doc_ci` system for the Documentation
#. :ref:`doc_style_docs8`
#. :ref:`doc_interspinx`
#. :ref:`doc_style_conv`

You can contribute to the following Open Issues on documentation.

#. `First Timers Only Issues List <https://github.com/aboutcode-org/scancode-toolkit/issues/1826>`_
#. `Documentation Inconsistencies Tracker <https://github.com/aboutcode-org/scancode-toolkit/issues/1813>`_
#. `ScanCode-Toolkit Documentation Roadmap <https://github.com/aboutcode-org/scancode-toolkit/issues/1824>`_
#. `Issues with label Documentation <https://github.com/aboutcode-org/scancode-toolkit/issues?q=is%3Aopen+is%3Aissue+label%3Adocumentation>`_

.. note::

    Refer :ref:`improve_docs` to report Documentation Errors or to request Improvements.

Also, consider contributing to other Aboutcode Project Documentations, as they need more support.

.. _newcomer_gsoc_gsod:


Participate in GSoC/GSoD
^^^^^^^^^^^^^^^^^^^^^^^^

If you want to participate in any of the two programs:

- `Google Summer of Code <https://summerofcode.withgoogle.com>`_
- `Google Season of Docs <https://developers.google.com/season-of-docs>`_

Then:

#. Keep an eye out for Application Timelines.
#. Solve multiple of these :ref:`newcomer_good_first_issue` to demonstrate your skills,
   and improve your chances of selection.
#. Refer to the Projects Ideas List for details on tentative projects.

     - `GSoC2023 <https://github.com/nexB/aboutcode/wiki/GSOC-2023>`_

#. Remain active in Element and talk with the organization mentors well ahead of the deadlines.
#. Select projects according to your skills and finalize project proposals.
#. Discuss your proposals extensively with corresponding mentors.
#. Apply for the Programs well before the Deadline.
