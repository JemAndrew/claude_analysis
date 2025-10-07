#!/usr/bin/env python3
"""
Tier 4: Cold Storage Manager
Encrypted document vault for secure original storage
British English throughout

Location: src/memory/tier4_cold_storage.py
"""

import json
import hashlib
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

try:
    from cryptography.fernet import Fernet
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False
    print("WARNING: cryptography not installed. Install with: pip install cryptography")


class ColdStorageManager:
    """
    Manages encrypted cold storage (Tier 4)
    
    Purpose:
        - Secure storage of all original documents
        - Encrypted at rest
        - On-demand decryption and retrieval
        - Audit trail of all access
    
    Strategy:
        - Encrypt immediately upon ingestion
        - Store encrypted files in vault
        - Maintain metadata in SQLite
        - Decrypt only when specifically requested
        - Log all access for security
    """
    
    def __init__(self, vault_path: Path, config):
        """
        Initialise Cold Storage Manager
        
        Args:
            vault_path: Where to store encrypted vault
            config: System configuration
        """
        self.vault_path = Path(vault_path)
        self.config = config
        
        # Set up logging
        self.logger = logging.getLogger('ColdStorage')
        
        # Create vault structure
        self.encrypted_dir = self.vault_path / "encrypted"
        self.encrypted_dir.mkdir(parents=True, exist_ok=True)
        
        # Metadata database
        self.db_path = self.vault_path / "vault_metadata.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        # Encryption key management
        self.key_file = self.vault_path / "vault.key"
        self.encryption_key = self._load_or_create_key()
        
        if ENCRYPTION_AVAILABLE:
            self.cipher = Fernet(self.encryption_key)
        else:
            self.cipher = None
            self.logger.warning("Encryption not available - documents stored unencrypted!")
    
    def _init_database(self):
        """Initialise metadata database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vault_documents (
                doc_id TEXT PRIMARY KEY,
                original_filename TEXT NOT NULL,
                encrypted_filename TEXT NOT NULL,
                folder TEXT,
                doc_type TEXT,
                importance INTEGER,
                size_bytes INTEGER,
                encrypted_size_bytes INTEGER,
                original_hash TEXT,
                encrypted_hash TEXT,
                encryption_date TEXT,
                last_accessed TEXT,
                access_count INTEGER DEFAULT 0,
                metadata_json TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS access_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id TEXT,
                access_time TEXT,
                access_type TEXT,
                user TEXT,
                purpose TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_or_create_key(self) -> bytes:
        """Load existing encryption key or create new one"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                return f.read()
        
        # Generate new key
        if ENCRYPTION_AVAILABLE:
            key = Fernet.generate_key()
            
            # Save key securely
            with open(self.key_file, 'wb') as f:
                f.write(key)
            
            # Restrict permissions (Unix-like systems)
            try:
                self.key_file.chmod(0o600)
            except:
                pass
            
            self.logger.info("New encryption key generated")
            return key
        
        return b'NO_ENCRYPTION_AVAILABLE'
    
    def encrypt_and_store(self, 
                        file_path: Path = None,
                        doc_path: Path = None,
                        doc_metadata: Dict[str, Any] = None,
                        **kwargs) -> bool:
        """
        Encrypt document and store in vault
        Accepts both file_path and doc_path for compatibility
        
        Args:
            file_path: Path to original document (new naming)
            doc_path: Path to original document (old naming - deprecated)
            doc_metadata: Document metadata
            
        Returns:
            True if stored successfully
        """
        # Use whichever parameter was provided
        path = file_path or doc_path
        
        if not path or not path.exists():
            self.logger.error(f"Document not found: {path}")
            return False
        
        try:
            # Generate unique doc ID
            doc_id = self._generate_doc_id(path, doc_metadata or {})
            
            # Read original file
            with open(path, 'rb') as f:
                original_data = f.read()
            
            # Calculate original hash
            original_hash = hashlib.sha256(original_data).hexdigest()
            
            # Encrypt data
            if self.cipher:
                encrypted_data = self.cipher.encrypt(original_data)
            else:
                # No encryption available - store as-is (NOT RECOMMENDED)
                encrypted_data = original_data
                self.logger.warning(f"Storing {path.name} UNENCRYPTED")
            
            # Generate encrypted filename
            encrypted_filename = f"{doc_id}.enc"
            encrypted_path = self.encrypted_dir / encrypted_filename
            
            # Write encrypted file
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted_data)
            
            # Calculate encrypted hash
            encrypted_hash = hashlib.sha256(encrypted_data).hexdigest()
            
            # Store metadata in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO vault_documents
                (doc_id, original_filename, encrypted_filename, folder, doc_type,
                importance, size_bytes, encrypted_size_bytes, original_hash,
                encrypted_hash, encryption_date, last_accessed, access_count,
                metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc_id,
                path.name,
                encrypted_filename,
                doc_metadata.get('folder', 'unknown') if doc_metadata else 'unknown',
                doc_metadata.get('doc_type', 'unknown') if doc_metadata else 'unknown',
                doc_metadata.get('importance', 5) if doc_metadata else 5,
                len(original_data),
                len(encrypted_data),
                original_hash,
                encrypted_hash,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                0,
                json.dumps(doc_metadata) if doc_metadata else '{}'
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Stored in vault: {path.name} ({len(original_data)} bytes)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store {path.name if path else 'unknown'}: {e}")
            return False
    
    def retrieve_documents(self, 
                          doc_ids: List[str],
                          decrypt: bool = True) -> List[Dict[str, Any]]:
        """
        Retrieve and optionally decrypt documents
        
        Args:
            doc_ids: List of document IDs to retrieve
            decrypt: Whether to decrypt the documents
            
        Returns:
            List of document dicts with content
        """
        results = []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for doc_id in doc_ids:
            try:
                # Get metadata
                cursor.execute("""
                    SELECT encrypted_filename, original_filename, folder, 
                           doc_type, size_bytes, metadata_json
                    FROM vault_documents
                    WHERE doc_id = ?
                """, (doc_id,))
                
                row = cursor.fetchone()
                if not row:
                    self.logger.warning(f"Document not found: {doc_id}")
                    continue
                
                encrypted_filename, original_filename, folder, doc_type, size_bytes, metadata_json = row
                
                # Read encrypted file
                encrypted_path = self.encrypted_dir / encrypted_filename
                if not encrypted_path.exists():
                    self.logger.error(f"Encrypted file missing: {encrypted_filename}")
                    continue
                
                with open(encrypted_path, 'rb') as f:
                    encrypted_data = f.read()
                
                # Decrypt if requested
                if decrypt and self.cipher:
                    try:
                        decrypted_data = self.cipher.decrypt(encrypted_data)
                    except Exception as e:
                        self.logger.error(f"Decryption failed for {doc_id}: {e}")
                        continue
                else:
                    decrypted_data = encrypted_data
                
                # Update access stats
                cursor.execute("""
                    UPDATE vault_documents
                    SET last_accessed = ?, access_count = access_count + 1
                    WHERE doc_id = ?
                """, (datetime.now().isoformat(), doc_id))
                
                # Log access
                self._log_access(doc_id, 'retrieve', 'system', 'memory_retrieval')
                
                # Build result
                results.append({
                    'doc_id': doc_id,
                    'filename': original_filename,
                    'folder': folder,
                    'doc_type': doc_type,
                    'content': decrypted_data,
                    'size_bytes': size_bytes,
                    'metadata': json.loads(metadata_json) if metadata_json else {},
                    'tokens': size_bytes // 4  # Rough estimate
                })
                
            except Exception as e:
                self.logger.error(f"Failed to retrieve {doc_id}: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Retrieved {len(results)} documents from cold storage")
        return results
    
    def _log_access(self, 
                   doc_id: str,
                   access_type: str,
                   user: str,
                   purpose: str):
        """Log document access for audit trail"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO access_log (doc_id, access_time, access_type, user, purpose)
            VALUES (?, ?, ?, ?, ?)
        """, (
            doc_id,
            datetime.now().isoformat(),
            access_type,
            user,
            purpose
        ))
        
        conn.commit()
        conn.close()
    
    def verify_integrity(self, doc_id: str) -> Dict[str, bool]:
        """
        Verify document integrity using hashes
        
        Args:
            doc_id: Document to verify
            
        Returns:
            Dict with verification results
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT encrypted_filename, encrypted_hash
            FROM vault_documents
            WHERE doc_id = ?
        """, (doc_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {'found': False}
        
        encrypted_filename, stored_hash = row
        encrypted_path = self.encrypted_dir / encrypted_filename
        
        if not encrypted_path.exists():
            return {'found': True, 'file_exists': False}
        
        # Calculate current hash
        with open(encrypted_path, 'rb') as f:
            current_data = f.read()
        
        current_hash = hashlib.sha256(current_data).hexdigest()
        
        return {
            'found': True,
            'file_exists': True,
            'integrity_ok': current_hash == stored_hash,
            'stored_hash': stored_hash,
            'current_hash': current_hash
        }
    
    def get_vault_statistics(self) -> Dict[str, Any]:
        """Get statistics about the vault"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total documents
        cursor.execute("SELECT COUNT(*) FROM vault_documents")
        total_docs = cursor.fetchone()[0]
        
        # Total size
        cursor.execute("SELECT SUM(size_bytes), SUM(encrypted_size_bytes) FROM vault_documents")
        original_size, encrypted_size = cursor.fetchone()
        original_size = original_size or 0
        encrypted_size = encrypted_size or 0
        
        # Most accessed documents
        cursor.execute("""
            SELECT original_filename, access_count
            FROM vault_documents
            ORDER BY access_count DESC
            LIMIT 10
        """)
        most_accessed = cursor.fetchall()
        
        # Total accesses
        cursor.execute("SELECT COUNT(*) FROM access_log")
        total_accesses = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_documents': total_docs,
            'original_size_mb': round(original_size / 1_000_000, 2),
            'encrypted_size_mb': round(encrypted_size / 1_000_000, 2),
            'compression_ratio': round(encrypted_size / original_size, 3) if original_size > 0 else 0,
            'total_accesses': total_accesses,
            'avg_accesses_per_doc': round(total_accesses / total_docs, 2) if total_docs > 0 else 0,
            'most_accessed': [
                {'filename': filename, 'access_count': count}
                for filename, count in most_accessed
            ]
        }
    
    def _generate_doc_id(self, doc_path: Path, doc_metadata: Dict) -> str:
        """Generate unique document ID"""
        unique_str = f"{doc_metadata.get('folder', '')}/{doc_path.name}"
        return hashlib.md5(unique_str.encode()).hexdigest()
    
    def get_status(self) -> Dict[str, Any]:
        """Get Tier 4 status"""
        stats = self.get_vault_statistics()
        
        return {
            'tier': 4,
            'name': 'Cold Storage (Encrypted Vault)',
            'active': True,
            'encrypted': ENCRYPTION_AVAILABLE,
            'documents': stats['total_documents'],
            'size_mb': stats['encrypted_size_mb'],
            'total_accesses': stats['total_accesses'],
            'vault_path': str(self.vault_path)
        }
    
    def export_access_log(self, days: int = 30) -> Path:
        """Export recent access log for audit"""
        export_path = self.vault_path / f"access_log_{datetime.now().strftime('%Y%m%d')}.json"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT doc_id, access_time, access_type, user, purpose
            FROM access_log
            WHERE access_time >= datetime('now', '-' || ? || ' days')
            ORDER BY access_time DESC
        """, (days,))
        
        logs = []
        for row in cursor.fetchall():
            logs.append({
                'doc_id': row[0],
                'access_time': row[1],
                'access_type': row[2],
                'user': row[3],
                'purpose': row[4]
            })
        
        conn.close()
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
        
        return export_path