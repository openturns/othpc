"""otwrap module."""

from .OpenTURNSWrapper import OpenTURNSWrapper
from .SLURMJobArrayWrapper import SLURMJobArrayWrapper


__all__ = [
    "OpenTURNSWrapper",
    "SLURMJobArrayWrapper"
]
__version__ = "0.0.1"
