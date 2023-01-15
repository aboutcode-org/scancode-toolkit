@echo OFF
@setlocal

@rem Copyright (c) nexB Inc. and others. All rights reserved.
@rem SPDX-License-Identifier: Apache-2.0
@rem See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
@rem See https://github.com/nexB/ for support or download.
@rem See https://aboutcode.org for more information about nexB OSS projects.


@rem ################################
@rem # A configuration script to set things up:
@rem # create a virtualenv and install or update thirdparty packages.
@rem # Source this script for initial configuration
@rem # Use configure --help for details

@rem # NOTE: please keep in sync with POSIX script configure

@rem # This script will search for a virtualenv.pyz app in etc\thirdparty\virtualenv.pyz
@rem # Otherwise it will download the latest from the VIRTUALENV_PYZ_URL default
@rem ################################


@rem ################################
@rem # Defaults. Change these variables to customize this script
@rem ################################

@rem # Requirement arguments passed to pip and used by default or with --dev.
set "REQUIREMENTS=--editable . --constraint requirements.txt"
set "DEV_REQUIREMENTS=--editable .[testing] --constraint requirements.txt --constraint requirements-dev.txt"
set "DOCS_REQUIREMENTS=--editable .[docs] --constraint requirements.txt"

@rem # where we create a virtualenv
set "VIRTUALENV_DIR=venv"

@rem # Cleanable files and directories to delete with the --clean option
set "CLEANABLE=build dist venv .cache .eggs"

@rem # extra  arguments passed to pip
set "PIP_EXTRA_ARGS= "

@rem # the URL to download virtualenv.pyz if needed
set VIRTUALENV_PYZ_URL=https://bootstrap.pypa.io/virtualenv.pyz
@rem ################################


@rem ################################
@rem # Current directory where this script lives
set CFG_ROOT_DIR=%~dp0
set "CFG_BIN_DIR=%CFG_ROOT_DIR%\%VIRTUALENV_DIR%\Scripts"


@rem ################################
@rem # Thirdparty package locations and index handling
@rem # Find packages from the local thirdparty directory
if exist "%CFG_ROOT_DIR%\thirdparty" (
    set PIP_EXTRA_ARGS=--find-links "%CFG_ROOT_DIR%\thirdparty"
)


@rem ################################
@rem # Set the quiet flag to empty if not defined
if not defined CFG_QUIET (
    set "CFG_QUIET= "
)


@rem ################################
@rem # Main command line entry point
set "CFG_REQUIREMENTS=%REQUIREMENTS%"

:again
if not "%1" == "" (
    if "%1" EQU "--help"   (goto cli_help)
    if "%1" EQU "--clean"  (goto clean)
    if "%1" EQU "--dev"    (
        set "CFG_REQUIREMENTS=%DEV_REQUIREMENTS%"
    )
    if "%1" EQU "--docs"    (
        set "CFG_REQUIREMENTS=%DOCS_REQUIREMENTS%"
    )
    shift
    goto again
)

set "PIP_EXTRA_ARGS=%PIP_EXTRA_ARGS%"


@rem ################################
@rem # Find a proper Python to run
@rem # Use environment variables or a file if available.
@rem # Otherwise the latest Python by default.
if not defined PYTHON_EXECUTABLE (
    @rem # check for a file named PYTHON_EXECUTABLE
    if exist "%CFG_ROOT_DIR%\PYTHON_EXECUTABLE" (
        set /p PYTHON_EXECUTABLE=<"%CFG_ROOT_DIR%\PYTHON_EXECUTABLE"
    ) else (
        set "PYTHON_EXECUTABLE=py"
    )
)


@rem ################################
:create_virtualenv
@rem # create a virtualenv for Python
@rem # Note: we do not use the bundled Python 3 "venv" because its behavior and
@rem # presence is not consistent across Linux distro and sometimes pip is not
@rem # included either by default. The virtualenv.pyz app cures all these issues.

