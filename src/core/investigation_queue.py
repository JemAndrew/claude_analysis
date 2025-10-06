#!/usr/bin/env python3
"""
Investigation Queue for Managing Autonomous Investigations
Handles priority-based investigation scheduling with parent-child relationships
British English throughout
"""

from queue import PriorityQueue
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import hashlib


@dataclass
class Investigation:
    """Represents an investigation thread"""
    topic: str
    priority: int  # 1-10
    trigger_data: Dict
    parent_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_id(self) -> str:
        """Generate unique investigation ID"""
        timestamp = self.created_at.strftime('%Y%m%d_%H%M%S_%f')
        topic_hash = hashlib.md5(self.topic.encode()).hexdigest()[:8]
        return f"inv_{timestamp}_{topic_hash}"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialisation"""
        return {
            'id': self.get_id(),
            'topic': self.topic,
            'priority': self.priority,
            'trigger_data': self.trigger_data,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat()
        }
    
    def __lt__(self, other):
        """For priority queue comparison (higher priority = processed first)"""
        return self.priority > other.priority


class InvestigationQueue:
    """Priority queue for managing investigation threads"""
    
    def __init__(self):
        self.queue = PriorityQueue()
        self.active = {}
        self.completed = []
        self.completed_by_id = {}
    
    def add(self, investigation: Investigation):
        """
        Add investigation to queue
        Higher priority investigations are processed first
        """
        self.queue.put(investigation)
    
    def pop(self) -> Optional[Investigation]:
        """
        Get highest priority investigation from queue
        Moves investigation to active tracking
        """
        if self.queue.empty():
            return None
        
        investigation = self.queue.get()
        self.active[investigation.get_id()] = investigation
        return investigation
    
    def mark_complete(self, investigation: Investigation):
        """
        Mark investigation as complete
        Moves from active to completed tracking
        """
        inv_id = investigation.get_id()
        if inv_id in self.active:
            self.completed.append(self.active[inv_id])
            self.completed_by_id[inv_id] = self.active[inv_id]
            del self.active[inv_id]
    
    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return self.queue.empty()
    
    def get_status(self) -> Dict:
        """
        Get current queue status
        Returns counts for queued, active, and completed investigations
        """
        return {
            'queued': self.queue.qsize(),
            'active': len(self.active),
            'completed': len(self.completed)
        }
    
    def get_active_investigations(self) -> List[Investigation]:
        """Get list of currently active investigations"""
        return list(self.active.values())
    
    def get_completed_investigations(self) -> List[Investigation]:
        """Get list of completed investigations"""
        return self.completed
    
    def find_children(self, parent_id: str) -> List[Investigation]:
        """
        Find all investigations spawned by a parent investigation
        Searches both active and completed investigations
        """
        children = []
        
        # Search active investigations
        for inv in self.active.values():
            if inv.parent_id == parent_id:
                children.append(inv)
        
        # Search completed investigations
        for inv in self.completed:
            if inv.parent_id == parent_id:
                children.append(inv)
        
        return children
    
    def get_investigation_tree(self, root_id: str) -> Dict:
        """
        Get complete investigation tree starting from root
        Returns hierarchical structure showing parent-child relationships
        """
        def build_tree(inv_id: str) -> Dict:
            # Find investigation
            investigation = None
            if inv_id in self.active:
                investigation = self.active[inv_id]
            else:
                for inv in self.completed:
                    if inv.get_id() == inv_id:
                        investigation = inv
                        break
            
            if not investigation:
                return None
            
            # Build tree node
            node = investigation.to_dict()
            children = self.find_children(inv_id)
            
            if children:
                node['children'] = [build_tree(child.get_id()) for child in children]
            
            return node
        
        return build_tree(root_id)
    
    def get_statistics(self) -> Dict:
        """
        Get detailed queue statistics
        Returns metrics useful for monitoring and optimisation
        """
        stats = self.get_status()
        
        if self.completed:
            # Calculate average priority of completed investigations
            avg_priority = sum(inv.priority for inv in self.completed) / len(self.completed)
            
            # Count root vs child investigations
            root_investigations = sum(1 for inv in self.completed if inv.parent_id is None)
            child_investigations = len(self.completed) - root_investigations
            
            stats['average_priority'] = round(avg_priority, 2)
            stats['root_investigations'] = root_investigations
            stats['child_investigations'] = child_investigations
        
        return stats
    
    def clear(self):
        """
        Clear all investigations from queue
        WARNING: This removes all queued, active, and completed investigations
        """
        self.queue = PriorityQueue()
        self.active.clear()
        self.completed.clear()
    
    def export_state(self) -> Dict:
        """
        Export complete queue state for checkpointing
        Returns serialisable state that can be restored later
        """
        return {
            'queued': [inv.to_dict() for inv in list(self.queue.queue)],
            'active': [inv.to_dict() for inv in self.active.values()],
            'completed': [inv.to_dict() for inv in self.completed],
            'statistics': self.get_statistics()
        }