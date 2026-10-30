.. _install-scancode-from-release-archives:

Install ScanCode from releases archives
=======================================

Get the ScanCode-Toolkit tarball archive of a specific version and your
operating system by going to the `project releases page <https://github.com/aboutcode-org/scancode-toolkit/releases/>`_

.. _install-scancode-from-release-archives-linux:

Install ScanCode on Linux
-------------------------

Download the archive for your operating system and extract
the archive from command line::

    tar -xvf scancode-toolkit-30.0.1_py38-linux.tar.gz


Or, on Linux, right click and select "Extract Here".

Check whether the :ref:`install-scancode-required-packages` are installed. Open a terminal
in the extracted directory and run::

    ./scancode --help

This will configure ScanCode and display the command line :ref:`cli-help-text-options`.

If the command doesn't throw an error, congratulations! You are good to go to :ref:`running-a-scan`.

.. Note::

    ScanCode archives come with packaged with all required dependencies except
    for Python that has to be downloaded and installed separately.
    On more recent versions of Ubuntu, you will have to install Python 3.9 manually.
    One possibility is to use the Deadsnakes PPA (Personal Package Archive) which is
    a project that provides older Python version builds for Debian and Ubuntu and is
    available at https://github.com/deadsnakes/ and https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa
    ::

        sudo apt-get update && sudo apt-get upgrade
        sudo add-apt-repository ppa:deadsnakes/ppa --yes
        sudo apt-get install python3.9 python3.9-distutils

.. _install-scancode-from-release-archives-mac:

Install ScanCode on Mac
-----------------------

.. note::
   If you encounter a "No matching distribution" error while running the ``./configure`` command on a Mac M1, it may indicate compatibility issues with the current architecture. Here's a step-by-step guide to address this:

   - **Change Mac M1 Architecture to x86_64:**
     Switch the architecture from amd64 to x86_64 using the command:
     ::

         env /usr/bin/arch -x86_64 /bin/zsh --login
   - **Use Rosetta Translation:**
     Enable Rosetta translation in Terminal by executing:
     ::

         softwareupdate --install-rosetta
   - **Transition Homebrew from arm64 to Intel:**
     Change Homebrew from the arm64 architecture to the Intel (x86) architecture by running:
     ::

         /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
   - **Install Intel-Specific Python:**
     Use Homebrew to install Python specifically optimized for Intel architecture with:
     ::

         /usr/local/Homebrew/bin/brew install python3

   Then rerun the ``./configure`` command. This sets up the project according to the new architecture and ensures proper configuration.
   Following these steps should help resolve compatibility issues and allow smooth operation of the project on Mac M1 devices.

.. _install-scancode-from-release-archives-windows:

Install ScanCode on Windows 10/11
---------------------------------

- Download the latest ScanCode release zip file for Windows from the latest
  version at https://github.com/aboutcode-org/scancode-toolkit/releases/

- In the File Explorer, select the downloaded ScanCode zip and right-click.

- In the pop-up menu select 'Extract All...'

- In the pop-up window 'Extract Compressed (Zipped) Folders' use the default options to extract.

- Once the extraction is complete, a new File Explorer window will pop up.

- In this Explorer window, select the new folder that was created and right-click.

.. note::

  On Windows, double-click the new folder, select one of the files inside the folder
  (e.g., 'setup.py'), and right-click.

- In the pop-up menu select 'Properties'.

- In the pop-up window 'Properties', select the Location value. Copy this to the clipboard and
  close the 'Properties' window.

- Press the start menu button, click the search box or search icon in the taskbar.

- In the search box type::

    cmd

- Select 'cmd.exe' or 'Command Prompt' listed in the search results.

- A new 'Command Prompt'pops up.

- In this window (aka a 'command prompt'), type 'cd' followed by a space and
  then Right-click in this window and select Paste. This will paste the path you
  copied before and is where you extracted ScanCode::

    cd path\to\extracted\ScanCode

- Press Enter.

- This will change the current location of your command prompt to the root directory where
  ScanCode is installed.

- Then type::

    scancode -h

- Press enter. This first command will configure your ScanCode installation.
  Several messages are displayed followed by the ScanCode command help.

- The installation is complete. Congratulations!, you are good to go to :ref:`running-a-scan`.


Uninstall ScanCode
------------------

#. Delete the directory in which you extracted ScanCode.
#. Delete any temporary files created in your system temp and user temp directory
   under a ScanCode-prefixed directory such as .scancode-tk or .cache/scancode-tk.


.. note::

  The above installation process can be used with **Command Prompt**
  ``cmd``, and **PowerShell**. **Git Bash** is not tested and using it may
  introduce unexpected behavior. If you're using **Windows Subsystem for
  Linux** ``WSL2``, please refer to :ref:`install-scancode-from-release-archives-linux` section
  above.
