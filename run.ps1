# run.ps1 - Launcher script for Lismore Analysis System
# Usage: .\run.ps1 pass1 --limit=50

# Set Python path
$env:PYTHONPATH = "$PSScriptRoot\src;$env:PYTHONPATH"

# Run main.py with all arguments
python "$PSScriptRoot\main.py" $args
