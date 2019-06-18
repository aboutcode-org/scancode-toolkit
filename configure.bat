@echo OFF
@rem Copyright (c) nexB Inc. http://www.nexb.com/ - All rights reserved.

@rem ################################
@rem # Defaults. change these variables to customize this script locally
@rem ################################
@rem # you can define one or more thirdparty dirs, each prefixed with TPP_DIR
set TPP_DIR=thirdparty

set DEFAULT_PYTHON=python

@rem # default configurations for dev
set CONF_DEFAULT="etc/conf/dev"
@rem #################################

set CFG_ROOT_DIR=%~dp0

@rem Collect all command line arguments in a variable
@rem Use a trailing space in the next line to set the variable to an empty string
set CFG_CMD_LINE_ARGS=

@rem a possible alternative way and simpler way to slurp args
@rem set CFG_CMD_LINE_ARGS=%*

:collectarg
 if ""%1""=="""" goto continue
 call set CFG_CMD_LINE_ARGS=%CFG_CMD_LINE_ARGS% %1
 shift
 goto collectarg

:continue

@rem Set defaults when no args are passed
if "%CFG_CMD_LINE_ARGS%"=="" set CFG_CMD_LINE_ARGS="%CONF_DEFAULT%"
if "%PYTHON_EXE%"=="" set PYTHON_EXE=%DEFAULT_PYTHON%


call "%PYTHON_EXE%" "%CFG_ROOT_DIR%etc\configure.py" %CFG_CMD_LINE_ARGS%

@rem Return a proper return code on failure
if %errorlevel% neq 0 (
    exit /b %errorlevel%
)

@rem Activate the virtualenv
endlocal
if exist "%CFG_ROOT_DIR%bin\activate" (
    "%CFG_ROOT_DIR%bin\activate"
)
