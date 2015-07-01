@rem build_w32vc.bat
@echo off

rem This file builds and tests CCCC under Microsoft Visual Studio.
rem Path to Microsoft Visual Studio standard edition release 6.0
set VCDIR=c:\Program Files\Microsoft Visual Studio\vc98
if not exist "%VCDIR%\bin\vcvars32.bat" goto no_vc

call "%VCDIR%\bin\vcvars32.bat"
if not exist pccts\bin mkdir pccts\bin

cd pccts\dlg
if exist *.obj del *.obj
nmake -f DlgMS.mak
copy dlg.exe ..\bin
cd ..\..

cd pccts\antlr
if exist *.obj del *.obj
nmake -f AntlrMS.mak
copy antlr.exe ..\bin
cd ..\..

cd cccc
if exist *.obj del *.obj
if exist *.cpp del *.cpp
nmake -f w32vc.mak
cd ..

cd test
nmake -f w32vc.mak
cd ..

cd vcaddin
nmake -f CcccDevStudioAddIn.mak CFG="CcccDevStudioAddIn - Win32 Release"
cd ..


goto end

:no_vc
echo This script expects MS Visual C++ to be in %VCDIR%
echo Please modify the script if the location is different.



:end





