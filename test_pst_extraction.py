"""
Test PST Extraction - Single File Test
Tests extraction on one PST file to validate the approach before full extraction

Usage:
    python test_pst_extraction.py

Requirements:
    - Microsoft Outlook installed
    - pywin32 installed
    
Output:
    - test_emails.json (sample emails from one PST)
    - test_stats.json (test statistics)
"""

import json
import win32com.client
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from tqdm import tqdm
import hashlib

class TestPSTExtractor:
    """Test PST extraction on a single file"""
    
    def __init__(self, pst_folder: Path, output_folder: Path):
        self.pst_folder = pst_folder
        self.output_folder = output_folder
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        # Statistics
        self.stats = {
            'test_file': '',
            'total_emails_found': 0,
            'emails_extracted': 0,
            'duplicates_skipped': 0,
            'errors': 0,
            'folders_processed': 0,
            'start_time': datetime.now().isoformat()
        }
        
        self.seen_message_ids = set()
        
    def connect_outlook(self):
        """Initialise Outlook COM connection"""
        print("📧 Connecting to Microsoft Outlook...")
        try:
            self.outlook = win32com.client.Dispatch("Outlook.Application")
            self.namespace = self.outlook.GetNamespace("MAPI")
            print("✅ Connected to Outlook successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Outlook: {e}")
            print("\n⚠️  Troubleshooting:")
            print("   1. Make sure Microsoft Outlook is installed")
            print("   2. Try running: python -c \"import win32com.client\"")
            print("   3. You may need to run: python Scripts/pywin32_postinstall.py -install")
            return False
    
    def extract_email_metadata(self, mail_item) -> Optional[Dict]:
        """Extract metadata from a single email"""
        try:
            # Basic properties
            subject = str(mail_item.Subject) if mail_item.Subject else "(No Subject)"
            sender = str(mail_item.SenderName) if mail_item.SenderName else "(Unknown Sender)"
            sender_email = str(mail_item.SenderEmailAddress) if mail_item.SenderEmailAddress else ""
            
            # Recipients
            recipients = []
            try:
                for recipient in mail_item.Recipients:
                    recipients.append({
                        'name': str(recipient.Name) if recipient.Name else "",
                        'email': str(recipient.Address) if recipient.Address else ""
                    })
            except:
                pass
            
            # Dates
            received_time = None
            sent_time = None
            try:
                if mail_item.ReceivedTime:
                    received_time = mail_item.ReceivedTime.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
            
            try:
                if mail_item.SentOn:
                    sent_time = mail_item.SentOn.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
            
            # Body (first 1000 chars for testing)
            body_preview = ""
            try:
                if mail_item.Body:
                    body_preview = str(mail_item.Body)[:1000]
            except:
                pass
            
            # Generate unique ID
            unique_string = f"{sender_email}|{subject}|{sent_time}|{body_preview[:200]}"
            message_id = hashlib.md5(unique_string.encode()).hexdigest()
            
            # Check duplicates
            if message_id in self.seen_message_ids:
                self.stats['duplicates_skipped'] += 1
                return None
            
            self.seen_message_ids.add(message_id)
            
            # Build email data
            email_data = {
                'message_id': message_id,
                'subject': subject,
                'sender_name': sender,
                'sender_email': sender_email,
                'recipients': recipients,
                'received_time': received_time,
                'sent_time': sent_time,
                'body_preview': body_preview,
                'has_attachments': mail_item.Attachments.Count > 0 if hasattr(mail_item, 'Attachments') else False,
                'importance': str(mail_item.Importance) if hasattr(mail_item, 'Importance') else "Normal",
                'size_kb': round(mail_item.Size / 1024, 2) if hasattr(mail_item, 'Size') else 0
            }
            
            self.stats['emails_extracted'] += 1
            return email_data
            
        except Exception as e:
            self.stats['errors'] += 1
            return None
    
    def process_folder_recursive(self, folder, emails: List[Dict], pbar: tqdm, max_emails: int = 100):
        """
        Process folder recursively but stop after max_emails for testing
        
        Args:
            folder: Outlook folder object
            emails: List to store extracted emails
            pbar: Progress bar
            max_emails: Maximum emails to extract (for testing)
        """
        if len(emails) >= max_emails:
            return
        
        try:
            items = folder.Items
            folder_name = str(folder.Name) if hasattr(folder, 'Name') else "Unknown"
            self.stats['total_emails_found'] += items.Count
            self.stats['folders_processed'] += 1
            
            print(f"\n   📁 Processing folder: {folder_name} ({items.Count} items)")
            
            for item in items:
                if len(emails) >= max_emails:
                    break
                
                pbar.update(1)
                
                # Only process mail items
                if hasattr(item, 'Class') and item.Class == 43:  # olMail
                    email_data = self.extract_email_metadata(item)
                    if email_data:
                        emails.append(email_data)
            
            # Process subfolders
            for subfolder in folder.Folders:
                if len(emails) >= max_emails:
                    break
                self.process_folder_recursive(subfolder, emails, pbar, max_emails)
                
        except Exception as e:
            print(f"\n⚠️  Error processing folder: {e}")
            self.stats['errors'] += 1
    
    def test_single_pst(self, pst_path: Path, max_emails: int = 100) -> List[Dict]:
        """
        Test extraction on a single PST file
        
        Args:
            pst_path: Path to PST file
            max_emails: Maximum emails to extract for testing
            
        Returns:
            List of extracted email metadata
        """
        print(f"\n{'='*60}")
        print(f"🧪 TESTING: {pst_path.name}")
        print(f"   Size: {pst_path.stat().st_size / (1024**3):.2f} GB")
        print(f"   Extracting up to {max_emails} emails for testing")
        print(f"{'='*60}")
        
        self.stats['test_file'] = pst_path.name
        emails = []
        
        try:
            # Add PST to Outlook
            print("\n📂 Loading PST into Outlook...")
            self.namespace.AddStore(str(pst_path))
            
            # Find the PST's root folder
            root_folder = None
            for folder in self.namespace.Folders:
                folder_name = str(folder.Name).lower()
                if pst_path.stem.lower() in folder_name or "personal folders" in folder_name:
                    root_folder = folder
                    print(f"   ✅ Found root folder: {folder.Name}")
                    break
            
            if not root_folder:
                print("   ⚠️  Using last folder as root")
                root_folder = self.namespace.Folders.GetLast()
            
            # Process with progress bar
            print("\n📧 Extracting emails...")
            with tqdm(total=max_emails, desc="   Progress", unit="email") as pbar:
                self.process_folder_recursive(root_folder, emails, pbar, max_emails)
            
            # Remove PST from Outlook
            try:
                self.namespace.RemoveStore(root_folder)
            except:
                pass
            
            print(f"\n✅ Test extraction complete!")
            print(f"   Emails extracted: {len(emails)}")
            print(f"   Folders processed: {self.stats['folders_processed']}")
            print(f"   Duplicates skipped: {self.stats['duplicates_skipped']}")
            print(f"   Errors: {self.stats['errors']}")
            
        except Exception as e:
            print(f"\n❌ Error during test extraction: {e}")
            self.stats['errors'] += 1
        
        return emails
    
    def save_test_results(self, emails: List[Dict]):
        """Save test results"""
        
        # Save emails
        output_file = self.output_folder / "test_emails.json"
        print(f"\n💾 Saving test results to {output_file}...")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(emails, f, indent=2, ensure_ascii=False)
        
        # Update stats
        self.stats['end_time'] = datetime.now().isoformat()
        self.stats['final_email_count'] = len(emails)
        
        # Calculate duration
        start = datetime.fromisoformat(self.stats['start_time'])
        end = datetime.fromisoformat(self.stats['end_time'])
        duration = (end - start).total_seconds()
        self.stats['duration_seconds'] = round(duration, 2)
        
        # Save stats
        stats_file = self.output_folder / "test_stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2)
        
        # Print sample emails
        if emails:
            print("\n" + "="*60)
            print("📧 SAMPLE EMAILS (first 3)")
            print("="*60)
            for idx, email in enumerate(emails[:3], 1):
                print(f"\n{idx}. {email['subject']}")
                print(f"   From: {email['sender_name']} ({email['sender_email']})")
                print(f"   Date: {email['sent_time']}")
                print(f"   Size: {email['size_kb']} KB")
                print(f"   Body preview: {email['body_preview'][:150]}...")
        
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"Test file:        {self.stats['test_file']}")
        print(f"Emails extracted: {len(emails)}")
        print(f"Folders checked:  {self.stats['folders_processed']}")
        print(f"Duration:         {self.stats['duration_seconds']} seconds")
        print(f"\n✅ Test results saved to: {output_file}")
        print(f"📈 Statistics saved to: {stats_file}")
        
        # Estimate full extraction
        if len(emails) > 0 and self.stats['duration_seconds'] > 0:
            emails_per_second = len(emails) / self.stats['duration_seconds']
            estimated_total = 500000  # Estimated total emails
            estimated_hours = (estimated_total / emails_per_second) / 3600
            
            print("\n" + "="*60)
            print("⏱️  FULL EXTRACTION ESTIMATES")
            print("="*60)
            print(f"Extraction speed: {emails_per_second * 60:.0f} emails/minute")
            print(f"For 500,000 emails: ~{estimated_hours:.1f} hours")
            print(f"For 1,000,000 emails: ~{estimated_hours * 2:.1f} hours")


