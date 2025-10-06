#!/usr/bin/env python3
"""
Automated LIS1.1 Folder Organisation Script
Organises litigation documents into intelligent hierarchy
British English throughout
"""

import shutil
from pathlib import Path
from typing import Dict, List
import json
from datetime import datetime


class LISFolderOrganiser:
    """Organises LIS1.1 folders into optimised structure"""
    
    def __init__(self, source_root: Path, target_root: Path):
        """
        Initialise organiser
        
        Args:
            source_root: LIS1.1 folder location
            target_root: data/input target location
        """
        self.source_root = Path(source_root)
        self.target_root = Path(target_root)
        
        # Folder mapping: source folder → target category
        self.folder_mapping = self._define_folder_mapping()
        
        # Track operations
        self.manifest = {
            'organised_at': datetime.now().isoformat(),
            'source': str(source_root),
            'target': str(target_root),
            'folders_processed': [],
            'errors': []
        }
    
    def _define_folder_mapping(self) -> Dict[str, tuple]:
        """
        Define where each LIS folder should go
        Returns: {folder_number: (target_path, priority_tier, description)}
        """
        
        mapping = {
            # ============================================================
            # 1_LEGAL_KNOWLEDGE - Foundation & Context
            # ============================================================
            '25': ('1_LEGAL_KNOWLEDGE/arbitration_rules', 5, 'LCIA Rules'),
            '26': ('1_LEGAL_KNOWLEDGE/research', 5, 'Tuna Bond Research'),
            '36': ('1_LEGAL_KNOWLEDGE/related_cases/P&ID_v_Nigeria_Arbitration', 4, 'Related arbitration context'),
            '37': ('1_LEGAL_KNOWLEDGE/related_cases/P&ID_v_Nigeria_Comm_Court', 4, 'Related court proceedings'),
            '47': ('1_LEGAL_KNOWLEDGE/case_law', 5, 'Amit Forlit US Cases'),
            
            # ============================================================
            # 2_CASE_PLEADINGS - Parties' Legal Arguments
            # ============================================================
            '5': ('2_CASE_PLEADINGS/claimant/Request_for_Arbitration', 7, 'Initial request'),
            '29': ('2_CASE_PLEADINGS/claimant/Statement_of_Claim', 8, 'Lismore main pleading'),
            '72': ('2_CASE_PLEADINGS/claimant/Submissions_6_Oct_2025', 8, 'Latest Lismore submission'),
            
            '35': ('2_CASE_PLEADINGS/respondent/Statement_of_Defence', 8, 'PHL main defence'),
            '43': ('2_CASE_PLEADINGS/respondent/Defence_Shared_with_Counsel', 8, 'Defence working version'),
            '30': ('2_CASE_PLEADINGS/respondent/Reply', 7, 'PHL reply'),
            '62': ('2_CASE_PLEADINGS/respondent/Reply_and_Rejoinder', 7, 'PHL further pleadings'),
            '63': ('2_CASE_PLEADINGS/respondent/Rejoinder_30_May_2025', 7, 'PHL rejoinder'),
            
            '1': ('2_CASE_PLEADINGS/applications/Stay_Application', 6, 'Stay application docs'),
            '10': ('2_CASE_PLEADINGS/applications/Lismore_Response_Stay', 7, 'Lismore response to stay'),
            '13': ('2_CASE_PLEADINGS/applications/Lismore_Response_Stay_v2', 7, 'Lismore response (duplicate?)'),
            '27': ('2_CASE_PLEADINGS/applications/Security_for_Costs_Application', 6, 'Security application'),
            '28': ('2_CASE_PLEADINGS/applications/Lismore_Response_Security', 7, 'Lismore response to security'),
            '71': ('2_CASE_PLEADINGS/applications/Lismore_Response_PHL_Disclosure_25_Sep', 7, 'Response to PHL disclosure application'),
            
            # ============================================================
            # 3_WITNESS_EVIDENCE - Witness Statements (HIGH PRIORITY)
            # ============================================================
            '12': ('3_WITNESS_EVIDENCE/claimant_witnesses/Brendan_Cahill', 9, 'BC witness statements'),
            '44': ('3_WITNESS_EVIDENCE/claimant_witnesses/BC_GT_MQ_Exhibits', 9, 'Exhibits to multiple witnesses'),
            '61': ('3_WITNESS_EVIDENCE/consolidated/Witness_Statements', 8, 'All witness statements'),
            
            '40': ('3_WITNESS_EVIDENCE/respondent_witnesses/Isha_Taiga', 9, 'IT witness statement'),
            
            # ============================================================
            # 4_DISCLOSURE - RAW EVIDENCE (HIGHEST PRIORITY)
            # ============================================================
            '2': ('4_DISCLOSURE/initial_disclosure', 10, 'Initial disclosure batch'),
            '55': ('4_DISCLOSURE/respondent_production/batch_001_Document_Production', 10, 'PHL document production'),
            '56': ('4_DISCLOSURE/respondent_production/batch_002_11_April_2025', 10, 'PHL docs 11 April'),
            '64': ('4_DISCLOSURE/respondent_production/batch_003_23_June_2025', 10, 'PHL docs 23 June'),
            '66': ('4_DISCLOSURE/respondent_production/batch_004_15_Aug_2025', 10, 'PHL docs 15 Aug'),
            '69': ('4_DISCLOSURE/respondent_production/batch_005_15_Sep_2025', 10, 'PHL docs 15 Sep'),
            '70': ('4_DISCLOSURE/respondent_production/batch_006_COMPLETE_SETS', 10, '⭐ COMPLETE PHL DISCLOSURE'),
            
            '54': ('4_DISCLOSURE/claimant_production/Trial_Bundle_7_March_2025', 8, 'Lismore trial bundle'),
            '58': ('4_DISCLOSURE/claimant_production/Docs_List_7_March', 7, 'Lismore docs list'),
            '60': ('4_DISCLOSURE/claimant_production/Exhibits_12_May_2025', 8, 'Lismore exhibits'),
            
            '38': ('4_DISCLOSURE/issues/Missing_Exhibits', 8, 'Missing exhibits tracking'),
            
            # ============================================================
            # 5_TRIBUNAL_ORDERS - Procedural Rulings (REFERENCE)
            # ============================================================
            '4': ('5_TRIBUNAL_ORDERS/PO1', 6, 'Procedural Order 1'),
            '8': ('5_TRIBUNAL_ORDERS/PO2', 6, 'Procedural Order 2'),
            '39': ('5_TRIBUNAL_ORDERS/PO2_v2', 6, 'PO2 (duplicate?)'),
            '42': ('5_TRIBUNAL_ORDERS/PO3', 6, 'Procedural Order 3'),
            
            '22': ('5_TRIBUNAL_ORDERS/Stay_Ruling', 7, 'Ruling on stay application'),
            '31': ('5_TRIBUNAL_ORDERS/Security_Costs_Ruling', 7, 'Ruling on security for costs'),
            '53': ('5_TRIBUNAL_ORDERS/Stern_Schedule_Decisions', 7, 'Tribunal decisions on Stern schedules'),
            '65': ('5_TRIBUNAL_ORDERS/Ruling_31_July_2025', 7, 'Tribunal ruling 31 July'),
            '68': ('5_TRIBUNAL_ORDERS/Ruling_2_Sep_2025', 7, 'Tribunal ruling 2 Sep'),
            
            # ============================================================
            # 6_CORRESPONDENCE - Emails & Letters (MEDIUM-HIGH PRIORITY)
            # ============================================================
            '33': ('6_CORRESPONDENCE/General_Correspondence', 7, 'General correspondence'),
            '36': ('6_CORRESPONDENCE/Chronological_Email_Run', 8, '⭐ EMAIL CHAIN'),
            '67': ('6_CORRESPONDENCE/Draft_Letters_22_Aug', 6, 'Draft letters'),
            
            # ============================================================
            # 7_DISCLOSURE_DISPUTES - Shows What's Missing (IMPORTANT)
            # ============================================================
            '41': ('7_DISCLOSURE_DISPUTES/Production_Requests/PHL_Requests', 7, 'PHL document requests'),
            '45': ('7_DISCLOSURE_DISPUTES/Objections/PHL_Objections', 7, 'PHL objections'),
            '46': ('7_DISCLOSURE_DISPUTES/Objections/Lismore_Objections', 7, 'Lismore objections'),
            '48': ('7_DISCLOSURE_DISPUTES/Objections/BC_Objections', 7, 'BC objections'),
            '49': ('7_DISCLOSURE_DISPUTES/Stern_Schedules/PHL_Stern_Schedule', 7, 'PHL Stern schedule'),
            '50': ('7_DISCLOSURE_DISPUTES/Stern_Schedules/Lismore_Stern_Schedule', 7, 'Lismore Stern schedule'),
            '57': ('7_DISCLOSURE_DISPUTES/Responses/PHL_Responses_to_Lismore_Disclosure', 7, 'PHL responses'),
            
            # ============================================================
            # 8_PROCEDURAL_LOW_PRIORITY - Admin Documents (SKIP IN PASS 1)
            # ============================================================
            '11': ('8_PROCEDURAL_LOW_PRIORITY/Transcripts/Epiq', 3, 'Epiq transcripts'),
            '59': ('8_PROCEDURAL_LOW_PRIORITY/Transcripts/Trial_Transcripts', 3, 'Trial transcripts'),
            '9': ('8_PROCEDURAL_LOW_PRIORITY/Transcripts/Opus2_Quote', 2, 'Transcription quote'),
            
            '14': ('8_PROCEDURAL_LOW_PRIORITY/Hearing_Bundles/Bundle_as_Served', 4, 'Hearing bundle'),
            '15': ('8_PROCEDURAL_LOW_PRIORITY/Hearing_Bundles/Covers_and_Spines', 2, 'Bundle covers'),
            '7': ('8_PROCEDURAL_LOW_PRIORITY/Hearing_Bundles/Stay_CMC_Hearing_Docs', 4, 'Stay hearing docs'),
            
            '16': ('8_PROCEDURAL_LOW_PRIORITY/Reading_Lists/Draft', 3, 'Draft reading list'),
            '17': ('8_PROCEDURAL_LOW_PRIORITY/Reading_Lists/Final', 3, 'Final reading list'),
            '18': ('8_PROCEDURAL_LOW_PRIORITY/Reading_Lists/IDRC_Remote_Hearing', 3, 'IDRC hearing docs'),
            
            '19': ('8_PROCEDURAL_LOW_PRIORITY/Exhibits/Respondent_Additional', 4, 'PHL additional exhibits'),
            
            '20': ('8_PROCEDURAL_LOW_PRIORITY/Case_Admin/Dramatis_Personae', 4, 'Dramatis personae'),
            '21': ('8_PROCEDURAL_LOW_PRIORITY/Case_Admin/Chronology', 5, 'Chronology'),
            '24': ('8_PROCEDURAL_LOW_PRIORITY/Case_Admin/Minutes_of_Meetings', 4, 'Meeting minutes'),
            '32': ('8_PROCEDURAL_LOW_PRIORITY/Case_Admin/Minutes_of_Meetings_v2', 4, 'Meeting minutes (duplicate?)'),
            '23': ('8_PROCEDURAL_LOW_PRIORITY/Case_Admin/Costs_Spreadsheet', 3, 'Costs spreadsheet'),
            
            '51': ('8_PROCEDURAL_LOW_PRIORITY/Indices/Hyperlinked_Index', 3, 'Hyperlinked index'),
            '52': ('8_PROCEDURAL_LOW_PRIORITY/Indices/Consolidated_Index_Claimant', 3, 'Lismore consolidated index'),
            
            '3': ('8_PROCEDURAL_LOW_PRIORITY/Timetable/Amended_Timetable', 4, 'Amended timetable'),
            '6': ('8_PROCEDURAL_LOW_PRIORITY/Responses/Various_Responses', 4, 'Various responses'),
            
            # ============================================================
            # 9_EXPERT_INSTRUCTIONS - Future Expert Evidence
            # ============================================================
            '34': ('9_EXPERT_INSTRUCTIONS/Instructions_to_Experts', 6, 'Expert instructions'),
        }
        
        return mapping
    
    def organise_folders(self, dry_run: bool = False) -> Dict:
        """
        Main organisation method
        
        Args:
            dry_run: If True, only simulate (don't copy files)
            
        Returns:
            Manifest dict with operation results
        """
        
        print("="*70)
        print("LIS1.1 FOLDER ORGANISATION")
        print("="*70)
        print(f"Source: {self.source_root}")
        print(f"Target: {self.target_root}")
        print(f"Mode: {'DRY RUN (simulation only)' if dry_run else 'LIVE (copying files)'}")
        print("="*70)
        
        # Get all folders in source
        source_folders = [f for f in self.source_root.iterdir() if f.is_dir()]
        
        print(f"\nFound {len(source_folders)} folders in source")
        print(f"Mapping defined for {len(self.folder_mapping)} folders\n")
        
        # Process each mapped folder
        for folder_num, (target_path, priority, description) in self.folder_mapping.items():
            # Find matching source folder
            source_folder = self._find_source_folder(folder_num)
            
            if not source_folder:
                print(f"⚠️  Folder {folder_num}: NOT FOUND in source")
                self.manifest['errors'].append({
                    'folder': folder_num,
                    'error': 'Source folder not found',
                    'expected_target': target_path
                })
                continue
            
            # Build target path
            full_target = self.target_root / target_path
            
            # Log operation
            operation = {
                'folder_number': folder_num,
                'source_name': source_folder.name,
                'target_path': str(target_path),
                'priority_tier': priority,
                'description': description,
                'file_count': self._count_files(source_folder),
                'status': 'pending'
            }
            
            print(f"📁 [{folder_num}] {source_folder.name}")
            print(f"   → {target_path}")
            print(f"   Priority: {priority}/10 | Files: {operation['file_count']} | {description}")
            
            if not dry_run:
                try:
                    # Create target directory
                    full_target.mkdir(parents=True, exist_ok=True)
                    
                    # Copy folder contents
                    self._copy_folder_contents(source_folder, full_target)
                    
                    operation['status'] = 'success'
                    print(f"   ✅ Copied successfully")
                    
                except Exception as e:
                    operation['status'] = 'failed'
                    operation['error'] = str(e)
                    print(f"   ❌ Error: {str(e)[:100]}")
                    
                    self.manifest['errors'].append({
                        'folder': folder_num,
                        'error': str(e),
                        'source': str(source_folder)
                    })
            else:
                operation['status'] = 'simulated'
                print(f"   ✓ Would copy {operation['file_count']} files")
            
            self.manifest['folders_processed'].append(operation)
            print()
        
        # Identify unmapped folders
        self._identify_unmapped_folders(source_folders)
        
        # Generate summary
        self._generate_summary()
        
        return self.manifest
    
    def _find_source_folder(self, folder_num: str) -> Path:
        """Find source folder by number prefix"""
        for folder in self.source_root.iterdir():
            if folder.is_dir() and folder.name.startswith(f"{folder_num}-") or folder.name.startswith(f"{folder_num}."):
                return folder
        return None
    
    def _count_files(self, folder: Path) -> int:
        """Count all files in folder recursively"""
        count = 0
        for item in folder.rglob('*'):
            if item.is_file():
                count += 1
        return count
    
    def _copy_folder_contents(self, source: Path, target: Path):
        """Copy all contents from source to target"""
        for item in source.rglob('*'):
            if item.is_file():
                # Calculate relative path
                rel_path = item.relative_to(source)
                target_file = target / rel_path
                
                # Create parent directories
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                shutil.copy2(item, target_file)
    
    def _identify_unmapped_folders(self, source_folders: List[Path]):
        """Identify folders that weren't mapped"""
        mapped_numbers = set(self.folder_mapping.keys())
        
        unmapped = []
        for folder in source_folders:
            # Extract folder number
            folder_num = self._extract_folder_number(folder.name)
            if folder_num and folder_num not in mapped_numbers:
                unmapped.append({
                    'folder_number': folder_num,
                    'folder_name': folder.name,
                    'file_count': self._count_files(folder)
                })
        
        if unmapped:
            print("⚠️  UNMAPPED FOLDERS (not in organisation plan):")
            for item in unmapped:
                print(f"   [{item['folder_number']}] {item['folder_name']} ({item['file_count']} files)")
            
            self.manifest['unmapped_folders'] = unmapped
    
    def _extract_folder_number(self, folder_name: str) -> str:
        """Extract folder number from name"""
        import re
        match = re.match(r'^(\d+)[-\.]', folder_name)
        return match.group(1) if match else None
    
    def _generate_summary(self):
        """Generate organisation summary"""
        print("\n" + "="*70)
        print("ORGANISATION SUMMARY")
        print("="*70)
        
        total_processed = len(self.manifest['folders_processed'])
        successful = sum(1 for f in self.manifest['folders_processed'] if f['status'] == 'success')
        failed = sum(1 for f in self.manifest['folders_processed'] if f['status'] == 'failed')
        simulated = sum(1 for f in self.manifest['folders_processed'] if f['status'] == 'simulated')
        
        print(f"Total folders processed: {total_processed}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Simulated (dry run): {simulated}")
        print(f"  Errors: {len(self.manifest['errors'])}")
        
        # Count by priority tier
        print("\nBy Priority Tier:")
        tier_counts = {}
        for folder in self.manifest['folders_processed']:
            tier = folder['priority_tier']
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        for tier in sorted(tier_counts.keys(), reverse=True):
            print(f"  Tier {tier}: {tier_counts[tier]} folders")
        
        # Total files
        total_files = sum(f['file_count'] for f in self.manifest['folders_processed'])
        print(f"\nTotal files organised: {total_files:,}")
        
        print("="*70)
    
    def save_manifest(self, output_file: Path = None):
        """Save manifest to JSON file"""
        if output_file is None:
            output_file = self.target_root / "organisation_manifest.json"
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.manifest, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Manifest saved: {output_file}")


