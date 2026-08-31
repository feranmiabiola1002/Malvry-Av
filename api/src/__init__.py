"""
Malvryx AV - Next-Generation Antivirus Engine
"""

__version__ = "1.0.0"
__author__ = "Malvryx"
__license__ = "MIT"

from .main import MalvryxAV
from .scanner import Scanner
from .behavior import BehaviorMonitor
from .quarantine import Quarantine
from .watcher import FileWatcher
from .database import Database
from .config import *

__all__ = [
    'MalvryxAV',
    'Scanner',
    'BehaviorMonitor',
    'Quarantine',
    'FileWatcher',
    'Database',
]
