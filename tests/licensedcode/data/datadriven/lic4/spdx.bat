@REM ## @file
@REM # Makefile
@REM #
@REM # Copyright (c) 2007 - 2018, Intel Corporation. All rights reserved.<BR>
@REM # SPDX-License-Identifier: BSD-2-Clause-Patent
@REM #

@echo off
setlocal
set TOOL_ERROR=0
SET NMAKE_COMMAND=%1
SHIFT

:loop
if "%1"=="" goto success


