#!/usr/bin/env python3
"""
Tier 5: Analysis Cache Manager
Caches processed analysis outputs for instant retrieval
British English throughout

Location: src/memory/tier5_analysis_cache.py
"""

import json
import hashlib
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging


class AnalysisCacheManager:
    """
    Manages analysis output cache (Tier 5)
    
    Purpose:
        - Cache expensive Claude API analysis results
        - Instant retrieval of previous analyses
        - Avoid redundant API calls
        - Track analysis evolution over time
    
    Strategy:
        - Cache keyed by query + documents analysed
        - Store full Claude responses
        - Metadata for cache management
        - Automatic expiry of stale cache
        - Track which analyses are most valuable
    """
    
    def __init__(self, cache_path: Path, config):
        """
        Initialise Analysis Cache Manager
        
        Args:
            cache_path: Where to store cache
            config: System configuration
        """
        self.cache_path = Path(cache_path)
        self.config = config
        
        # Set up logging
        self.logger = logging.getLogger('AnalysisCache')
        
        # Create cache structure
        self.cache_path.mkdir(parents=True, exist_ok=True)
        
        # Cache database
        self.db_path = self.cache_path / "cache_metadata.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        # Cache expiry settings
        self.default_ttl_days = 30  # Time-to-live
        
        # Hit/miss statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'total_queries': 0
        }
    
    def _init_database(self):
        """Initialise cache metadata database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_cache (
                cache_key TEXT PRIMARY KEY,
                query_text TEXT NOT NULL,
                query_hash TEXT NOT NULL,
                document_ids TEXT,
                analysis_type TEXT,
                model_used TEXT,
                response_tokens INTEGER,
                cost_estimate REAL,
                created_date TEXT,
                last_accessed TEXT,
                access_count INTEGER DEFAULT 0,
                expiry_date TEXT,
                cache_filename TEXT,
                metadata_json TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache_stats (
                date TEXT PRIMARY KEY,
                hits INTEGER DEFAULT 0,
                misses INTEGER DEFAULT 0,
                cost_saved REAL DEFAULT 0.0
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_query_hash 
            ON analysis_cache(query_hash)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_expiry 
            ON analysis_cache(expiry_date)
        """)
        
        conn.commit()
        conn.close()
    
    def cache_analysis(self,
                      query_text: str,
                      analysis_result: Dict[str, Any],
                      document_ids: List[str] = None,
                      analysis_type: str = 'general',
                      model_used: str = 'claude-opus',
                      ttl_days: int = None) -> str:
        """
        Cache an analysis result
        
        Args:
            query_text: The query that was analysed
            analysis_result: The complete analysis output
            document_ids: Documents that were analysed
            analysis_type: Type of analysis (contradiction, pattern, etc.)
            model_used: Which Claude model was used
            ttl_days: Time-to-live in days (uses default if None)
            
        Returns:
            Cache key for retrieval
        """
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(query_text, document_ids)
            query_hash = self._hash_query(query_text)
            
            # Calculate expiry date
            ttl = ttl_days or self.default_ttl_days
            expiry_date = (datetime.now() + timedelta(days=ttl)).isoformat()
            
            # Estimate response tokens and cost
            response_tokens = self._estimate_tokens(str(analysis_result))
            cost_estimate = self._estimate_cost(response_tokens, model_used)
            
            # Save analysis result to file
            cache_filename = f"{cache_key}.json"
            cache_file_path = self.cache_path / cache_filename
            
            with open(cache_file_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, indent=2, ensure_ascii=False)
            
            # Store metadata in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO analysis_cache
                (cache_key, query_text, query_hash, document_ids, analysis_type,
                 model_used, response_tokens, cost_estimate, created_date,
                 last_accessed, access_count, expiry_date, cache_filename, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cache_key,
                query_text,
                query_hash,
                json.dumps(document_ids) if document_ids else None,
                analysis_type,
                model_used,
                response_tokens,
                cost_estimate,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                0,
                expiry_date,
                cache_filename,
                json.dumps({
                    'cached_at': datetime.now().isoformat(),
                    'ttl_days': ttl
                })
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Cached analysis: {cache_key} ({response_tokens} tokens, ~£{cost_estimate:.3f})")
            return cache_key
            
        except Exception as e:
            self.logger.error(f"Failed to cache analysis: {e}")
            return ""
    
    def get_cached_analysis(self,
                           query_text: str,
                           document_ids: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached analysis if available
        
        Args:
            query_text: The query being made
            document_ids: Documents being analysed
            
        Returns:
            Cached analysis result or None if not found/expired
        """
        self.stats['total_queries'] += 1
        
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(query_text, document_ids)
            
            # Check database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT cache_filename, expiry_date, response_tokens, cost_estimate
                FROM analysis_cache
                WHERE cache_key = ?
            """, (cache_key,))
            
            row = cursor.fetchone()
            
            if not row:
                self.stats['misses'] += 1
                self._update_daily_stats('miss', 0)
                conn.close()
                return None
            
            cache_filename, expiry_date, response_tokens, cost_estimate = row
            
            # Check if expired
            if datetime.fromisoformat(expiry_date) < datetime.now():
                self.logger.info(f"Cache expired: {cache_key}")
                self.stats['misses'] += 1
                self._update_daily_stats('miss', 0)
                conn.close()
                return None
            
            # Load cached result
            cache_file_path = self.cache_path / cache_filename
            
            if not cache_file_path.exists():
                self.logger.warning(f"Cache file missing: {cache_filename}")
                self.stats['misses'] += 1
                conn.close()
                return None
            
            with open(cache_file_path, 'r', encoding='utf-8') as f:
                cached_result = json.load(f)
            
            # Update access statistics
            cursor.execute("""
                UPDATE analysis_cache
                SET last_accessed = ?, access_count = access_count + 1
                WHERE cache_key = ?
            """, (datetime.now().isoformat(), cache_key))
            
            conn.commit()
            conn.close()
            
            # Record hit
            self.stats['hits'] += 1
            self._update_daily_stats('hit', cost_estimate)
            
            self.logger.info(f"Cache HIT: {cache_key} (saved ~£{cost_estimate:.3f})")
            
            # Add cache metadata to result
            cached_result['_cache_metadata'] = {
                'cache_hit': True,
                'tokens_saved': response_tokens,
                'cost_saved': cost_estimate,
                'cache_key': cache_key
            }
            
            return cached_result
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve from cache: {e}")
            self.stats['misses'] += 1
            return None
    
    def _update_daily_stats(self, stat_type: str, cost_saved: float):
        """Update daily cache statistics"""
        today = datetime.now().date().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get or create today's stats
        cursor.execute("""
            INSERT OR IGNORE INTO cache_stats (date, hits, misses, cost_saved)
            VALUES (?, 0, 0, 0.0)
        """, (today,))
        
        # Update stats
        if stat_type == 'hit':
            cursor.execute("""
                UPDATE cache_stats
                SET hits = hits + 1, cost_saved = cost_saved + ?
                WHERE date = ?
            """, (cost_saved, today))
        else:
            cursor.execute("""
                UPDATE cache_stats
                SET misses = misses + 1
                WHERE date = ?
            """, (today,))
        
        conn.commit()
        conn.close()
    
    def clear_old_cache(self, days: int = 30):
        """
        Clear cache entries older than specified days
        
        Args:
            days: Clear entries older than this many days
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get expired entries
        cursor.execute("""
            SELECT cache_key, cache_filename
            FROM analysis_cache
            WHERE created_date < ? OR expiry_date < ?
        """, (cutoff_date, datetime.now().isoformat()))
        
        expired_entries = cursor.fetchall()
        
        # Delete files and database entries
        deleted_count = 0
        for cache_key, cache_filename in expired_entries:
            # Delete cache file
            cache_file_path = self.cache_path / cache_filename
            if cache_file_path.exists():
                cache_file_path.unlink()
            
            # Delete database entry
            cursor.execute("DELETE FROM analysis_cache WHERE cache_key = ?", (cache_key,))
            deleted_count += 1
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Cleared {deleted_count} old cache entries")
        return deleted_count
    
    def invalidate_cache(self, cache_key: str = None, query_text: str = None):
        """
        Invalidate specific cache entry or all entries matching query
        
        Args:
            cache_key: Specific cache key to invalidate
            query_text: Invalidate all entries matching this query
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if cache_key:
            # Invalidate specific entry
            cursor.execute("""
                SELECT cache_filename FROM analysis_cache WHERE cache_key = ?
            """, (cache_key,))
            row = cursor.fetchone()
            
            if row:
                cache_filename = row[0]
                cache_file_path = self.cache_path / cache_filename
                if cache_file_path.exists():
                    cache_file_path.unlink()
                
                cursor.execute("DELETE FROM analysis_cache WHERE cache_key = ?", (cache_key,))
                self.logger.info(f"Invalidated cache: {cache_key}")
        
        elif query_text:
            # Invalidate all entries matching query
            query_hash = self._hash_query(query_text)
            
            cursor.execute("""
                SELECT cache_key, cache_filename
                FROM analysis_cache
                WHERE query_hash = ?
            """, (query_hash,))
            
            entries = cursor.fetchall()
            
            for cache_key, cache_filename in entries:
                cache_file_path = self.cache_path / cache_filename
                if cache_file_path.exists():
                    cache_file_path.unlink()
            
            cursor.execute("DELETE FROM analysis_cache WHERE query_hash = ?", (query_hash,))
            self.logger.info(f"Invalidated {len(entries)} cache entries for query")
        
        conn.commit()
        conn.close()
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total entries
        cursor.execute("SELECT COUNT(*) FROM analysis_cache")
        total_entries = cursor.fetchone()[0]
        
        # Total size
        total_size = sum(
            f.stat().st_size 
            for f in self.cache_path.glob("*.json")
        )
        
        # Total cost saved
        cursor.execute("SELECT SUM(cost_estimate) FROM analysis_cache")
        total_cost_saved = cursor.fetchone()[0] or 0
        
        # Hit rate
        hit_rate = (self.stats['hits'] / self.stats['total_queries'] * 100) \
            if self.stats['total_queries'] > 0 else 0
        
        # Most valuable cached analyses (by access count)
        cursor.execute("""
            SELECT query_text, access_count, cost_estimate
            FROM analysis_cache
            ORDER BY access_count DESC
            LIMIT 10
        """)
        most_valuable = [
            {
                'query': row[0][:100],
                'access_count': row[1],
                'cost_saved': row[1] * row[2]
            }
            for row in cursor.fetchall()
        ]
        
        # Recent performance (last 7 days)
        cursor.execute("""
            SELECT SUM(hits), SUM(misses), SUM(cost_saved)
            FROM cache_stats
            WHERE date >= date('now', '-7 days')
        """)
        week_stats = cursor.fetchone()
        week_hits, week_misses, week_cost_saved = week_stats if week_stats else (0, 0, 0)
        
        conn.close()
        
        return {
            'total_entries': total_entries,
            'total_size_mb': round(total_size / 1_000_000, 2),
            'total_cost_saved': round(total_cost_saved, 2),
            'hit_rate': round(hit_rate, 1),
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'total_queries': self.stats['total_queries'],
            'week_stats': {
                'hits': week_hits or 0,
                'misses': week_misses or 0,
                'cost_saved': round(week_cost_saved or 0, 2),
                'hit_rate': round((week_hits / (week_hits + week_misses) * 100) 
                                 if (week_hits + week_misses) > 0 else 0, 1)
            },
            'most_valuable': most_valuable
        }
    
    def _generate_cache_key(self, 
                           query_text: str,
                           document_ids: List[str] = None) -> str:
        """Generate cache key from query and documents"""
        # Normalise query text
        query_normalised = query_text.strip().lower()
        
        # Create compound key
        if document_ids:
            doc_ids_sorted = sorted(document_ids)
            compound = f"{query_normalised}|{'|'.join(doc_ids_sorted)}"
        else:
            compound = query_normalised
        
        return hashlib.sha256(compound.encode()).hexdigest()[:32]
    
    def _hash_query(self, query_text: str) -> str:
        """Hash query text for lookup"""
        query_normalised = query_text.strip().lower()
        return hashlib.md5(query_normalised.encode()).hexdigest()
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count"""
        return len(text) // 4
    
    def _estimate_cost(self, tokens: int, model: str) -> float:
        """Estimate cost based on tokens and model"""
        # Opus pricing: £15 per 1M input tokens
        cost_per_million = {
            'claude-opus': 15.0,
            'claude-sonnet': 3.0,
            'claude-haiku': 0.25
        }
        
        rate = cost_per_million.get(model, 15.0)
        return (tokens / 1_000_000) * rate
    
    def get_status(self) -> Dict[str, Any]:
        """Get Tier 5 status"""
        stats = self.get_cache_statistics()
        
        return {
            'tier': 5,
            'name': 'Analysis Cache',
            'active': True,
            'entries': stats['total_entries'],
            'size_mb': stats['total_size_mb'],
            'hit_rate': f"{stats['hit_rate']}%",
            'cost_saved': f"£{stats['total_cost_saved']:.2f}",
            'cache_path': str(self.cache_path)
        }
    
    def export_cache_report(self) -> Path:
        """Export detailed cache performance report"""
        report_path = self.cache_path / f"cache_report_{datetime.now().strftime('%Y%m%d')}.json"
        
        stats = self.get_cache_statistics()
        
        # Add daily breakdown
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT date, hits, misses, cost_saved
            FROM cache_stats
            ORDER BY date DESC
            LIMIT 30
        """)
        
        daily_stats = [
            {
                'date': row[0],
                'hits': row[1],
                'misses': row[2],
                'cost_saved': row[3],
                'hit_rate': round((row[1] / (row[1] + row[2]) * 100) 
                                 if (row[1] + row[2]) > 0 else 0, 1)
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        report = {
            'generated': datetime.now().isoformat(),
            'summary': stats,
            'daily_breakdown': daily_stats
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report_path