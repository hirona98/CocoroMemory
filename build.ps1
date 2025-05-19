Write-Host "CocoroMemory ビルドを開始します..."

# 仮想環境を有効化
& .\.venv\Scripts\activate

$src = "src/main.py"
$spec = "CocoroMemory.spec"
$datasEntry = "        ('pgsql/bin/*', 'pgsql/bin'),"

# specファイルがなければ生成
if (-not (Test-Path $spec)) {
    pyinstaller --name CocoroMemory $src --onefile --noconfirm
}

# datas に pgsql/bin を追加（重複しない場合のみ）
$specContent = Get-Content $spec
if ($specContent -notmatch "pgsql/bin") {
    $newSpec = @()
    $inAnalysis = $false
    foreach ($line in $specContent) {
        $newSpec += $line
        if ($line -match '^a = Analysis') {
            $inAnalysis = $true
        }
        if ($inAnalysis -and $line -match 'datas=\[') {
            $newSpec += $datasEntry
            $inAnalysis = $false
        }
    }
    $newSpec | Set-Content $spec -Encoding UTF8
}

# PyInstallerでパッケージングを実行
pyinstaller --clean $spec

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
