"""Pytest configuration for Indian Agri tests."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure src is on the path for imports
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
