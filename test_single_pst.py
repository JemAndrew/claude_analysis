# test_single_pst.py
import win32com.client
from pathlib import Path
import shutil

# Copy ONE PST to test
source_folder = Path(r"C:\Users\JemAndrew\Velitor\Communication site - Documents\LIS1.1\36- Chronological Email Run")
test_local = Path(r"C:\PST_Test")
test_local.mkdir(exist_ok=True)

# Find smallest PST
pst_files = list(source_folder.glob("*.pst"))
smallest = min(pst_files, key=lambda p: p.stat().st_size)

print(f"Copying test PST: {smallest.name}")
test_pst = test_local / smallest.name
shutil.copy2(smallest, test_pst)
print(f"✅ Copied to: {test_pst}")

# Try to load it
print("\nTesting Outlook load...")
try:
    outlook = win32com.client.Dispatch("Outlook.Application")
    namespace = outlook.GetNamespace("MAPI")
    
    namespace.AddStore(str(test_pst))
    print("✅ SUCCESS! PST loaded from local drive")
    
    # Find the folder
    for folder in namespace.Folders:
        if smallest.stem.lower() in str(folder.Name).lower():
            print(f"✅ Found folder: {folder.Name}")
            print(f"✅ Item count: {folder.Items.Count}")
            namespace.RemoveStore(folder)
            break
    
    outlook.Quit()
    print("\n🎉 Local PSTs will work! Copy all PSTs to C:\\PST_Local")
    
except Exception as e:
    print(f"❌ Still failed: {e}")
    print("\nTry SOLUTION 3 below...")