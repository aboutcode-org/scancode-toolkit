@echo OFF
@rem Copyright (c) nexB Inc. http://www.nexb.com/ - All rights reserved.

@rem  A wrapper to ScanCode command line entry point

@rem Delayed expansion is required to allow the content of the variables to be manipulated prior to use
setlocal EnableDelayedExpansion

set SCANCODE_ROOT_DIR=%~dp0
set SCANCODE_CONFIGURED_PYTHON=%SCANCODE_ROOT_DIR%Scripts\python.exe

@rem Collect all command line arguments in a variable
@rem Use a trailing space in the next line sets the variable to an empty string (rather than unseting it)
set "SCANCODE_CMD_LINE_ARGS= "

:collectarg
@rem Capture the current argument value
	set CurrentParam=%1
    if ""%1""=="""" goto continue
	@rem Replace a % sign with an arbitrary placeholder sting
	@rem Note: the double percent sign (%%) is required to escape the percent sign.
	@rem The statement "set CurrentParam=!CurrentParam:%%=##PC##!" takes the value
	@rem of CurrentParam, replaces any percent signs with ##PC## and assigns it back to CurrentParam
	set CurrentParam=!CurrentParam:%%=##PC##!
    call set SCANCODE_CMD_LINE_ARGS=%SCANCODE_CMD_LINE_ARGS% %CurrentParam%
    shift
goto collectarg

:continue

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
set SCANCODE_CMD_LINE_ARGS=!SCANCODE_CMD_LINE_ARGS:##PC##=%%!
"%SCANCODE_ROOT_DIR%Scripts\scancode" %SCANCODE_CMD_LINE_ARGS%
