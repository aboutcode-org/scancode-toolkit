@echo OFF
@rem Copyright (c) nexB Inc. http://www.nexb.com/ - All rights reserved.

@rem  A wrapper to ScanCode command line entry point

set SCANCODE_ROOT_DIR=%~dp0
set SCANCODE_CONFIGURED_PYTHON=%SCANCODE_ROOT_DIR%Scripts\python.exe

if not exist "%SCANCODE_CONFIGURED_PYTHON%" goto configure
goto scancode

:configure
echo * Configuring ScanCode for first use...
@rem FIXME: we did not set a given Python PATH
set CONFIGURE_QUIET=1
call "%SCANCODE_ROOT_DIR%configure" etc/conf

@rem Return a proper return code on failure
if %errorlevel% neq 0 (
    exit /b %errorlevel%
)

:scancode
@rem without this things may not always work on Windows 10, but this makes things slower
set PYTHONDONTWRITEBYTECODE=1

@rem Revert the placeholders back to single percent signs before passing through to ScanCode executable
echo "%SCANCODE_ROOT_DIR%Scripts\scancode %*" >> d:\ScanCode.txt
"%SCANCODE_ROOT_DIR%Scripts\scancode" %*
