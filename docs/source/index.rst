ScanCode-Toolkit Documentation
==============================

ScanCode Toolkit is a set of code scanning tools that detect the origin (copyrights), license
and vulnerabilities of code, packages and dependencies in a codebase.
It is the leading tool in scanning depth and accuracy, used by hundreds of software teams.
You can use ScanCode Toolkit as a command line tool or as a library.

ScanCode is part of the AboutCode community! Join our `friendly Slack <https://aboutcode-org.slack.com>`_  to ask questions,
share ideas or discuss your challenges with other members of our community.
If you want to ask questions or anything else that you think are not bugs/new
features, open a `discussion <https://github.com/aboutcode-org/scancode-toolkit/discussions>`_ with the ScanCode repository.

Documentation overview
~~~~~~~~~~~~~~~~~~~~~~

The overview below outlines how the documentation is structured
to help you know where to look for certain things.

.. rst-class:: clearfix row

.. rst-class:: column column2 top-left

:ref:`getting-started`
~~~~~~~~~~~~~~~~~~~~~~

Start here if you are new to ScanCode.

- :ref:`install-scancode`

 - :ref:`install-scancode-from-release-archives`
 - :ref:`install-scancode-using-docker`
 - :ref:`install-scancode-from-source`
 - :ref:`install-scancode-using-pip`

- :ref:`faq`


.. rst-class:: column column2 top-right

:ref:`tutorials`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Learn via practical step-by-step guides.

- :ref:`running-a-scan`
- :ref:`visualizing-scan-results`
- :ref:`configuring-scan-output-formats`
- :ref:`configuring-scan-detection`
- :ref:`adding-a-post-scan-plugin`

.. rst-class:: column column2 bottom-left

:ref:`how-to-guides`
~~~~~~~~~~~~~~~~~~~~

Helps you accomplish things.

- :ref:`how-to-add-new-license`
- :ref:`how-to-add-new-license-detection-rule`
- :ref:`how-to-install-new-license-plugin`
- :ref:`how-to-generate-attribution-docs`

.. rst-class:: column column2 bottom-right

:ref:`reference` and :ref:`explanation`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Consult the reference to find CLI parameters.

- :ref:`cli-scancode` options
- :ref:`plugins` to extend ScanCode at different stages
- :ref:`supported-packages`
- Rebuild the license index with the :ref:`cli-scancode-reindex-licenses`

Broaden your understanding using the explanation of ScanCode key concepts.

- Innerworkings of :ref:`scancode-license-detection`

.. rst-class:: row clearfix

Improving Documentation
~~~~~~~~~~~~~~~~~~~~~~~

.. include::  /rst-snippets/improve-docs.rst

.. toctree::
   :maxdepth: 2
   :hidden:

   getting-started/index
   tutorials/index
   how-to-guides/index
   reference/index
   explanation/index
