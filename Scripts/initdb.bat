@echo off
setlocal

set PGROOT=%~dp0..\pgsql
set DATADIR=%~dp0..\Data
set LOGDIR=%~dp0..\Logs
set PWFILE=%~dp0pg_pw.txt

REM Data, Logs フォルダ作成（既にあってもOK）
mkdir "%DATADIR%" 2>nul
mkdir "%LOGDIR%" 2>nul

REM initdb 実行（既に初期化済みならエラーになるので注意）
"%PGROOT%\bin\initdb.exe" -D "%DATADIR%" -U postgres -A password --pwfile="%PWFILE%" -E UTF8 --locale=C

echo Init Finish

REM PostgreSQLを起動
"%PGROOT%\bin\pg_ctl.exe" start -D "%DATADIR%" -l "%LOGDIR%\postgresql.log"

REM 起動完了まで少し待つ（環境により調整してください）
timeout /t 3 >nul

REM pg_pw.txt からパスワード読み込み
set /p PGPASSWORD=<"%PWFILE%"

REM vector拡張を有効化
"%PGROOT%\bin\psql.exe" -U postgres -d postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"

REM PostgreSQLを停止
"%PGROOT%\bin\pg_ctl.exe" stop -D "%DATADIR%" -m fast

REM 環境変数クリア
set PGPASSWORD=

endlocal
