# Interactive PowerShell helper: download dataset from Roboflow and then run training
# Usage: Open PowerShell in project root and run: .\scripts\download_dataset.ps1

Param()

Write-Host "This script will download a YOLOv8 dataset from Roboflow into data/ and then exit so you can run training."

$apiKey = Read-Host -Prompt "Roboflow API key (will not be stored)"
$workspace = Read-Host -Prompt "Roboflow workspace (e.g. jason-fml5e)"
$project = Read-Host -Prompt "Roboflow project (e.g. ceit-id-lace)"
$version = Read-Host -Prompt "Roboflow version (e.g. 1)"

if (-not $apiKey -or -not $workspace -or -not $project -or -not $version) {
    Write-Host "Missing required input. Aborting." -ForegroundColor Red
    exit 1
}

# set environment variables for this session
$env:ROBOFLOW_API_KEY = $apiKey
$env:ROBOFLOW_WORKSPACE = $workspace
$env:ROBOFLOW_PROJECT = $project
$env:ROBOFLOW_VERSION = $version

Write-Host "Environment variables set for this PowerShell session. Running dataset download..."

# Call the python helper to download dataset
python - <<'PY'
from scripts.download_dataset import download_dataset
from pathlib import Path
try:
    data_yaml = download_dataset(api_key=None, workspace=None, project=None, version=None)
    print(f"Downloaded dataset: {data_yaml}")
except Exception as e:
    print('Download failed:', e)
    raise
PY

Write-Host "Download step finished. If successful, run training with: python -m src.train --epochs 30 --batch 8" -ForegroundColor Green
