"""othpc module."""

from .dask_function import DaskFunction
from .utils import TempWorkDir

__all__ = [
    "DaskFunction",
    "TempWorkDir"
]
__version__ = "0.0.1"
