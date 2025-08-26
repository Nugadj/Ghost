"""
Ghost Protocol - Python-based Adversary Simulation Platform

A comprehensive C2 framework for security training and red team exercises.
"""

__version__ = "1.0.0"
__author__ = "Ghost Protocol Team"
__description__ = "Python-based adversary simulation platform for security training and testing"

from .core import Config, EventBus, setup_logging

__all__ = ["Config", "EventBus", "setup_logging"]
