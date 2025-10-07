#!/usr/bin/env python3
"""
Automated Document Prioritiser
Uses cheap Haiku to score documents by importance before expensive analysis
Solves the budget constraint: 21k docs = £2,198, but budget = £200
British English throughout - Lismore v Process Holdings
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple
from anthropic import Anthropic
import time


class DocumentPrioritiser:
    """Score and prioritise documents using lightweight AI analysis"""
    
    def __init__(self, config):
        self.config = config
        self.client = Anthropic(api_key=config.api_config['api_key'])
        self.scores_file = config.output_dir / "document_scores.json"
        self.scores_cache = self._load_scores_cache()
    
    def _load_scores_cache(self) -> Dict[str, float]:
        """Load previously scored documents to avoid rescoring"""
        if self.scores_file.exists():
            with open(self.scores_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_scores_cache(self):
        """Save scores to disk"""
        self.scores_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.scores_file, 'w', encoding='utf-8') as f:
            json.dump(self.scores_cache, f, indent=2, ensure_ascii=False)
    
    def score_document(self, doc: Dict) -> float:
        """
        Score a single document's importance (0-10)
        Uses filename + first 2000 chars only (cheap)
        
        Args:
            doc: Document dict with 'filename', 'content', 'metadata'
            
        Returns:
            float: Score from 0.0 (irrelevant) to 10.0 (critical)
        """
        
        filename = doc.get('metadata', {}).get('filename', doc.get('filename', 'unknown'))
        
        # Check cache first
        if filename in self.scores_cache:
            return self.scores_cache[filename]
        
        # Extract preview
        content = doc.get('content', '')
        preview = content[:2000]  # First 2000 chars only
        
        # Create scoring prompt
        prompt = f"""Score this document's importance for Lismore Capital v Process Holdings/VR Capital arbitration (0-10).

**Filename**: {filename}
**Preview**: {preview}

**Scoring criteria**:
- **10 (NUCLEAR)**: Smoking gun evidence of wrongdoing, fraud, or document withholding
- **9 (CRITICAL)**: Contracts, witness statements, board minutes, financial misrepresentation
- **8 (HIGH)**: Key parties mentioned (Lismore, Process Holdings, VR Capital, directors)
- **7 (SIGNIFICANT)**: Critical dates/events (2021-2024), financial transactions, disclosure obligations
- **6 (IMPORTANT)**: Communications between key parties, meeting notes, strategic planning
- **5 (RELEVANT)**: Background information on parties, industry context, related disputes
- **4 (USEFUL)**: General corporate documents, policies, procedures
- **3 (LOW)**: Tangentially related information, peripheral parties
- **2 (MINIMAL)**: Administrative documents, routine correspondence
- **1 (IRRELEVANT)**: Spam, duplicate, unrelated topics

**Priority document types** (score 8-10):
- Share Purchase Agreements, Shareholder Agreements
- Witness Statements, Affidavits, Expert Reports
- Board Minutes, Resolutions
- Financial statements, valuations, audit reports
- Document production schedules, disclosure lists
- Communications re: withholding evidence
- Emails between directors, solicitors, accountants

**WE ARE ARGUING FOR LISMORE** - prioritise evidence that:
- Shows Process Holdings breached duties
- Proves VR Capital exerted improper influence
- Demonstrates document withholding or spoliation
- Reveals financial misrepresentation
- Exposes conflicts of interest

