#!/usr/bin/env python3
"""
Multi-tier Memory System for Litigation Intelligence
Coordinates permanent, semantic, and analytical memory

Location: src/memory/__init__.py
British English throughout
"""

# Import in correct order to avoid circular dependencies
from .hierarchical_system import HierarchicalMemory, MemoryQuery, MemoryResult

# Import tier managers (these may not all be used directly)
try:
    from .tier1_project import ProjectKnowledgeManager
except ImportError as e:
    print(f"Warning: Could not import tier1_project: {e}")
    ProjectKnowledgeManager = None

try:
    from .tier2_vector import VectorStoreManager
except ImportError as e:
    print(f"Warning: Could not import tier2_vector (chromadb may not be installed): {e}")
    VectorStoreManager = None

try:
    from .tier3_graph_enhanced import EnhancedGraphManager
except ImportError as e:
    print(f"Warning: Could not import tier3_graph_enhanced: {e}")
    EnhancedGraphManager = None

try:
    from .tier4_cold_storage import ColdStorageManager
except ImportError as e:
    print(f"Warning: Could not import tier4_cold_storage: {e}")
    ColdStorageManager = None

try:
    from .tier5_analysis_cache import AnalysisCacheManager
except ImportError as e:
    print(f"Warning: Could not import tier5_analysis_cache: {e}")
    AnalysisCacheManager = None

__version__ = '1.0.0'

__all__ = [
    # Main system
    'HierarchicalMemory',
    'MemoryQuery',
    'MemoryResult',
    
    # Individual tier managers
    'ProjectKnowledgeManager',
    'VectorStoreManager',
    'EnhancedGraphManager',
    'ColdStorageManager',
    'AnalysisCacheManager',
]

# Module-level documentation
__doc__ = """
Hierarchical Memory System for Litigation Intelligence

Five-tier architecture:
    Tier 1: Claude Projects (100 docs, permanent, £0/query)
    Tier 2: Vector Database (semantic search, all documents)
    Tier 3: Knowledge Graph (relationships, patterns, contradictions)
    Tier 4: Cold Storage (encrypted vault, on-demand retrieval)
    Tier 5: Analysis Cache (processed outputs, fast access)

Usage:
    from memory import HierarchicalMemory, MemoryQuery
    
    memory = HierarchicalMemory(config, knowledge_graph)
    
    query = MemoryQuery(
        query_text="Find contradictions in witness statements",
        max_tokens=50000
    )
    
    results = memory.retrieve_relevant_context(query)
"""