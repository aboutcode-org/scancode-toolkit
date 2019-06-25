@echo OFF
setlocal
@rem Copyright (c) nexB Inc. http://www.nexb.com/ - All rights reserved.

@rem ################################
@rem # A configuration script for Windows
@rem # The possible options and arguments are:
@rem #  --clean : this is exclusive of anything else and cleans the environment
@rem #    from built and installed files
@rem #  <some conf path> : this must be the last argument and sets the path to a
@rem #    configuration directory to use.
@rem #  --python < path to python.exe> : this must be the first argument and set
@rem #    the path to the Python executable to use. If < path to python.exe> is
@rem #    set to "path", then the executable will be the python.exe available
@rem #    in the PATH.
@rem ################################

@rem ################################
@rem # Defaults. Change these variables to customize this script locally
@rem ################################
@rem # you can define one or more thirdparty dirs, each prefixed with TPP_DIR
set TPP_DIR=thirdparty

@rem # A fallback Python location.
@rem # To use a given interpreter, you should use the --python option with a
@rem # value pointing to your Python executable
set DEFAULT_PYTHON=C:\Python27\python.exe

@rem # default configurations for dev
set "CONF_DEFAULT=etc/conf/dev"
@rem #################################

set CFG_ROOT_DIR=%~dp0

set CONFIGURED_PYTHON=%CFG_ROOT_DIR%Scripts\python.exe

set "CFG_CMD_LINE_ARGS= "

python --version
python -c "import sys;print(sys.executable)"


@rem parse command line options and arguments 
if ""%1""=="""" (
    set CFG_CMD_LINE_ARGS=%CONF_DEFAULT%
    goto python
)

if ""%1""==""--clean"" (
    set CFG_CMD_LINE_ARGS=--clean
    goto python
)


if ""%1""==""--python"" (
    set PROVIDED_PYTHON=%2
    if ""%3""=="""" (
        set CFG_CMD_LINE_ARGS=%CONF_DEFAULT%
    ) else (
        set CFG_CMD_LINE_ARGS=%3
    )
    goto python
) else (
    set CFG_CMD_LINE_ARGS=%1
    goto python
)


@rem Pick a Python interpreter
:python

if exist "%CONFIGURED_PYTHON%" (
    if not ""%1""==""--clean"" (
        @rem we do not want to use the configured Python in clean... it will be deleted
        set PYTHON_EXECUTABLE=%CONFIGURED_PYTHON%
        goto run
    )
)

if ""%PROVIDED_PYTHON%""==""path"" (
    @rem use a bare python available in the PATH
    set PYTHON_EXECUTABLE=python
    goto run
)

if exist "%PROVIDED_PYTHON%" (
    set PYTHON_EXECUTABLE=%PROVIDED_PYTHON%
    goto run
)

if exist %DEFAULT_PYTHON% (
    set PYTHON_EXECUTABLE=%DEFAULT_PYTHON%
    goto run
)

if not exist "%PYTHON_EXECUTABLE%" (
    echo * Unable to find an installation of Python.
    exit /b 1
)

:run

call ""%PYTHON_EXECUTABLE%"" "%CFG_ROOT_DIR%etc\configure.py" %CFG_CMD_LINE_ARGS%

@rem Return a proper return code on failure
if %errorlevel% neq 0 (
    exit /b %errorlevel%
)

@rem Activate the virtualenv
endlocal
if exist "%CFG_ROOT_DIR%Scripts\activate" (
    "%CFG_ROOT_DIR%Scripts\activate"
)
