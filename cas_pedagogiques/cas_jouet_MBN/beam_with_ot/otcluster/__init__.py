"""otcluster module."""

from .MemoizeWithCSVFile import MemoizeWithCSVFile
from .FunctionInsideDirectory import FunctionInsideDirectory
from .WcKeyChecker import WcKeyChecker
from .SLURMJobArrayFunction import (
    SLURMJobArrayFunction,
)
from .SLURMJobArrayMachine import SLURMJobArrayJob, SLURMJobArrayMachine

__all__ = [
    "MemoizeWithCSVFile",
    "SLURMJobArrayFunction",
    "SLURMJobArrayJob",
    "SLURMJobArrayMachine",
    "FunctionInsideDirectory",
    "WcKeyChecker",
]

try:
    from .DaskFunction import DaskFunction
    __all__.append("DaskFunction")
except ModuleNotFoundError as err:
    print(f"Warning: Unable to load DaskFunction. {err}")

__version__ = "1.1"
