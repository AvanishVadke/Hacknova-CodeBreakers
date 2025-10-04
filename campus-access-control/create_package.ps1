# ====================================================================
# Enhanced Access Control - Package Creator Script
# ====================================================================
# This script automatically creates a deployment package with all
# necessary files for running the Enhanced_Access_Control notebook
# on another system.
# ====================================================================

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  Enhanced Access Control - Package Creator v1.0" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$SourceDir = Get-Location
$PackageName = "Enhanced_Access_Control_Package"
$PackageDir = Join-Path (Split-Path $SourceDir) $PackageName
$ZipName = "Enhanced_Access_Control_v1.0.zip"
$ZipPath = Join-Path (Split-Path $SourceDir) $ZipName

# Number of sample images to include
$SampleImageCount = 20

Write-Host "📂 Source Directory: $SourceDir" -ForegroundColor Green
Write-Host "📦 Package Directory: $PackageDir" -ForegroundColor Green
Write-Host "🗜️  ZIP File: $ZipPath" -ForegroundColor Green
Write-Host ""

# Step 1: Clean up existing package
Write-Host "[1/7] Cleaning up previous package..." -ForegroundColor Yellow
if (Test-Path $PackageDir) {
    Remove-Item $PackageDir -Recurse -Force
    Write-Host "      ✅ Previous package removed" -ForegroundColor Green
}
if (Test-Path $ZipPath) {
    Remove-Item $ZipPath -Force
    Write-Host "      ✅ Previous ZIP removed" -ForegroundColor Green
}

# Step 2: Create package directory
Write-Host ""
Write-Host "[2/7] Creating package directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $PackageDir -Force | Out-Null
Write-Host "      ✅ Directory created" -ForegroundColor Green

# Step 3: Copy main files
Write-Host ""
Write-Host "[3/7] Copying main files..." -ForegroundColor Yellow

$MainFiles = @(
    "Enhanced_Access_Control.ipynb",
    "requirements_notebook.txt",
    ".env.example"
)

foreach ($file in $MainFiles) {
    if (Test-Path $file) {
        Copy-Item $file $PackageDir
        $size = (Get-Item $file).Length
        Write-Host "      ✅ $file ($([math]::Round($size/1KB, 2)) KB)" -ForegroundColor Green
    } else {
        Write-Host "      ⚠️  $file not found - SKIPPING" -ForegroundColor Red
    }
}

# Step 4: Copy documentation
Write-Host ""
Write-Host "[4/7] Copying documentation..." -ForegroundColor Yellow

# Copy README as main README.md
if (Test-Path "README_PACKAGE.md") {
    Copy-Item "README_PACKAGE.md" (Join-Path $PackageDir "README.md")
    Write-Host "      ✅ README.md (from README_PACKAGE.md)" -ForegroundColor Green
}

$DocFiles = @(
    "DEPLOYMENT_PACKAGE_GUIDE.md",
    "INSTALLATION_INSTRUCTIONS.md",
    "PRE_DEPLOYMENT_CHECKLIST.md",
    "FILES_TO_SEND.md"
)

foreach ($file in $DocFiles) {
    if (Test-Path $file) {
        Copy-Item $file $PackageDir
        $size = (Get-Item $file).Length
        Write-Host "      ✅ $file ($([math]::Round($size/1KB, 2)) KB)" -ForegroundColor Green
    } else {
        Write-Host "      ⚠️  $file not found - SKIPPING" -ForegroundColor Red
    }
}

# Step 5: Copy models folder
Write-Host ""
Write-Host "[5/7] Copying YOLO model..." -ForegroundColor Yellow

if (Test-Path "models") {
    Copy-Item "models" $PackageDir -Recurse
    
    $modelPath = Join-Path $PackageDir "models\best.pt"
    if (Test-Path $modelPath) {
        $modelSize = (Get-Item $modelPath).Length
        Write-Host "      ✅ models/best.pt ($([math]::Round($modelSize/1MB, 2)) MB)" -ForegroundColor Green
    } else {
        Write-Host "      ⚠️  models/best.pt not found!" -ForegroundColor Red
    }
} else {
    Write-Host "      ❌ models/ folder not found!" -ForegroundColor Red
}

