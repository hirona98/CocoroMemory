Write-Host "CocoroMemory ビルドを開始します..."

# 仮想環境を有効化
& .\.venv\Scripts\activate

$src = "src/main.py"
$spec = "CocoroMemory.spec"
$datasEntry = "        ('pgsql/bin/*', 'pgsql/bin'),"

# specファイルがなければエラー
if (-not (Test-Path $spec)) {
    Write-Host "Error: $spec ファイルが見つかりません。" -ForegroundColor Red
    Write-Host "最初に手動でspecファイルを作成する必要があります。" -ForegroundColor Red
    exit 1
}

# PyInstallerでパッケージングを実行（-yで確認プロンプトをスキップ）
pyinstaller --clean -y $spec

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
