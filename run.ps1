# Check current disk space
$free = [math]::Round((Get-PSDrive C).Free / 1GB, 1)
Write-Host "Current free space: $free GB" -ForegroundColor Red

# DELETE ALL TEMP PST FILES IMMEDIATELY
Write-Host "`nDeleting temp PST files..." -ForegroundColor Yellow

# Delete from temp folder
Remove-Item "C:\PST_Local_Temp\*.pst" -Force -ErrorAction SilentlyContinue

# Check if any remain
$remaining = Get-ChildItem "C:\PST_Local_Temp" -Filter "*.pst" -ErrorAction SilentlyContinue
if ($remaining) {
    Write-Host "Found $($remaining.Count) locked files - force closing Outlook..." -ForegroundColor Yellow
    Stop-Process -Name "OUTLOOK" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 5
    Remove-Item "C:\PST_Local_Temp\*.pst" -Force -ErrorAction SilentlyContinue
}

# Check new free space
$free = [math]::Round((Get-PSDrive C).Free / 1GB, 1)
Write-Host "`nFree space after cleanup: $free GB" -ForegroundColor Green

# Also check temp folder
$tempSize = (Get-ChildItem "C:\Temp" -Recurse -File -ErrorAction SilentlyContinue | 
             Measure-Object -Property Length -Sum).Sum / 1GB
Write-Host "C:\Temp is using: $([math]::Round($tempSize, 1)) GB" -ForegroundColor Cyan