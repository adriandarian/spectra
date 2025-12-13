"""
Core module - Pure domain logic with no external dependencies.

This module contains:
- domain/: Entities, value objects, and domain enums
- ports/: Abstract interfaces that adapters must implement
- exceptions: Centralized exception hierarchy
- constants: Application-wide constants and defaults
"""

from .domain import *
from .ports import *
from .exceptions import *
from .constants import *

