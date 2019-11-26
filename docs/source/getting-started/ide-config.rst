.. _ide_config:

IDE Configuration
=================

The instructions below assume that you followed the :ref:`contrib_code_dev` including a python
virtualenv.

PyCharm
-------

Open the settings dialog and navigate to "Project Interpreter". Click on the gear button in the
upper left corner and select "Add Local". Find the python binary in the virtualenv
(``bin/python`` in the repository root) and confirm. Open a file that contains tests and set a
breakpoint. Right click in the test and select "Debug <name of test>". Afterwards you can re-run
the same test in the debugger using the appropriate keyboard shortcut (e.g. Shift-F9, depending
on platform and configured layout).

Visual Studio Code
------------------

Install the `Python extension from Microsoft <https://marketplace.visualstudio.com/items?itemName=ms-python.python>`_.

The ``configure`` script should have created a VSCode workspace directory with a basic
``settings.json``. To do this manually, add to or create the workspace settings file
``.vscode/settings.json``::

    "python.pythonPath": "${workspaceRoot}/bin/python",
    "python.unitTest.pyTestEnabled": true

If you created the file, also add ``{`` and ``}`` on the first and last line respectively.

When you open the project root folder in VSCode, the status bar should show the correct python
interpreter and, after a while, a "Run Tests" button. If not, try restarting VSCode.

Open a file that contains tests (e.g. ``tests/cluecode/test_copyrights.py``). Above the test
functions you should now see "Run Test" and "Debug Test". Set a breakpoint in a test function
and click on "Debug Test" above it. The debugger panel should show up on the left and show the
program state at the breakpoint. Stepping over and into code seems not to work. Clicking one of
those buttons just runs the test to completion. As a workaround, navigate to the function you want
to step into, set another breakpoint and click on "continue" instead.
