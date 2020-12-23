@echo OFF
@setlocal
@rem Copyright (c) nexB Inc. http://www.nexb.com/ - All rights reserved.

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

@rem # thirdparty packages directory
set "THIRDPARTY_LOC=thirdparty"

@rem # requirements used by defaults and with --dev
set "REQUIREMENTS=--editable .[full] --constraint requirements.txt"
set "DEV_REQUIREMENTS=--editable .[full] --requirement requirements-dev.txt --constraint requirements.txt"

@rem # default supported Python version 
set SUPPORTED_PYTHON=3.6

@rem #################################

@rem Current directory where this script lives
set PROJECT_ROOT_DIR=%~dp0

@rem parse command line options
set CLI_ARGS="%REQUIREMENTS%"
set PYTHON_EXECUTABLE=
:
collectopts
    if "%1" EQU "--help"   (goto cli_help)
    if "%1" EQU "--clean"  (set CLI_ARGS=--clean) && goto find_python
    if "%1" EQU "--dev"    (set CLI_ARGS=%DEV_REQUIREMENTS%) && goto collectopts


@rem find a proper Python to run

if exist ""%PYTHON_EXECUTABLE%"" (
    goto run
)

:find_python

@rem Check the existence of the "py" launcher available in Python 3
@rem If we have it, check if we have a py -3 installed with the required version
@rem Exits if all fails

where py >nul 2>nul
if %ERRORLEVEL% == 0 (
    @rem we have a py launcher, check for the availability of our Python 3 version
    py -%SUPPORTED_PYTHON% --version >nul 2>nul
    if %ERRORLEVEL% == 0 (
        set PYTHON_EXECUTABLE=py -%SUPPORTED_PYTHON%
    ) else (
        @rem we have py and no python 3, exit
        echo * Unable to find an installation of Python.
        exit /b 1
    )
) else (
    @rem we use a Python in the path as the last resort
    set PYTHON_EXECUTABLE=python
)

@rem ################################
@rem # setup development and run configure scripts
:run

if ""%CLI_ARGS%""==""%DEV_REQUIREMENTS%"" (
    @rem # Add development tag file for license index auto-regeneration on file changes
    echo. 2>SCANCODE_DEV_MODE
)

@rem without this there are some heisenbugs on Windows 10
@rem but this make scancode run a little bit slower
set PYTHONDONTWRITEBYTECODE=1


call %PYTHON_EXECUTABLE% "%PROJECT_ROOT_DIR%etc\configure.py" %CLI_ARGS%

@rem Return a proper return code on failure
if %ERRORLEVEL% neq 0 (
    exit /b %ERRORLEVEL%
)

endlocal

@rem # Activate the virtualenv
if exist "%PROJECT_ROOT_DIR%Scripts\activate" (
    "%PROJECT_ROOT_DIR%Scripts\activate"
)
exit /b 0
