#!/usr/bin/env python3
"""
Memory System Initialisation - FIXED
Properly exports HierarchicalMemory, MemoryQuery, MemoryResult
British English throughout
"""

__version__ = '1.0.0'

# Import the classes from their modules
try:
    from memory.hierarchical_system import (
        HierarchicalMemory,
        MemoryQuery,
        MemoryResult
    )
    
    __all__ = ['HierarchicalMemory', 'MemoryQuery', 'MemoryResult']
    
    print("✅ Memory system classes loaded successfully")
    
except ImportError as e:
    # If dependencies missing, provide graceful fallback
    print(f"⚠️  Memory system import failed: {e}")
    print("   Run: pip install chromadb sentence-transformers")
    
    # Set to None so orchestrator can detect and use fallback
    HierarchicalMemory = None
    MemoryQuery = None
    MemoryResult = None
    
    __all__ = []

except Exception as e:
    print(f"❌ Unexpected error loading memory system: {e}")
    HierarchicalMemory = None
    MemoryQuery = None
    MemoryResult = None
    __all__ = []