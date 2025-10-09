# Delete EVERYTHING - Complete Fresh Start
# British English

Write-Host ""
Write-Host ("="*70) -ForegroundColor Red
Write-Host "COMPLETE FRESH START - DELETE ALL" -ForegroundColor Red
Write-Host ("="*70) -ForegroundColor Red

$tempFolder = "C:\Temp\PST_Extraction"
$outputFolder = "C:\Users\JemAndrew\OneDrive - Velitor\EmailExtraction"

Write-Host ""
Write-Host "WARNING: THIS DELETES EVERYTHING!" -ForegroundColor Red
Write-Host ""
Write-Host "This will DELETE:" -ForegroundColor Red
Write-Host "  - All temp PST files in C:\Temp\PST_Extraction" -ForegroundColor Red
Write-Host "  - Your checkpoint (10 PSTs completed)" -ForegroundColor Red
Write-Host "  - Extraction progress (14,126 emails extracted)" -ForegroundColor Red
Write-Host ""
Write-Host "After this, extraction will start from PST 1/32 (beginning)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Are you SURE? (Type YES to confirm): " -NoNewline -ForegroundColor Red
$response = Read-Host

if ($response -ne "YES") {
    Write-Host ""
    Write-Host "Cancelled - nothing deleted" -ForegroundColor Green
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

Write-Host ""
Write-Host "Starting complete cleanup..." -ForegroundColor Cyan

# Step 1: Delete temp PST files
if (Test-Path $tempFolder) {
    Write-Host ""
    Write-Host "Step 1: Deleting temp PST files..." -ForegroundColor Cyan
    
    $pstFiles = Get-ChildItem $tempFolder -Filter "*.pst" -ErrorAction SilentlyContinue
    if ($pstFiles) {
        $tempSize = ($pstFiles | Measure-Object -Property Length -Sum).Sum / 1GB
        $tempSizeRounded = [math]::Round($tempSize, 2)
        Write-Host "  Found: $($pstFiles.Count) PST files ($tempSizeRounded GB)"
        
        try {
            Remove-Item "$tempFolder\*.pst" -Force -ErrorAction Stop
            Write-Host "  Temp PST files deleted" -ForegroundColor Green
        } catch {
            Write-Host "  Could not delete some files: $($_.Exception.Message)" -ForegroundColor Yellow
            Write-Host "  Try closing Outlook first, then run this again" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  No PST files found in temp folder" -ForegroundColor Gray
    }
} else {
    Write-Host ""
    Write-Host "Step 1: Temp folder does not exist (skipped)" -ForegroundColor Gray
}

# Step 2: Delete checkpoint and all progress
Write-Host ""
Write-Host "Step 2: Deleting checkpoint and progress files..." -ForegroundColor Cyan

if (Test-Path $outputFolder) {
    $filesToDelete = @(
        "extraction_checkpoint.json",
        "seen_message_ids.json",
        "emails_extracted.json",
        "extraction_stats.json",
        "extraction_log.txt"
    )

    $deletedCount = 0
    foreach ($file in $filesToDelete) {
        $filePath = Join-Path $outputFolder $file
        if (Test-Path $filePath) {
            try {
                Remove-Item $filePath -Force
                Write-Host "  Deleted: $file" -ForegroundColor Green
                $deletedCount++
            } catch {
                Write-Host "  Could not delete: $file" -ForegroundColor Yellow
            }
        }
    }
    
    if ($deletedCount -eq 0) {
        Write-Host "  No progress files found (already clean)" -ForegroundColor Gray
    }
} else {
    Write-Host "  Output folder does not exist (will be created on first run)" -ForegroundColor Gray
}

# Step 3: Verify cleanup
Write-Host ""
Write-Host "Step 3: Verifying cleanup..." -ForegroundColor Cyan

$allClean = $true

# Check temp folder
if (Test-Path $tempFolder) {
    $remainingPSTs = Get-ChildItem $tempFolder -Filter "*.pst" -ErrorAction SilentlyContinue
    if ($remainingPSTs) {
        Write-Host "  Warning: $($remainingPSTs.Count) PST files still in temp" -ForegroundColor Yellow
        $allClean = $false
    } else {
        Write-Host "  Temp folder clean" -ForegroundColor Green
    }
}

# Check output folder
if (Test-Path $outputFolder) {
    $checkpointPath = Join-Path $outputFolder "extraction_checkpoint.json"
    if (Test-Path $checkpointPath) {
        Write-Host "  Warning: Checkpoint still exists" -ForegroundColor Yellow
        $allClean = $false
    } else {
        Write-Host "  No checkpoint found" -ForegroundColor Green
    }
}

# Final summary
Write-Host ""
Write-Host ("="*70) -ForegroundColor Green
if ($allClean) {
    Write-Host "COMPLETE CLEANUP SUCCESSFUL!" -ForegroundColor Green
} else {
    Write-Host "CLEANUP MOSTLY COMPLETE (some files may be locked)" -ForegroundColor Yellow
}
Write-Host ("="*70) -ForegroundColor Green

# Check free space
$freespace = (Get-PSDrive C).Free / 1GB
$freespaceRounded = [math]::Round($freespace, 2)

Write-Host ""
Write-Host "Free disk space: $freespaceRounded GB" -ForegroundColor Cyan
Write-Host ""
Write-Host "READY FOR FRESH START!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Close Outlook (if open)" -ForegroundColor White
Write-Host "  2. Run: python extract_emails_overnight.py" -ForegroundColor Cyan
Write-Host "  3. Go home, let it run overnight" -ForegroundColor White
Write-Host "  4. Will extract all 32 PSTs from beginning" -ForegroundColor White
Write-Host ""

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")