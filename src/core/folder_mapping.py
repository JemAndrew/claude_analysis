#!/usr/bin/env python3
"""
Folder Mapping Configuration
Maps LIS1.1 folder names to categories and priorities
No file copying needed - direct path access
British English throughout
"""

from typing import Dict, List, Optional
from pathlib import Path


class FolderMapping:
    """Maps source folders to categories and priorities"""
    
    # Master folder mapping: folder_name → metadata
    FOLDER_MAP = {
        # ================================================================
        # LEGAL_KNOWLEDGE - Foundation & Context (Priority 4-5)
        # ================================================================
        "25- LCIA Arbitration Rules": {
            "category": "legal_knowledge",
            "priority": 5,
            "description": "LCIA Rules",
            "pass_1_include": False  # Reference material, not triage
        },
        "26- Research - the Tuna Bond Scandal": {
            "category": "legal_knowledge",
            "priority": 5,
            "description": "Tuna Bond Research",
            "pass_1_include": False
        },
        "47. Amit Forlit US Cases": {
            "category": "legal_knowledge",
            "priority": 5,
            "description": "Amit Forlit case law",
            "pass_1_include": False
        },
        "36- P&ID v Nigeria Arbitration": {
            "category": "legal_knowledge",
            "priority": 4,
            "description": "Related arbitration context",
            "pass_1_include": False
        },
        "37- P&ID v Nigeria Comm Court Trial": {
            "category": "legal_knowledge",
            "priority": 4,
            "description": "Related court proceedings",
            "pass_1_include": False
        },
        
        # ================================================================
        # CASE_PLEADINGS - Parties' Legal Arguments (Priority 6-8)
        # ================================================================
        "5- Request for Arbitration": {
            "category": "pleadings_claimant",
            "priority": 7,
            "description": "Initial request for arbitration",
            "pass_1_include": True  # Need to know what Lismore claims
        },
        "29- Claimant's Statement of Claim": {
            "category": "pleadings_claimant",
            "priority": 8,
            "description": "Lismore main pleading",
            "pass_1_include": True  # CRITICAL - Lismore's case
        },
        "72. Lismore's Submission (6 October 2025)": {
            "category": "pleadings_claimant",
            "priority": 8,
            "description": "Latest Lismore submission",
            "pass_1_include": True
        },
        
        "35- First Respondent's Statement of Defence": {
            "category": "pleadings_respondent",
            "priority": 8,
            "description": "PHL main defence",
            "pass_1_include": True  # CRITICAL - PHL's defence
        },
        "43. Statement of Defence Shared with Counsel": {
            "category": "pleadings_respondent",
            "priority": 8,
            "description": "Defence working version",
            "pass_1_include": True
        },
        "30- Respondent's Reply": {
            "category": "pleadings_respondent",
            "priority": 7,
            "description": "PHL reply",
            "pass_1_include": True
        },
        "62. First Respondent's Reply and Rejoinder": {
            "category": "pleadings_respondent",
            "priority": 7,
            "description": "PHL further pleadings",
            "pass_1_include": True
        },
        "63. PHL's Rejoinder to Lismore's Reply of 30 May 2025": {
            "category": "pleadings_respondent",
            "priority": 7,
            "description": "PHL rejoinder",
            "pass_1_include": True
        },
        
        # Applications
        "1- Application to Stay Arbitral Proceedings": {
            "category": "applications",
            "priority": 6,
            "description": "Stay application docs",
            "pass_1_include": False  # Procedural, not substantive
        },
        "10- Claimant's Response to the First Respondent's Stay Application": {
            "category": "applications",
            "priority": 7,
            "description": "Lismore response to stay",
            "pass_1_include": False
        },
        "13- Claimant's Response to Stay Application": {
            "category": "applications",
            "priority": 7,
            "description": "Lismore response (duplicate?)",
            "pass_1_include": False
        },
        "27. Security for Costs Application": {
            "category": "applications",
            "priority": 6,
            "description": "Security application",
            "pass_1_include": False
        },
        "28- Claimant's Response to the First Respondent's application for security for costs": {
            "category": "applications",
            "priority": 7,
            "description": "Lismore response to security",
            "pass_1_include": False
        },
        "71. Response to PHL Application re Lismore Disclosure (25 September 2025)": {
            "category": "applications",
            "priority": 7,
            "description": "Response to PHL disclosure application",
            "pass_1_include": False
        },
        
        # ================================================================
        # WITNESS_EVIDENCE - Witness Statements (Priority 8-9)
        # ================================================================
        "12- Brendan Cahill's witness statements": {
            "category": "witness_claimant",
            "priority": 9,
            "description": "BC witness statements",
            "pass_1_include": True  # Test against contemporaneous docs
        },
        "44. Exhibits to BC and GT and MQ Witness Statements": {
            "category": "witness_claimant",
            "priority": 9,
            "description": "Exhibits to multiple witnesses",
            "pass_1_include": True
        },
        "61. Witness Statements": {
            "category": "witness_consolidated",
            "priority": 8,
            "description": "All witness statements",
            "pass_1_include": True
        },
        
        "40- Isha Taiga Witness Statement": {
            "category": "witness_respondent",
            "priority": 9,
            "description": "IT witness statement",
            "pass_1_include": True
        },
        
        # ================================================================
        # DISCLOSURE - RAW EVIDENCE (Priority 10 - HIGHEST)
        # ================================================================
        "2- Disclosure": {
            "category": "disclosure_initial",
            "priority": 10,
            "description": "Initial disclosure batch",
            "pass_1_include": True  # PRIMARY TARGET
        },
        "55. Document Production": {
            "category": "disclosure_respondent",
            "priority": 10,
            "description": "PHL document production",
            "pass_1_include": True  # PRIMARY TARGET
        },
        "56- Documents received from Three Crowns on 11 April 2025": {
            "category": "disclosure_respondent",
            "priority": 10,
            "description": "PHL docs 11 April",
            "pass_1_include": True  # PRIMARY TARGET
        },
        "64. PHL's documents sent on 23 June 2025": {
            "category": "disclosure_respondent",
            "priority": 10,
            "description": "PHL docs 23 June",
            "pass_1_include": True  # PRIMARY TARGET
        },
        "66. PHL's additional documents (15 Aug 2025)": {
            "category": "disclosure_respondent",
            "priority": 10,
            "description": "PHL docs 15 Aug",
            "pass_1_include": True  # PRIMARY TARGET
        },
        "69. PHL's disclosure (15 September 2025)": {
            "category": "disclosure_respondent",
            "priority": 10,
            "description": "PHL docs 15 Sep",
            "pass_1_include": True  # PRIMARY TARGET
        },
        "70. Complete Sets of PHL Disclosure to date": {
            "category": "disclosure_respondent",
            "priority": 10,
            "description": "COMPLETE PHL DISCLOSURE",
            "pass_1_include": True  # PRIMARY TARGET - MOST IMPORTANT
        },
        
        "54- Trial Bundle (7 March 2025)": {
            "category": "disclosure_claimant",
            "priority": 8,
            "description": "Lismore trial bundle",
            "pass_1_include": True
        },
        "58- List of Claimant Docs sent on 7 March 2025": {
            "category": "disclosure_claimant",
            "priority": 7,
            "description": "Lismore docs list",
            "pass_1_include": True
        },
        "60. Exhibits from the Claimant's response to the First Respondent's Application dated 12 May 2025": {
            "category": "disclosure_claimant",
            "priority": 8,
            "description": "Lismore exhibits",
            "pass_1_include": True
        },
        
        "38- Missing Exhibits": {
            "category": "disclosure_issues",
            "priority": 8,
            "description": "Missing exhibits tracking",
            "pass_1_include": True  # Shows what PH is hiding
        },
        
        # ================================================================
        # TRIBUNAL_ORDERS - Procedural Rulings (Priority 6-7)
        # ================================================================
        "4- PO1": {
            "category": "tribunal_orders",
            "priority": 6,
            "description": "Procedural Order 1",
            "pass_1_include": False
        },
        "8- PO2": {
            "category": "tribunal_orders",
            "priority": 6,
            "description": "Procedural Order 2",
            "pass_1_include": False
        },
        "39- Procedural Order No. 2": {
            "category": "tribunal_orders",
            "priority": 6,
            "description": "PO2 (duplicate?)",
            "pass_1_include": False
        },
        "42. Procedural Order No. 3": {
            "category": "tribunal_orders",
            "priority": 6,
            "description": "Procedural Order 3",
            "pass_1_include": False
        },
        
        "22- Tribunal's Ruling on the Stay Application": {
            "category": "tribunal_rulings",
            "priority": 7,
            "description": "Ruling on stay application",
            "pass_1_include": False
        },
        "31- Tribunal's Ruling on Application for Security for Costs": {
            "category": "tribunal_rulings",
            "priority": 7,
            "description": "Ruling on security for costs",
            "pass_1_include": False
        },
        "53- Tribunal's Decisions on Stern Schedules": {
            "category": "tribunal_rulings",
            "priority": 7,
            "description": "Tribunal decisions on Stern schedules",
            "pass_1_include": False
        },
        "65. Tribunal's Ruling dated 31 July 2025": {
            "category": "tribunal_rulings",
            "priority": 7,
            "description": "Tribunal ruling 31 July",
            "pass_1_include": False
        },
        "68. Tribunal's Ruling (2 September 2025)": {
            "category": "tribunal_rulings",
            "priority": 7,
            "description": "Tribunal ruling 2 Sep",
            "pass_1_include": False
        },
        
        # ================================================================
        # CORRESPONDENCE - Emails & Letters (Priority 7-8)
        # ================================================================
        "33- Correspondence": {
            "category": "correspondence",
            "priority": 7,
            "description": "General correspondence",
            "pass_1_include": True
        },
        "36- Chronological Email Run": {
            "category": "correspondence",
            "priority": 8,
            "description": "EMAIL CHAIN - contemporaneous",
            "pass_1_include": True  # Real-time communications
        },
        "67. First Respondent's Draft Letter of 22 August 2025": {
            "category": "correspondence",
            "priority": 6,
            "description": "Draft letters",
            "pass_1_include": False
        },
        
        # ================================================================
        # DISCLOSURE_DISPUTES - What's Missing (Priority 7)
        # ================================================================
        "41- First Respondent's Document Production Requests": {
            "category": "disclosure_disputes",
            "priority": 7,
            "description": "PHL document requests",
            "pass_1_include": True  # Shows what PH wants
        },
        "45. First Respondent's Objections to Document Production Requests": {
            "category": "disclosure_disputes",
            "priority": 7,
            "description": "PHL objections",
            "pass_1_include": True
        },
        "46. Claimant's Objections to Document Production Requests": {
            "category": "disclosure_disputes",
            "priority": 7,
            "description": "Lismore objections",
            "pass_1_include": True
        },
        "48. Brendan Cahill's Objections to Document Production Requests": {
            "category": "disclosure_disputes",
            "priority": 7,
            "description": "BC objections",
            "pass_1_include": True
        },
        "49. First Respondent's Stern Schedule": {
            "category": "disclosure_disputes",
            "priority": 7,
            "description": "PHL Stern schedule",
            "pass_1_include": True
        },
        "50. Claimant's Stern Schedule": {
            "category": "disclosure_disputes",
            "priority": 7,
            "description": "Lismore Stern schedule",
            "pass_1_include": True
        },
        "57- First Respondent's Responses to Claimant's disclosure": {
            "category": "disclosure_disputes",
            "priority": 7,
            "description": "PHL responses",
            "pass_1_include": True
        },
        
        # ================================================================
        # PROCEDURAL_LOW_PRIORITY - Admin (Priority 2-5)
        # ================================================================
        "11- Epiq Transcription": {
            "category": "procedural",
            "priority": 3,
            "description": "Epiq transcripts",
            "pass_1_include": False
        },
        "59. Trial Transcripts": {
            "category": "procedural",
            "priority": 3,
            "description": "Trial transcripts",
            "pass_1_include": False
        },
        "9- Opus 2 Transcription Quote": {
            "category": "procedural",
            "priority": 2,
            "description": "Transcription quote",
            "pass_1_include": False
        },
        
        "14- Hearing Bundle - as served": {
            "category": "procedural",
            "priority": 4,
            "description": "Hearing bundle",
            "pass_1_include": False
        },
        "15- Covers and Spines for the Hearing Bundle of Stay Application and CMC": {
            "category": "procedural",
            "priority": 2,
            "description": "Bundle covers",
            "pass_1_include": False
        },
        "7- Documents of Hearing of Stay Application and CMC": {
            "category": "procedural",
            "priority": 4,
            "description": "Stay hearing docs",
            "pass_1_include": False
        },
        
        "16- Draft Reading List": {
            "category": "procedural",
            "priority": 3,
            "description": "Draft reading list",
            "pass_1_include": False
        },
        "17- Reading List as sent to the Tribunal": {
            "category": "procedural",
            "priority": 3,
            "description": "Final reading list",
            "pass_1_include": False
        },
        "18- IDRC remote hearing documents": {
            "category": "procedural",
            "priority": 3,
            "description": "IDRC hearing docs",
            "pass_1_include": False
        },
        
        "19- Respondent's Additional Factual Exhibits and Legal Authorities": {
            "category": "procedural",
            "priority": 4,
            "description": "PHL additional exhibits",
            "pass_1_include": False
        },
        
        "20- Dramatis Personae": {
            "category": "procedural",
            "priority": 4,
            "description": "Dramatis personae",
            "pass_1_include": False
        },
        "21- Chronology": {
            "category": "procedural",
            "priority": 5,
            "description": "Chronology",
            "pass_1_include": False
        },
        "24- Minutes of Meetings": {
            "category": "procedural",
            "priority": 4,
            "description": "Meeting minutes",
            "pass_1_include": False
        },
        "32- Minutes of Meetings": {
            "category": "procedural",
            "priority": 4,
            "description": "Meeting minutes (duplicate?)",
            "pass_1_include": False
        },
        "23- Velitor's costs spreadsheet - Stay Application": {
            "category": "procedural",
            "priority": 3,
            "description": "Costs spreadsheet",
            "pass_1_include": False
        },
        
        "51. Hyperlinked Index": {
            "category": "procedural",
            "priority": 3,
            "description": "Hyperlinked index",
            "pass_1_include": False
        },
        "52- Hyperlinked Consolidated Index of the Claimant": {
            "category": "procedural",
            "priority": 3,
            "description": "Lismore consolidated index",
            "pass_1_include": False
        },
        
        "3- Amended proposed timetable - LCIA Arbitration No. 215173": {
            "category": "procedural",
            "priority": 4,
            "description": "Amended timetable",
            "pass_1_include": False
        },
        "6- Responses": {
            "category": "procedural",
            "priority": 4,
            "description": "Various responses",
            "pass_1_include": False
        },
        
        # ================================================================
        # EXPERT_INSTRUCTIONS - Future Evidence (Priority 6)
        # ================================================================
        "34- Instructions to Experts": {
            "category": "expert_instructions",
            "priority": 6,
            "description": "Expert instructions",
            "pass_1_include": False
        },
    }
    
    @classmethod
    def get_folder_metadata(cls, folder_name: str) -> Optional[Dict]:
        """
        Get metadata for a folder using fuzzy matching
        
        Args:
            folder_name: Name of folder (e.g., "55. Document Production")
            
        Returns:
            Dict with category, priority, description, pass_1_include
                or None if folder not mapped
        """
        # Try exact match first
        if folder_name in cls.FOLDER_MAP:
            return cls.FOLDER_MAP[folder_name]
        
        # Fuzzy match by number prefix
        import re
        match = re.match(r'^(\d+[-\.])\s*', folder_name)
        if match:
            prefix = match.group(1)
            # Find matching folder in map
            for map_key, metadata in cls.FOLDER_MAP.items():
                if map_key.startswith(prefix):
                    return metadata
        
        return None
    
    @classmethod
    def get_priority(cls, folder_name: str) -> int:
        """Get priority tier for a folder (1-10)"""
        metadata = cls.get_folder_metadata(folder_name)
        return metadata['priority'] if metadata else 5  # Default mid-priority
    
    @classmethod
    def get_category(cls, folder_name: str) -> str:
        """Get category for a folder"""
        metadata = cls.get_folder_metadata(folder_name)
        return metadata['category'] if metadata else 'unknown'
    
    @classmethod
    def should_include_in_pass_1(cls, folder_name: str) -> bool:
        """Check if folder should be included in Pass 1 triage"""
        metadata = cls.get_folder_metadata(folder_name)
        return metadata['pass_1_include'] if metadata else True  # Default include
    
    @classmethod
    def get_pass_1_folders(cls) -> List[str]:
        """Get list of folder names to include in Pass 1"""
        return [
            name for name, meta in cls.FOLDER_MAP.items()
            if meta['pass_1_include']
        ]
    
    @classmethod
    def get_folders_by_category(cls, category: str) -> List[str]:
        """Get all folders in a specific category"""
        return [
            name for name, meta in cls.FOLDER_MAP.items()
            if meta['category'] == category
        ]
    
    @classmethod
    def get_folders_by_priority(cls, min_priority: int = 1, max_priority: int = 10) -> List[str]:
        """Get folders within a priority range"""
        return [
            name for name, meta in cls.FOLDER_MAP.items()
            if min_priority <= meta['priority'] <= max_priority
        ]
    
    @classmethod
    def get_disclosure_folders(cls) -> List[str]:
        """Get all disclosure folders (priority 10)"""
        return cls.get_folders_by_priority(min_priority=10, max_priority=10)
    
    @classmethod
    def get_pleadings_folders(cls) -> List[str]:
        """Get all pleading folders"""
        pleading_categories = ['pleadings_claimant', 'pleadings_respondent', 'applications']
        folders = []
        for cat in pleading_categories:
            folders.extend(cls.get_folders_by_category(cat))
        return folders
    
    @classmethod
    def print_summary(cls):
        """Print folder mapping summary"""
        print("=" * 70)
        print("FOLDER MAPPING SUMMARY")
        print("=" * 70)
        
        # Count by category
        categories = {}
        for meta in cls.FOLDER_MAP.values():
            cat = meta['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\nTotal folders mapped: {len(cls.FOLDER_MAP)}")
        print(f"\nBy category:")
        for cat, count in sorted(categories.items()):
            print(f"  {cat}: {count} folders")
        
        # Count by priority
        priorities = {}
        for meta in cls.FOLDER_MAP.values():
            pri = meta['priority']
            priorities[pri] = priorities.get(pri, 0) + 1
        
        print(f"\nBy priority tier:")
        for pri in sorted(priorities.keys(), reverse=True):
            print(f"  Tier {pri}: {priorities[pri]} folders")
        
        # Pass 1 inclusion
        pass_1_count = sum(1 for m in cls.FOLDER_MAP.values() if m['pass_1_include'])
        print(f"\nPass 1 triage: {pass_1_count}/{len(cls.FOLDER_MAP)} folders")
        
        print("=" * 70)


if __name__ == "__main__":
    # Test the mapping
    FolderMapping.print_summary()
    
    print("\nPass 1 folders:")
    for folder in FolderMapping.get_pass_1_folders():
        pri = FolderMapping.get_priority(folder)
        print(f"  [{pri}] {folder}")