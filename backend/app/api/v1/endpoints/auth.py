"""Compatibility import for the versioned auth module."""
import sys
from app.api import auth

sys.modules[__name__] = auth
