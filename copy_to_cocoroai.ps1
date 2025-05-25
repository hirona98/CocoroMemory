# CocoroMemoryのビルド成果物をCocoroAIディレクトリにコピーするスクリプト

# スクリプトのパスを取得
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# パスの定義
$sourceDir = Join-Path $scriptPath "dist\CocoroMemory"
$targetDir = Join-Path (Split-Path -Parent $scriptPath) "CocoroAI\CocoroMemory"

# ソースディレクトリの存在確認
if (-not (Test-Path $sourceDir)) {
    Write-Host "エラー: ソースディレクトリが見つかりません: $sourceDir" -ForegroundColor Red
    Write-Host "先に build.ps1 を実行してビルドを完了させてください。" -ForegroundColor Yellow
    exit 1
}

# ターゲットディレクトリの確認
Write-Host "コピー先: $targetDir" -ForegroundColor Cyan

# ユーザーに確認
$confirmation = Read-Host "ターゲットディレクトリの中身を削除してからコピーします。続行しますか？ (y/N)"
if ($confirmation -ne 'y') {
    Write-Host "処理をキャンセルしました。" -ForegroundColor Yellow
    exit 0
}

# ターゲットディレクトリが存在する場合、中身を削除
if (Test-Path $targetDir) {
    Write-Host "ターゲットディレクトリの中身を削除中..." -ForegroundColor Yellow
    try {
        Get-ChildItem -Path $targetDir -Recurse | Remove-Item -Recurse -Force
        Write-Host "削除完了" -ForegroundColor Green
    }
    catch {
        Write-Host "エラー: ファイルの削除に失敗しました: $_" -ForegroundColor Red
        exit 1
    }
}
else {
    # ディレクトリが存在しない場合は作成
    Write-Host "ターゲットディレクトリを作成中..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
}

# ファイルをコピー
Write-Host "ファイルをコピー中..." -ForegroundColor Yellow
try {
    # robocopyを使用して高速にコピー
    $robocopyArgs = @(
        $sourceDir,
        $targetDir,
        "*.*",
        "/E",      # サブディレクトリを含む
        "/MIR",    # ミラーリング（余分なファイルも削除）
        "/R:3",    # リトライ回数
        "/W:10"    # リトライ待機時間（秒）
    )
    
    $result = robocopy @robocopyArgs
    
    # robocopyの終了コードを確認（0-7は成功）
    if ($LASTEXITCODE -ge 8) {
        throw "robocopyでエラーが発生しました（終了コード: $LASTEXITCODE）"
    }
    
    Write-Host "コピー完了！" -ForegroundColor Green
    
    # LICENSES.txtをコピー
    $licensesSource = Join-Path $scriptPath "LICENSES.txt"
    $licensesTarget = Join-Path $targetDir "LICENSES.txt"
    
    if (Test-Path $licensesSource) {
        Write-Host "LICENSES.txtをコピー中..." -ForegroundColor Yellow
        try {
            Copy-Item -Path $licensesSource -Destination $licensesTarget -Force
            Write-Host "LICENSES.txtのコピー完了" -ForegroundColor Green
        }
        catch {
            Write-Host "警告: LICENSES.txtのコピーに失敗しました: $_" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "警告: LICENSES.txtが見つかりません: $licensesSource" -ForegroundColor Yellow
    }
    
    Write-Host "コピー先: $targetDir" -ForegroundColor Cyan
}
catch {
    Write-Host "エラー: ファイルのコピーに失敗しました: $_" -ForegroundColor Red
    exit 1
}