Write-Host "CocoroMemory ビルドを開始します..."

# 仮想環境を有効化
& .\.venv\Scripts\activate

# PyInstallerでパッケージングを実行
pyinstaller --clean CocoroMemory.spec


# データディレクトリの初期化スクリプトをコピー
if (-not (Test-Path "dist\CocoroMemory\Data")) {
    New-Item -Path "dist\CocoroMemory\Data" -ItemType Directory
}

if (-not (Test-Path "dist\CocoroMemory\Logs")) {
    New-Item -Path "dist\CocoroMemory\Logs" -ItemType Directory
}

# 仮想環境を無効化
deactivate

Write-Host ""
Write-Host "ビルドが完了しました！"
Write-Host "実行ファイルは dist\CocoroMemory フォルダにあります"