# Step 6: Copy sample training data
Write-Host ""
Write-Host "[6/7] Copying sample training data..." -ForegroundColor Yellow

$TrainingDataSource = "data\training_data"
$TrainingDataDest = Join-Path $PackageDir "data\training_data"

if (Test-Path $TrainingDataSource) {
    New-Item -ItemType Directory -Path $TrainingDataDest -Force | Out-Null
    
    $images = Get-ChildItem $TrainingDataSource -Filter "*.jpg" | Select-Object -First $SampleImageCount
    
    $totalSize = 0
    foreach ($image in $images) {
        Copy-Item $image.FullName $TrainingDataDest
        $totalSize += $image.Length
    }
    
    Write-Host "      ✅ Copied $($images.Count) sample images ($([math]::Round($totalSize/1MB, 2)) MB)" -ForegroundColor Green
} else {
    Write-Host "      ⚠️  data/training_data/ not found - No sample images copied" -ForegroundColor Red
}

# Step 7: Create ZIP archive
Write-Host ""
Write-Host "[7/7] Creating ZIP archive..." -ForegroundColor Yellow

try {
    Compress-Archive -Path "$PackageDir\*" -DestinationPath $ZipPath -Force
    $zipSize = (Get-Item $ZipPath).Length
    Write-Host "      ✅ ZIP created: $ZipName ($([math]::Round($zipSize/1MB, 2)) MB)" -ForegroundColor Green
} catch {
    Write-Host "      ❌ Failed to create ZIP: $_" -ForegroundColor Red
}

# Summary
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  PACKAGE CREATION COMPLETE!" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# Calculate total size
if (Test-Path $PackageDir) {
    $folderSize = (Get-ChildItem $PackageDir -Recurse | Measure-Object -Property Length -Sum).Sum
    Write-Host "📦 Package Folder: $([math]::Round($folderSize/1MB, 2)) MB" -ForegroundColor Green
}

if (Test-Path $ZipPath) {
    $zipSize = (Get-Item $ZipPath).Length
    Write-Host "🗜️  ZIP File: $([math]::Round($zipSize/1MB, 2)) MB" -ForegroundColor Green
}

Write-Host ""
Write-Host "📋 Package Contents:" -ForegroundColor Yellow
Get-ChildItem $PackageDir -Recurse -File | ForEach-Object {
    $relativePath = $_.FullName.Substring($PackageDir.Length + 1)
    $size = if ($_.Length -gt 1MB) { "$([math]::Round($_.Length/1MB, 2)) MB" } else { "$([math]::Round($_.Length/1KB, 2)) KB" }
    Write-Host "   • $relativePath ($size)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "✅ Package Location: $PackageDir" -ForegroundColor Green
Write-Host "✅ ZIP File Location: $ZipPath" -ForegroundColor Green
Write-Host ""

# Verification checklist
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  VERIFICATION CHECKLIST" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

$checks = @(
    @{ Name = "Enhanced_Access_Control.ipynb"; Path = "Enhanced_Access_Control.ipynb" },
    @{ Name = "requirements_notebook.txt"; Path = "requirements_notebook.txt" },
    @{ Name = ".env.example"; Path = ".env.example" },
    @{ Name = "README.md"; Path = "README.md" },
    @{ Name = "models/best.pt"; Path = "models\best.pt" },
    @{ Name = "data/training_data/ (images)"; Path = "data\training_data" }
)

foreach ($check in $checks) {
    $fullPath = Join-Path $PackageDir $check.Path
    if (Test-Path $fullPath) {
        Write-Host "✅ $($check.Name)" -ForegroundColor Green
    } else {
        Write-Host "❌ $($check.Name) - MISSING!" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# Next steps
Write-Host "📝 Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Verify ZIP file extracts correctly:" -ForegroundColor Gray
Write-Host "   Expand-Archive -Path '$ZipName' -DestinationPath 'test_extract'" -ForegroundColor White
Write-Host ""
Write-Host "2. Review FILES_TO_SEND.md for delivery options" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Send the ZIP file to recipient with installation instructions" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Clean up package folder (optional):" -ForegroundColor Gray
Write-Host "   Remove-Item '$PackageName' -Recurse" -ForegroundColor White
Write-Host ""

Write-Host "🎉 Package is ready to send!" -ForegroundColor Green
Write-Host ""