Reply with ONLY a single number between 0 and 10. No explanation."""

        try:
            response = self.client.messages.create(
                model="claude-haiku-3.5-20241022",  # Cheapest model (£0.25/1M input)
                max_tokens=10,
                temperature=0.0,  # Consistent scoring
                messages=[{"role": "user", "content": prompt}]
            )
            
            score_text = response.content[0].text.strip()
            score = float(score_text)
            score = min(10.0, max(0.0, score))  # Clamp to 0-10
            
            # Cache the score
            self.scores_cache[filename] = score
            
            return score
            
        except Exception as e:
            print(f"  ⚠️  Error scoring {filename}: {e}")
            return 5.0  # Default medium score on error
    
    def prioritise_folder(self, 
                         folder_path: Path, 
                         top_n: int = 500,
                         min_score: float = 7.0) -> Tuple[List[Dict], List[Dict]]:
        """
        Score all documents in folder, return top N highest-scored documents
        
        Args:
            folder_path: Path to folder containing documents
            top_n: Number of top documents to return
            min_score: Minimum score threshold
            
        Returns:
            Tuple of (priority_docs, all_scored_docs)
        """
        
        from utils.document_loader import DocumentLoader
        
        loader = DocumentLoader(self.config)
        all_docs = loader.load_directory(folder_path)
        
        print(f"\n{'='*70}")
        print(f"DOCUMENT PRIORITISATION: {folder_path.name}")
        print(f"{'='*70}")
        print(f"Total documents: {len(all_docs)}")
        print(f"Scoring documents using Haiku 4 (cheap)...\n")
        
        scored_docs = []
        
        for i, doc in enumerate(all_docs):
            if i % 50 == 0:
                print(f"  Progress: {i}/{len(all_docs)} documents scored")
                self._save_scores_cache()  # Save periodically
            
            score = self.score_document(doc)
            
            scored_docs.append({
                **doc,
                'priority_score': score
            })
            
            # Tiny delay to avoid rate limits
            if i % 100 == 0 and i > 0:
                time.sleep(0.5)
        
        # Final save
        self._save_scores_cache()
        
        # Sort by score (descending)
        scored_docs.sort(key=lambda x: x['priority_score'], reverse=True)
        
        # Get priority documents
        priority_docs = [
            doc for doc in scored_docs 
            if doc['priority_score'] >= min_score
        ][:top_n]
        
        # Stats
        print(f"\n{'='*70}")
        print(f"PRIORITISATION COMPLETE")
        print(f"{'='*70}")
        print(f"Documents scored: {len(scored_docs)}")
        print(f"Score distribution:")
        print(f"  Nuclear (9-10):    {len([d for d in scored_docs if d['priority_score'] >= 9.0])}")
        print(f"  Critical (8-9):    {len([d for d in scored_docs if 8.0 <= d['priority_score'] < 9.0])}")
        print(f"  High (7-8):        {len([d for d in scored_docs if 7.0 <= d['priority_score'] < 8.0])}")
        print(f"  Significant (6-7): {len([d for d in scored_docs if 6.0 <= d['priority_score'] < 7.0])}")
        print(f"  Lower (<6):        {len([d for d in scored_docs if d['priority_score'] < 6.0])}")
        print(f"\nPriority documents selected: {len(priority_docs)}")
        print(f"  (Score >= {min_score}, max {top_n} documents)")
        
        return priority_docs, scored_docs
    
    def save_priority_list(self, 
                          priority_docs: List[Dict], 
                          output_file: Path):
        """Save priority document list for review"""
        
        output_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_priority_docs': len(priority_docs),
            'documents': [
                {
                    'filename': doc.get('metadata', {}).get('filename', 'unknown'),
                    'score': doc.get('priority_score', 0.0),
                    'source_folder': doc.get('metadata', {}).get('source_folder', 'unknown'),
                    'doc_type': doc.get('metadata', {}).get('classification', 'general'),
                    'has_dates': doc.get('metadata', {}).get('has_dates', False),
                    'has_amounts': doc.get('metadata', {}).get('has_amounts', False)
                }
                for doc in priority_docs
            ]
        }
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nPriority list saved: {output_file}")
    
    def estimate_prioritisation_cost(self, doc_count: int) -> Dict:
        """
        Estimate cost of prioritising documents
        
        Args:
            doc_count: Number of documents to score
            
        Returns:
            Dict with cost estimates
        """
        # Haiku pricing
        input_cost_per_1m = 0.25  # £0.25 per 1M input tokens
        
        # Estimate tokens per scoring call
        # ~500 chars preview + 200 char prompt = ~175 tokens
        tokens_per_doc = 175
        total_tokens = doc_count * tokens_per_doc
        
        cost_gbp = (total_tokens / 1_000_000) * input_cost_per_1m
        
        # Estimate time (Haiku is fast: ~50 docs/minute)
        estimated_minutes = doc_count / 50
        
        return {
            'document_count': doc_count,
            'total_tokens': total_tokens,
            'cost_gbp': round(cost_gbp, 2),
            'estimated_time_minutes': round(estimated_minutes, 1),
            'estimated_time_hours': round(estimated_minutes / 60, 2)
        }
    
    def get_priority_summary(self, scored_docs: List[Dict]) -> Dict:
        """
        Get summary statistics about scored documents
        
        Args:
            scored_docs: List of documents with priority_score
            
        Returns:
            Summary statistics dict
        """
        if not scored_docs:
            return {}
        
        scores = [doc.get('priority_score', 0.0) for doc in scored_docs]
        
        return {
            'total_documents': len(scored_docs),
            'average_score': round(sum(scores) / len(scores), 2),
            'max_score': max(scores),
            'min_score': min(scores),
            'nuclear_count': len([s for s in scores if s >= 9.0]),
            'critical_count': len([s for s in scores if 8.0 <= s < 9.0]),
            'high_count': len([s for s in scores if 7.0 <= s < 8.0]),
            'significant_count': len([s for s in scores if 6.0 <= s < 7.0]),
            'low_count': len([s for s in scores if s < 6.0])
        }
    
    def export_top_documents_by_category(self, 
                                        scored_docs: List[Dict], 
                                        output_dir: Path,
                                        top_n_per_category: int = 50):
        """
        Export top N documents for each category (contracts, witness statements, etc.)
        
        Args:
            scored_docs: List of scored documents
            output_dir: Directory to save category files
            top_n_per_category: How many docs per category
        """
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Group by classification
        by_category = {}
        for doc in scored_docs:
            category = doc.get('metadata', {}).get('classification', 'general')
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(doc)
        
        # Sort each category by score and export top N
        for category, docs in by_category.items():
            sorted_docs = sorted(docs, key=lambda x: x.get('priority_score', 0.0), reverse=True)
            top_docs = sorted_docs[:top_n_per_category]
            
            category_file = output_dir / f"top_{category}_documents.json"
            
            with open(category_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'category': category,
                    'total_in_category': len(docs),
                    'top_n': len(top_docs),
                    'documents': [
                        {
                            'filename': d.get('metadata', {}).get('filename', 'unknown'),
                            'score': d.get('priority_score', 0.0),
                            'source_folder': d.get('metadata', {}).get('source_folder', '')
                        }
                        for d in top_docs
                    ]
                }, f, indent=2, ensure_ascii=False)
            
            print(f"  Exported top {len(top_docs)} {category} documents")
    
    def create_prioritisation_report(self, 
                                    scored_docs: List[Dict],
                                    priority_docs: List[Dict],
                                    output_file: Path):
        """
        Create comprehensive prioritisation report
        
        Args:
            scored_docs: All scored documents
            priority_docs: Selected priority documents
            output_file: Path to save report
        """
        
        summary = self.get_priority_summary(scored_docs)
        
        report = f"""# DOCUMENT PRIORITISATION REPORT
