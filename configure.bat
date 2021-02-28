@echo OFF
@setlocal

@rem Copyright (c) nexB Inc. and others. All rights reserved.
@rem SPDX-License-Identifier: Apache-2.0
@rem See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
@rem ScanCode is a trademark of nexB Inc.
@rem See https://github.com/nexB/scancode-toolkit for support or download.
@rem See https://aboutcode.org for more information about nexB OSS projects.

@rem ################################
@rem # A configuration script to set things up: create a virtualenv and install
@rem # update thirdparty packages
goto config
:cli_help
    echo An initial configuration script
    echo "  usage: configure [options]"
    echo.
    echo The default is to configure for regular use.
    echo The script will attempt to find a suitable Python executable.
    echo Set the PYTHON_EXECUTABLE environment variable to provide your own
    echo Python executable path.
    echo.
    echo The options are:
    echo  "--clean: clean built and installed files and exit."
    echo  "--dev:   configure the environment for development."
    echo  "--help:  display these help messages and exit."
    echo.
    endlocal
    exit /b 0


:config
@rem ################################
@rem # Defaults. Change these variables to customize this script locally
@rem ################################

@rem # thirdparty package locations
set "THIRDPARTY_DIR=thirdparty"
set "THIRDPARTY_LINKS=https://thirdparty.aboutcode.org/pypi"

@rem # requirements used by defaults and with --dev
set "REQUIREMENTS=--editable . --constraint requirements.txt"
set "DEV_REQUIREMENTS=--editable .[dev] --constraint requirements.txt --constraint requirements-dev.txt"

@rem # default supported Python version
if not defined CONFIGURE_SUPPORTED_PYTHON (
    set CONFIGURE_SUPPORTED_PYTHON=3.6
)

@rem #################################

@rem Current directory where this script lives
set PROJECT_ROOT_DIR=%~dp0


@rem parse command line options
set CLI_ARGS="%REQUIREMENTS%"
set CONFIGURE_DEV_MODE=0
if "%1" EQU "--help"   (goto cli_help)
if "%1" EQU "--clean"  (set CLI_ARGS=--clean)
if "%1" EQU "--dev"    (
    set CLI_ARGS=%DEV_REQUIREMENTS%
    set CONFIGURE_DEV_MODE=1
)


@rem find a proper Python to run
if defined CONFIGURE_PYTHON_EXECUTABLE (
    if exist "%CONFIGURE_PYTHON_EXECUTABLE%" (
        goto run
    )
)

:find_python

@rem Check the existence of the "py" launcher available in Python 3
@rem If we have it, check if we have a py -3 installed with the required version
@rem Try to use a Python in the path if all else fail

where py >nul 2>nul
if %ERRORLEVEL% == 0 (
    @rem we have a py launcher, check for the availability of our Python 3 version
    set CONFIGURE_PYTHON_EXECUTABLE=py -%CONFIGURE_SUPPORTED_PYTHON%%
    %CONFIGURE_PYTHON_EXECUTABLE% --version >nul 2>nul
    if %ERRORLEVEL% neq 0 (
        echo "* Unable to find a suitable installation of Python %CONFIGURE_SUPPORTED_PYTHON%."
        exit /b 1
    )
) else (
    echo "* Unable to find a suitable installation of Python %CONFIGURE_SUPPORTED_PYTHON%."
    exit /b 1
)

:run
@rem ################################

@rem # Setup development mode

if "%CONFIGURE_DEV_MODE%" == 1 (
    @rem # Add development tag file to auto-regen license index on file changes
    echo. 2>%%PROJECT_ROOT_DIR%\SCANCODE_DEV_MODE"
)

@rem # Run configure scripts proper and activate

@rem without this there are some heisenbugs on Windows 10
@rem but this make scancode run slower
set PYTHONDONTWRITEBYTECODE=1


call %CONFIGURE_PYTHON_EXECUTABLE% "%PROJECT_ROOT_DIR%etc\configure.py" %CLI_ARGS%

@rem Return a proper return code on failure
if %ERRORLEVEL% neq 0 (
    exit /b %ERRORLEVEL%
)

endlocal

@rem # Activate the virtualenv if it exists
if exist "%PROJECT_ROOT_DIR%Scripts\activate" (
    "%PROJECT_ROOT_DIR%Scripts\activate"
)
exit /b 0
