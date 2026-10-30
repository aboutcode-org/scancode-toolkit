.. _install-scancode-from-source:

Install ScanCode from source
============================

You can download the source code of the ScanCode and build it locally.
This approach is recommended in the following scenarios:

- You are contributing to the development of ScanCode, adding new patches, or running tests.
- You need to test or run a specific version, checkpoint, or branch from the version control system.


Download ScanCode source code
-----------------------------

Run the following once you have `Git <https://git-scm.com/>`_ installed

.. code-block:: shell

    git clone https://github.com/aboutcode-org/scancode-toolkit.git
    cd scancode-toolkit


Configure the build
-------------------

ScanCode utilizes a configuration script to create an isolated virtual environment
and install the necessary package dependencies.

On Linux/Mac:

#. Open a terminal
#. Navigate to the clone directory using ``cd``
#. Run ``./configure``
#. Activate the virtual environment using ``source venv/bin/activate``

On Windows:

#. Open a command prompt
#. Navigate to the clone directory using ``cd``
#. Run ``configure``
#. Activate the virtual environment: ``venv\Scripts\activate``

Verify installation
-------------------

To verify that ScanCode has been installed correctly,
it is recommended to run the help command.


.. code-block:: shell

    scancode --help

 No errors? Congratulations! You are good to go to :ref:`running-a-scan`.

.. NOTE::

    For use in development, run instead ``configure --dev``. If your encounter
    issues while configuring a previous version, use ``configure --clean`` to
    clean and reset your enviroment. After that, run ``configure`` again.
