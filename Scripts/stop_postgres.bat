@echo off
setlocal

set PGROOT=%~dp0..\pgsql
set DATADIR=%~dp0..\Data

"%PGROOT%\bin\pg_ctl.exe" -D "%DATADIR%" stop

echo PostgreSQL Stopped.
endlocal
