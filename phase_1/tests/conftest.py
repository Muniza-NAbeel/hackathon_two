"""
Pytest Configuration - Phase I Todo Application

Configures pytest to find src modules properly.
"""

import sys
from pathlib import Path

# Add phase_1 directory to Python path so 'src' module can be imported
phase1_dir = Path(__file__).parent.parent
sys.path.insert(0, str(phase1_dir))
