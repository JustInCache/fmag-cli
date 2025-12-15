"""
FMAG - Focus Mode Ambience Generator

AI-powered ambient soundscapes for deep focus and productivity.
"""

__version__ = "1.0.0"
__author__ = "FMAG Contributors"

from .core import AmbienceGenerator
from .presets import PRESETS, get_preset, list_presets

__all__ = [
    "AmbienceGenerator",
    "PRESETS",
    "get_preset",
    "list_presets",
    "__version__",
]

