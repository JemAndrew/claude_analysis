"""
Find Large Files - Disk Space Investigation
British English

Identifies what's consuming disk space on C: drive
"""

from pathlib import Path
import os


def get_folder_size(folder_path):
    """Calculate folder size"""
    total = 0
    try:
        for entry in os.scandir(folder_path):
            if entry.is_file(follow_symlinks=False):
                total += entry.stat().st_size
            elif entry.is_dir(follow_symlinks=False):
                total += get_folder_size(entry.path)
    except (PermissionError, FileNotFoundError):
        pass
    return total


def format_size(bytes_value):
    """Format bytes to GB"""
    return bytes_value / (1024**3)


def main():
    """Find what's using disk space"""
    
    print("="*70)
    print("🔍 DISK SPACE INVESTIGATION")
    print("="*70)
    print("Scanning key folders... (this may take 2-3 minutes)")
    print()
    
    # Key folders to check
    user_home = Path.home()
    
    folders_to_check = {
        'OneDrive': user_home / "OneDrive - Velitor",
        'Velitor Sync': Path(r"C:\Users\JemAndrew\Velitor"),
        'Desktop': user_home / "Desktop",
        'Documents': user_home / "Documents", 
        'Downloads': user_home / "Downloads",
        'AppData Local': user_home / "AppData" / "Local",
        'AppData Roaming': user_home / "AppData" / "Roaming",
        'Temp': Path(r"C:\Temp"),
    }
    
    sizes = {}
    
    for name, path in folders_to_check.items():
        if path.exists():
            print(f"Scanning: {name}...", end=" ", flush=True)
            size = get_folder_size(path)
            sizes[name] = size
            print(f"{format_size(size):.1f} GB")
        else:
            print(f"Skipping: {name} (not found)")
    
    print("\n" + "="*70)
    print("📊 RESULTS (sorted by size)")
    print("="*70)
    
    # Sort by size
    sorted_sizes = sorted(sizes.items(), key=lambda x: x[1], reverse=True)
    
    total_scanned = 0
    for name, size in sorted_sizes:
        size_gb = format_size(size)
        total_scanned += size
        print(f"   {name:20s} {size_gb:>8.1f} GB")
    
    print("="*70)
    print(f"   {'TOTAL SCANNED':20s} {format_size(total_scanned):>8.1f} GB")
    print("="*70)
    
    # Check for Pass 1 output
    print("\n🔍 Checking for Pass 1 output...")
    
    claude_folders = [
        user_home / "OneDrive - Velitor" / "Claude",
        Path(r"C:\Users\JemAndrew\OneDrive - Velitor\Claude"),
    ]
    
    for folder in claude_folders:
        if folder.exists():
            output_folder = folder / "claude_analysis-master" / "output"
            if output_folder.exists():
                output_size = get_folder_size(output_folder)
                print(f"   Pass 1 output: {format_size(output_size):.2f} GB")
                print(f"   Location: {output_folder}")
                
                # Check for large files
                try:
                    files = list(output_folder.rglob("*"))
                    large_files = [f for f in files if f.is_file() and f.stat().st_size > 100*(1024**2)]  # > 100 MB
                    
                    if large_files:
                        print(f"\n   Large files (>100 MB) in Pass 1 output:")
                        for f in sorted(large_files, key=lambda x: x.stat().st_size, reverse=True)[:10]:
                            print(f"      • {f.name}: {format_size(f.stat().st_size):.2f} GB")
                except:
                    pass
    
    print("\n" + "="*70)
    print("💡 RECOMMENDATIONS:")
    print("="*70)
    
    # Find biggest consumer
    if sorted_sizes:
        biggest = sorted_sizes[0]
        if format_size(biggest[1]) > 50:
            print(f"⚠️  {biggest[0]} is using {format_size(biggest[1]):.1f} GB")
            print(f"   Consider cleaning up this folder")
    
    print("\n✅ For email extraction:")
    print("   • You have 19.2 GB free")
    print("   • Direct processing only needs ~2 GB")
    print("   • You should be fine to continue")
    
    print("\n⚠️  If Pass 1 is creating large files:")
    print("   • Monitor both processes")
    print("   • Pass 1 output might be filling disk")
    print("   • Consider pausing Pass 1 if disk fills up")
    
    print("="*70)


if __name__ == "__main__":
    main()