@echo OFF

@rem Copyright (c) 2018 nexB Inc. http://www.nexb.com/ - All rights reserved.

@rem ################################
@rem # change these variables to customize this script locally
@rem ################################
@rem # you can define one or more thirdparty dirs, each prefixed with TPP_DIR
set TPP_DIR=thirdparty

@rem # default configurations for dev
set CONF_DEFAULT="etc/conf/dev"
@rem #################################

set SCANCODE_ROOT_DIR=%~dp0
@rem !!!!!!!!!!! ATTENTION !!!!!
@rem there is a space at the end of the set SCANCODE_CLI_ARGS=  line ... 
@rem NEVER remove this!
@rem otherwise, this script and scancode do not work.  
set SCANCODE_CLI_ARGS= 
@rem Collect/Slurp all command line arguments in a variable
:collectarg
 if ""%1""=="""" (
    goto continue
 )
 call set SCANCODE_CLI_ARGS=%SCANCODE_CLI_ARGS% %1
 shift
 goto collectarg

:continue

@rem default to dev configuration when no args are passed
if "%SCANCODE_CLI_ARGS%"==" " (
    set SCANCODE_CLI_ARGS="%CONF_DEFAULT%"
    goto configure
)

:configure
if not exist "c:\python3.6.1\python.exe" (
    echo(
    echo On Windows, ScanCode requires Python 3.6.x 32 bits to be installed first.
    echo(
    echo Please download and install Python 3.6 ^(Windows x86 MSI installer^) version 3.6.1
    echo Install Python on the c: drive and use all default installer options.
    echo Do NOT install Python v2 or any 64 bits edition.
    echo Instead download Python from this url and see the README.rst file for more details:
    echo(
    echo    https://www.python.org/ftp/python/3.6.1/python-3.6.1.exe
    echo(
    exit /b 1
)

call c:\python36\python.exe "%SCANCODE_ROOT_DIR%etc\configure.py" %SCANCODE_CLI_ARGS%
if %errorlevel% neq 0 (
    exit /b %errorlevel%
)
if exist "%SCANCODE_ROOT_DIR%bin\activate" (
    "%SCANCODE_ROOT_DIR%bin\activate"
)
goto EOS

:EOS