def main():
    """Main execution"""
    
    # Define paths
    source = Path(r"C:\Users\JemAndrew\Velitor\Communication site - Documents\LIS1.1")
    target = Path(r"C:\Users\JemAndrew\OneDrive - Velitor\Claude\claude_analysis-master\data")
    
    # Validate source exists
    if not source.exists():
        print(f"❌ ERROR: Source folder not found: {source}")
        print("Please update the source path in the script.")
        return
    
    # Create organiser
    organiser = LISFolderOrganiser(source, target)
    
    # Ask user: dry run or live?
    print("\n" + "="*70)
    print("ORGANISATION MODE")
    print("="*70)
    print("1. DRY RUN (simulation only - see what would happen)")
    print("2. LIVE RUN (actually copy files)")
    print()
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == '1':
        dry_run = True
        print("\n🔍 Running in DRY RUN mode (simulation only)\n")
    elif choice == '2':
        confirm = input("⚠️  This will copy files. Continue? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("Cancelled.")
            return
        dry_run = False
        print("\n📁 Running in LIVE mode (copying files)\n")
    else:
        print("Invalid choice. Exiting.")
        return
    
    # Run organisation
    manifest = organiser.organise_folders(dry_run=dry_run)
    
    # Save manifest
    organiser.save_manifest()
    
    print("\n✅ Organisation complete!")
    
    if dry_run:
        print("\n💡 This was a dry run. Run again with option 2 to actually copy files.")
    else:
        print("\n🎯 Files organised! Your system is ready to run.")
        print(f"\nNext step: Update config.py paths to point to:")
        print(f"  {target}")


if __name__ == "__main__":
    main()