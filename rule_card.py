#!/usr/bin/env python3
"""
Enhanced Rule Card Generator with UTF-8 encoding fix and better pattern extraction
Weaponises legal treatise text for Phase 0A
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict

class RuleCardGenerator:
    """
    Transform legal treatise text into weaponised rule cards for Lismore
    """
    
    def __init__(self):
        self.text_dir = Path("legal_resources/processed/text")
        self.metadata_dir = Path("legal_resources/processed/metadata")
        self.output_dir = Path("legal_resources/rule_cards")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Categories aligned with Phase 0A prompt requirements
        self.weapon_categories = {
            'offensive_doctrines': [],
            'procedural_weapons': [],
            'criminal_crossovers': [],
            'settlement_leverage': [],
            'arbitrator_psychology': []
        }
        
        # Track statistics
        self.stats = {
            'files_processed': 0,
            'patterns_found': 0,
            'nuclear_weapons': 0,
            'high_impact': 0
        }
    
    def generate_all_rule_cards(self):
        """
        Main pipeline to generate rule cards from all extracted texts
        """
        print("\n⚔️  RULE CARD GENERATION FOR PHASE 0A")
        print("=" * 60)
        
        # Process each text file
        text_files = list(self.text_dir.glob("*.txt"))
        print(f"Found {len(text_files)} extracted text files")
        
        # Process in batches to show progress
        for idx, text_file in enumerate(text_files, 1):
            if idx % 50 == 0:
                print(f"Progress: {idx}/{len(text_files)} files processed")
            
            try:
                # Load text with UTF-8 encoding
                with open(text_file, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                
                # Skip very short files
                if len(text) < 500:
                    continue
                
                # Load metadata if available
                metadata_file = self.metadata_dir / f"{text_file.stem}.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                else:
                    metadata = {'category': 'unknown', 'treatise': 'unknown'}
                
                # Extract weapons based on content type
                self.extract_all_weapons(text, metadata, text_file.stem)
                self.stats['files_processed'] += 1
                
            except Exception as e:
                print(f"Error processing {text_file.name}: {e}")
        
        print(f"\nProcessed {self.stats['files_processed']} files")
        print(f"Found {self.stats['patterns_found']} weapon patterns")
        
        # Save all rule cards
        self.save_rule_cards()
        self.generate_phase_0a_playbook()
    
    def extract_all_weapons(self, text: str, metadata: Dict, filename: str):
        """
        Extract all types of weapons from text
        """
        # Determine source treatise
        treatise = metadata.get('treatise', 'unknown')
        category = metadata.get('category', 'unknown')
        
        # Apply different extraction strategies based on source
        if 'arbitration' in category or 'Redfern' in treatise or 'Handbook' in treatise:
            self.extract_arbitration_weapons(text, metadata, filename)
        
        if 'civil' in category or 'White' in treatise:
            self.extract_civil_procedure_weapons(text, metadata, filename)
        
        if 'pleading' in category or 'Bullen' in treatise:
            self.extract_pleading_weapons(text, metadata, filename)
        
        # Always look for these universal weapons
        self.extract_adverse_inference_weapons(text, metadata, filename)
        self.extract_fraud_indicators(text, metadata, filename)
        self.extract_disclosure_violations(text, metadata, filename)
    
    def extract_adverse_inference_weapons(self, text: str, metadata: Dict, filename: str):
        """
        Extract adverse inference opportunities - our PRIME weapon
        """
        patterns = [
            # More comprehensive patterns
            r'(?:tribunal|court|arbitrator).{0,50}(?:may|can|should|must|will).{0,50}(?:draw|infer|make).{0,30}adverse inference[^.]*\.',
            r'adverse inference.{0,50}(?:where|when|if)[^.]*\.',
            r'failure to (?:produce|provide|disclose).{0,50}(?:document|evidence)[^.]*\.',
            r'(?:destruction|spoliation|suppression).{0,30}(?:of|evidence|document)[^.]*\.',
            r'withh[oe]ld.{0,30}document[^.]*\.',
            r'refus\w+ to produce[^.]*\.',
            r'no.{0,20}satisfactory explanation.{0,30}(?:for|why)[^.]*\.'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches[:2]:  # Limit per pattern
                if len(match) > 30:  # Meaningful content
                    rule_card = {
                        'doctrine': 'Adverse Inference - Document Withholding',
                        'source': f"{metadata.get('treatise', 'Legal Authority')} - {filename}",
                        'rule_text': self.clean_text(match),
                        'elements': [
                            'Documents within party control',
                            'Request for production made',
                            'Failure to produce',
                            'No adequate explanation',
                            'Inference would be logical'
                        ],
                        'process_holdings_vulnerability': 'Multiple document categories missing from disclosure',
                        'evidence_needed': 'Document requests and correspondence showing demands',
                        'devastation_rating': 'HIGH',
                        'deployment_timing': 'After disclosure phase closes',
                        'category': 'offensive_doctrines'
                    }
                    self.weapon_categories['offensive_doctrines'].append(rule_card)
                    self.stats['patterns_found'] += 1
    
    def extract_arbitration_weapons(self, text: str, metadata: Dict, filename: str):
        """
        Extract arbitration-specific procedural weapons
        """
        # IBA Rules on Taking of Evidence
        iba_patterns = [
            r'IBA Rules?.{0,50}Article 9[^.]*\.',
            r'Article 9.{0,50}adverse inference[^.]*\.',
            r'excluded from evidence.{0,50}if[^.]*\.'
        ]
        
        for pattern in iba_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches[:1]:
                if len(match) > 30:
                    rule_card = {
                        'doctrine': 'IBA Rules Article 9 - Evidence Exclusion',
                        'source': f"{metadata.get('treatise', 'Arbitration')} - {filename}",
                        'rule_text': self.clean_text(match),
                        'trigger': 'Privilege abuse, bad faith, procedural economy',
                        'devastation_rating': 'HIGH',
                        'category': 'procedural_weapons'
                    }
                    self.weapon_categories['procedural_weapons'].append(rule_card)
                    self.stats['patterns_found'] += 1
        
        # Tribunal powers
        tribunal_patterns = [
            r'tribunal.{0,30}(?:power|authority|discretion).{0,50}(?:to|may)[^.]*\.',
            r'arbitrator.{0,30}may.{0,30}(?:order|direct|require)[^.]*\.'
        ]
        
        for pattern in tribunal_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches[:1]:
                if 'sanction' in match.lower() or 'strike' in match.lower() or 'dismiss' in match.lower():
                    rule_card = {
                        'doctrine': 'Tribunal Sanction Powers',
                        'source': f"{metadata.get('treatise', 'Arbitration')} - {filename}",
                        'rule_text': self.clean_text(match),
                        'devastation_rating': 'NUCLEAR' if 'dismiss' in match.lower() else 'HIGH',
                        'category': 'procedural_weapons'
                    }
                    self.weapon_categories['procedural_weapons'].append(rule_card)
                    self.stats['patterns_found'] += 1
    
    def extract_civil_procedure_weapons(self, text: str, metadata: Dict, filename: str):
        """
        Extract CPR-based weapons from White Book
        """
        # Disclosure failures under CPR 31
        cpr_patterns = [
            r'CPR (?:31|Part 31)[^.]*\.',
            r'(?:duty|obligation) (?:of|to) disclos[^.]*\.',
            r'standard disclosure.{0,50}require[^.]*\.',
            r'specific disclosure[^.]*\.',
            r'unless order[^.]*\.',
            r'strike.{0,20}out.{0,50}(?:if|where|when)[^.]*\.'
        ]
        
        for pattern in cpr_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches[:2]:
                if len(match) > 30:
                    rule_card = {
                        'doctrine': 'CPR 31 - Disclosure Breach',
                        'source': f"White Book 2025 - {filename}",
                        'rule_text': self.clean_text(match),
                        'remedies': ['Unless order', 'Strike out', 'Adverse inference'],
                        'devastation_rating': 'HIGH',
                        'category': 'procedural_weapons'
                    }
                    self.weapon_categories['procedural_weapons'].append(rule_card)
                    self.stats['patterns_found'] += 1
        
        # Summary judgment
        summary_patterns = [
            r'summary judgment[^.]*\.',
            r'Part 24[^.]*\.',
            r'no real prospect.{0,30}(?:of|success)[^.]*\.'
        ]
        
        for pattern in summary_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches[:1]:
                if len(match) > 30:
                    rule_card = {
                        'doctrine': 'Summary Judgment - CPR Part 24',
                        'source': f"White Book 2025 - {filename}",
                        'rule_text': self.clean_text(match),
                        'test': 'No real prospect of successfully defending',
                        'devastation_rating': 'NUCLEAR',
                        'category': 'offensive_doctrines'
                    }
                    self.weapon_categories['offensive_doctrines'].append(rule_card)
                    self.stats['patterns_found'] += 1
                    self.stats['nuclear_weapons'] += 1
    
    def extract_pleading_weapons(self, text: str, metadata: Dict, filename: str):
        """
        Extract pleading-based attacks from Bullen & Leake
        """
        # Fraud pleading
        fraud_patterns = [
            r'fraud.{0,50}(?:must|shall|should).{0,30}(?:be|plead)[^.]*particular[^.]*\.',
            r'particulars of fraud[^.]*\.',
            r'deceit[^.]*element[^.]*\.',
            r'fraudulent misrepresentation[^.]*\.'
        ]
        
        for pattern in fraud_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches[:1]:
                if len(match) > 30:
                    rule_card = {
                        'doctrine': 'Fraud - Deceit Action',
                        'source': f"Bullen & Leake - {filename}",
                        'rule_text': self.clean_text(match),
                        'elements': [
                            'False representation of fact',
                            'Knowledge of falsity (or recklessness)',
                            'Intent that claimant rely',
                            'Claimant did rely',
                            'Damage resulted'
                        ],
                        'criminal_crossover': True,
                        'devastation_rating': 'NUCLEAR',
                        'category': 'criminal_crossovers'
                    }
                    self.weapon_categories['criminal_crossovers'].append(rule_card)
                    self.stats['patterns_found'] += 1
                    self.stats['nuclear_weapons'] += 1
        
        # Conspiracy
        conspiracy_patterns = [
            r'conspiracy.{0,50}(?:agreement|combination)[^.]*\.',
            r'unlawful means conspiracy[^.]*\.',
            r'lawful means conspiracy[^.]*\.'
        ]
        
        for pattern in conspiracy_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches[:1]:
                if len(match) > 30:
                    rule_card = {
                        'doctrine': 'Conspiracy to Injure',
                        'source': f"Bullen & Leake - {filename}",
                        'rule_text': self.clean_text(match),
                        'types': ['Unlawful means', 'Lawful means'],
                        'criminal_crossover': True,
                        'personal_liability': 'Directors personally liable',
                        'devastation_rating': 'NUCLEAR',
                        'category': 'criminal_crossovers'
                    }
                    self.weapon_categories['criminal_crossovers'].append(rule_card)
                    self.stats['patterns_found'] += 1
                    self.stats['nuclear_weapons'] += 1
    
    def extract_fraud_indicators(self, text: str, metadata: Dict, filename: str):
        """
        Extract fraud and criminal law crossovers
        """
        fraud_patterns = [
            r'(?:fraud|deceit|dishonest).{0,50}(?:element|requirement|prove)[^.]*\.',
            r'criminal.{0,30}(?:liability|prosecution|referral)[^.]*\.',
            r'money laundering[^.]*\.',
            r'bribery[^.]*\.',
            r'corrupt[^.]*practice[^.]*\.'
        ]
        
        for pattern in fraud_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches[:1]:
                if len(match) > 30 and 'fraud' in match.lower():
                    rule_card = {
                        'doctrine': 'Criminal Fraud Indicators',
                        'source': f"{metadata.get('treatise', 'Authority')} - {filename}",
                        'rule_text': self.clean_text(match),
                        'criminal_referral': True,
                        'devastation_rating': 'NUCLEAR',
                        'category': 'criminal_crossovers'
                    }
                    self.weapon_categories['criminal_crossovers'].append(rule_card)
                    self.stats['patterns_found'] += 1
    
    def extract_disclosure_violations(self, text: str, metadata: Dict, filename: str):
        """
        Extract disclosure violation consequences
        """
        disclosure_patterns = [
            r'(?:fail|refus).{0,30}(?:to|disclos|produc)[^.]*(?:sanction|strike|adverse)[^.]*\.',
            r'non.?compliance.{0,30}(?:with|disclos)[^.]*\.',
            r'breach.{0,30}(?:duty|obligation).{0,30}disclos[^.]*\.'
        ]
        
        for pattern in disclosure_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches[:1]:
                if len(match) > 30:
                    rule_card = {
                        'doctrine': 'Disclosure Non-Compliance Sanctions',
                        'source': f"{metadata.get('treatise', 'Authority')} - {filename}",
                        'rule_text': self.clean_text(match),
                        'consequences': ['Strike out', 'Adverse inference', 'Costs sanctions'],
                        'devastation_rating': 'HIGH',
                        'category': 'procedural_weapons'
                    }
                    self.weapon_categories['procedural_weapons'].append(rule_card)
                    self.stats['patterns_found'] += 1
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text for readability
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove page numbers
        text = re.sub(r'\b\d{1,4}\b(?:\s|$)', '', text)
        # Trim
        text = text.strip()
        # Limit length
        if len(text) > 500:
            text = text[:497] + '...'
        return text
    
    def save_rule_cards(self):
        """
        Save all rule cards to JSON files by category
        """
        print("\n💾 Saving Rule Cards")
        print("=" * 60)
        
        for category, cards in self.weapon_categories.items():
            if not cards:
                continue
            
            # Deduplicate based on doctrine
            seen = set()
            unique_cards = []
            for card in cards:
                doctrine_key = card.get('doctrine', '') + card.get('rule_text', '')[:50]
                if doctrine_key not in seen:
                    seen.add(doctrine_key)
                    unique_cards.append(card)
            
            # Save to JSON
            output_file = self.output_dir / f"{category}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(unique_cards, f, indent=2, ensure_ascii=False)
            
            print(f"  {category}: {len(unique_cards)} unique rule cards")
            
            # Update stats
            for card in unique_cards:
                if card.get('devastation_rating') == 'NUCLEAR':
                    self.stats['nuclear_weapons'] += 1
                elif card.get('devastation_rating') == 'HIGH':
                    self.stats['high_impact'] += 1
    
    def generate_phase_0a_playbook(self):
        """
        Generate strategic playbook with UTF-8 encoding
        """
        playbook_dir = Path("legal_resources/playbooks")
        playbook_dir.mkdir(parents=True, exist_ok=True)
        playbook_path = playbook_dir / "phase_0a_arsenal.md"
        
        content = []
        content.append("# PHASE 0A LEGAL ARSENAL - LISMORE VS PROCESS HOLDINGS")
        content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        content.append("=" * 60)
        content.append("")
        content.append("## NUCLEAR WEAPONS (Case-Ending)")
        content.append("")
        
        nuclear_count = 0
        for category, cards in self.weapon_categories.items():
            for card in cards:
                if card.get('devastation_rating') == 'NUCLEAR':
                    nuclear_count += 1
                    content.append(f"### {nuclear_count}. {card.get('doctrine', 'Unknown')}")
                    content.append(f"- Source: {card.get('source', 'Unknown')}")
                    content.append(f"- Category: {category.replace('_', ' ').title()}")
                    if card.get('criminal_crossover'):
                        content.append("- **CRIMINAL REFERRAL POSSIBLE**")
                    content.append("")
        
        content.append("## HIGH-IMPACT WEAPONS")
        content.append("")
        
        high_count = 0
        for category, cards in self.weapon_categories.items():
            for card in cards:
                if card.get('devastation_rating') == 'HIGH':
                    high_count += 1
                    content.append(f"### {high_count}. {card.get('doctrine', 'Unknown')}")
                    content.append(f"- Source: {card.get('source', 'Unknown')}")
                    content.append("")
        
        content.append("## STATISTICS")
        content.append(f"- Files processed: {self.stats['files_processed']}")
        content.append(f"- Weapon patterns found: {self.stats['patterns_found']}")
        content.append(f"- Nuclear weapons: {nuclear_count}")
        content.append(f"- High-impact weapons: {high_count}")
        content.append("")
        content.append("=" * 60)
        
        # Write with UTF-8 encoding
        with open(playbook_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        
        print(f"\n📋 Phase 0A Playbook saved to: {playbook_path}")
        print(f"   Nuclear weapons: {nuclear_count}")
        print(f"   High-impact weapons: {high_count}")
        print(f"   Total patterns extracted: {self.stats['patterns_found']}")

if __name__ == "__main__":
    generator = RuleCardGenerator()
    generator.generate_all_rule_cards()
    
    print("\n✅ Rule card generation complete!")
    print("🚀 Ready to run Phase 0A with weaponised legal framework!")
    print("\nNext step: python main.py --phase 0A")