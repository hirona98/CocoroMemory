@echo off
setlocal

set PGROOT=%~dp0..\pgsql
set DATADIR=%~dp0..\Memory
set LOGDIR=%~dp0..\Logs

"%PGROOT%\bin\pg_ctl.exe" -D "%DATADIR%" -l "%LOGDIR%\postgres.log" -o "-p 5432 -k ." start

echo PostgreSQL Starting...
endlocal
