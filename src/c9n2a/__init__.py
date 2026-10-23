"""c9n2a: C9orf72-Nature2Agent shared library.

Reproducibility utilities (paths, seeds, config, logging, provenance) plus the
scientific tools, data IO, and agent infrastructure used across the project.
"""
from __future__ import annotations

from . import config, logging_utils, paths, provenance, seeds

__version__ = "0.1.0"

__all__ = ["paths", "seeds", "config", "logging_utils", "provenance", "__version__"]