if not exist "%CFG_BIN_DIR%\python.exe" (
    if not exist "%CFG_BIN_DIR%" (
        mkdir "%CFG_BIN_DIR%"
    )

    if exist "%CFG_ROOT_DIR%\etc\thirdparty\virtualenv.pyz" (
        %PYTHON_EXECUTABLE% "%CFG_ROOT_DIR%\etc\thirdparty\virtualenv.pyz" ^
            --wheel embed --pip embed --setuptools embed ^
            --seeder pip ^
            --never-download ^
            --no-periodic-update ^
            --no-vcs-ignore ^
            %CFG_QUIET% ^
            "%CFG_ROOT_DIR%\%VIRTUALENV_DIR%"
    ) else (
        if not exist "%CFG_ROOT_DIR%\%VIRTUALENV_DIR%\virtualenv.pyz" (
            curl -o "%CFG_ROOT_DIR%\%VIRTUALENV_DIR%\virtualenv.pyz" %VIRTUALENV_PYZ_URL%

            if %ERRORLEVEL% neq 0 (
                exit /b %ERRORLEVEL%
            )
        )
        %PYTHON_EXECUTABLE% "%CFG_ROOT_DIR%\%VIRTUALENV_DIR%\virtualenv.pyz" ^
            --wheel embed --pip embed --setuptools embed ^
            --seeder pip ^
            --never-download ^
            --no-periodic-update ^
            --no-vcs-ignore ^
            %CFG_QUIET% ^
            "%CFG_ROOT_DIR%\%VIRTUALENV_DIR%"
    )
)

if %ERRORLEVEL% neq 0 (
    exit /b %ERRORLEVEL%
)


@rem ################################
:install_packages
@rem # install requirements in virtualenv
@rem # note: --no-build-isolation means that pip/wheel/setuptools will not
@rem # be reinstalled a second time and reused from the virtualenv and this
@rem # speeds up the installation.
@rem # We always have the PEP517 build dependencies installed already.

"%CFG_BIN_DIR%\pip" install ^
    --upgrade ^
    --no-build-isolation ^
    %CFG_QUIET% ^
    %PIP_EXTRA_ARGS% ^
    %CFG_REQUIREMENTS%


@rem ################################
:create_bin_junction
@rem # Create junction to bin to have the same directory between linux and windows
if exist "%CFG_ROOT_DIR%\%VIRTUALENV_DIR%\bin" (
    rmdir /s /q "%CFG_ROOT_DIR%\%VIRTUALENV_DIR%\bin"
)
mklink /J "%CFG_ROOT_DIR%\%VIRTUALENV_DIR%\bin" "%CFG_ROOT_DIR%\%VIRTUALENV_DIR%\Scripts"

if %ERRORLEVEL% neq 0 (
    exit /b %ERRORLEVEL%
)

exit /b 0


@rem ################################
:cli_help
    echo An initial configuration script
    echo "  usage: configure [options]"
    echo " "
    echo The default is to configure for regular use. Use --dev for development.
    echo " "
    echo The options are:
    echo " --clean: clean built and installed files and exit."
    echo " --dev:   configure the environment for development."
    echo " --help:  display this help message and exit."
    echo " "
    echo By default, the python interpreter version found in the path is used.
    echo Alternatively, the PYTHON_EXECUTABLE environment variable can be set to
    echo configure another Python executable interpreter to use. If this is not
    echo set, a file named PYTHON_EXECUTABLE containing a single line with the
    echo path of the Python executable to use will be checked last.
    exit /b 0


@rem ################################
:clean
@rem # Remove cleanable file and directories and files from the root dir.
echo "* Cleaning ..."
for %%F in (%CLEANABLE%) do (
    rmdir /s /q "%CFG_ROOT_DIR%\%%F" >nul 2>&1
    del /f /q "%CFG_ROOT_DIR%\%%F" >nul 2>&1
)
exit /b 0
