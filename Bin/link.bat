::link == 1
@echo off
if "%1"=="" (
    set "mode="
) else (
    call set "mode=%*"
)
::
::
::
::----



::----
::
::
::
call "%EXE%" %mode%