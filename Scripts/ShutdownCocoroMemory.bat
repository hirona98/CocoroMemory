@echo off
REM CocoroMemoryを安全に停止するスクリプト

echo CocoroMemoryを停止しています...

REM CocoroMemory.exeプロセスにSIGTERMシグナルを送信
taskkill /IM CocoroMemory.exe 2>nul

REM 5秒待機
timeout /t 5 /nobreak >nul

REM まだ実行中の場合は強制終了
taskkill /F /IM CocoroMemory.exe 2>nul

echo CocoroMemoryを停止しました。