def main():
    """Main test execution"""
    
    # Configuration
    PST_FOLDER = Path(r"C:\Users\JemAndrew\Velitor\Communication site - Documents\LIS1.1\36- Chronological Email Run")
    ROOT_DISCLOSURE_FOLDER = Path(r"C:\Users\JemAndrew\Velitor\Communication site - Documents\LIS1.1")  # Root folder for MSG scanning
    OUTPUT_FOLDER = Path(r"C:\Users\JemAndrew\OneDrive - Velitor\Claude\claude_analysis-master\data\emails\test")
    
    print("="*60)
    print("🧪 EMAIL EXTRACTION TEST")
    print("="*60)
    print(f"PST Folder:    {PST_FOLDER}")
    print(f"Root Folder:   {ROOT_DISCLOSURE_FOLDER}")
    print(f"Output Folder: {OUTPUT_FOLDER}")
    print("="*60)
    
    # Check PST folder exists
    if not PST_FOLDER.exists():
        print(f"\n❌ Error: PST folder not found: {PST_FOLDER}")
        print("\n💡 Please update PST_FOLDER path in the script")
        return
    
    # Find PST files
    pst_files = list(PST_FOLDER.glob("*.pst"))
    
    if not pst_files:
        print(f"\n❌ No PST files found in {PST_FOLDER}")
        return
    
    print(f"\n📊 Found {len(pst_files)} PST files")
    
    # Select smallest PST for testing
    smallest_pst = min(pst_files, key=lambda p: p.stat().st_size)
    
    print(f"\n🎯 Selected smallest PST for testing:")
    print(f"   {smallest_pst.name}")
    print(f"   {smallest_pst.stat().st_size / (1024**3):.2f} GB")
    
    # Check for MSG files
    if ROOT_DISCLOSURE_FOLDER.exists():
        print(f"\n🔍 Scanning for MSG files (this may take a minute)...")
        msg_files = list(ROOT_DISCLOSURE_FOLDER.rglob("*.msg"))
        print(f"   ✅ Found {len(msg_files):,} MSG files across all folders")
        
        # Show some sample locations
        if msg_files:
            print("\n📁 Sample MSG file locations:")
            sample_folders = set()
            for msg in msg_files[:10]:
                folder = msg.parent.name
                sample_folders.add(folder)
            for folder in sorted(sample_folders)[:5]:
                count = len([m for m in msg_files if m.parent.name == folder])
                print(f"   • {folder}: {count} files")
    else:
        print(f"\n⚠️  Root folder not found: {ROOT_DISCLOSURE_FOLDER}")
        msg_files = []
    
    # Initialise tester
    tester = TestPSTExtractor(PST_FOLDER, OUTPUT_FOLDER)
    
    # Connect to Outlook
    if not tester.connect_outlook():
        return
    
    # Test extraction (100 emails max from PST)
    emails = tester.test_single_pst(smallest_pst, max_emails=100)
    
    # Test MSG extraction if available
    if msg_files and len(msg_files) > 0:
        print("\n" + "="*60)
        print("🧪 TESTING MSG FILE EXTRACTION")
        print("="*60)
        print(f"Testing with first 10 MSG files...")
        
        msg_sample = msg_files[:10]
        msg_emails = []
        
        from tqdm import tqdm
        with tqdm(total=len(msg_sample), desc="   Extracting", unit="msg") as pbar:
            for msg_path in msg_sample:
                try:
                    mail_item = tester.outlook.Session.OpenSharedItem(str(msg_path))
                    email_data = tester.extract_email_metadata(mail_item)
                    if email_data:
                        msg_emails.append(email_data)
                except:
                    pass
                pbar.update(1)
        
        print(f"\n✅ Extracted {len(msg_emails)} emails from MSG files")
        emails.extend(msg_emails)
    
    if emails:
        # Save results
        tester.save_test_results(emails)
        
        print("\n🎉 Test successful!")
        print("\n💡 Results show:")
        print(f"   • PST extraction working: {len([e for e in emails if 'pst' not in e.get('source', '')])} emails")
        if msg_files:
            print(f"   • MSG extraction working: {len([e for e in emails if 'msg' in e.get('source', '')])} emails")
        print("\n💡 If results look good, run the full extraction:")
        print("   python extract_emails.py")
        print(f"\n📊 Estimated totals:")
        print(f"   • From PST files: ~500,000 emails")
        print(f"   • From MSG files: ~{len(msg_files):,} emails")
        print(f"   • Total unique: ~{500000 + len(msg_files):,} emails")
    else:
        print("\n❌ Test failed - no emails extracted")
        print("\n🔍 Troubleshooting steps:")
        print("   1. Check if Outlook opens the PST file correctly")
        print("   2. Verify PST files aren't password-protected")
        print("   3. Try opening Outlook manually and checking the PST")


if __name__ == "__main__":
    main()