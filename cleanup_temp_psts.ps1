# Quick PST Temp Folder Cleanup
# Run this when disk space gets low

Write-Host ""
Write-Host "PST TEMP CLEANUP SCRIPT" -ForegroundColor Cyan
Write-Host "============================================================"

# Check current free space
$freespace = (Get-PSDrive C).Free / 1GB
$freespaceRounded = [math]::Round($freespace, 2)
Write-Host ""
Write-Host "Current free space: $freespaceRounded GB"

# Check temp folder
$tempFolder = "C:\Temp\PST_Extraction"
if (Test-Path $tempFolder) {
    $tempFiles = Get-ChildItem $tempFolder -Filter "*.pst"
    
    if ($tempFiles.Count -eq 0) {
        Write-Host ""
        Write-Host "No temp files to clean!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Press any key to exit..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit
    }
    
    $tempSize = ($tempFiles | Measure-Object -Property Length -Sum).Sum / 1GB
    $tempSizeRounded = [math]::Round($tempSize, 2)
    
    Write-Host "Temp PST files: $($tempFiles.Count) files ($tempSizeRounded GB)"
} else {
    Write-Host ""
    Write-Host "Temp folder does not exist!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

Write-Host ""
Write-Host "WARNING: This will:" -ForegroundColor Yellow
Write-Host "  1. Force close Outlook"
Write-Host "  2. Delete all PST files in temp folder"
Write-Host "  3. Free up approximately $tempSizeRounded GB"
Write-Host ""
Write-Host "Continue? (Y/N): " -ForegroundColor Yellow -NoNewline
$response = Read-Host

if ($response -ne "Y" -and $response -ne "y") {
    Write-Host ""
    Write-Host "Cancelled" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "Starting cleanup..." -ForegroundColor Cyan

# Step 1: Force close Outlook
Write-Host ""
Write-Host "Step 1: Closing Outlook..."
try {
    Stop-Process -Name "OUTLOOK" -Force -ErrorAction SilentlyContinue
    Write-Host "  Outlook closed" -ForegroundColor Green
    Start-Sleep -Seconds 3
} catch {
    Write-Host "  Outlook was not running" -ForegroundColor Gray
}

# Step 2: Delete temp PSTs
Write-Host ""
Write-Host "Step 2: Deleting temp PST files..."
try {
    Remove-Item "$tempFolder\*.pst" -Force -ErrorAction Stop
    Write-Host "  Temp files deleted!" -ForegroundColor Green
} catch {
    Write-Host "  Some files could not be deleted" -ForegroundColor Yellow
    Write-Host "  You may need to restart your computer" -ForegroundColor Yellow
}

# Step 3: Check results
Start-Sleep -Seconds 2
$newFreespace = (Get-PSDrive C).Free / 1GB
$newFreespaceRounded = [math]::Round($newFreespace, 2)
$freedUp = $newFreespace - $freespace
$freedUpRounded = [math]::Round($freedUp, 2)

Write-Host ""
Write-Host "============================================================"
Write-Host "CLEANUP RESULTS" -ForegroundColor Cyan
Write-Host "============================================================"
Write-Host "Free space before: $freespaceRounded GB"
Write-Host "Free space after:  $newFreespaceRounded GB"
Write-Host "Space freed:       $freedUpRounded GB" -ForegroundColor Green
Write-Host "============================================================"

Write-Host ""
Write-Host "Cleanup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "You can now continue the email extraction"
Write-Host "It will automatically resume from where it left off"
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")