@echo OFF
@rem  Copyright (c) 2015 nexB Inc. http://www.nexb.com/ - All rights reserved.
@rem  


@rem  A minimal shell wrapper to the CLI entry point

set SCANCODE_ROOT_DIR=%~dp0

set SCANCODE_CMD_LINE_ARGS= 
set SCANCODE_CONFIGURED_PYTHON=%SCANCODE_ROOT_DIR%\bin\python.exe

@rem Collect all command line arguments in a variable
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
 if %errorlevel% neq 0 (
    exit /b %errorlevel%
 )

:scancode
"%SCANCODE_ROOT_DIR%\bin\extractcode" %SCANCODE_CMD_LINE_ARGS%

:EOS
