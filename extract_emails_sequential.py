"""
Sequential PST Email Extraction - Handles Large PST Collections
Extracts PST files ONE AT A TIME to minimize disk space requirements

Usage:
    python extract_emails_sequential.py

Features:
    - Only needs 7-10 GB free space (not 227 GB!)
    - Copies one PST, extracts, deletes, repeats
    - Fully automated
    - Saves progress after each PST
    - Can resume if interrupted
"""

import json
import win32com.client
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from tqdm import tqdm
import hashlib
import shutil

class SequentialPSTExtractor:
    """Extract PSTs one at a time to save disk space"""
    
    def __init__(self, pst_folder: Path, output_folder: Path, temp_folder: Path, root_folder: Path = None):
        self.pst_folder = pst_folder
        self.output_folder = output_folder
        self.temp_folder = temp_folder
        self.root_folder = root_folder
        
        # Create folders
        self.output_folder.mkdir(parents=True, exist_ok=True)
        self.temp_folder.mkdir(parents=True, exist_ok=True)
        
        # Statistics
        self.stats = {
            'pst_files_processed': 0,
            'pst_files_total': 0,
            'msg_files_processed': 0,
            'total_emails_extracted': 0,
            'duplicates_skipped': 0,
            'errors': 0,
            'start_time': datetime.now().isoformat(),
            'pst_progress': []
        }
        
        # Track seen message IDs
        self.seen_message_ids = set()
        
        # All extracted emails
        self.all_emails = []
    
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
            return False
    
    def extract_email_metadata(self, mail_item) -> Optional[Dict]:
        """Extract metadata from a single email"""
        try:
            # Get basic properties with better error handling
            subject = ""
            try:
                subject = str(mail_item.Subject) if mail_item.Subject else "(No Subject)"
            except:
                subject = "(No Subject)"
            
            sender = ""
            sender_email = ""
            try:
                sender = str(mail_item.SenderName) if mail_item.SenderName else ""
                sender_email = str(mail_item.SenderEmailAddress) if mail_item.SenderEmailAddress else ""
            except:
                pass
            
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
            
            # Body (limit to 50,000 chars)
            body = ""
            try:
                if mail_item.Body:
                    body = str(mail_item.Body)[:50000]
            except:
                pass
            
            # Generate unique ID - use multiple fields for better uniqueness
            # Only use fields that are likely to be unique
            unique_string = f"{sender_email}|{subject}|{sent_time}"
            if body:
                unique_string += f"|{body[:100]}"  # Only first 100 chars of body
            
            message_id = hashlib.md5(unique_string.encode()).hexdigest()
            
            # Check for duplicates
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
                'body': body,
                'has_attachments': mail_item.Attachments.Count > 0 if hasattr(mail_item, 'Attachments') else False,
                'importance': str(mail_item.Importance) if hasattr(mail_item, 'Importance') else "Normal",
                'size_kb': mail_item.Size / 1024 if hasattr(mail_item, 'Size') else 0
            }
            
            return email_data
            
        except Exception as e:
            # Don't increment errors for every single email failure
            # Only log occasionally to avoid spam
            if self.stats['errors'] % 1000 == 0:
                print(f"\n   ⚠️  Email extraction error (logged every 1000): {str(e)[:100]}")
            self.stats['errors'] += 1
            return None
    
    def process_folder_recursive(self, folder, emails: List[Dict], pbar: tqdm):
        """Recursively process all folders in the PST"""
        try:
            items = folder.Items
            
            for item in items:
                pbar.update(1)
                
                if hasattr(item, 'Class') and item.Class == 43:  # olMail
                    email_data = self.extract_email_metadata(item)
                    if email_data:
                        emails.append(email_data)
            
            # Process subfolders
            for subfolder in folder.Folders:
                self.process_folder_recursive(subfolder, emails, pbar)
                
        except Exception as e:
            self.stats['errors'] += 1
    
    def _count_items_recursive(self, folder) -> int:
        """Count total items in folder and subfolders"""
        try:
            count = folder.Items.Count
            for subfolder in folder.Folders:
                count += self._count_items_recursive(subfolder)
            return count
        except:
            return 0
    
    def extract_single_pst(self, pst_path: Path) -> List[Dict]:
        """
        Extract a single PST file
        
        Returns:
            List of emails extracted from this PST
        """
        print(f"\n📂 Processing: {pst_path.name} ({pst_path.stat().st_size / (1024**3):.2f} GB)")
        
        # Copy to temp folder
        temp_pst = self.temp_folder / pst_path.name
        
        print(f"   📋 Copying to temp folder...")
        try:
            shutil.copy2(pst_path, temp_pst)
            print(f"   ✅ Copy complete")
        except Exception as e:
            print(f"   ❌ Copy failed: {e}")
            return []
        
        emails = []
        
        try:
            # Load PST into Outlook
            print("   📥 Loading PST into Outlook...")
            self.namespace.AddStore(str(temp_pst))
            
            # Find the PST's root folder
            root_folder = None
            for folder in self.namespace.Folders:
                if pst_path.stem.lower() in str(folder.Name).lower():
                    root_folder = folder
                    break
            
            if not root_folder:
                root_folder = self.namespace.Folders.GetLast()
            
            # Count items
            print("   📊 Counting emails...")
            total_items = self._count_items_recursive(root_folder)
            print(f"   Found ~{total_items:,} items to process")
            
            # Extract
            with tqdm(total=total_items, desc=f"   Extracting", unit="email") as pbar:
                self.process_folder_recursive(root_folder, emails, pbar)
            
            # Remove PST from Outlook
            try:
                self.namespace.RemoveStore(root_folder)
            except:
                pass
            
            # CRITICAL: Force close and restart Outlook to release file locks
            print(f"   🔄 Releasing Outlook file locks...")
            try:
                self.outlook.Quit()
                import time
                time.sleep(3)  # Wait for Outlook to fully close
                # Reconnect for next PST
                if self.connect_outlook():
                    print(f"   ✅ Outlook reconnected")
            except:
                pass
            
            print(f"   ✅ Extracted {len(emails):,} unique emails from this PST")
            
            # Add to main collection
            self.all_emails.extend(emails)
            
        except Exception as e:
            print(f"   ❌ Error extracting PST: {e}")
            self.stats['errors'] += 1
        
        finally:
            # Delete temp PST file
            print(f"   🗑️  Deleting temporary PST...")
            try:
                if temp_pst.exists():
                    import time
                    time.sleep(2)  # Wait a moment for locks to release
                    temp_pst.unlink()
                    print(f"   ✅ Temporary file deleted")
            except Exception as e:
                print(f"   ⚠️  Could not delete temp file: {e}")
                print(f"   💡 File will remain in temp folder (manual cleanup needed)")
        
        return emails
    
    def extract_all_pst_files_sequential(self) -> List[Dict]:
        """Extract all PST files sequentially"""
        
        if not self.connect_outlook():
            return []
        
        # Find all PST files
        pst_files = sorted(list(self.pst_folder.glob("*.pst")))
        
        if not pst_files:
            print(f"❌ No PST files found in {self.pst_folder}")
            return []
        
        self.stats['pst_files_total'] = len(pst_files)
        
        print("\n" + "="*70)
        print("📧 SEQUENTIAL PST EXTRACTION")
        print("="*70)
        print(f"PST files to process: {len(pst_files)}")
        print(f"Strategy: Extract one at a time (saves disk space)")
        print(f"Temp folder: {self.temp_folder}")
        print("="*70)
        
        # Load existing progress if resuming
        progress_file = self.output_folder / "extraction_progress.json"
        if progress_file.exists():
            print("\n📂 Found existing progress file - resuming...")
            with open(progress_file, 'r', encoding='utf-8') as f:
                self.stats = json.load(f)
                self.all_emails = self.stats.get('emails_so_far', [])
                processed_files = set(self.stats.get('pst_progress', []))
                # Rebuild seen_message_ids
                self.seen_message_ids = set(e['message_id'] for e in self.all_emails)
                print(f"   Resuming with {len(self.all_emails):,} emails already extracted")
        else:
            processed_files = set()
        
        # Process each PST
        for idx, pst_path in enumerate(pst_files, 1):
            print(f"\n{'='*70}")
            print(f"PST {idx}/{len(pst_files)}")
            print(f"{'='*70}")
            
            # Skip if already processed
            if pst_path.name in processed_files:
                print(f"   ⏭️  Already processed - skipping")
                continue
            
            # Extract this PST
            emails_from_pst = self.extract_single_pst(pst_path)
            
            if len(emails_from_pst) > 0:
                self.stats['pst_files_processed'] += 1
                self.stats['total_emails_extracted'] = len(self.all_emails)
                self.stats['pst_progress'].append(pst_path.name)
                
                # Save progress after each PST
                self.save_progress()
                
                print(f"\n📈 Overall Progress:")
                print(f"   PSTs completed: {self.stats['pst_files_processed']}/{len(pst_files)}")
                print(f"   Total unique emails: {len(self.all_emails):,}")
                print(f"   Duplicates skipped: {self.stats['duplicates_skipped']:,}")
                print(f"   Errors encountered: {self.stats['errors']}")
            else:
                print(f"\n⚠️  No emails extracted from this PST")
                self.stats['pst_progress'].append(pst_path.name)  # Still mark as processed
                self.save_progress()
        
        return self.all_emails
    
    def save_progress(self):
        """Save progress after each PST"""
        progress_file = self.output_folder / "extraction_progress.json"
        
        progress_data = {
            **self.stats,
            'emails_so_far': self.all_emails,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, indent=2, ensure_ascii=False)
    
    def extract_msg_files(self) -> List[Dict]:
        """Extract MSG files"""
        if not self.root_folder or not self.root_folder.exists():
            return []
        
        print("\n" + "="*70)
        print("STEP 2: MSG FILE EXTRACTION")
        print("="*70)
        
        msg_files = list(self.root_folder.rglob("*.msg"))
        print(f"Found {len(msg_files):,} MSG files")
        
        if not msg_files:
            return []
        
        emails = []
        
        with tqdm(total=len(msg_files), desc="   Extracting MSG", unit="file") as pbar:
            for msg_path in msg_files:
                try:
                    mail_item = self.outlook.Session.OpenSharedItem(str(msg_path))
                    email_data = self.extract_email_metadata(mail_item)
                    if email_data:
                        emails.append(email_data)
                        self.stats['msg_files_processed'] += 1
                except:
                    pass
                pbar.update(1)
        
        print(f"   ✅ Extracted {len(emails):,} emails from MSG files")
        return emails
    
    def save_final_results(self):
        """Save final extraction results"""
        
        output_file = self.output_folder / "emails_extracted.json"
        print(f"\n💾 Saving final results to {output_file}...")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.all_emails, f, indent=2, ensure_ascii=False)
        
        # Update stats
        self.stats['end_time'] = datetime.now().isoformat()
        self.stats['final_email_count'] = len(self.all_emails)
        
        start = datetime.fromisoformat(self.stats['start_time'])
        end = datetime.fromisoformat(self.stats['end_time'])
        duration = (end - start).total_seconds() / 3600
        self.stats['duration_hours'] = round(duration, 2)
        
        stats_file = self.output_folder / "extraction_stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2)
        
        print("\n" + "="*70)
        print("📊 EXTRACTION COMPLETE!")
        print("="*70)
        print(f"PST files processed:     {self.stats['pst_files_processed']}/{self.stats['pst_files_total']}")
        print(f"MSG files processed:     {self.stats['msg_files_processed']}")
        print(f"Total unique emails:     {len(self.all_emails):,}")
        print(f"Duplicates skipped:      {self.stats['duplicates_skipped']:,}")
        print(f"Errors:                  {self.stats['errors']}")
        print(f"Duration:                {self.stats['duration_hours']:.2f} hours")
        print(f"\n✅ Results saved to: {output_file}")


