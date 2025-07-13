@echo off
setlocal

set PGROOT=%~dp0..\pgsql
set DATADIR=%~dp0..\Memory

"%PGROOT%\bin\pg_ctl.exe" -D "%DATADIR%" stop

echo PostgreSQL Stopped.
endlocal
