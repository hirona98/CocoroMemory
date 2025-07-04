Write-Host "Starting CocoroMemory build..."

# Activate virtual environment
& .\.venv\Scripts\activate

$src = "src/main.py"
$spec = "CocoroMemory.spec"
$datasEntry = "        ('pgsql/bin/*', 'pgsql/bin'),"

# Error if spec file doesn't exist
if (-not (Test-Path $spec)) {
    Write-Host "Error: $spec file not found." -ForegroundColor Red
    Write-Host "You need to create the spec file manually first." -ForegroundColor Red
    exit 1
}

# Run PyInstaller packaging (skip confirmation prompts with -y)
pyinstaller --clean -y $spec

# Copy data directory initialization script
if (-not (Test-Path "dist\CocoroMemory\Data")) {
    New-Item -Path "dist\CocoroMemory\Data" -ItemType Directory
}

if (-not (Test-Path "dist\CocoroMemory\Logs")) {
    New-Item -Path "dist\CocoroMemory\Logs" -ItemType Directory
}

# Deactivate virtual environment
deactivate

Write-Host ""
Write-Host "Build completed successfully!"
Write-Host "Executable file is located in the dist\CocoroMemory folder"