def main():
    """Main execution"""
    
    # Configuration
    PST_FOLDER = Path(r"C:\Users\JemAndrew\Velitor\Communication site - Documents\LIS1.1\36- Chronological Email Run")
    ROOT_FOLDER = Path(r"C:\Users\JemAndrew\Velitor\Communication site - Documents\LIS1.1")
    OUTPUT_FOLDER = Path(r"C:\Users\JemAndrew\OneDrive - Velitor\EmailExtraction")  # Saves to OneDrive (uses 1TB quota!)
    TEMP_FOLDER = Path(r"C:\Temp\PST_Extraction")  # Temporary folder for one PST at a time
    
    print("="*70)
    print("📧 SEQUENTIAL PST EMAIL EXTRACTION")
    print("="*70)
    print(f"PST Folder:    {PST_FOLDER}")
    print(f"Temp Folder:   {TEMP_FOLDER} (7 GB needed)")
    print(f"Output Folder: {OUTPUT_FOLDER}")
    print("="*70)
    print("\n💡 This script extracts PSTs ONE AT A TIME to save disk space")
    print("   Only needs ~7-10 GB free (not 227 GB!)")
    print("="*70)
    
    # Check if PST folder exists
    if not PST_FOLDER.exists():
        print(f"\n❌ Error: PST folder not found: {PST_FOLDER}")
        return
    
    # Initialise extractor
    extractor = SequentialPSTExtractor(PST_FOLDER, OUTPUT_FOLDER, TEMP_FOLDER, ROOT_FOLDER)
    
    # Extract PSTs sequentially
    print("\n" + "="*70)
    print("STEP 1: SEQUENTIAL PST EXTRACTION")
    print("="*70)
    
    extractor.extract_all_pst_files_sequential()
    # Note: emails are already added to extractor.all_emails during extraction
    
    # Extract MSG files
    msg_emails = extractor.extract_msg_files()
    extractor.all_emails.extend(msg_emails)
    
    # Save final results
    if extractor.all_emails:
        extractor.save_final_results()
        print("\n🎉 Extraction complete!")
        print(f"\n📧 {len(extractor.all_emails):,} unique emails ready for Phase 5 analysis")
    else:
        print("\n❌ No emails extracted")


if __name__ == "__main__":
    main()