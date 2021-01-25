@echo OFF
@rem Copyright (c) nexB Inc. http://www.nexb.com/ - All rights reserved.

@rem  A wrapper to ScanCode command line entry point

set SCANCODE_ROOT_DIR=%~dp0
set SCANCODE_CONFIGURED_PYTHON=%SCANCODE_ROOT_DIR%Scripts\python.exe

if not exist "%SCANCODE_CONFIGURED_PYTHON%" goto configure
goto scancode

:configure
echo * Configuring ScanCode for first use...
echo * WARNING: Native Windows will be deprecated in the future in favor of Windows Subsystem for Linux
echo * WARNING: Please visit https://github.com/nexB/scancode-toolkit/issues/2366 for details and to provide feedback
set CONFIGURE_QUIET=1
call "%SCANCODE_ROOT_DIR%configure"

@rem Return a proper return code on failure
if %errorlevel% neq 0 (
    exit /b %errorlevel%
)

:scancode
@rem without this things may not always work on Windows 10, but this makes things slower
set PYTHONDONTWRITEBYTECODE=1

"%SCANCODE_ROOT_DIR%Scripts\scancode" %*
