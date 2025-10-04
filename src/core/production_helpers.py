#!/usr/bin/env python3
"""
Production Helper Functions
Error handling, validation, and safety wrappers
British English throughout
"""

import logging
from functools import wraps
from typing import Callable, Any
import traceback

logger = logging.getLogger(__name__)


def safe_execution(fallback_value: Any = None):
    """
    Decorator for safe method execution with error handling
    
    Usage:
        @safe_execution(fallback_value={})
        def risky_method(self):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                logger.debug(traceback.format_exc())
                return fallback_value
        return wrapper
    return decorator


def validate_input(validator: Callable[[Any], bool], error_message: str):
    """
    Decorator for input validation
    
    Usage:
        @validate_input(lambda x: len(x) > 0, "Input must not be empty")
        def process(self, data):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Validate first positional argument after 'self'
            if len(args) > 1 and not validator(args[1]):
                raise ValueError(f"{func.__name__}: {error_message}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


class ProductionSafetyGuard:
    """Production safety features"""
    
    def __init__(self, config):
        self.config = config
        self.cost_tracking = {
            'total_spent_gbp': 0.0,
            'budget_limit_gbp': getattr(config, 'budget_limit_gbp', 200.0)
        }
    
    def check_budget(self, estimated_cost_gbp: float) -> bool:
        """
        Check if operation is within budget
        
        Returns False if budget would be exceeded
        """
        projected_total = self.cost_tracking['total_spent_gbp'] + estimated_cost_gbp
        
        if projected_total > self.cost_tracking['budget_limit_gbp']:
            logger.warning(
                f"Budget limit reached: £{self.cost_tracking['total_spent_gbp']:.2f} / "
                f"£{self.cost_tracking['budget_limit_gbp']:.2f}"
            )
            return False
        
        return True
    
    def record_cost(self, cost_gbp: float) -> None:
        """Record actual cost spent"""
        self.cost_tracking['total_spent_gbp'] += cost_gbp
        
        logger.info(
            f"Cost: £{cost_gbp:.2f} | "
            f"Total: £{self.cost_tracking['total_spent_gbp']:.2f} / "
            f"£{self.cost_tracking['budget_limit_gbp']:.2f}"
        )
    
    def get_remaining_budget(self) -> float:
        """Get remaining budget"""
        return self.cost_tracking['budget_limit_gbp'] - self.cost_tracking['total_spent_gbp']