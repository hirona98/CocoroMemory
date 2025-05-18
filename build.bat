@echo off
echo CocoroMemory ビルドを開始します...

:: 仮想環境を有効化
call .venv\Scripts\activate

:: PyInstallerでパッケージングを実行
pyinstaller --clean CocoroMemory.spec

echo ビルドが完了しました！
echo 実行ファイルは dist\CocoroMemory フォルダにあります

:: データディレクトリの初期化スクリプトをコピー
if not exist "dist\CocoroMemory\Data" (
    mkdir "dist\CocoroMemory\Data"
)

if not exist "dist\CocoroMemory\Logs" (
    mkdir "dist\CocoroMemory\Logs"
)

:: 仮想環境を無効化
deactivate

pause
