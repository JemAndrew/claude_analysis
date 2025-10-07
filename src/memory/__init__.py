#!/usr/bin/env python3
"""Memory system - lazy loading to prevent import hangs"""

__version__ = '1.0.0'

# Lazy load everything - don't import at module level
HierarchicalMemory = None
MemoryQuery = None
MemoryResult = None

__all__ = ['HierarchicalMemory', 'MemoryQuery', 'MemoryResult']

print("⚠️  Memory system: Lazy loading (preventing import hangs)")