## Lismore Capital v Process Holdings

**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}
**Total Documents Scored**: {len(scored_docs)}
**Priority Documents Selected**: {len(priority_docs)}

---

## SCORE DISTRIBUTION

| Score Range | Category | Count | Percentage |
|------------|----------|-------|------------|
| 9.0 - 10.0 | Nuclear  | {summary['nuclear_count']} | {summary['nuclear_count']/len(scored_docs)*100:.1f}% |
| 8.0 - 8.9  | Critical | {summary['critical_count']} | {summary['critical_count']/len(scored_docs)*100:.1f}% |
| 7.0 - 7.9  | High     | {summary['high_count']} | {summary['high_count']/len(scored_docs)*100:.1f}% |
| 6.0 - 6.9  | Significant | {summary['significant_count']} | {summary['significant_count']/len(scored_docs)*100:.1f}% |
| 0.0 - 5.9  | Lower    | {summary['low_count']} | {summary['low_count']/len(scored_docs)*100:.1f}% |

**Average Score**: {summary['average_score']}

---

## TOP 20 PRIORITY DOCUMENTS

| Rank | Filename | Score | Type |
|------|----------|-------|------|
"""
        
        for i, doc in enumerate(priority_docs[:20], 1):
            filename = doc.get('metadata', {}).get('filename', 'unknown')
            score = doc.get('priority_score', 0.0)
            doc_type = doc.get('metadata', {}).get('classification', 'general')
            report += f"| {i} | {filename[:50]} | {score:.1f} | {doc_type} |\n"
        
        report += f"""
---

## BUDGET IMPACT

**Original Analysis Cost** (all {len(scored_docs)} documents):
- Estimated: £{int(len(scored_docs) * 2198 / 21264)}

**Prioritised Analysis Cost** ({len(priority_docs)} documents):
- Estimated: £{int(len(priority_docs) * 2198 / 21264)}

**Cost Savings**: £{int(len(scored_docs) * 2198 / 21264) - int(len(priority_docs) * 2198 / 21264)}

---

## NEXT STEPS

1. Review priority document list
2. Run: `python main.py estimate` to verify costs
3. Run: `python main.py phase0` to build knowledge foundation
4. Run: `python main.py phase1` to analyse priority documents

---

*Report generated by Document Prioritiser*
*Lismore Litigation Intelligence System*
"""
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\nPrioritisation report saved: {output_file}")