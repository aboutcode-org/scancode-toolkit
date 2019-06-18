@echo OFF
@rem Copyright (c) nexB Inc. http://www.nexb.com/ - All rights reserved.

@rem  A wrapper to the command line entry point

set SCANCODE_ROOT_DIR=%~dp0
set SCANCODE_CONFIGURED_PYTHON=%SCANCODE_ROOT_DIR%\Scripts\python.exe

@rem Collect all command line arguments in a variable
@rem Use a trailing space in the next line to set the variable to an empty string
set SCANCODE_CMD_LINE_ARGS=

@rem a possible alternative way and simpler way to slurp args
@rem set SCANCODE_CMD_LINE_ARGS=%*

:collectarg
 if ""%1""=="""" goto continue
 call set SCANCODE_CMD_LINE_ARGS=%SCANCODE_CMD_LINE_ARGS% %1
 shift
 goto collectarg

:continue

if not exist "%SCANCODE_CONFIGURED_PYTHON%" goto configure
goto scancode

:configure
echo * Configuring ScanCode for first use...
set CONFIGURE_QUIET=1
call "%SCANCODE_ROOT_DIR%\configure" etc/conf

@rem Return a proper return code on failure
if %errorlevel% neq 0 (
    exit /b %errorlevel%
)

:scancode
"%SCANCODE_ROOT_DIR%Scripts\scancode" %SCANCODE_CMD_LINE_ARGS%

